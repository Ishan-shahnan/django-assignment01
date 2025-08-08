from django import template

register = template.Library()


def has_group(user, group_name):
    """
    Returns True if the user is in the given group, else False.
    Usage: {% if user|has_group:"Admin" %}
    """
    return user.groups.filter(name=group_name).exists()


register.filter('has_group', has_group)
