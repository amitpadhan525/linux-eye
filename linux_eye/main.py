from linux_eye.monitors import process_monitor, network_monitor, file_monitor
from linux_eye.utils.config import CONFIG
import time
import threading


def monitor_loop():
    while True:
        process_monitor.run()
        network_monitor.run()
        time.sleep(CONFIG['general']['refresh_interval'])
        print('RUNNING')

def main():
    print("------- LinuxEye Started -------")

    t1 = threading.Thread(target=monitor_loop,daemon=True)
    t2 = threading.Thread(target=file_monitor.run,daemon=True)

    t1.start()
    t2.start()

    t1.join()
    t2.join()

if __name__ == "__main__":
    main()