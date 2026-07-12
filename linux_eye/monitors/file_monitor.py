from inotify_simple import INotify, flags
from linux_eye.utils.logger import log_critical,log_warning

def run():
    CRITICAL_FILES=['passwd','shadow','sudoers']
    watch_flags=flags.MODIFY | flags.DELETE | flags.ATTRIB
    inotify=INotify()
    wd=inotify.add_watch('/etc',watch_flags)
    while True:
        events=inotify.read()
        for event in events:
            if event.name in CRITICAL_FILES:
                if event.mask & flags.MODIFY:
                    log_critical(
                        source='Files_monitor',
                        message="Critical system file modified",
                        details={
                            'filename':event.name,
                            'path':f'/etc/{event.name}',
                            'event_type':'MODIFIED'}
                    )
                elif event.mask & flags.DELETE:
                    log_critical(
                        source='Files_monitor',
                        message="Critical system file deleted",
                        details={
                        'filename':event.name,
                        'path':f'/etc/{event.name}',
                            'event_type':'DELETED'}
                    )
                elif event.mask & flags.ATTRIB:
                    log_warning(
                        source='Files_monitor',
                        message="Critical system file permission changed",
                        details={
                            'filename':event.name,
                            'path':f'/etc/{event.name}',
                            'event_type':'Permission Changed'}
                    )
