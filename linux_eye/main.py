import time
import signal
import sys
import threading
from linux_eye.monitors import (
    process_monitor,
    network_monitor,
    file_monitor,
    login_monitor,
    usb_monitor
)
from linux_eye.utils.config import CONFIG

# Global flag to signal workers to stop
running = True

def signal_handler(signum, frame):
    """Handle termination signals for clean shutdown."""
    global running
    print("\n[!] Stopping LinuxEye gracefully...")
    running = False
    sys.exit(0)

def periodic_monitor_loop(refresh_interval):
    """Periodically execute polling-based monitors."""
    while running:
        process_monitor.run()
        network_monitor.run()
        time.sleep(refresh_interval)

def main():
    # Register signal listeners
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    refresh_interval = CONFIG.get('general', {}).get('refresh_interval', 5)
    tool_name = CONFIG.get('general', {}).get('tool_name', 'LinuxEye')

    print(f"========================================")
    print(f"        👁️  {tool_name} Security Monitor")
    print(f"========================================")
    print(f"[*] Process & Network scan interval: {refresh_interval}s")
    print(f"[*] Log output: {CONFIG.get('general', {}).get('log_dir', 'logs')}/{CONFIG.get('general', {}).get('log_file', 'linux-eye.log')}")
    print(f"[*] Press Ctrl+C to stop.\n")

    # Initialize monitor threads
    threads = [
        threading.Thread(target=periodic_monitor_loop, args=(refresh_interval,), name="PeriodicMonitor", daemon=True),
        threading.Thread(target=file_monitor.run, name="FileMonitor", daemon=True),
        threading.Thread(target=login_monitor.run, name="LoginMonitor", daemon=True),
        threading.Thread(target=usb_monitor.run, name="USBMonitor", daemon=True),
    ]

    for t in threads:
        t.start()

    # Keep main thread alive and responsive to signals
    try:
        while running:
            time.sleep(1)
    except KeyboardInterrupt:
        signal_handler(None, None)

if __name__ == "__main__":
    main()