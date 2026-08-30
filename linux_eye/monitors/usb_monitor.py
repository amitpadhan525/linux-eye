from linux_eye.utils.logger import log_info, log_warning

def run():
    """Monitor system for USB device insertion and removal events using pyudev."""
    try:
        import pyudev
    except ImportError:
        print("[*] pyudev library not installed. USB monitoring is disabled.")
        return

    try:
        context = pyudev.Context()
        monitor = pyudev.Monitor.from_netlink(context)
        # Filter for USB subsystem devices
        monitor.filter_by(subsystem='usb')
    except Exception as e:
        print(f"[!] Could not initialize USB monitor: {e}")
        return

    print("[*] USB monitor active.")
    try:
        for device in iter(monitor.poll, None):
            action = device.action
            dev_type = device.get('DEVTYPE', '')

            # Focus on actual usb_device nodes rather than sub-interfaces
            if dev_type == 'usb_device':
                vendor = device.get('ID_VENDOR_FROM_DATABASE') or device.get('ID_VENDOR', 'Unknown Vendor')
                model = device.get('ID_MODEL_FROM_DATABASE') or device.get('ID_MODEL', 'Unknown Model')
                serial = device.get('ID_SERIAL_SHORT', 'N/A')
                dev_node = device.device_node or device.sys_path

                details = {
                    'action': action,
                    'vendor': vendor,
                    'model': model,
                    'serial': serial,
                    'node': dev_node
                }

                if action == 'add':
                    log_warning(
                        source='usb_monitor',
                        message=f"USB device connected: {vendor} - {model}",
                        details=details
                    )
                elif action == 'remove':
                    log_info(
                        source='usb_monitor',
                        message=f"USB device disconnected: {vendor} - {model}",
                        details=details
                    )
    except Exception as e:
        print(f"[!] USB monitor error: {e}")
