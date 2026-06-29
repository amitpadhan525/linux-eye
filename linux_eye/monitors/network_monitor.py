import psutil
import time
from linux_eye.utils.logger import log_critical, log_info


dic={}

def clean_old_entries():
    current_time=time.time()
    for ip in list(dic.keys()):
        dic[ip]=[
            entry for entry in dic[ip]
            if current_time-entry[1]<=3
        ]

    return dic
    
def check_suspicious():
    for ip in dic:
        ports=set()
        current_time=time.time()
        for tuple in dic[ip]:
            if current_time-tuple[1]<=3:
                ports.add(tuple[0])
        if len(ports)>2:
            log_critical(
                source='network_monitor',
                message="Possible port scan detected",
                details=f"{ip} hit {ports} multiple ports recently"
            )
      


def run():
    # 1. get connections
    connections=psutil.net_connections()
    for con in connections:
        if con.raddr:
            if con.raddr.ip in dic:
                dic[con.raddr.ip].append((con.raddr.port,time.time()))
            else:
                dic[con.raddr.ip]=[(con.raddr.port,time.time())]
    # 2. store in dictionary
    # 3. clean old entries
    clean_old_entries()
    # 4. check for suspicious activity
    check_suspicious()