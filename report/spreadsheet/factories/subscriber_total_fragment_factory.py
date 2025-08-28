"""Subscriber total fragment factory for creating subscriber total fragments."""

from typing import List, Optional
from domain import Factory, FactoryDecorator
from ..spreadsheet_fragment import SpreadsheetFragment
from domain import Channel


class SubscriberTotalFragmentFactory(FactoryDecorator):
    """Factory decorator for creating subscriber total fragments.
    
    Decorates a base factory to add subscriber total fragment creation capabilities.
    """
    
    def __init__(self, factory: Factory):
        """Initialize with a factory to decorate.
        
        Args:
            factory: The base factory to wrap (typically SpreadsheetFragmentFactory)
        """
        super().__init__(factory)
    
    def create(self, **kwargs) -> SpreadsheetFragment:
        """Create subscriber totals fragment.
        
        Args:
            **kwargs: Must include:
                - channel: Channel object with subscriber_count
                - months: List of month keys
            
        Returns:
            SpreadsheetFragment with subscriber totals
        """
        channel = kwargs.get('channel')
        months = kwargs.get('months', [])
        
        if not channel or not hasattr(channel, 'subscriber_count'):
            return self.factory.create()
        
        # Use the wrapped factory to create base fragment
        fragment = self.factory.create()
        
        row = ['Всего подписчиков']
        for _ in months:
            # This would need cumulative calculation in real implementation
            row.extend([str(channel.subscriber_count), '', ''])
        
        return fragment.with_row(row)