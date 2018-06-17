#!/bin/bash

tar_db_host=166.111.71.107
tar_db_port=8066
tar_db_user=root
tar_db_pass=131071
tar_db_name=ww_test
tar_jdbc_url=jdbc:mysql://${tar_db_host}:${tar_db_port}/${tar_db_name}
# ?interactiveClient=true

num_wh=150
num_con=50
ramp_up=300
duration=7200

# execute sql using mycat
function execute_sql()
{
    local sql="$1"
    if [ -z "$sql" ]; then
        sql=`cat`
    fi

    mysql -h ${tar_db_host} -P ${tar_db_port} -u ${tar_db_user} -p ${tar_db_name} -s -N -e "$sql"
}

function main()
{
    local datetime=`date +'%Y%m%d%H%M%S'`
    # create table
    # time execute_sql < create_tables.sql > report_${datetime}.log

    datetime=`date +'%Y%m%d%H%M%S'`
    # create index and foreign key
    # time execute_sql < add_fkey_idx.sql > report_${datetime}.log

    datetime=`date +'%Y%m%d%H%M%S'`
    # load data
    # time java -Xms2048m -Xms2048m com.codefutures.tpcc.TpccLoad -l "$tar_jdbc_url" -u ${tar_db_user} -p ${tar_db_pass} -m JDBC -w $num_wh -s 1 -i 1 > report_${datetime}.log

    datetime=`date +'%Y%m%d%H%M%S'`
    # count all tables after running
    # time java com.codefutures.tpcc.util.CountTable -l "$tar_jdbc_url" -u ${tar_db_user} -p ${tar_db_pass} > report_${datetime}.log

    datetime=`date +'%Y%m%d%H%M%S'`
    # execute main test program
    # time java -Xms6144m -Xms6144m -Dcom.sun.management.jmxremote -Dcom.sun.management.jmxremote.port=10101 -Dcom.sun.management.jmxremote.ssl=false -Dcom.sun.management.jmxremote.authenticate=false com.codefutures.tpcc.Tpcc -l "$tar_jdbc_url" -u ${tar_db_user} -p ${tar_db_pass} -w $num_wh -c $num_con -r $ramp_up -t $duration > report_${datetime}.log

    datetime=`date +'%Y%m%d%H%M%S'`
    # drop table
   	# time java com.codefutures.tpcc.util.DropTable -l "$tar_jdbc_ur l" -u ${tar_db_user} -p ${tar_db_pass} > report_${datetime}.log
    # time execute_sql < truncate_tables.sql > report_${datetime}.log
   
}

main "$@"
