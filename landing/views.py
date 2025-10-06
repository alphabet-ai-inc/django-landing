from django.shortcuts import render, get_object_or_404
from .models import Page, PageElement

def page_view(request, slug):
    page = get_object_or_404(Page, slug=slug)
    root_elements = PageElement.objects.filter(page=page)
    return render(request, page.template, {'page': page, 'root_elements': root_elements})