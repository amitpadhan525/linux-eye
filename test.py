import psutil

for proc in psutil.process_iter(['pid', 'name', 'username']):
    print(proc.info)  # proc.info is a dict of what you asked for
