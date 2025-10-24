from django import template
from django.template.loader import render_to_string
import json

from django.utils.safestring import mark_safe

register = template.Library()


@register.simple_tag(takes_context=True)
def render_element(context, element):
    if element.type.lower() == 'image':
        print('test')
        print(f"🔍 IMAGE {element.id}")
        print(f": html_attrs='{element.html_attrs}...'")
    edit_mode = context.get('edit_mode', False)

    tag = element.get_tag()
    css_classes = element.css_classes or ''

    # ✅ БЕЗОПАСНАЯ обработка html_attrs
    html_attrs_safe = getattr(element, 'html_attrs', {}) or {}
    if isinstance(html_attrs_safe, str):
        try:
            html_attrs_safe = json.loads(html_attrs_safe)
        except:
            html_attrs_safe = {}

    if (element.type.lower() == 'image'):
        attrs_str = f' src="{element.image.url}"'
    else:
        attrs_str = ''
    for key, value in html_attrs_safe.items():
        if value is not None:
            if not (element.type.lower() == 'image' and key == 'src'):
              attrs_str += f' {key}="{value}"'

    # ✅ СТИЛИ
    style_parts = []
    if element.type == 'header':
        bg_image = element.props.get('background_image')
        if bg_image:
            style_parts.append(f"background-image: url({bg_image});")
        style_attr = html_attrs_safe.get('style')
        if style_attr:
            style_parts.append(str(style_attr))
    style_str = f' style="{"; ".join(style_parts)}"' if style_parts else ''

    content_html = ''
    if element.type.lower() == 'image' and element.image:
        alt = html_attrs_safe.get('alt', element.props.get('alt', ''))
        img_attrs = ''
        for key, value in html_attrs_safe.items():
            if key != 'style' and key != 'src' and value is not None:  # 🔥 ИГНОР src!
                print(f'найден attr для image {element.id}: {key}={value}')
                safe_value = str(value).replace('"', '&quot;')
                img_attrs += f' {key}="{safe_value}"'
        content_html = '' # f'<img class="{css_classes}" src="{element.image.url}" alt="{alt}"{img_attrs} />'
    elif element.content and element.type != 'image':  # 🔥 СТРОГО!
        if element.type == 'text':
            content_html = f"<p class='{css_classes}'>{element.content}</p>"
        else:
            content_html = element.content

    children_html = render_children(context, element) if (edit_mode or element.children.exists()) else ''

    context_dict = {
        'element': element, 'tag': tag, 'css_classes': css_classes,
        'html_attrs': mark_safe(attrs_str), 'style_str': style_str,
        'content_html': content_html, 'children_html': children_html,
        'edit_mode': edit_mode,
    }

    return render_to_string('elements/_element_base.html', context_dict)


def render_children(context, element):
    children_html = ''
    for child in element.children.all():
        try:
            child_html = render_element(context, child)
            children_html += child_html
        except:
            pass
    return children_html