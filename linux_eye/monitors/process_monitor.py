import psutil
import shlex
from linux_eye.utils.logger import log_critical, log_info

SUSPICIOUS_PATTERNS = [
    # Reverse shells
    "bash -i",
    "sh -i",
    "/dev/tcp/",
    "mkfifo",
    "nc -e",

    # Download & execute
    "curl | bash",
    "curl | sh",
    "wget | bash",
    "wget | sh",

    # Inline code execution
    "python -c",
    "python3 -c",
    "perl -e",
    "ruby -e",
    "php -r",

    # Dangerous shell execution
    "eval(",
    "exec(",
    "system(",
    "os.system",
    "subprocess",
    "popen",

    # Persistence
    "systemctl enable",
    "systemctl start",

    # Obfuscation
    "base64",

    # Dangerous commands
    "chmod 777",
    "chmod +x",
    "rm -rf",
    "dd if=",
]
SUSPICIOUS_TOOLS = {
    "nmap",
    "masscan",
    "arp-scan",
    "netdiscover",
    "sqlmap",
    "nikto",
    "hydra",
    "john",
    "hashcat",
    "tcpdump",
    "ettercap",
    "bettercap",
    "responder",
    "msfconsole",
    "msfvenom",
    "meterpreter",
    "netcat",
    "ncat",
    "socat",
}

def get_all_processes():
    process_list = []
    for proc in psutil.process_iter(['pid', 'name', 'username', 'cmdline', 'exe']):
        try:
            process_list.append(proc.info)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass  # skip this process and continue
    return process_list

def check_suspicious(proc):
    cmdline = " ".join(proc.get("cmdline", []))
    cmdline = cmdline.lower()

    try:
        tokens = set(shlex.split(cmdline))
    except ValueError:
        tokens = set(cmdline.split())

    # Exact executable/tool names
    for tool in SUSPICIOUS_TOOLS:
        if tool in tokens:
            return True

    # Multi-word patterns
    for pattern in SUSPICIOUS_PATTERNS:
        if pattern in cmdline:
            return True

    return False
def run():
    for proc in get_all_processes():
        if check_suspicious(proc):
            log_critical(
                source='process_monitor',
                message=f"Suspicious command detected: {' '.join(proc.get('cmdline', []))}",
                details=proc
            )
        # else:
        #     log_info(
        #         source='process_monitor',
        #         message=f"Process running: {proc['name']}",
        #         details=proc
        #     )


