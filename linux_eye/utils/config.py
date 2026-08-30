import os
import yaml

# Find the project root directory
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CONFIG_PATH = os.path.join(BASE_DIR, 'config', 'config.yaml')

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

def load_config():
    if os.path.exists(CONFIG_PATH):
        try:
            with open(CONFIG_PATH, 'r') as f:
                loaded = yaml.safe_load(f)
                if isinstance(loaded, dict):
                    # Merge with defaults
                    merged = DEFAULT_CONFIG.copy()
                    for key, val in loaded.items():
                        if isinstance(val, dict) and key in merged:
                            merged[key].update(val)
                        else:
                            merged[key] = val
                    return merged
        except Exception as e:
            print(f"[!] Error loading {CONFIG_PATH}: {e}. Using defaults.")
    else:
        print(f"[!] Config file not found at {CONFIG_PATH}. Using default configuration.")
    return DEFAULT_CONFIG

CONFIG = load_config()