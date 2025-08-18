"""Factory decorators for Google Sheets exporters."""

from typing import Type, Any, List, Optional
from models.factories.base import FactoryDecorator, Factory
from exporters.google_sheets_exported import GoogleSheetsExported


class GoogleSheetsFactoryDecorator(FactoryDecorator):
    """Decorator that wraps factory results with Google Sheets Exported class."""
    
    def __init__(
        self,
        factory: Factory,
        exported_class: Type[GoogleSheetsExported],
        spreadsheet_id: Optional[str] = None,
        create_new: bool = True,
        share_emails: Optional[List[str]] = None
    ):
        """Initialize with wrapped factory and Google Sheets Exported class.
        
        Args:
            factory: The factory to wrap
            exported_class: The Google Sheets Exported class to wrap results with
            spreadsheet_id: ID of existing spreadsheet or None to create new
            create_new: Whether to create a new spreadsheet
            share_emails: List of emails to share the spreadsheet with
        """
        super().__init__(factory)
        self.exported_class = exported_class
        self.spreadsheet_id = spreadsheet_id
        self.create_new = create_new
        self.share_emails = share_emails or []
    
    def create(self, **kwargs) -> Any:
        """Create instance and wrap with Google Sheets Exported class.
        
        Args:
            **kwargs: Arguments for creating the instance
            
        Returns:
            Instance wrapped with Google Sheets Exported class
        """
        # Create the base instance using wrapped factory
        instance = self.factory.create(**kwargs)
        
        # Wrap with Google Sheets Exported class
        wrapped = self.exported_class(instance)
        
        # Set Google Sheets specific attributes if the exported class supports them
        if hasattr(wrapped, 'spreadsheet_id'):
            wrapped.spreadsheet_id = self.spreadsheet_id
        if hasattr(wrapped, 'create_new'):
            wrapped.create_new = self.create_new
        if hasattr(wrapped, 'share_emails'):
            wrapped.share_emails = self.share_emails
        
        return wrapped


class GoogleSheetsListFactoryDecorator(FactoryDecorator):
    """Decorator that wraps list factory results with Google Sheets Exported classes."""
    
    def __init__(
        self,
        factory: Factory,
        exported_class: Type[GoogleSheetsExported],
        spreadsheet_id: Optional[str] = None,
        create_new: bool = True,
        share_emails: Optional[List[str]] = None
    ):
        """Initialize with wrapped factory and Google Sheets Exported class.
        
        Args:
            factory: The factory to wrap (must return a list)
            exported_class: The Google Sheets Exported class to wrap each item with
            spreadsheet_id: ID of existing spreadsheet or None to create new
            create_new: Whether to create a new spreadsheet
            share_emails: List of emails to share the spreadsheet with
        """
        super().__init__(factory)
        self.exported_class = exported_class
        self.spreadsheet_id = spreadsheet_id
        self.create_new = create_new
        self.share_emails = share_emails or []
    
    def create(self, **kwargs) -> List[Any]:
        """Create list of instances and wrap each with Google Sheets Exported class.
        
        Args:
            **kwargs: Arguments for creating the instances
            
        Returns:
            List of instances wrapped with Google Sheets Exported class
        """
        # Create the base instances using wrapped factory
        instances = self.factory.create(**kwargs)
        
        # Ensure we got a list
        if not isinstance(instances, list):
            raise TypeError(f"Factory {self.factory} must return a list for GoogleSheetsListFactoryDecorator")
        
        # Wrap each instance with Google Sheets Exported class
        wrapped_instances = []
        for instance in instances:
            wrapped = self.exported_class(instance)
            
            # Set Google Sheets specific attributes if the exported class supports them
            if hasattr(wrapped, 'spreadsheet_id'):
                wrapped.spreadsheet_id = self.spreadsheet_id
            if hasattr(wrapped, 'create_new'):
                wrapped.create_new = self.create_new
            if hasattr(wrapped, 'share_emails'):
                wrapped.share_emails = self.share_emails
            
            wrapped_instances.append(wrapped)
        
        return wrapped_instances