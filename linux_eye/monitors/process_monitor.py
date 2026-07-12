import psutil
from linux_eye.utils.logger import log_critical, log_info
# SUSPICIOUS_KEYWORDS = ["cmd.exe", "powershell", "bash", "sh", "eval(", "exec(", "system(", "subprocess", "os.system", "popen", "spawn", "`", "|", "&&", "||", ";", "$(", "${", "select * from", "drop table", "delete from", "insert into", "union select", "or 1=1", "--", "/*", "*/", "xp_cmdshell", "sp_executesql", "information_schema", "../", "..\\", "/etc/passwd", "/etc/shadow", "C:\\Windows", "C:\\System32", "var/log", "proc/self", "file://", "wget", "curl", "nc -e", "netcat", "nmap", "sqlmap", "nikto", "burp", "metasploit", "meterpreter", "reverse shell", "bind shell", "base64", "import os", "import subprocess", "compile(", "execfile(", "__import__", "getattr", "setattr", "globals", "locals", "<script>", "javascript:", "onerror=", "onload=", "alert(", "document.cookie", "eval(unescape", "iframe", "object", "sudo", "su -", "chmod 777", "chmod +x", "passwd", "useradd", "cron", "crontab", "authorized_keys", "id_rsa", ".env", "secret", "password", "api_key", "token", "private_key"]
SUSPICIOUS_KEYWORDS = [
    # Reverse shells
    "bash -i",
    "sh -i",
    "/dev/tcp/",
    "mkfifo",
    "nc -e",
    "ncat",
    "netcat",
    "socat",

    # Download & execute
    "curl | bash",
    "curl | sh",
    "wget | bash",
    "wget | sh",
    "curl http",
    "wget http",

    # Command execution
    "eval(",
    "exec(",
    "system(",
    "os.system",
    "subprocess",
    "popen",
    "__import__",
    "compile(",

    # Interpreters used for payloads
    "python -c",
    "python3 -c",
    "perl -e",
    "ruby -e",
    "php -r",

    # Encoding / obfuscation
    "base64",
    "xxd",
    "openssl enc",

    # Privilege escalation
    "sudo",
    "su -",
    "pkexec",

    # Persistence
    "crontab",
    "cron",
    "systemctl enable",
    "systemctl start",
    "authorized_keys",

    # Sensitive files
    "/etc/passwd",
    "/etc/shadow",
    ".ssh",
    "id_rsa",
    ".env",

    # Suspicious directories
    "/tmp/",
    "/dev/shm/",
    "/var/tmp/",

    # Reconnaissance
    "nmap",
    "masscan",
    "arp-scan",
    "netdiscover",
    "whoami",
    "hostname",
    "id",
    "uname -a",
    "ifconfig",
    "ip addr",

    # Password attacks
    "hydra",
    "john",
    "hashcat",

    # Exploitation
    "msfconsole",
    "msfvenom",
    "meterpreter",
    "sqlmap",
    "nikto",
    "searchsploit",

    # Packet sniffing
    "tcpdump",
    "wireshark",
    "ettercap",
    "bettercap",
    "responder",

    # File permission abuse
    "chmod 777",
    "chmod +x",
    "chown root",

    # Dangerous deletion
    "rm -rf",
    "dd if=",

    # Secrets
    "password",
    "passwd",
    "token",
    "api_key",
    "secret",
    "private_key"
]

def get_all_processes():
    process_list = []
    for proc in psutil.process_iter(['pid', 'name', 'username']):
        try:
            process_list.append(proc.info)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass  # skip this process and continue
    return process_list

def check_suspicious(proc):
    if proc['name'] in SUSPICIOUS_KEYWORDS:
        return True
    else:
        return False
    
def run():
    for proc in get_all_processes():
        if check_suspicious(proc):
            log_critical(
                source='process_monitor',
                message=f"Suspicious process detected: {proc['name']}",
                details=proc
            )
        # else:
        #     log_info(
        #         source='process_monitor',
        #         message=f"Process running: {proc['name']}",
        #         details=proc
        #     )


