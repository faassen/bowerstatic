import os
import inspect


def module_relative_path(path):
    """return an absolute path from a given path which
    is relative to the calling module"""
    if os.path.isabs(path):
        return path

    calling_file = inspect.stack()[1][1]
    calling_dir = os.path.split(calling_file)[0]
    return os.path.join(calling_dir, path)
