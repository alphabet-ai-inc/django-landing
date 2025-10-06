from django import template


register = template.Library()


@register.filter
def get_partial_template(element):
    return f"elements/_{element.type}.html"

# @register.filter
# def get_partial_template(element):
#     type_map = {
#         'header': 'elements/_header.html',
#         'text': 'elements/_text.html',
#         'image': 'elements/_image.html',
#         'container': 'elements/_container.html',
#         'list': 'elements/_list.html',
#         'button': 'elements/_button.html',
#         'section': 'elements/_section.html',
#     }
#     return type_map.get(element.type, 'elements/_default.html')
