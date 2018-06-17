import sys

PARTITION_N = 3  # number of partitions
WAREHOUSE_N = 1  # number of warehouses, SPECIAL FOR TPCC


def calcE(f, n):
	"""
	Calculate expected number of copies of a tuple.
	Formula as shown in Appendix A.
	Actually n is constant, so basically it's a function of f.

    Args:
        f: Frequency of that tuple.
        n: The number of partitions.

    Returns:
        A float number representing the expectation.
    """
	if f == 0:
		return 1.0

	max_x = min(f, n)
	stirling = [[-1 for j in range(max_x+1)] for i in range(n+1)]
	for i in range(1, n+1):
		stirling[i][0], stirling[i][1] = 0, 1
		if max_x >= i:
			stirling[i][i] = 1
	for i in range(3, n+1):
		for j in range(1, min(i, max_x+1)):
			stirling[i][j] = stirling[i-1][j-1] + j * stirling[i-1][j]
	
	prob = [-1.0]
	for x in range(1, max_x+1):
		value = 1.0
		for i in range(n-x+1, n+1):
			value *= i
		value = value * stirling[n][x] / (n ** f)
		prob.append(value)

	ans = 0.0
	for x in range(1, max_x+1):
		ans += x * prob[x]

	return ans


def calcTimer(frequency, table_size, exp_dict):
	"""
	Calculate redundancy factor of an eage in the graph.
	Formula as shown in Appendix A.

    Args:
        frequency: A list of the tuple frequencies in referencing table.
        table_size: Size of referencing table.
        exp_dict: Dict to store preprocessed E.

    Returns:
        A float number representing the r(e).
    """
	expectation = 0.0
	for f in frequency:
		if not f in exp_dict:
			exp_dict[f] = calcE(f, PARTITION_N)
		expectation += exp_dict[f]
	return expectation / table_size


class Node(object):
	"""
	Node in the graph of schema, correspond with a table.

    Attributes:
        name: Name of the table.
        label: Size of the table.
        neighbors: List of Nodes which are neighbors of this one.
        frequencies: List of frequencies of every tuple of join key.
    """
	def __init__(self, name, x, frequencies):
		self.name = name
		self.label = x
		self.neighbors = []
		self.frequencies = frequencies

	def addNeighbor(self, node):
		"""Add a neighbor Node to neighbors."""
		self.neighbors.append(node)


class PartitionConfig(object):
	"""
	Partitioning config of the schema.
	As defined in Listing 1.

    Attributes:
        estimatedSize: Total size of all tables after partitioning.
        timer: List of size timer when partitioning, r(e) stored in referencing table.
        exp_dict: Dict storing preprocessed E, from f to value.
        nodes: Dict storing all nodes in the graph, from name to Node.
        index_dict: Dict matching from index to name.
        seed: Number of seed table from which the partitioning starts, HASH partitioned.
    """
	def __init__(self, size, num, nodes, index_dict, seed_num):
		self.estimatedSize = size
		self.timer = [1 for i in range(num)]
		self.exp_dict = {}
		self.nodes = nodes
		self.index_dict = index_dict
		self.seed = seed_num

	def addScheme(self, to_num, from_num, method):
		"""
		Partition a new table and add into current configuration.

	    Args:
	        to_num: Referencing table index, seed table if method == 'HASH'.
	        from_num: Referemced table index, -1 if method == 'HASH'.
	        method: Partitioning method, 'HASH' or 'PREF'.
	    """
		if method == 'HASH':
			self.timer[to_num] = 1
		elif method == 'PREF':
			to_table = self.nodes[self.index_dict[to_num]]
			from_table = self.nodes[self.index_dict[from_num]]
			ratio = calcTimer(to_table.frequencies, to_table.label, self.exp_dict)
			self.timer[to_num] = self.timer[from_num] * ratio
		else:
			print 'Partitioning plan' + method + 'doesn\'t exist!'

	def estimate(self):
		"""Calculate and refresh estimatedSize."""
		ans = 0.0
		for i in range(len(self.nodes)):
			table = self.nodes[self.index_dict[i]]
			ans += table.label * self.timer[i]
		self.estimatedSize = ans


def input(filename):
	"""
	Read from a file basic information about the database schema.
	Input format like:
	tables
	table_name1 size1 tuple_values11Xfrequency11/tuple_values12Xfrequency12...
	table_name2 size2 tuple_values21Xfrequency21/tuple_values22Xfrequency22...
	...

	fks
	table_name1 table_name2
	table_name3 table_name4
	...

    Args:
        filename: The name of the file where information stores.

    Returns:
        ans: Dict of table information, from name to Node.
        eages: List of eage informaton, format like [table1, table2, weight].
    """
	r = open(filename, 'r')
	all_data = r.read().strip()
	tables, fks = all_data.split('\n\n')
	tables = tables.split('\n')[1:]
	fks = fks.split('\n')[1:]
	ans = {} 
	eages = []
	for table in tables:
		name, x, fre = table.split(' ')
		final_fre = []
		processed_fre = [i.split('X') for i in fre.split('/')]
		for i in processed_fre:
			final_fre.extend([int(i[1]) for j in range(int(i[0]))])
		# SPECIAL FOR TPCC
		if name == 'item':
			ans[name] = Node(name, int(x), final_fre)
		else:
			ans[name] = Node(name, int(x) * WAREHOUSE_N, final_fre * WAREHOUSE_N)
	for fk in fks:
		t1, t2 = fk.split(' ')
		eages.append([t1, t2, min(ans[t1].label, ans[t2].label)])
		ans[t1].addNeighbor(ans[t2])
		ans[t2].addNeighbor(ans[t1])

	return ans, eages


