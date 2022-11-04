
from django.urls import reverse
from django import template

register = template.Library()

@register.filter
def get_key_value(dict, key):
    return dict.get(key, '')

@register.inclusion_tag('breadcrumbs/item.html')
def breadcrumb_item(text, viewname, *args, **kwargs):
    return {
        'text': text,
        'url': reverse(viewname, args=[*args, *kwargs.values()])
    }

@register.inclusion_tag('breadcrumbs/item_active.html')
def breadcrumb_item_active(text):
    return {
        'text': text
    }

@register.filter
def get_type(value):
    return type(value).__name__

# Credit for filter implementation: https://stackoverflow.com/a/2507447/10640126
@register.filter(is_safe=True)
def url_target_blank(a_tag_text):
    return a_tag_text.replace('<a ', '<a target="_blank" ')