"""Decorator that wraps factory results with Exported classes."""

from typing import Type, Any
from models.factories.base import FactoryDecorator, Factory
from exporters.base import Exported


class ExportedFactoryDecorator(FactoryDecorator):
    """Decorator that wraps factory results with an Exported class."""
    
    def __init__(self, factory: Factory, exported_class: Type[Exported]):
        """Initialize with wrapped factory and Exported class.
        
        Args:
            factory: The factory to wrap
            exported_class: The Exported class to wrap results with
        """
        super().__init__(factory)
        self.exported_class = exported_class
    
    def create(self, **kwargs) -> Any:
        """Create instance and wrap with Exported class.
        
        Args:
            **kwargs: Arguments for creating the instance
            
        Returns:
            Instance wrapped with Exported class
        """
        # Create the base instance using wrapped factory
        instance = self.factory.create(**kwargs)
        
        # Wrap with Exported class
        return self.exported_class(instance)