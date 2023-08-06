cmake_minimum_required(VERSION 3.0)
project(TPCC-MYSQL)



set(BLOCK_DB_DIR ${CMAKE_SOURCE_DIR})

include_directories(/usr/include/mysql)
set(EXECUTABLE_OUTPUT_PATH ${BLOCK_DB_DIR}/bin)

add_subdirectory(src)