# -*- coding: utf-8 -*-

import os
from PerfectoLibrary.keywords import *
from PerfectoLibrary.listeners import *
from PerfectoLibrary.version import VERSION

__version__ = VERSION


class PerfectoLibrary(
    _DeviceKeywords,
	_PerfectoListener,
):
    """

    """

    ROBOT_LIBRARY_SCOPE = 'GLOBAL'
    ROBOT_LIBRARY_VERSION = VERSION

    def __init__(self):
        """
        """
        for base in PerfectoLibrary.__bases__:
            base.__init__(self)
