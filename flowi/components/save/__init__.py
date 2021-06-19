"""
Load data from several sources and compile them to a dask Dataframe
"""

from ._save_local import SaveLocal
from ._save_s3 import SaveS3


__all__ = ["SaveLocal", "SaveS3"]
