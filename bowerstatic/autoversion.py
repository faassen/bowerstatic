from datetime import datetime
import os


VCS_NAMES = ['.svn', '.git', '.bzr', '.hg']
IGNORE_EXTENSIONS = ['.swp', '.tmp', '.pyc', '.pyo']


def list_directory(path, ignore_directories, ignore_extensions):
    for root, dirs, files in os.walk(path):
        # skip over directories to ignore
        for dir in ignore_directories:
            try:
                dirs.remove(dir)
            except ValueError:
                pass
        # we are interested in the directory itself
        yield root
        for file in files:
            _, ext = os.path.splitext(file)
            if ext in ignore_extensions:
                continue
            yield os.path.join(root, file)


def autoversion(path):
    latest = 0
    for path in list_directory(
            path,
            ignore_directories=VCS_NAMES,
            ignore_extensions=IGNORE_EXTENSIONS):
        mtime = os.path.getmtime(path)
        latest = max(mtime, latest)
    return datetime.fromtimestamp(latest).isoformat()[:-1]
