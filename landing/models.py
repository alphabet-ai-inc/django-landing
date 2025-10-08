from django.db import models
from mptt.models import MPTTModel, TreeForeignKey
import os

def page_image_upload_to(instance, filename):
    """Generate path for downloading images based on page.slug"""
    return f"{instance.page.static_dir}/images/{os.path.basename(filename)}"

class Page(models.Model):
    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    template = models.CharField(max_length=255, default='landing_basic.html')
    external_url = models.URLField(blank=True, null=True)
    css_files = models.JSONField(default=list, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    @property
    def static_dir(self):
        """Path for page static files (page_<slug>/)"""
        return f"page_{self.slug}"

class PageElement(MPTTModel):
    ELEMENT_TYPES = (
        ('body', 'Body (page)'), # tag body
        ('pageheader', 'Header (page)'), # tag header
        ('header', 'Header (h1-h6)'),  # props: {'level': 1-6}
        ('text', 'Text/Paragraph'),  # Simple p с content
        ('image', 'Image'),  # props: {'alt': '...', 'size': 'full/small'}
        ('container', 'Simple Container'),  # div for nesting, props: {'layout': 'flex/grid'}
        ('grid', 'Grid Container'),  # div with columns, props: {'columns': 2/3, 'gap': 'md'}
        ('card', 'Card/Block'),  # div for services (h3 + p + img)
        ('list', 'List (ul/ol)'),  # props: {'ordered': True, 'items': [{'text': '...', 'subitems': [...]}]}
        ('button', 'Button/Link'),  # props: {'href': '...', 'type': 'submit', 'text': '...'}
        ('section', 'Section'),  # section for large blocks
    )

    page = models.ForeignKey(Page, on_delete=models.CASCADE, related_name='elements')
    type = models.CharField(max_length=50, choices=ELEMENT_TYPES)
    content = models.TextField(blank=True, null=True)
    props = models.JSONField(default=dict, blank=True)
    html_attrs = models.JSONField(default=dict, blank=True)
    image = models.ImageField(upload_to=page_image_upload_to, blank=True, null=True)  # Используем функцию
    css_classes = models.CharField(max_length=255, blank=True, null=True)
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    parent = TreeForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children')

    class MPTTMeta:
        order_insertion_by = ['order']

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.get_tag()} ({self.type}) for {self.page.title} id {self.id}"

    def get_render_props(self):
        if self.type == 'image':
            return {
                'src': self.image.url if self.image else self.props.get('src'),
                'alt': self.html_attrs.get('alt', ''),
                **self.props
            }
        elif self.type == 'list':
            return {'items': self.props.get('items', []), 'ordered': self.props.get('ordered', False)}
        elif self.type == 'grid':
            return {'columns': self.props.get('columns', 1), **self.props}
        elif self.type == 'card':
            return {'layout': self.props.get('layout', 'vertical'), **self.props}
        return self.props

    def get_static_path(self, filename):
        """Full path for static file (css или img)"""
        page_dir = self.page.static_dir
        if filename.endswith('.css'):
            return f"{page_dir}/css/{os.path.basename(filename)}"
        else:
            return f"{page_dir}/images/{os.path.basename(filename)}"

    def get_tag(self):
        tag_map = {
            'header': f"h{self.props.get('level', 2)}",
            'text': 'p',
            'image': 'img',
            'container': 'div',
            'list': 'ul' if not self.props.get('ordered', False) else 'ol',
            'button': 'button' if not self.props.get('href') else 'a',
            'section': 'section',
        }
        return tag_map.get(self.type, 'div')  # Дефолт div для неизвестных
