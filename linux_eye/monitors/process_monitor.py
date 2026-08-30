import shlex
import psutil
from linux_eye.utils.logger import log_critical

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

    # Dangerous destructive commands
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

# Cache of already alerted PIDs to prevent repeated log flooding
_alerted_pids = set()

def get_all_processes():
    """Retrieve running process details safely."""
    process_list = []
    for proc in psutil.process_iter(['pid', 'name', 'username', 'cmdline', 'exe']):
        try:
            info = proc.info
            # Ensure cmdline is always a list of strings
            if info.get('cmdline') is None:
                info['cmdline'] = []
            process_list.append(info)
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue
    return process_list

def check_suspicious(proc):
    """Check if a process command line or executable name matches suspicious patterns."""
    cmdline_list = proc.get("cmdline") or []
    cmdline = " ".join(cmdline_list).lower()
    proc_name = (proc.get("name") or "").lower()

    # Extract command line tokens safely
    try:
        tokens = set(shlex.split(cmdline))
    except ValueError:
        tokens = set(cmdline.split())

    # 1. Match executable name directly
    if proc_name in SUSPICIOUS_TOOLS:
        return True

    # 2. Match exact tool tokens in command line
    for tool in SUSPICIOUS_TOOLS:
        if tool in tokens:
            return True

    # 3. Match multi-word suspicious phrases in command line
    if cmdline:
        for pattern in SUSPICIOUS_PATTERNS:
            if pattern in cmdline:
                return True

    return False

def run():
    """Scan all active processes for suspicious activities."""
    current_pids = set()

    for proc in get_all_processes():
        pid = proc.get('pid')
        current_pids.add(pid)

        if check_suspicious(proc):
            # Only log an alert if we haven't already reported this running PID
            if pid not in _alerted_pids:
                cmdline_str = " ".join(proc.get('cmdline') or []) or proc.get('name', 'Unknown')
                log_critical(
                    source='process_monitor',
                    message=f"Suspicious command detected: {cmdline_str}",
                    details=proc
                )
                _alerted_pids.add(pid)

    # Clean up terminated PIDs from the alerted cache
    _alerted_pids.intersection_update(current_pids)
