# views.py
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json

from landing.models import PageElement


@require_http_methods(["GET"])
def element_has_content(request, element_id):
    element = get_object_or_404(PageElement, id=element_id) #, page__slug=request.resolver_match.kwargs['slug'])
    return JsonResponse(
        {
            'has_content': bool(element.content),
            'content': element.content,
        }
    )

@csrf_exempt
@require_http_methods(["POST"])
def update_element_content(request, element_id):
    element = get_object_or_404(PageElement, id=element_id)
    data = json.loads(request.body)
    element.content = data.get('content', '')
    element.save()
    return JsonResponse({'success': True})

@require_http_methods(["GET"])
def element_config(request, element_id):
    element = get_object_or_404(PageElement, id=element_id)
    form_html = f"""
        <input type="hidden" name="element_id" value="{element.id}">
        <div>
            <label>Type: <strong>{element.get_type_display()}</strong></label>
        </div>
        <div>
            <label>CSS Classes:</label>
            <input type="text" name="css_classes" value="{element.css_classes or ''}" class="form-control">
        </div>
        <!-- Добавь другие поля в зависимости от типа -->
    """
    return JsonResponse({
        'id': element.id,
        'type': element.type,
        'form_html': form_html
    })

@csrf_exempt
@require_http_methods(["POST"])
def update_element_config(request, element_id):
    element = get_object_or_404(PageElement, id=element_id)
    form_data = request.POST
    element.css_classes = form_data.get('css_classes', '')
    element.save()
    return JsonResponse({'success': True})

@csrf_exempt
@require_http_methods(["POST"])
def delete_element(request, element_id):
    element = get_object_or_404(PageElement, id=element_id)
    element.delete()
    return JsonResponse({'success': True})