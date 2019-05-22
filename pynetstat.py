#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os
import argparse
import time
from common.daemon import Daemon
from common.logger import Logger
import commands
import redis
import json

#增加统计 iptables -A INPUT -p tcp --dport 28080   |  移除统计：iptables -D INPUT -p tcp --dport 28080
#增加统计 iptables -A INPUT -p tcp --sport 28080   |  移除统计：iptables -D INPUT -p tcp --sport 28080

#-------- 配置 ---------#
interval_second = 1
port_list = ["8081", "28080", "28180", "443", "80", "38080"]
redis_open = 0
redis_ip = "127.0.0.1"
redis_port = "6379"
redis_password = ""
redis_db = 0
redis_key = "netflow:root"

# ---------------------#
flow_counter = {}
sflow_counter = {}

for port in port_list:
    flow_counter[port] = 0
    sflow_counter[port] = 0

if interval_second <= 0:
    interval_second = 1

redis_client = None

if redis_ip != "" and redis_port != "":
    print "start redis sync"
    try:
        pool = redis.ConnectionPool(
            host=redis_ip,
            port=redis_port,
            db=redis_db,
            password=redis_password)
        redis_client = redis.StrictRedis(connection_pool=pool)
    except Exception, e:
        Logger.logger.error(e)


def execute_port_flow():
    result = {}
    total = 0
    for port, old_counter in flow_counter.items():
        cmd = "iptables -L -v -n -x | grep 'tcp dpt:%s' | awk '{print $2}' | head -n 1" % port
        code, output = commands.getstatusoutput(cmd)
        if not output:
            output = "0"
        new_counter = int(str(output))
        counter = new_counter - old_counter
        flow_counter[port] = new_counter
        result[port] = counter / interval_second
        total += result[port]

    output = "recv port flow : "
    for port, res in result.items():
        sub = "%s = %d B/s\t" % (port, res)
        output += sub

    Logger.logger.info(output)

    return total


def execute_sport_flow():
    result = {}
    total = 0
    for port, old_counter in sflow_counter.items():
        cmd = "iptables -L -v -n -x | grep 'tcp spt:%s' | awk '{print $2}' | head -n 1" % port
        code, output = commands.getstatusoutput(cmd)
        if not output:
            output = "0"
        new_counter = int(str(output))
        counter = new_counter - old_counter
        sflow_counter[port] = new_counter
        result[port] = counter / interval_second
        total += result[port]

    output = "send port flow : "
    for port, res in result.items():
        sub = "%s = %d B/s\t" % (port, res)
        output += sub

    Logger.logger.info(output)

    return total


sub_counter = {"all": 0, "tcp": 0, "udp": 0, "icmp": 0}


def execute_netstat():
    cmd = "netstat -n -p|grep SYN_REC | wc -l"
    code, output = commands.getstatusoutput(cmd)
    if not output:
        output = "0"

    cmd2 = "netstat -n -p|grep EST | wc -l"
    code2, output2 = commands.getstatusoutput(cmd2)
    if not output2:
        output2 = "0"

    Logger.logger.info(
        "[netstat]: SYN_RECV=%s\tESTABLISH=%s" % (output, output2))


def init_iptables():
    for port in port_list:
        dcmd = "iptables -D INPUT -p tcp --dport %s" % port
        commands.getstatusoutput(dcmd)
        scmd = "iptables -D INPUT -p tcp --sport %s" % port
        commands.getstatusoutput(scmd)

        dcmd1 = "iptables -D OUTPUT -p tcp --dport %s" % port
        commands.getstatusoutput(dcmd1)
        scmd1 = "iptables -D OUTPUT -p tcp --sport %s" % port
        commands.getstatusoutput(scmd1)

        dcmd2 = "iptables -A INPUT -p tcp --dport %s" % port
        commands.getstatusoutput(dcmd2)
        scmd2 = "iptables -A OUTPUT -p tcp --sport %s" % port
        commands.getstatusoutput(scmd2)


def set_redis(recv, send):
    if redis_client and redis_open == 1:
        Logger.logger.info(
            "(sync redis) recv= %d B/s, send= %d B/s" % (recv, send))
        ret = {
            "in_Bytes": recv,
            "out_Bytes": send,
            "timestamp": int(time.time())
        }
        json_ret = json.dumps(ret)
        redis_client.set(redis_key, json_ret)
    else:
        Logger.logger.info("recv= %d B/s, send= %d B/s" % (recv, send))


def main():

    init_iptables()

    while True:
        recv = execute_port_flow()
        send = execute_sport_flow()
        set_redis(recv, send)
        execute_netstat()
        time.sleep(interval_second)
        commands.getstatusoutput("echo '' >> /data/logs/pynetstat/stdout.log")


class ExampleDaemon(Daemon):
    def __init__(self, pid):
        super(self.__class__, self).__init__(pid)

    def run(self):
        if not os.path.exists("/data/logs"):
            os.makedirs("/data/logs")

        main()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('cmd', default="start", help='start, stop, restart')
    parser.add_argument('-p', '--pidfile', default="./proc/pynetstat.pid")

    log_path = "/data/logs/pynetstat"

    args = parser.parse_args()
    pidpath = os.path.abspath(args.pidfile)
    dirname = os.path.dirname(pidpath)
    if not os.path.exists(dirname):
        os.makedirs(dirname)

    if not os.path.exists(log_path):
        os.makedirs(log_path)

    daemon = ExampleDaemon(pidpath)
    if 'start' == args.cmd:
        daemon.start()
    elif 'stop' == args.cmd:
        daemon.stop()
    elif 'restart' == args.cmd:
        daemon.restart()
    else:
        print "Unknown command"
        sys.exit(2)
