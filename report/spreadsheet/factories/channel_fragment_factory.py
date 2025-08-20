"""Channel fragment factory for creating channel data fragments."""

from typing import List
from models.factories.base import Factory, FactoryDecorator
from ..spreadsheet_fragment import SpreadsheetFragment
from models import Channel


class ChannelFragmentFactory(FactoryDecorator):
    """Factory decorator for creating channel data fragments.
    
    Decorates a base factory to add channel fragment creation capabilities.
    """
    
    def __init__(self, factory: Factory):
        """Initialize with a factory to decorate.
        
        Args:
            factory: The base factory to wrap (typically SpreadsheetFragmentFactory)
        """
        super().__init__(factory)
    
    def create(self, **kwargs) -> SpreadsheetFragment:
        """Create channel info fragment.
        
        Args:
            **kwargs: Must include:
                - channel: Channel object to export
                - months: List of month keys (YYYY-MM format)
            
        Returns:
            SpreadsheetFragment with channel data
        """
        channel = kwargs.get('channel')
        months = kwargs.get('months', [])
        
        if not channel:
            return self.factory.create()
        
        # Use the wrapped factory to create base fragment
        fragment = self.factory.create()
        
        # Row 1: Video count
        row1 = ['Количество роликов']
        for _ in months:
            # For now, show total video count (ideally per-month uploads)
            row1.extend([str(channel.video_count), '', ''])
        fragment = fragment.with_row(row1)
        
        # Row 2: Advertiser count (placeholder)
        row2 = ['Количество рекламодателей']
        for _ in months:
            if channel.advertiser_count is not None:
                row2.extend([str(channel.advertiser_count), '', ''])
            else:
                row2.extend(['[Требуется ручной ввод]', '', ''])
        fragment = fragment.with_row(row2)
        
        # Row 3: Integrations (placeholder)
        row3 = ['Интеграции Ghost Writer или Школьных продуктов']
        for _ in months:
            if channel.integrations:
                row3.extend([channel.integrations, '', ''])
            else:
                row3.extend(['[Требуется ручной ввод]', '', ''])
        fragment = fragment.with_row(row3)
        
        return fragment