"""Base factory interfaces and abstract classes."""

from abc import ABC, abstractmethod
from typing import Any


class Factory(ABC):
    """Abstract base class for all factories."""
    
    @abstractmethod
    def create(self, **kwargs) -> Any:
        """Create an instance of the target class.
        
        Args:
            **kwargs: Arguments for creating the instance
            
        Returns:
            Created instance
        """
        pass


class FactoryDecorator(Factory):
    """Abstract base class for factory decorators.
    
    Implements the decorator pattern for factories, allowing
    additional behavior to be added to factories dynamically.
    """
    
    def __init__(self, factory: Factory):
        """Initialize with the factory to decorate.
        
        Args:
            factory: The factory instance to wrap
        """
        self.factory = factory
    
    @abstractmethod
    def create(self, **kwargs) -> Any:
        """Create an instance, potentially modifying behavior.
        
        Subclasses should implement this to add their specific behavior
        before/after delegating to the wrapped factory.
        
        Args:
            **kwargs: Arguments for creating the instance
            
        Returns:
            Created instance with decorator behavior applied
        """
        pass