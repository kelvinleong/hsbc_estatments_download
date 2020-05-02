"""
-------------------------------------------------------------------------------
File Watcher to monitor asynchroneously new downloaded files
-------------------------------------------------------------------------------
"""

import time
import tempfile
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, PatternMatchingEventHandler
from shutil import copyfile
import logging

log = logging.getLogger('AutoDownloads.filewatcher')


class FileWatcher:

    class Handler(PatternMatchingEventHandler):

        def __init__(self, watcher):
            super(FileWatcher.Handler, self).__init__(patterns = ["*.pdf"], ignore_directories = True)
            self.watcher = watcher

        def on_any_event(self, event):
            log.debug("Trace received %s event - %s.", event.event_type, event.src_path)

        def on_moved(self, event):
            # file is downloaded with .crdownload suffix and once downloaded renamed to target name
            # captured as a move to the expected target suffix
            log.debug("Received moved event - %s -> %s.", event.src_path, event.dest_path)
            self.watcher.notify(Path(event.dest_path))

    def __init__(self, watchdir = None):
        if watchdir is None:
            self.watched_dir = tempfile.TemporaryDirectory()
            self.watched_dir_path = Path(self.watched_dir.name)
        else:
            self.watched_dir = str(watchdir)
            self.watched_dir_path = watchdir
        log.debug("temp dir for download is [{!s}]".format(self.watched_dir))
        self.new_file = None
        self.observer = Observer()
        self.observer.start()
        self.watch = None

    def get_dir(self):
        return self.watched_dir_path

    def notify(self, f):
        self.new_file = f

    def _new_handler(self):
        return FileWatcher.Handler(self)

    def _init_observer(self):
        if self.watch is None:
            event_handler = self._new_handler()
            self.new_file = None
            self.watch = self.observer.schedule(event_handler, str(self.watched_dir_path), recursive=False)
            log.debug('start waiting for download')

    def start(self):
        self._init_observer()

    def wait_move_file(self, target, timeout=40):
        self._init_observer()
        try:
            while self.new_file is None and timeout >= 0:
                time.sleep(1)
                timeout -= 1
            self.observer.unschedule(self.watch)
            if self.new_file is not None:
                if not target.is_file():
                    copyfile(str(self.new_file), str(target))
                    self.new_file.unlink()
                    log.info("File downloaded : %s", str(target))
                else:
                    log.warning("File already existed dowloaded file is trashed")
            else:
                log.error("download failed with timeout")
        except:
            self.observer.unschedule(self.watch)
            log.exception("error while waiting for file download")

        self.watch = None
        return self.new_file is not None