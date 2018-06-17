# DDBS-Partition
Data partitioning implementation and experiment in distributed database system

Undergraduate thesis training based project

- find_pc.py：数据库模式驱动的自动分区算法
- schema.txt：算法的样例输入文件
- tpcc-mysql：单机TPC-C在MySQL上的测试文件夹
- tpcc-msqter-new：并行数据库基于Mycat在TPC-C上的测试文件夹
  - TPCC-mycat.docx：测试步骤
  - database/tpcc_test.sh：测试时指令文件
- Mycat_Confs：Mycat配置文件集
  - MOD：简单驱魔方法
  - PREF：基于谓语的引用分区方法
  - official：原Mycat文件夹中配置文件
  - original：原测试时使用配置文件