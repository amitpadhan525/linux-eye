from linux_eye.monitors import process_monitor
from linux_eye.utils.config import CONFIG
import time

print("-------THIS IS STARTING-------")

while True:
    process_monitor.run()
    time.sleep(CONFIG['general']['refresh_interval'])
    print('RUNNING')
