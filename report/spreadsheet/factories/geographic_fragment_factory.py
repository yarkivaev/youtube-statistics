"""Geographic fragment factory for creating geographic data fragments."""

from typing import List, Dict, Any
from models.factories.base import Factory, FactoryDecorator
from ..spreadsheet_fragment import SpreadsheetFragment


class GeographicFragmentFactory(FactoryDecorator):
    """Factory decorator for creating geographic metrics fragments.
    
    Decorates a base factory to add geographic metrics fragment creation capabilities.
    """
    
    def __init__(self, factory: Factory):
        """Initialize with a factory to decorate.
        
        Args:
            factory: The base factory to wrap (typically SpreadsheetFragmentFactory)
        """
        super().__init__(factory)
    
    def create(self, **kwargs) -> SpreadsheetFragment:
        """Create geographic metrics fragment.
        
        Args:
            **kwargs: Must include:
                - monthly_data: Dictionary with month keys and metric values including geographic data
                - months: Sorted list of month keys
            
        Returns:
            SpreadsheetFragment with geographic data
        """
        monthly_data = kwargs.get('monthly_data', {})
        months = kwargs.get('months', [])
        
        # Use the wrapped factory to create base fragment
        fragment = self.factory.create()
        
        # Section header for geographic views
        header_row = ['География просмотров']
        for _ in months:
            header_row.extend(['', '', ''])
        fragment = fragment.with_row(header_row)
        
        # Find max number of countries across all months
        max_countries = 0
        for month_key in months:
            month_data = monthly_data.get(month_key, {})
            geo_views = month_data.get('geographic_views_top', [])
            max_countries = max(max_countries, len(geo_views))
        
        # Add countries by views (up to max found or 9, whichever is smaller)
        rows_to_show = min(max_countries, 9)
        for i in range(rows_to_show):
            row = [f'География, топ-{i+1}']
            for month_key in months:
                month_data = monthly_data.get(month_key, {})
                geo_views = month_data.get('geographic_views_top', [])
                total_views = month_data.get('views', 0)
                
                if i < len(geo_views):
                    # geo_views contains GeographicMetrics objects or dicts
                    if isinstance(geo_views[i], dict):
                        country = geo_views[i].get('country', '')
                        views = geo_views[i].get('views', 0)
                    else:
                        # It's a GeographicMetrics object
                        country = geo_views[i].country_code if hasattr(geo_views[i], 'country_code') else ''
                        views = geo_views[i].views if hasattr(geo_views[i], 'views') else 0
                    
                    # Calculate percentage
                    percentage = round((views / total_views * 100), 1) if total_views > 0 else 0
                    
                    # Spread across 3 cells: country code, number, percentage
                    row.extend([country, str(views) if views else '', f"{percentage}%" if percentage else ''])
                else:
                    # Empty cells
                    row.extend(['', '', ''])
            fragment = fragment.with_row(row)
        
        # Add "Other" row for remaining views not in top countries (right after last country)
        other_row = ['География, остальные']
        for month_key in months:
            month_data = monthly_data.get(month_key, {})
            geo_views = month_data.get('geographic_views_top', [])
            total_views = month_data.get('views', 0)
            
            # Calculate sum of top countries' views
            top_countries_views = 0
            for geo in geo_views:
                if isinstance(geo, dict):
                    top_countries_views += geo.get('views', 0)
                else:
                    top_countries_views += geo.views if hasattr(geo, 'views') else 0
            
            # Calculate "Other" views
            other_views = total_views - top_countries_views
            if other_views > 0:
                percentage = round((other_views / total_views * 100), 1) if total_views > 0 else 0
                other_row.extend(['Other', str(other_views), f"{percentage}%"])
            else:
                other_row.extend(['', '', ''])
        fragment = fragment.with_row(other_row)
        
        # Add empty rows to reach 9 total if needed
        for i in range(rows_to_show + 1, 9):  # +1 to account for "Other" row
            row = [f'География, топ-{i+1}']
            for _ in months:
                row.extend(['', '', ''])
            fragment = fragment.with_row(row)
        
        # Empty row before subscribers section
        empty_row = [''] * (1 + 3 * len(months))
        fragment = fragment.with_row(empty_row)
        
        # Section header for geographic subscribers
        sub_header_row = ['География подписчиков']
        for _ in months:
            sub_header_row.extend(['', '', ''])
        fragment = fragment.with_row(sub_header_row)
        
        # Find max number of countries with subscribers across all months
        max_sub_countries = 0
        for month_key in months:
            month_data = monthly_data.get(month_key, {})
            geo_subs = month_data.get('geographic_subscribers_top', [])
            max_sub_countries = max(max_sub_countries, len(geo_subs))
        
        # Add countries by subscribers (up to max found or 5, whichever is smaller)
        sub_rows_to_show = min(max_sub_countries, 5)
        for i in range(sub_rows_to_show):
            row = [f'топ-{i+1}']
            for month_key in months:
                month_data = monthly_data.get(month_key, {})
                geo_subs = month_data.get('geographic_subscribers_top', [])
                total_subscribers = month_data.get('subscribers_gained', 0)
                
                if i < len(geo_subs):
                    # geo_subs contains GeographicMetrics objects or dicts
                    if isinstance(geo_subs[i], dict):
                        country = geo_subs[i].get('country', '')
                        subscribers = geo_subs[i].get('subscribers', 0)
                    else:
                        # It's a GeographicMetrics object
                        country = geo_subs[i].country_code if hasattr(geo_subs[i], 'country_code') else ''
                        subscribers = geo_subs[i].subscribers_gained if hasattr(geo_subs[i], 'subscribers_gained') else 0
                    
                    # Calculate percentage
                    percentage = round((subscribers / total_subscribers * 100), 1) if total_subscribers > 0 else 0
                    
                    # Spread across 3 cells: country code, number, percentage
                    row.extend([country, str(subscribers) if subscribers else '', f"{percentage}%" if percentage else ''])
                else:
                    # Empty cells
                    row.extend(['', '', ''])
            fragment = fragment.with_row(row)
        
        # Add "Other" row for remaining subscribers not in top countries (right after last country)
        if sub_rows_to_show > 0:  # Only add if there's at least one country
            other_sub_row = ['остальные']
            for month_key in months:
                month_data = monthly_data.get(month_key, {})
                geo_subs = month_data.get('geographic_subscribers_top', [])
                total_subscribers = month_data.get('subscribers_gained', 0)
                
                # Calculate sum of top countries' subscribers
                top_countries_subs = 0
                for geo in geo_subs:
                    if isinstance(geo, dict):
                        top_countries_subs += geo.get('subscribers', 0)
                    else:
                        top_countries_subs += geo.subscribers_gained if hasattr(geo, 'subscribers_gained') else 0
                
                # Calculate "Other" subscribers
                other_subs = total_subscribers - top_countries_subs
                if other_subs > 0:
                    percentage = round((other_subs / total_subscribers * 100), 1) if total_subscribers > 0 else 0
                    other_sub_row.extend(['Other', str(other_subs), f"{percentage}%"])
                else:
                    other_sub_row.extend(['', '', ''])
            fragment = fragment.with_row(other_sub_row)
            
            # Add empty rows to reach 5 total if needed
            for i in range(sub_rows_to_show + 1, 5):  # +1 to account for "Other" row
                row = [f'топ-{i+1}']
                for _ in months:
                    row.extend(['', '', ''])
                fragment = fragment.with_row(row)
        else:
            # No subscriber data, just add 5 empty rows
            for i in range(5):
                row = [f'топ-{i+1}']
                for _ in months:
                    row.extend(['', '', ''])
                fragment = fragment.with_row(row)
        
        return fragment