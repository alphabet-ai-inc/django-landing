from django import template


register = template.Library()


@register.filter
def get_partial_template(element):
    return f"elements/_{element.type}.html"
