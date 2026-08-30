import os
import yaml

# Project root directory
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
LOCAL_CONFIG_PATH = os.path.join(BASE_DIR, 'config', 'config.yaml')
SYSTEM_CONFIG_PATH = '/etc/linux-eye/config.yaml'

DEFAULT_CONFIG = {
    'general': {
        'tool_name': 'LinuxEye',
        'log_dir': 'logs',
        'log_file': 'linux-eye.log',
        'refresh_interval': 5,
    },
    'login_monitor': {
        'window_seconds': 60,
        'threshold': 3,
    },
    'network_monitor': {
        'window_seconds': 3,
        'port_threshold': 2,
    },
    'file_monitor': {
        'watch_dir': '/etc',
        'critical_files': ['passwd', 'shadow', 'sudoers'],
    }
}

def get_config_path():
    """Find appropriate config path with priority: system-wide -> local repo."""
    if os.path.exists(SYSTEM_CONFIG_PATH):
        return SYSTEM_CONFIG_PATH
    if os.path.exists(LOCAL_CONFIG_PATH):
        return LOCAL_CONFIG_PATH
    return None

def load_config():
    config_file = get_config_path()
    if config_file and os.path.exists(config_file):
        try:
            with open(config_file, 'r') as f:
                loaded = yaml.safe_load(f)
                if isinstance(loaded, dict):
                    # Merge with defaults
                    merged = DEFAULT_CONFIG.copy()
                    for key, val in loaded.items():
                        if isinstance(val, dict) and key in merged:
                            merged[key] = {**merged[key], **val}
                        else:
                            merged[key] = val
                    return merged
        except Exception as e:
            print(f"[!] Error loading {config_file}: {e}. Using defaults.")
    return DEFAULT_CONFIG

CONFIG = load_config()