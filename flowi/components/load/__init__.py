"""
Load data from several sources and compile them to a dask Dataframe
"""

from ._load_local import LoadLocal


__all__ = [
    'LoadLocal',
]
