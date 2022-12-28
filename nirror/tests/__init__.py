"""packages initialisation: paths for unittests"""
import os
import sys

sys.path.append(
    os.path.abspath(f"{__file__}/../../../nirror/")
)

import nirlibs
import nirlibs.download as dl
