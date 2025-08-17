"""Decorator that wraps list factory results with Exported classes."""

from typing import Type, Any, List
from models.factories.base import Factory
from exporters.base import Exported


class ExportedListFactoryDecorator(Factory):
    """Decorator that wraps each item in a list with an Exported class."""
    
    def __init__(self, factory: Factory, exported_class: Type[Exported]):
        """Initialize with wrapped factory and Exported class.
        
        Args:
            factory: The factory that returns a list
            exported_class: The Exported class to wrap each item with
        """
        self.factory = factory
        self.exported_class = exported_class
    
    def create(self, **kwargs) -> List[Any]:
        """Create list and wrap each item with Exported class.
        
        Args:
            **kwargs: Arguments for creating the list
            
        Returns:
            List of instances wrapped with Exported class
        """
        # Create the list using wrapped factory
        items = self.factory.create(**kwargs)
        
        # Wrap each item with Exported class
        return [self.exported_class(item) for item in items]