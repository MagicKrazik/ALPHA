from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    # Main pages
    path('', views.home, name='home'),
    path('registro/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('contacto/', views.contact, name='contact'),
    
    # Patient and Treatment Case URLs
    path('pacientes/', views.patient_list, name='patient-list'),
    path('pacientes/nuevo/', views.patient_create, name='patient-create'),
    path('pacientes/<uuid:pk>/', views.patient_detail, name='patient-detail'),
    path('pacientes/<uuid:pk>/editar/', views.patient_update, name='patient-update'),
    path('pacientes/<uuid:pk>/eliminar/', views.patient_delete, name='patient-delete'),

    # Pre-surgery form URLs (using case_id for creation, form id for detail/edit)
    path('casos/<uuid:case_id>/presurgery/nuevo/', 
          views.presurgery_create, name='presurgery-create'),
    path('presurgery/<uuid:pk>/', 
          views.presurgery_detail, name='presurgery-detail'),
    path('presurgery/<uuid:pk>/editar/', 
         views.presurgery_update, name='presurgery-update'),
    
    # Post-surgery form URLs (using case_id for creation, form id for detail/edit)
    path('casos/<uuid:case_id>/postsurgery/nuevo/', 
         views.postsurgery_create, 
         name='postsurgery-create'),
    path('postsurgery/<uuid:pk>/', 
         views.postsurgery_detail, 
         name='postsurgery-detail'),
    path('postsurgery/<uuid:pk>/editar/', 
         views.postsurgery_update, 
         name='postsurgery-update'),

    # Dashboard URLs
    path('dashboard/', views.dashboard, name='dashboard'),
    path('api/dashboard/stats/', views.get_dashboard_stats, name='dashboard-stats'),
    path('api/dashboard/export/', views.export_dashboard, name='dashboard-export'),

    # Alert System URLs
    path('alertas/', views.alerts_list, name='alerts-list'),
    path('alertas/<uuid:pk>/', views.alert_detail, name='alert-detail'),
    path('alertas/<uuid:pk>/reconocer/', views.alert_acknowledge, name='alert-acknowledge'),
]