"""
Comprehensive test script for LinuxEye monitors and utilities.
"""
import time
import os
from linux_eye.utils.config import CONFIG, BASE_DIR
from linux_eye.utils.logger import log_info, log_warning, log_critical
from linux_eye.monitors import (
    process_monitor,
    network_monitor,
    login_monitor,
    file_monitor,
    usb_monitor
)

def test_config():
    print("[*] Testing configuration loader...")
    assert os.path.exists(BASE_DIR)
    assert 'general' in CONFIG
    assert 'login_monitor' in CONFIG
    assert 'network_monitor' in CONFIG
    assert 'file_monitor' in CONFIG
    print("    -> Config loaded successfully.")

def test_logger():
    print("[*] Testing logger utility...")
    log_info("test", "Test info message", {"sample": 1})
    log_warning("test", "Test warning message")
    log_critical("test", "Test critical message")
    print("    -> Logger wrote entries without error.")

def test_process_monitor():
    print("[*] Testing process monitor...")
    # Safe handling of None cmdline
    safe_proc = {'pid': 10001, 'name': 'systemd', 'cmdline': None, 'username': 'root'}
    assert not process_monitor.check_suspicious(safe_proc)

    # Detection of reverse shell
    suspicious_proc = {
        'pid': 10002,
        'name': 'bash',
        'cmdline': ['bash', '-i'],
        'username': 'attacker'
    }
    assert process_monitor.check_suspicious(suspicious_proc)

    # Detection of hacking tools
    nmap_proc = {
        'pid': 10003,
        'name': 'nmap',
        'cmdline': ['nmap', '-sS', '192.168.1.1'],
        'username': 'attacker'
    }
    assert process_monitor.check_suspicious(nmap_proc)

    # Live system scan
    process_monitor.run()
    print("    -> Process monitor checks and live scan passed.")

def test_network_monitor():
    print("[*] Testing network monitor...")
    mock_ip = "198.51.100.24"
    now = time.time()

    # Simulate multi-port incoming scan
    network_monitor.connection_history[mock_ip] = [
        (22, now),
        (80, now),
        (443, now)
    ]
    network_monitor.check_suspicious()

    # Verify clean_old_entries removes expired IPs
    network_monitor.connection_history["expired.ip"] = [(22, now - 10)]
    network_monitor.clean_old_entries()
    assert "expired.ip" not in network_monitor.connection_history

    # Live socket scan
    network_monitor.run()
    print("    -> Network monitor checks and live scan passed.")

def test_login_monitor():
    print("[*] Testing login monitor...")
    test_user = "test_intruder"

    # Feed 3 failed attempts
    for _ in range(3):
        sample_fail = f"pam_unix(sudo:auth): authentication failure; logname= uid=1000 euid=0 tty=/dev/pts/1 ruser={test_user} rhost=  user={test_user}"
        login_monitor.process_log_line(sample_fail)

    # Check brute-force tracker
    assert test_user in login_monitor.failed_logins
    assert len(login_monitor.failed_logins[test_user]) == 3

    # Reset on successful login
    sample_success = f"pam_unix(sudo:session): session opened for user {test_user} by amit(uid=0)"
    login_monitor.process_log_line(sample_success)
    assert test_user not in login_monitor.failed_logins
    print("    -> Login monitor brute force tracking and reset passed.")

if __name__ == "__main__":
    print("========================================")
    print("      🧪 Running LinuxEye Unit Tests    ")
    print("========================================")
    test_config()
    test_logger()
    test_process_monitor()
    test_network_monitor()
    test_login_monitor()
    print("\n✅ All tests completed successfully!")