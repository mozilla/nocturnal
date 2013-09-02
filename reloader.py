import os
import time

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from scrape import CURRENT_PATH, OUTPUT_PATH, main

from jinja2 import TemplateSyntaxError


class FileSystemChangeHandler(FileSystemEventHandler):
    def on_any_event(self, event):
        """
        Handler for any file system change.

        Runs more often than probably nessasary, but reloading is cheap since we have
        all our resources downloaded.
        """
        if not event.src_path.startswith(os.path.join(CURRENT_PATH, OUTPUT_PATH)):
            print 'Reloading'
            try:
                main()
            except (TemplateSyntaxError, UnicodeEncodeError) as e:
                print e
            else:
                print 'Reloaded'


if __name__ == "__main__":
    # Initial Run
    print 'Starting initial build (make sure you have internet).'
    main()

    event_handler = FileSystemChangeHandler()
    observer = Observer()
    observer.schedule(event_handler, CURRENT_PATH, recursive=True)
    observer.start()
    print 'Listening to file system changes.'
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
