from django import template

register = template.Library()


@register.filter
def has_file(field):
    """Check if an ImageField or FileField has an associated file."""
    try:
        return bool(field and field.name)
    except (ValueError, AttributeError):
        return False
