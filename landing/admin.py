from django.contrib import admin
from django.utils.safestring import mark_safe
from django.utils.html import format_html
from mptt.admin import MPTTModelAdmin
from adminsortable2.admin import SortableAdminBase, SortableInlineAdminMixin
from .models import Page, PageElement


class PageElementInline(SortableInlineAdminMixin, admin.TabularInline):
    model = PageElement
    extra = 1
    fields = ('type', 'content_preview', 'image', 'css_classes', 'order', 'parent')
    readonly_fields = ('content_preview',)

    def content_preview(self, obj):
        if obj.type == 'image' and obj.image:
            return format_html('<img src="{}" width="50" />', obj.image.url)
        return mark_safe(obj.content[:50] + '...' if obj.content and len(obj.content) > 50 else obj.content)

    content_preview.short_description = 'Content Preview'


@admin.register(Page)
class PageAdmin(SortableAdminBase, admin.ModelAdmin):  # Изменено: добавлено SortableAdminBase
    list_display = ('title', 'slug', 'created_at', 'updated_at')
    list_filter = ('created_at',)
    search_fields = ('title', 'slug')
    inlines = [PageElementInline]


@admin.register(PageElement)
class PageElementAdmin(MPTTModelAdmin, SortableInlineAdminMixin):
    list_display = ('id', 'type', 'page', 'content_preview', 'css_classes', 'order')
    list_filter = ('type', 'page', 'parent')
    search_fields = ('content', 'css_classes')
    sortable_by = ('order',)
    mptt_level_indent = 20

    def content_preview(self, obj):
        if obj.type == 'image' and obj.image:
            return format_html('<img src="{}" width="50" />', obj.image.url)
        return mark_safe(obj.content[:50] + '...' if obj.content and len(obj.content) > 50 else obj.content)

    content_preview.short_description = 'Content Preview'

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('page').prefetch_related('children')

    class Media:
        css = {
            'all': ('admin/css/custom_admin.css',)
        }
        js = ('admin/js/custom_sortable.js',)