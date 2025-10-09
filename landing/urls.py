from django.urls import path

from landing import views

urlpatterns = [
    path('page/<slug:slug>/', views.page_view, name='page'),
    path('page/<slug:slug>/signup/', views.signup_form, name='signup_form'),
]