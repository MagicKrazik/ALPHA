# website/utils.py - Simplified version without email activation
from django.conf import settings
from django.utils import timezone

# Simple utility functions for the project
def get_current_timestamp():
    """Get current timestamp"""
    return timezone.now()

def format_date_for_display(date):
    """Format date for display"""
    if date:
        return date.strftime('%d/%m/%Y')
    return ''

def format_datetime_for_display(datetime_obj):
    """Format datetime for display"""
    if datetime_obj:
        return datetime_obj.strftime('%d/%m/%Y %H:%M')
    return ''