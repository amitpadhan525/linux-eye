import re
import time
import subprocess
from collections import deque
from linux_eye.utils.config import CONFIG
from linux_eye.utils.logger import log_critical, log_info, log_warning

# Sliding window state: username -> deque([timestamps])
failed_logins = {}

# Configuration settings
WINDOW_SECONDS = CONFIG.get('login_monitor', {}).get('window_seconds', 60)
THRESHOLD = CONFIG.get('login_monitor', {}).get('threshold', 3)

def extract_username(log_line):
    """Extract username from PAM, sudo, or sshd log lines."""
    # Pattern 1: user=<username> or user = <username>
    match = re.search(r'user[ =]([a-zA-Z0-9._-]+)', log_line)
    if match:
        return match.group(1)

    # Pattern 2: session opened for user <username>
    match = re.search(r'for user ([a-zA-Z0-9._-]+)', log_line)
    if match:
        return match.group(1)

    # Pattern 3: Failed password for <username> / invalid user <username> (sshd)
    match = re.search(r'(?:Failed password for invalid user|Failed password for|invalid user) ([a-zA-Z0-9._-]+)', log_line)
    if match:
        return match.group(1)

    return None

def check_brute_force(username):
    """Check if failed login count for a user exceeds the threshold in the sliding window."""
    if not username:
        return

    now = time.time()

    if username not in failed_logins:
        failed_logins[username] = deque([now])
    else:
        failed_logins[username].append(now)

    # Evict timestamps older than the sliding window
    user_queue = failed_logins[username]
    while user_queue and (now - user_queue[0] > WINDOW_SECONDS):
        user_queue.popleft()

    # Trigger critical alert if threshold exceeded
    if len(user_queue) >= THRESHOLD:
        log_critical(
            source='login_monitor',
            message=f"Possible brute-force attack detected on user '{username}'",
            details={
                "username": username,
                "failure_count": len(user_queue),
                "window_seconds": WINDOW_SECONDS,
                "threshold": THRESHOLD
            }
        )

def process_log_line(line):
    """Analyze a single journal log line for login and authentication events."""
    line = line.strip()
    if not line:
        return

    # Successful login or session start
    if ('pam_unix(sudo:session): session opened' in line
            or 'Accepted password for' in line
            or 'Accepted publickey for' in line):
        username = extract_username(line)
        if username and username in failed_logins:
            # Clear failed login history on successful authentication
            failed_logins.pop(username, None)

        log_info(
            source='login_monitor',
            message=f"Login successful for user '{username or 'unknown'}'",
            details=line
        )

    # Authentication failure
    elif ('pam_unix(sudo:auth): authentication failure' in line
          or 'authentication failure' in line
          or 'Failed password for' in line):
        username = extract_username(line)
        log_warning(
            source='login_monitor',
            message=f"Failed authentication attempt for user '{username or 'unknown'}'",
            details=line
        )

        if username:
            check_brute_force(username)

def run():
    """Stream auth logs from journalctl and inspect login activity."""
    cmd = ['journalctl', '-u', 'systemd-journald', '-u', 'sshd', '-u', 'sudo', '-f', '-n', '0']
    
    # Fallback to general follow if specific units are not isolated
    general_cmd = ['journalctl', '-f', '-n', '0']

    try:
        process = subprocess.Popen(
            general_cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            text=True,
            bufsize=1
        )
    except FileNotFoundError:
        print("[!] journalctl not found on this system.")
        return
    except Exception as e:
        print(f"[!] Unable to start login monitor: {e}")
        return

    try:
        for line in process.stdout:
            process_log_line(line)
    except Exception:
        pass
    finally:
        if process.poll() is None:
            process.terminate()
