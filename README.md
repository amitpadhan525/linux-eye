# linux-eye

linux-eye is a lightweight, low-footprint Linux security monitor designed to watch your system for suspicious process activity and network behavior in real-time.

It is dependency-free apart from `psutil` and `PyYAML`, and records structured, JSON-formatted entries to `logs/linux-eye.log` by default.

---

## Features

### 1. Process Monitoring
* **Suspicious Keyword Matching**: Periodically scans all running processes and checks their executable/process names against a list of suspicious keywords (e.g., shell utilities, hacking tools, common exploitation syntax, and unexpected system administrative commands).
* **Logging**: Generates detailed `INFO` logs for standard running processes and elevated `CRITICAL` alerts when process names match the signature list.

### 2. Network Connection & Port Scan Detection
* **Active Connections Tracking**: Continuously tracks remote socket connections on the system.
* **Port Scan Detection**: Tracks connection attempts per remote IP address. If a single remote IP attempts connections to more than **2 distinct ports within a 3-second window**, it triggers a `CRITICAL` "Possible port scan detected" alert.

---

## Requirements

* Python 3.10 or newer
* A Linux system with access to `/proc` and network interfaces
* Root/sudo privileges (recommended, to inspect socket connections owned by other users and all running processes)

---

## Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/amitpadhan525/linux-eye.git
   cd linux-eye
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

---

## Configuration

The application reads its runtime configuration from [config/config.yaml](file:///home/amit/github/linux-eye/config/config.yaml):

```yaml
general:
  tool_name: LinuxEye
  log_dir: logs/
  log_file: linux-eye.log
  refresh_interval: 5
```

* `tool_name`: Display name used by the monitor.
* `log_dir`: The directory where the log files will be written.
* `log_file`: The filename of the log output.
* `refresh_interval`: Scan frequency delay in seconds between cycles.

---

## Running the Application

To run the monitor, run the main package module from the repository root:

```bash
python -m linux_eye.main
```

> [!NOTE]
> Running as a standard user will successfully monitor processes owned by that user but might miss connections or process information owned by other users or root. Running with `sudo` is recommended for full visibility.

---

## How It Works

1. **Entry Point**: The application starts in [linux_eye/main.py](file:///home/amit/github/linux-eye/linux_eye/main.py) with a `while True` loop that executes the active monitors.
2. **Execution Cycle**:
   * **Process Check**: Runs [process_monitor.run()](file:///home/amit/github/linux-eye/linux_eye/monitors/process_monitor.py), retrieving process tables using `psutil`.
   * **Network Check**: Runs [network_monitor.run()](file:///home/amit/github/linux-eye/linux_eye/monitors/network_monitor.py), checking open TCP/UDP socket connections.
   * **Wait**: Sleeps for `refresh_interval` seconds before the next check.
3. **Alerting / Logging**:
   * Log entries are serialized as JSON Lines to `logs/linux-eye.log` by [linux_eye/utils/logger.py](file:///home/amit/github/linux-eye/linux_eye/utils/logger.py).

### Example JSON Log Output
```json
{
  "timestamp": "2026-06-30T14:30:15.123456",
  "severity": "CRITICAL",
  "message": "Possible port scan detected",
  "source": "network_monitor",
  "details": "192.168.1.50 hit {80, 443, 22} multiple ports recently"
}
```

---

## Limitations

* **Keyword-based Process Detection**: Detection relies on process names and does not evaluate file hashes, deep system call activity, or command-line arguments.
* **Simple Network Heuristics**: Port scanning detection is time-and-port threshold based and might raise false positives on high-throughput machines or web browsers making rapid connections.

---

## Project Layout

```text
linux-eye/
├── config/
│   └── config.yaml            # Runtime configurations
├── linux_eye/
│   ├── main.py                # Main loop entry point
│   ├── monitors/
│   │   ├── network_monitor.py # Active connection monitoring & port scan detection
│   │   └── process_monitor.py # Process matching signatures
│   └── utils/
│       ├── config.py          # Config loader utility
│       └── logger.py          # JSON structured logging implementation
├── logs/
│   └── linux-eye.log          # Generated structured log files
├── idea.txt                   # Brainstormed development roadmap
├── requirements.txt           # Dependencies
└── LICENSE                    # Project license
```