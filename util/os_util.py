#!/usr/bin/env python
# -*- coding: utf8 -*-
import commands
import struct
import platform
import socket


def get_os_type():
    """
    获取服务器的类型
    """
    sysstr = platform.system()
    return sysstr


if cmp(get_os_type(), 'Linux') is 0:
    import fcntl


def get_netstat_bind_ip():
    (status, output) = commands.getstatusoutput(
        "netstat -tpln | grep -i ':22' | awk -F ' ' '{print $4}' | grep ':22$'| awk -F ':22' '{print $1}'"
    )

    if not output:
        print "netstat get nothing"
        return None

    bind_ip = None
    output_lines = output.split("\n")
    if len(output_lines) > 0:
        bind_ip = output_lines[len(output_lines) - 1]

    print "bind ip is :" + str(bind_ip)

    if bind_ip == "0.0.0.0":
        return None

    return bind_ip


def get_local_ip(limit_internal_address=False):
    """
    获取服务器的IP
    """
    address = ''
    try:
        if cmp(get_os_type(), 'Linux') is 0:
            try:
                output = None
                distname, version, id = platform.dist()
                if not version or version == '':  # 非linux的情况
                    (status, output) = commands.getstatusoutput(
                        "/sbin/ifconfig -a|grep inet|grep -v 127.0.0.1|grep -v inet6|awk '{print $2}'|tr -d 'addr:'"
                    )
                else:

                    bind_ip = get_netstat_bind_ip()
                    if bind_ip and len(bind_ip) > 7:
                        return bind_ip

                    print "netstat bind ip is invalid, using ifconfig to get up"

                    versionq = version.split(".")
                    if versionq and versionq[0] >= '7':
                        print "get centos 7 ip info"
                        (status, output) = commands.getstatusoutput(
                            "/sbin/ifconfig| grep 'inet' | awk '{print $2}'")
                    else:
                        print "get centos <7 ip info"
                        (status, output) = commands.getstatusoutput(
                            "/sbin/ifconfig -a|grep inet|grep -v 127.0.0.1|grep -v inet6|awk '{print $2}'|tr -d 'addr:'"
                        )

                if output:
                    print 'ip output: ' + output
                    iplines = output.split("\n")
                    for ip in iplines:
                        if ip and (ip.startswith('10.')
                                   or ip.startswith('192.168.')
                                   or ip.startswith('172.')):
                            address = ip
                            print 'get_local_ip | address is :%s' % address
                            return address
                else:
                    for if_name in [
                            'bond0', 'eth0', 'eth1', 'bond0.50', 'bond0.80'
                    ]:
                        try:
                            sock = socket.socket(socket.AF_INET,
                                                 socket.SOCK_DGRAM)
                            address = socket.inet_ntoa(
                                fcntl.ioctl(sock.fileno(), 0x8915,
                                            struct.pack('256s',
                                                        if_name[:15]))[20:24])
                            if limit_internal_address:
                                if address.startswith(
                                        '10.') or address.startswith(
                                            '192.168.') or address.startswith(
                                                '172.'):
                                    break
                                else:
                                    continue
                            else:
                                break
                        except Exception, e:
                            pass
            except Exception, e:
                pass

        else:
            address = socket.gethostbyname(socket.gethostname())
    except Exception, e:
        pass
    return address


ip_address = get_local_ip()
if ip_address.startswith('192.168'):
    DEBUG = True
else:
    DEBUG = False
