from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.home_view, name='home'),
    path('blog/', views.blog_list_view, name='blog_list'),
    path('blog/<slug:slug>/', views.blog_detail_view, name='blog_detail'),
    path('events/', views.events_list_view, name='events_list'),
    path('events/<slug:slug>/', views.event_detail_view, name='event_detail'),
    path('cases/<slug:slug>/', views.case_study_detail_view, name='case_detail'),
    path('presentations/<slug:slug>/', views.presentation_detail_view, name='presentation_detail'),
    path('about/', views.about_view, name='about'),
    path('contact/', views.contact_view, name='contact'),
    path('newsletter/signup/', views.newsletter_signup_view, name='newsletter_signup'),
]