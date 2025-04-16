from django.urls import path
from . import views
urlpatterns = [
    path('create_custom_user/', views.create_custom_user_view, name='custom_user'),
    path('create_admin_user/', views.create_admin_user_view, name='admin_user'),
    path('user_login/', views.user_login_view, name='user_login'),
    path('create_specialization/', views.create_specialization_view, name='specialization'),
    path('create_patient/', views.create_patient_view, name='patients'),
    path('create_specialist/', views.create_specialist_view, name='specialist'),
    path('create_ailment/', views.create_ailment_view, name='ailments'),
    path('create_report/', views.create_report_view, name='reports'),
    path('create_prescription/', views.create_prescription_view, name='prescriptions'),
]