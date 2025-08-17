"""Base Exported abstraction using decorator pattern."""

from abc import ABC, abstractmethod
from typing import Any


class Exported(ABC):
    """Abstract base class for exporters using decorator pattern.
    
    Each Exported class wraps an object and provides an export() method
    that returns the exported representation of that object.
    """
    
    def __init__(self, obj: Any):
        """Initialize with the object to export.
        
        Args:
            obj: The object to be exported
        """
        self._obj = obj
    
    @abstractmethod
    def export(self) -> Any:
        """Export the wrapped object.
        
        Returns:
            The exported representation (dict, string, etc.)
        """
        pass
    
    def __getattr__(self, name):
        """Forward all attribute access to the wrapped object.
        
        This makes the Exported wrapper transparent, allowing direct
        access to all attributes and methods of the wrapped object.
        """
        return getattr(self._obj, name)