def hasCycle(x, prev, eages, visited):
	"""
	Determine whether or not the graph has cycles.

    Args:
    	x: current visiting node.
        prev: previous visited node.
        eages: List of neighbors information, format like [neighbor1, neighbor2...]
        visited: List of flags whether or not node is visited.

    Returns:
        True if has cycle. False if not.
    """
	if visited[x]:
		return True
	visited[x] = True
	for y in eages[x]:
		if y != prev:
			if hasCycle(y, x, eages, visited):
				return True
	visited[x] = False
	return False


def findMAST(eages, nodes):
	"""
	Find the MAST (Maximum Spanning Tree) of the graph with weights.
	MAST is an acyclic graph.

    Args:
        eages: List of eages in the graph, format like [table1, table2, weight].
        nodes: Dict of nodes information, from name to Node.

    Returns:
        ans_eages: List of eages in MAST, format like [table1, table2, weight].
        DL: Data Locality ratio, formula as shown in part 3.2.
    """
	ans_eages = []
	num = len(nodes)
	sorted_eages = sorted(eages, key=lambda x: -x[2])
	for eage in sorted_eages:
		ans_eages.append(eage)
		local_eages = [[] for i in range(num)]
		visited = [False for i in range(num)]
		for triple in ans_eages:
			local_eages[triple[0]].append(triple[1])
			local_eages[triple[1]].append(triple[0])

		for i in range(num):
			if not visited[i] and hasCycle(i, -1, local_eages, visited):
				ans_eages.pop()
				break
		if len(ans_eages) == num - 1:
			break

	sum_origin = sum(x[2] for x in eages)
	sum_co = sum(x[2] for x in ans_eages)
	DL = float(sum_co) / float(sum_origin)

	return ans_eages, DL


def getGraph(filename):
	"""
	Get all information and parameters needed of the database schema.

    Args:
        filename: The name of the file where information stores.

    Returns:
    	nodes: Dict of nodes information, from name to Node.
        eages: List of eage informaton, format like [table1, table2, weight].
        MAST_eages: List of eages in MAST, format like [table1, table2, weight].
        DL: Data Locality ratio, formula as shown in part 3.2.
        name_dict: Dict matching from name to index.
        index_dict: Dict matching from index to name.
    """
	nodes, eages = input(filename)
	names = nodes.keys()
	name_dict = {}
	index_dict = {}
	counter = 0
	for name in names:
		name_dict[name] = counter
		index_dict[counter] = name
		counter += 1
	for eage in eages:
		eage[0] = name_dict[eage[0]]
		eage[1] = name_dict[eage[1]]
	MAST_eages, DL = findMAST(eages, nodes)
	return nodes, eages, MAST_eages, DL, name_dict, index_dict


def addPREF(eages_list, i, pc, valid):
	"""
	Add PREF partitionings into the partition configuration recursively.
	As defined in Listing 1.

    Args:
        eages_list: List of neighbors of all tables, format like [(neighbor1, weight1)...].
        i: Referenced table index.
        pc: PartitionConfig storing information of the partitioning scheme.
        valid: List of flags of whether or not the table is visited.
    """
	for item in eages_list[i]:
		if not valid[item[0]]:
			continue
		pc.addScheme(item[0], i, 'PREF')
		valid[item[0]] = False
		addPREF(eages_list, item[0], pc, valid)


def findOptimalPC(MAST_eages, nodes, index_dict):
	"""
	Find the best partitioning configuration based on its size, DR in the other word.
	As defined in Listing 1.

    Args:
        nodes: Dict of nodes information, from name to Node.
        MAST_eages: List of eages in MAST, format like [table1, table2, weight].
        index_dict: Dict matching from index to name.

    Returns:
        optimalPC: The best PartitionConfig.
    """
	num = len(nodes)
	eages_list = [[] for i in range(num)]
	for triple in MAST_eages:
		eages_list[triple[0]].append((triple[1], triple[2]))
		eages_list[triple[1]].append((triple[0], triple[2]))

	optimalPC = PartitionConfig(sys.maxint, num, nodes, index_dict, -1)
	for i in range(num):
		valid = [True for x in range(num)]
		valid[i] = False
		newPC = PartitionConfig(0, num, nodes, index_dict, i)
		newPC.addScheme(i, -1, 'HASH')
		addPREF(eages_list, i, newPC, valid)
		newPC.estimate()
		if newPC.estimatedSize < optimalPC.estimatedSize:
			optimalPC = newPC
	return optimalPC


nodes, eages, MAST_eages, DL, name_dict, index_dict = getGraph("schema.txt")
for key, value in nodes.items():
	print value.name, value.label
print eages, '\n', MAST_eages, '\nDL =', DL
opt_pc = findOptimalPC(MAST_eages, nodes, index_dict)
all_size = sum([x.label for x in nodes.values()])
DR = float(opt_pc.estimatedSize) / float(all_size) - 1
print index_dict[opt_pc.seed], opt_pc.estimatedSize, opt_pc.timer, '\nDR =', DR
