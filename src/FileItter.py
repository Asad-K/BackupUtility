import os.path as op
import os
from os import scandir
import hashlib


class FileItter:
    """
    produces an iterator for a file tree
    """

    def __init__(self, path):
        if not op.exists(path):
            FileNotFoundError(path)
        self.path = path

    def itter_files(self, path):
        """
        Recursively yield DirEntry objects for given directory
        """
        for entry in scandir(path):
            if entry.is_dir(follow_symlinks=False):
                yield from self.itter_files(entry.path)
            else:
                yield entry.path

    def itter_directories(self):  # consider os.scandir()
        """
        iteratively yield directories
        """
        for root, dirs, files in os.walk(self.path):
            for dir in dirs:
                yield os.path.join(root, dir)

    @staticmethod
    def hash_file(path):
        """
        hashes file with md5
        """
        BLOCKSIZE = 65536
        h = hashlib.md5()
        with open(path, 'rb') as f:
            buf = f.read(BLOCKSIZE)
            while len(buf) > 0:
                h.update(buf)
                buf = f.read(BLOCKSIZE)
        hash_ = h.hexdigest()
        return hash_.strip()
