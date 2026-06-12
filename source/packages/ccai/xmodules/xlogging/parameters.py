
from typing import Optional

class LoggingLocation:

    def __init__(self, directory: str, basename: str, ext: Optional[str] = ".log"):
        self.directory = directory
        self.basename = basename
        self.ext = ext
        return


class LoggingReduction:

    def __init__(self, reductionlevel: str, swap_name: str, ext: Optional[str] = ".log"):
        self.reductionlevel = reductionlevel
        self.swap_name = swap_name
        self.ext = ext
        return