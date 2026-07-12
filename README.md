# linux-eye

linux-eye is a lightweight Linux security monitor that watches three things in parallel:
process activity, network connections, and critical file changes under `/etc`.
It writes structured JSONL logs to `logs/linux-eye.log` by default.

## What it detects

### Process monitoring
The process monitor scans running processes with `psutil` and raises a `CRITICAL`
event when the command line matches known suspicious patterns or tool names.

The current signature set includes reverse-shell style commands, download-and-execute
patterns, inline code execution, common persistence commands, obfuscation markers,
and destructive commands such as `rm -rf` and `chmod 777`.

### Network monitoring
The network monitor tracks remote socket connections. If the same remote IP touches
more than 2 distinct ports within a 3 second window, it logs a `CRITICAL`
"Possible port scan detected" event.

### File monitoring
The file monitor watches `/etc` with inotify and alerts on changes to sensitive files:
`passwd`, `shadow`, and `sudoers`.

It logs:
* `CRITICAL` when one of those files is modified or deleted
* `WARNING` when file attributes or permissions change

## Requirements

* Python 3.10 or newer
* Linux with access to `/proc` and inotify
* Packages listed in [requirements.txt](requirements.txt)
* `sudo` is recommended for broader visibility into processes and sockets owned by other users

## Installation

1. Clone the repository.
2. Install dependencies.

```bash
git clone https://github.com/amitpadhan525/linux-eye.git
cd linux-eye
pip install -r requirements.txt
```

## Configuration

Runtime settings live in [config/config.yaml](config/config.yaml):

```yaml
general:
   tool_name: LinuxEye
   log_dir: logs/
   log_file: linux-eye.log
   refresh_interval: 5
```

* `tool_name` is the display name used by the app.
* `log_dir` is the directory for log output.
* `log_file` is the log filename.
* `refresh_interval` controls the sleep interval, in seconds, between process and network scans.

## Usage

Run the monitor from the repository root:

```bash
python -m linux_eye.main
```

The application starts two threads:
* one thread loops over process and network checks
* one thread blocks on file events under `/etc`

## Logging

Logs are written as JSON lines. Each entry contains a timestamp, severity, source,
message, and details payload.

Example:

```json
{
   "timestamp": "2026-07-12T14:30:15.123456",
   "severity": "CRITICAL",
   "message": "Possible port scan detected",
   "source": "network_monitor",
   "details": "192.168.1.50 hit {80, 443, 22} multiple ports recently"
}
```

## Project Layout

```text
linux-eye/
├── config/
│   └── config.yaml
├── linux_eye/
│   ├── main.py
│   ├── monitors/
│   │   ├── file_monitor.py
│   │   ├── network_monitor.py
│   │   └── process_monitor.py
│   └── utils/
│       ├── config.py
│       └── logger.py
├── logs/
├── idea.txt
├── requirements.txt
└── LICENSE
```

## Notes and limitations

* Process detection is command-line and name based. It does not inspect hashes, kernel events, or full behavioral telemetry.
* Network detection is heuristic and can produce false positives on busy hosts.
* File monitoring currently only watches `/etc` and a small list of sensitive filenames.
