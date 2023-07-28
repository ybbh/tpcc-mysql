cmake_minimum_required(VERSION 3.0)
project(TPCC-MYSQL)

add_subdirectory(src)

set(BLOCK_DB_DIR ${CMAKE_SOURCE_DIR}/../..)

include_directories(/usr/include/mysql)
include_directories(${BLOCK_DB_DIR}/third_party/include)
link_directories(${BLOCK_DB_DIR}/third_party/lib)
set(EXECUTABLE_OUTPUT_PATH ${BLOCK_DB_DIR}/bin)

set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -pthread")