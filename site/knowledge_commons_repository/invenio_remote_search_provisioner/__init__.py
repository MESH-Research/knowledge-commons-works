from __future__ import absolute_import, print_function
from .ext import InvenioRemoteSearchProvisioner

"""An InvenioRDM Flask extension to provision remote search indexes
   for InvenioRDM records.

Sends a POST request to a remote search index API endpoint to provide the
index with metadata whenever a new record is created in InvenioRDM.
"""

__version__ = "1.0.0a"

__all__ = ("__version__", "InvenioRemoteSearchProvisioner")
