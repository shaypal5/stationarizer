from .core import (  # noqa: F401
    simple_auto_stationarize,
)

from ._version import get_versions
__version__ = get_versions()['version']
del get_versions
