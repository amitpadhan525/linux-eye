import subprocess
from linux_eye.utils.logger import log_critical,log_info,log_warning
process=subprocess.Popen(['journalctl','-f'],stdout=subprocess.PIPE,text=True)

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