from django import template
from django.contrib.auth.models import Group

register = template.Library()


@register.filter(name='has_group')
def has_group(user, group_name):
    group = Group.objects.get(name=group_name)
    return True if group in user.groups.all() else False


@register.filter(name='multiply')
def multiply(value, arg):
    return value * arg


@register.filter(name='divide')
def divide(value, arg):
    if int(arg) == 0:
        return 0
    return int(value) // int(arg)


@register.filter(name='get_page_range')
def get_page_range(value, arg):
    start = int(value) - int(value) % 10 + 1
    end = start + 10
    if end > arg:
        end = arg
    return xrange(start, end)
