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


def get_latest_filesystem_datetime(path):
    latest = 0
    for path in list_directory(
            path,
            ignore_directories=VCS_NAMES,
            ignore_extensions=IGNORE_EXTENSIONS):
        mtime = os.path.getmtime(path)
        latest = max(mtime, latest)
    return datetime.fromtimestamp(latest)


def filesystem_microsecond_autoversion(path):
    """Filesystem latest change, microsecond granularity.

    On Linux this will include microsecond information in the generated
    versioning URLs.

    On some filesystems, such as MacOS X, there is no microsecond information,
    so that this behaves like filesystem_second_autoversion.
    """
    return get_latest_filesystem_datetime(path).isoformat()


def filesystem_second_autoversion(path):
    """Filesystem latest change, second granularity.

    Some filesystems such as MacOS X don't return microsecond timestamps.
    To make the autoversioning scheme behave consistently across platforms,
    rip off the microsecond information.
    """
    result = get_latest_filesystem_datetime(path)
    result = result.replace(microsecond=0)
    return result.isoformat()
