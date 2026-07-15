import subprocess
from linux_eye.utils.logger import log_critical,log_info,log_warning
process=subprocess.Popen(['journalctl','-f'],stdout=subprocess.PIPE,text=True)
from collections import deque
import time

failed_logins={}
WINDOW_SECONDS = 60
THRESHOLD = 5
def check_brute_force(line):
    if 'pam_unix(sudo:auth): authentication failure' not in line:
        return
    
    if 'user=' in line:
        username=line.split('user=')[1].split(' ')[0]
    else:
        username=None

    if username is None:
        return
    
    now=time.time()
    if username in failed_logins:
        failed_logins[username].append(now)
    else:
        failed_logins[username]=deque([now])

    while failed_logins[username] and now-failed_logins[username][0]>WINDOW_SECONDS:
        failed_logins[username].popleft()

   

    if len(failed_logins[username])>=THRESHOLD:
        log_critical(
            source='Log monitor',
            message=f"Multiple failed login attempt on username {username}.",
            details={
                "username": username,
                "failure_count": len(failed_logins[username]),
                "window_seconds": WINDOW_SECONDS
                }
        )


def run():
    for line in process.stdout:
        if 'pam_unix(sudo:session): session opened' in line:
            log_info(
                source='Log monitor',
                message="Login sucessfull",
                details=line
            )
        elif 'pam_unix(sudo:auth): authentication failure' in line:
            log_warning(
                source='Log monitor',
                message="Wrong Password entred",
                details=line
            )
        check_brute_force(line)
