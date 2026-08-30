import os
from inotify_simple import INotify, flags
from linux_eye.utils.config import CONFIG
from linux_eye.utils.logger import log_critical, log_warning

# Load monitored settings
file_cfg = CONFIG.get('file_monitor', {})
WATCH_DIR = file_cfg.get('watch_dir', '/etc')
CRITICAL_FILES = set(file_cfg.get('critical_files', ['passwd', 'shadow', 'sudoers']))

def run():
    """Monitor critical files for modifications, deletions, renames, and permission changes."""
    if not os.path.exists(WATCH_DIR):
        print(f"[!] File monitor target directory does not exist: {WATCH_DIR}")
        return

    # Watch for modifications, deletions, attribute changes, moves/renames, and creation
    watch_flags = (
        flags.MODIFY
        | flags.DELETE
        | flags.ATTRIB
        | flags.MOVED_TO
        | flags.CREATE
    )

    try:
        inotify = INotify()
        inotify.add_watch(WATCH_DIR, watch_flags)
    except PermissionError:
        print(f"[!] File monitor requires root privileges to watch {WATCH_DIR}.")
        return
    except Exception as e:
        print(f"[!] Error initializing file monitor on {WATCH_DIR}: {e}")
        return

    while True:
        try:
            events = inotify.read()
        except Exception:
            break

        for event in events:
            filename = event.name
            if filename in CRITICAL_FILES:
                file_path = os.path.join(WATCH_DIR, filename)

                if event.mask & (flags.MODIFY | flags.CREATE | flags.MOVED_TO):
                    event_name = "MODIFIED" if (event.mask & flags.MODIFY) else "REPLACED/CREATED"
                    log_critical(
                        source='file_monitor',
                        message=f"Critical system file {event_name.lower()}: {filename}",
                        details={
                            'filename': filename,
                            'path': file_path,
                            'event_type': event_name
                        }
                    )

                elif event.mask & flags.DELETE:
                    log_critical(
                        source='file_monitor',
                        message=f"Critical system file deleted: {filename}",
                        details={
                            'filename': filename,
                            'path': file_path,
                            'event_type': 'DELETED'
                        }
                    )

                elif event.mask & flags.ATTRIB:
                    log_warning(
                        source='file_monitor',
                        message=f"Critical system file permissions/attributes changed: {filename}",
                        details={
                            'filename': filename,
                            'path': file_path,
                            'event_type': 'ATTRIB_CHANGED'
                        }
                    )
