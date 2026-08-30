import os
import json
import threading
from datetime import datetime
from linux_eye.utils.config import CONFIG, BASE_DIR

# Determine log file destination
log_dir_setting = CONFIG['general'].get('log_dir', 'logs')
log_file_setting = CONFIG['general'].get('log_file', 'linux-eye.log')

# Resolve destination directory
if os.path.isabs(log_dir_setting):
    log_dir = log_dir_setting
elif os.path.exists('/etc/linux-eye/config.yaml') or 'site-packages' in BASE_DIR or 'dist-packages' in BASE_DIR:
    log_dir = '/var/log/linux-eye'
else:
    log_dir = os.path.join(BASE_DIR, log_dir_setting)

log_path = os.path.join(log_dir, log_file_setting)

try:
    os.makedirs(log_dir, exist_ok=True)
except Exception:
    # Fallback to local user / tmp directory if permission denied
    log_dir = os.path.expanduser('~/.local/state/linux-eye')
    os.makedirs(log_dir, exist_ok=True)
    log_path = os.path.join(log_dir, log_file_setting)

# Lock for thread-safe file writes
_log_lock = threading.Lock()

def _write_log(severity, source, message, details=None):
    entry = {
        'timestamp': datetime.now().isoformat(),
        'severity': severity,
        'message': message,
        'source': source,
        'details': details
    }
    with _log_lock:
        with open(log_path, 'a', encoding='utf-8') as log_file:
            log_file.write(json.dumps(entry) + '\n')

def log_info(source, message, details=None):
    _write_log('INFO', source, message, details)

def log_warning(source, message, details=None):
    _write_log('WARNING', source, message, details)

def log_critical(source, message, details=None):
    _write_log('CRITICAL', source, message, details)
