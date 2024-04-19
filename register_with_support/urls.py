from django.urls import path

from . import views

urlpatterns = [
    path('organisation-wizard/', views.OrganisationRegisterWithEditorFormView.as_view(), name='organisation_with_editor'),
    path('individual-wizard/', views.IndividualRegisterWithEditorFormView.as_view(), name='individual_with_editor'),
    path('project-wizard/', views.ProjectRegisterWithEditorFormView.as_view(), name='project_with_editor'),
    path('platform-wizard/', views.PlatformRegisterWithoutFormView.as_view(), name='platform_with_editor'),
    path('operation-wizard/', views.OperationRegisterWithoutFormView.as_view(), name='operation_with_editor'),
    path('instrument-wizard/', views.InstrumentRegisterWithoutFormView.as_view(), name='instrument_with_editor'),
]