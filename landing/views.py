from django.shortcuts import render, get_object_or_404, redirect
from django_landing import settings
from .models import Page, PageElement
from django.core.mail import send_mail
from django.contrib import messages


def main_page(request):
    return render(request, 'index.html')


def page_view(request, slug):
    page = get_object_or_404(Page, slug=slug)
    root_elements = PageElement.objects.filter(page=page, parent=None)  # Только корневые элементы
    can_edit_page = Page.can_edit(request)
    edit_mode = request.GET.get('edit') == '1' and can_edit_page

    context = {
        'page': page,
        'root_elements': root_elements,
        'can_edit': can_edit_page,
        'edit_mode': edit_mode,
        'element_data': {}  # Для хранения данных элементов при редактировании
    }

    return render(request, page.template, context)


def signup_form(request, slug):
    if request.method == 'POST':
        user_name = request.POST.get('user_name')
        user_email = request.POST.get('user_email')
        user_message = request.POST.get('user_message')

        try:
            send_mail(
                subject=f"Message from {user_name}",
                message=user_message,
                from_email=user_email,
                recipient_list=[settings.DEFAULT_FROM_EMAIL],
                fail_silently=False,
            )
            messages.success(request, 'Your message has been sent successfully!')
        except Exception as e:
            messages.error(request, f'Error sending message: {str(e)}')

        return redirect('landing_page', slug=slug)

    return render(request, 'landing/landing_basic.html', {'page': Page.objects.get(slug=slug)})