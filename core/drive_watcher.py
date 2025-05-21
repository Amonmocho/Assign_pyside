import os
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Change this to whatever path you picked above:
SUBMISSION_DIR = r"G:\My Drive\Assignments_test"


class NewFileHandler(FileSystemEventHandler):
    """Watches for new .txt files and invokes the callback."""

    def __init__(self, callback):
        """
        :param callback: function to call with the full path of each new file
        """
        super().__init__()
        self.callback = callback

    def on_created(self, event):
        # event.is_directory → ignore directory events
        if not event.is_directory and event.src_path.lower().endswith(".txt"):
            # Give the file a moment to finish writing
            time.sleep(0.1)
            self.callback(event.src_path)


def watch_folder(on_new_file):
    """
    Start watching SUBMISSION_DIR for new .txt files.

    :param on_new_file: function taking one argument (the file path)
    """
    # Ensure the directory exists
    os.makedirs(SUBMISSION_DIR, exist_ok=True)

    # Set up watchdog
    handler = NewFileHandler(on_new_file)
    observer = Observer()
    observer.schedule(handler, SUBMISSION_DIR, recursive=False)
    observer.start()

    print(f"Watching for new submissions in:\n  {SUBMISSION_DIR}\nPress Ctrl+C to stop.")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()


# Example usage when you run this module directly:
if __name__ == "__main__":
    def process_submission(path):
        print(f"New submission detected: {path}")

    watch_folder(process_submission)
