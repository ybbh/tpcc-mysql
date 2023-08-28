#!/usr/bin/env python3
import subprocess
import argparse
import os
import re
import json
import time
import multiprocessing
import re
import psutil
import queue

MYSQL_USER='root'
MYSQL_PASSWORD=''
MYSQL_INSTALL_DIR='/home/ybbh/mysql/usr/local/mysql/'
MYSQL_DB_NAME='tpcc'
MYSQL_PORT=3306

MYSQL_TPCC_RUN_SECONDS = 100

NUM_ITEM = 100000
CUST_PER_DIST = 1000
DIST_PER_WARE = 10
ORD_PER_DIST = 1000
MAX_NUM_ITEMS = 15
HOT_ITEM_NUM = 10

PROJECT_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def run_shell_command(shell_command):
    print("local shell command run")
    print(shell_command)
    p = subprocess.run(shell_command, shell=True,
                       capture_output=True, text=True)
    print(p.stdout)
    print(p.stderr)
    return p.returncode, p.stdout, p.stderr

def mysqld_startup(user, password, address):
    

    print("-------- MYSQL TPCC start mysqld {} --------".format(address))
    cmd = 'nohup mysqld_safe > mysqld.out 2>&1 </dev/null & \n'
    run_shell_command(shell_command=cmd)


def mysql_create_schema(user, address, database):
    print(PROJECT_PATH)
    print("-------- MYSQL TPCC create table --------")
    cmd_create_table = 'mysql -u root --skip-password {} -h {} < {}/create_table.sql \n'.format(
        '',
        address,
        PROJECT_PATH)

    run_shell_command(shell_command=cmd_create_table)



def tpcc_environment_variable():
    env = '''\
export MAXITEMS={}
export CUST_PER_DIST={}
export DIST_PER_WARE={}
export ORD_PER_DIST={}
export MAX_NUM_ITEMS={}
export MAX_ITEM_LEN=14
'''.format(NUM_ITEM, CUST_PER_DIST, DIST_PER_WARE, ORD_PER_DIST, MAX_NUM_ITEMS)
    return env


def mysql_load(address, mysql_user, mysql_password, mysql_db_name, warehouse):
    mysql_create_schema(mysql_user, address, mysql_db_name)
    print("-------- MYSQL TPCC load data --------")
    cmd_load_script = '''\
{}
{}/load.sh {} {} {} {} {}
    '''.format(tpcc_environment_variable(), PROJECT_PATH, mysql_db_name, warehouse,
               mysql_user, mysql_password, address)
    print(cmd_load_script)
    run_shell_command(shell_command=cmd_load_script)


def mysql_run_bench_tpcc(address, mysql_user, mysql_password, mysql_db_name,  warehouse, terminal):
    print("-------- MYSQL TPCC run benchmark --------")
    # use the last

    cmd_run_tpcc = '''\
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/usr/local/mysql/lib/mysql/:/usr/local/lib/
{}
{}/bin/tpcc_start -h{} -P{} -d{} -u{} -p{} -w{} -c{} -r10 -l{}
'''.format(tpcc_environment_variable(),
            PROJECT_PATH,
            address,  # -h
            MYSQL_PORT,  # -P
            mysql_db_name,  # -d
            mysql_user,  # -u
            mysql_password,  # -p
            warehouse,  # -w
            terminal,
            MYSQL_TPCC_RUN_SECONDS
            )
    print(cmd_run_tpcc)
    rc, stdout, _ = run_shell_command(shell_command=cmd_run_tpcc)
    if rc == 0:
        match = re.search(r"([0-9]+\.?[0-9]*)\s*TpmC", stdout)
        if match:
            tpm = float(match.group(1))
            output_result = {
                'terminals': terminal,
                'warehouses': warehouse,
                'num_item': NUM_ITEM,
                'tpm': tpm,
            }
            with open('output.txt', 'a') as file:
                file.write(json.dumps(output_result) + '\n')
            file.close()

def mysql_init(mysql_user, install_dir):
    # mysqld startup
        cmd = '''\
    mysqld --initialize-insecure --user={}
    cat {}/data/error.log
    '''.format(user, install_dir)
        run_shell_command(shell_command=cmd)


def cpu_usage(messqge_queue:multiprocessing.Queue):
    mysqld_process = None
    for p in psutil.process_iter():
        if p.name() == 'mysqld':
            mysqld_process = p
            break
    if mysqld_process is None:
        return

    pattern = 'pcputimes\(user=(.*), system=(.*), children_user=(.*), children_system=(.*), iowait=(.*)\)'
    p_cpu_times = re.compile(pattern)
    user = 0
    system = 0
    n = 0
    iowait = 0
    start = False
    while True:
        first = False
        try:
            item = messqge_queue.get(timeout=5)
            if item == 'cpu_usage':
                n += 1
                print("start calculate {}".format(n))
                start = True
                first = True
            elif item == "cpu_usage end":
                print("end calculate {}".format(n))
                start = False
        except queue.Empty:
            None

        if start:
            s_cpu_times = str(mysqld_process.cpu_times())
            #print(s_cpu_times)
            m = p_cpu_times.match(s_cpu_times)
            #print(m)
            user1 = float(m[1])
            system1 = float(m[2])
            iowait1 = float(m[5])
            if not first:
                print('user={}, system={}, iowait={}'.format(user1 - user, system1 - system, iowait1 - iowait))
            user = user1
            system = system1
            iowait = iowait1
            print("cpu percent {}%".format(mysqld_process.cpu_percent()))  


def test_cpu_usage():
    queue = multiprocessing.Queue()
    proc = multiprocessing.Process(target=cpu_usage, args=(queue,))
    proc.start()
    while True:
        queue.put('cpu_usage')
        time.sleep(10);

def main():
    parser = argparse.ArgumentParser(description='tpcc')
    parser.add_argument('-l', '--load', action='store_true', help='mysql load')
    parser.add_argument('-i', '--init', action='store_true', help='mysql init')
    parser.add_argument('-r', '--run', action='store_true', help='test mysql run')
    parser.add_argument('-t', '--cpu-times', action='store_true', help='CPU times')
    args = parser.parse_args()

    terminal = 8
    warehouse = 20
    address = '127.0.0.1'

    #if args.cpu_times:
    #    test_cpu_usage()

    if args.load:
        mysql_load(address, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DB_NAME, warehouse)
    elif args.init:
        mysql_init(MYSQL_USER, MYSQL_INSTALL_DIR)
        return
    elif args.run:
        if args.cpu_times:
            print('output cpu usage')
            queue = multiprocessing.Queue()
            proc = multiprocessing.Process(target=cpu_usage, args=(queue,))
            proc.start()
        for terminal in [1, 10, 50, 100, 150]:
            time.sleep(10);
            if args.cpu_times:
                queue.put('cpu_usage')
            mysql_run_bench_tpcc(address, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DB_NAME, warehouse, terminal)
            if args.cpu_times:
                queue.put('cpu_usage end')
        return

if __name__ == '__main__':
    main()
