# linux-eye

linux-eye is a small Linux process monitor that scans running processes in a loop and records anything it considers suspicious.

It is lightweight, dependency-free apart from `psutil` and `PyYAML`, and writes structured log entries to `logs/linux-eye.log`.

## What it does

Each cycle, the monitor:

1. Lists the current running processes.
2. Checks each process name against a built-in list of suspicious keywords.
3. Writes either an `INFO` or `CRITICAL` log entry for every process.

This is a keyword-based detector, not a full EDR or malware scanner.

## Requirements

- Python 3.10 or newer
- A Linux system

## Installation

```bash
git clone https://github.com/amitpadhan525/linux-eye.git
cd linux-eye
pip install -r requirements.txt
```

## Configuration

The default settings live in [config/config.yaml](config/config.yaml):

- `tool_name`: display name used by the project
- `log_dir`: directory for logs
- `log_file`: log filename
- `refresh_interval`: delay in seconds between scans

The logger writes JSON lines to `logs/linux-eye.log` by default.

## Run

Start the monitor from the repository root:

```bash
python -m linux_eye.main
```

The process runs continuously until you stop it with `Ctrl+C`.

## Logs

Each log entry includes:

- timestamp
- severity
- source
- message
- details about the process

Example output is stored in `logs/linux-eye.log`.

## How it works

The main loop is in [linux_eye/main.py](linux_eye/main.py). It calls the process monitor every `refresh_interval` seconds, and the monitor logic is in [linux_eye/monitors/process_monitor.py](linux_eye/monitors/process_monitor.py).

## Limitations

- Detection is based on process name matching only.
- False positives are possible because common shell tools and admin utilities are included in the keyword list.
- It does not inspect process arguments, hashes, network connections, or filesystem activity.

## Project layout

```text
linux_eye/
	main.py                # entry point
	monitors/
		process_monitor.py   # process scanning logic
	utils/
		config.py            # config loader
		logger.py            # JSON log writer
config/
	config.yaml            # runtime settings
logs/
	linux-eye.log          # generated log file
```