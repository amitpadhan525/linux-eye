import json
import os
from datetime import datetime
from linux_eye.utils.config import    CONFIG

log_dir=CONFIG['general']['log_dir']
log_file=CONFIG['general']['log_file']

log_path=log_dir+log_file
os.makedirs(log_dir,exist_ok=True)
def _write_log(severity, source, message, details):
    entry={
        'timestamp':datetime.now().isoformat(),
        'severity':severity,
        'message':message,
        'source':source,
        'details':details
    }
    with open(log_path,'a') as log:
        log.write(json.dumps(entry)+'\n')
    

def log_info(source,message,details=None):
    _write_log('INFO',source,message,details)

def log_warning(source,message,details=None):
    _write_log('WARNING',source,message,details)

def log_critical(source,message,details=None):
    _write_log('CRITICAL',source,message,details)



