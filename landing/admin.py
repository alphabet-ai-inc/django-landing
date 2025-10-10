from django.contrib import admin
from django.utils.safestring import mark_safe
from django.utils.html import format_html
from django.shortcuts import render, redirect
from django.urls import path, reverse
from django.contrib import messages
from django.utils.html import format_html
from mptt.admin import MPTTModelAdmin
from adminsortable2.admin import SortableAdminBase, SortableInlineAdminMixin
from .models import Page, PageElement
from .services.page_parser import PageParserService


class ImportPageForm:
    """Simple form class without Django forms"""
    pass


class PageElementInline(SortableInlineAdminMixin, admin.TabularInline):
    model = PageElement
    extra = 1
    fields = ('type', 'content', 'content_preview', 'image', 'css_classes', 'order', 'parent')
    readonly_fields = ('content_preview',)

    def content_preview(self, obj):
        if obj.type == 'image' and obj.image:
            return format_html('<img src="{}" width="50" />', obj.image.url)
        return mark_safe(obj.content[:50] + '...' if obj.content and len(obj.content) > 50 else obj.content or '')

    content_preview.short_description = 'Preview'


@admin.register(Page)
class PageAdmin(SortableAdminBase, admin.ModelAdmin):
    list_display = ('title', 'slug', 'created_at', 'updated_at')
    list_filter = ('created_at',)
    search_fields = ('title', 'slug')
    inlines = [PageElementInline]

    change_list_template = 'admin/landing/page/change_list.html'

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('import-from-url/', self.admin_site.admin_view(self.import_page_view), name='landing_page_import'),
        ]
        return custom_urls + urls

    def import_page_view(self, request):
        """View for importing a page from URL."""
        if request.method == 'POST':
            url = request.POST.get('url', '').strip()
            if url:
                try:
                    parser = PageParserService(url)
                    page = parser.parse_and_import()
                    messages.success(request, f'Successfully imported page: {page.title}')
                    return redirect('admin:landing_page_change', page.id)
                except Exception as e:
                    messages.error(request, f'Failed to import page: {str(e)}')
            else:
                messages.error(request, 'Please provide a URL')

        context = {
            **self.admin_site.each_context(request),
            'title': 'Import Page from URL',
            'opts': self.model._meta,
            'has_view_permission': self.has_view_permission(request),
        }
        return render(request, 'admin/landing/page/import_page.html', context)


@admin.register(PageElement)
class PageElementAdmin(MPTTModelAdmin):
    list_display = ('id', 'type', 'page', 'content_preview', 'parent', 'css_classes', 'order')
    list_filter = ('type', 'page', 'parent')
    search_fields = ('content', 'css_classes')
    mptt_level_indent = 20

    def content_preview(self, obj):
        if obj.type == 'image' and obj.image:
            return format_html('<img src="{}" width="50" />', obj.image.url)
        return mark_safe(obj.content[:50] + '...' if obj.content and len(obj.content) > 50 else obj.content or '')

    content_preview.short_description = 'Content Preview'

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('page').prefetch_related('children')

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        formfield = super().formfield_for_dbfield(db_field, request, **kwargs)
        if db_field.name in ['props', 'html_attrs']:
            formfield.widget.attrs['rows'] = 4
            formfield.widget.attrs['style'] = 'width: 100%; font-family: monospace;'
        if db_field.name == 'content':
            formfield.widget.attrs['rows'] = 6
            formfield.widget.attrs['style'] = 'width: 100%;'
        return formfield
