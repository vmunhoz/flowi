"""
Load data from several sources and compile them to a dask Dataframe
"""

from ._load_local import LoadLocal
from ._load_s3 import LoadS3


__all__ = ["LoadLocal", "LoadS3"]
