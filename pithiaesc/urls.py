from django.contrib import admin
from django.urls import include, path
from . import views

urlpatterns = [
    path('', views.index, name='home'),
    path('logout/', views.logout, name='logout'),
    # Include URLs
    path('', include('browse.urls')),
    path('ontology/', include('ontology.urls')),
    path('present/', include('present.urls')),
    path('search/', include('search.urls')),
    path('simple-search/', include('simple_search.urls')),
    path('admin/', admin.site.urls),
    path('data-resource-registration-guide', views.resource_registration_user_guide, name='resource_registration_user_guide'),
    path('terms-of-use', views.terms_of_use, name='terms_of_use'),
    path('privacy-policy', views.privacy_policy, name='privacy_policy'),
    path('support', views.support, name='support'),
    path('authorised/', include('pithiaesc.secure_urls')),
    path('', include('user_management.urls')),
]
