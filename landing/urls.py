from django.urls import path

from landing import views, api_views

urlpatterns = [
    path('page/<slug:slug>/', views.page_view, name='page'),
    path('page/<slug:slug>/signup/', views.signup_form, name='signup_form'),

    path('api/element/<int:element_id>/has-content/', api_views.element_has_content, name='element_has_content'),
    path('api/element/<int:element_id>/update-content/', api_views.update_element_content, name='update_element_content'),
    path('api/element/<int:element_id>/config/', api_views.element_config, name='element_config'),
    path('api/element/<int:element_id>/update-config/', api_views.update_element_config, name='update_element_config'),
    path('api/element/<int:element_id>/delete/', api_views.delete_element, name='delete_element'),

]