
add_library(tpcc_mysql
        delivery.c
        driver.c
        neword.c
        ordstat.c
        payment.c
        rthist.c
        sb_percentile.c
        sequence.c
        slev.c
        spt_proc.c
        support.c
        tpc.c
        )

add_executable(tpcc_load load.c)
add_executable(tpcc_start main.c)

target_link_libraries(tpcc_load
        tpcc_mysql
        mysqlclient
        pthread
        m)

target_link_libraries(tpcc_start
        tpcc_mysql
        mysqlclient
        pthread
        m)

set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -pthread")