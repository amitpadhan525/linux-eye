import time
import psutil
from linux_eye.utils.config import CONFIG
from linux_eye.utils.logger import log_critical

# Dictionary tracking remote IP -> list of (local_port, timestamp)
connection_history = {}

# Keep track of recently alerted (ip, port_set) to avoid repeated alerts in the same window
_recent_alerts = {}

# Configurable detection settings
WINDOW_SECONDS = CONFIG.get('network_monitor', {}).get('window_seconds', 3)
PORT_THRESHOLD = CONFIG.get('network_monitor', {}).get('port_threshold', 2)

def clean_old_entries():
    """Remove connection timestamps and alert records older than the sliding window."""
    now = time.time()
    
    # 1. Clean connection history
    for ip in list(connection_history.keys()):
        active_entries = [
            (port, ts) for port, ts in connection_history[ip]
            if now - ts <= WINDOW_SECONDS
        ]
        if active_entries:
            connection_history[ip] = active_entries
        else:
            # Delete empty keys to prevent memory growth
            del connection_history[ip]

    # 2. Clean recent alert deduplication cache
    for ip in list(_recent_alerts.keys()):
        if now - _recent_alerts[ip]['timestamp'] > WINDOW_SECONDS:
            del _recent_alerts[ip]

def check_suspicious():
    """Identify remote IPs contacting multiple distinct local ports in a short window."""
    now = time.time()
    for ip, entries in list(connection_history.items()):
        targeted_ports = {
            port for port, ts in entries
            if now - ts <= WINDOW_SECONDS
        }

        if len(targeted_ports) > PORT_THRESHOLD:
            # Check if we already alerted for this IP and port set recently
            last_alert = _recent_alerts.get(ip)
            if last_alert and last_alert['ports'] == targeted_ports:
                continue

            ports_str = ", ".join(map(str, sorted(targeted_ports)))
            log_critical(
                source='network_monitor',
                message="Possible port scan detected",
                details={
                    "remote_ip": ip,
                    "targeted_local_ports": sorted(list(targeted_ports)),
                    "window_seconds": WINDOW_SECONDS,
                    "summary": f"Remote host {ip} contacted {len(targeted_ports)} distinct ports ({ports_str}) recently"
                }
            )
            # Record alert
            _recent_alerts[ip] = {
                'ports': targeted_ports,
                'timestamp': now
            }

def run():
    """Inspect active sockets and track incoming connection patterns."""
    try:
        connections = psutil.net_connections(kind='inet')
    except (psutil.AccessDenied, PermissionError):
        return

    now = time.time()
    for con in connections:
        # Check for remote address and valid local listening/bound port
        if con.raddr and con.laddr:
            remote_ip = con.raddr.ip
            local_port = con.laddr.port

            # Ignore localhost / loopback traffic
            if remote_ip in ("127.0.0.1", "::1"):
                continue

            if remote_ip in connection_history:
                connection_history[remote_ip].append((local_port, now))
            else:
                connection_history[remote_ip] = [(local_port, now)]

    # Prune outdated records and evaluate port thresholds
    clean_old_entries()
    check_suspicious()