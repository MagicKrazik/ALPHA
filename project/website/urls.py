# Update urls.py with better error handling
from django.urls import path, re_path
from . import views
from django.views.defaults import page_not_found

urlpatterns = [
    path('', views.home, name='home'),
    path('registro/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('contacto/', views.contact, name='contact'),
    
    # Patient URLs
    path('pacientes/', views.patient_list, name='patient-list'),
    path('pacientes/nuevo/', views.patient_create, name='patient-create'),
    path('pacientes/<uuid:pk>/', views.patient_detail, name='patient-detail'),
    path('pacientes/<uuid:pk>/editar/', views.patient_update, name='patient-update'),
    path('pacientes/<uuid:pk>/eliminar/', views.patient_delete, name='patient-delete'),

    # Pre-surgery form URLs with better validation
    path('pacientes/<uuid:patient_id>/presurgery/nuevo/', 
          views.presurgery_create, name='presurgery-create'),
    path('pacientes/presurgery/<str:pk>/', 
          views.presurgery_detail, name='presurgery-detail'),
    path('pacientes/presurgery/<str:pk>/editar/', 
         views.presurgery_update, name='presurgery-update'),
    
    # Post-surgery form URLs - FIXED
    path('pacientes/<uuid:patient_id>/postsurgery/nuevo/', 
         views.postsurgery_create, 
         name='postsurgery-create'),
    path('pacientes/postsurgery/<str:pk>/', 
         views.postsurgery_detail, 
         name='postsurgery-detail'),
    path('pacientes/postsurgery/<str:pk>/editar/', 
         views.postsurgery_update, 
         name='postsurgery-update'),

    # Dashboard URLs
    path('dashboard/', views.dashboard, name='dashboard'),
    path('api/dashboard/stats/', views.get_dashboard_stats, name='dashboard-stats'),
    path('api/dashboard/export/', views.export_dashboard, name='dashboard-export'),
]

# Add custom error handlers
handler404 = 'website.views.custom_404'
handler500 = 'website.views.custom_500'