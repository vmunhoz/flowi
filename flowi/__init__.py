from importlib.metadata import version

print(version(__name__))
__version__ = version(__name__)

