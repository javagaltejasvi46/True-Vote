from django import template
import time

register = template.Library()

@register.filter(name='timestamp')
def timestamp(value):
    """Convert a datetime object to a Unix timestamp"""
    try:
        return time.mktime(value.timetuple())
    except (AttributeError, ValueError):
        return '' 