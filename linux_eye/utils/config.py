import yaml

config_path = 'config/config.yaml'

try:
    with open(config_path, 'r') as f:
        CONFIG = yaml.safe_load(f)
except FileNotFoundError:
    print('Config file not found')