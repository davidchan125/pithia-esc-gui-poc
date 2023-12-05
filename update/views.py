import logging
import os
from django.contrib import messages
from django.db import transaction
from django.shortcuts import (
    get_object_or_404,
    render,
    redirect,
)
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.generic.edit import FormView
from pyexpat import ExpatError

from common import models
from common.decorators import login_session_institution_required, institution_ownership_required
from common.mongodb_models import (
    AcquisitionCapabilityRevision,
    AcquisitionRevision,
    ComputationCapabilityRevision,
    ComputationRevision,
    CurrentAcquisition,
    CurrentAcquisitionCapability,
    CurrentComputation,
    CurrentComputationCapability,
    CurrentDataCollection,
    CurrentIndividual,
    CurrentInstrument,
    CurrentOperation,
    CurrentOrganisation,
    CurrentPlatform,
    CurrentProcess,
    CurrentProject,
    DataCollectionRevision,
    IndividualRevision,
    InstrumentRevision,
    OperationRevision,
    OrganisationRevision,
    PlatformRevision,
    ProcessRevision,
    ProjectRevision,
    CurrentCatalogue,
    CatalogueRevision,
    CurrentCatalogueEntry,
    CatalogueEntryRevision,
    CurrentCatalogueDataSubset,
    CatalogueDataSubsetRevision,
)
from handle_management.xml_utils import (
    add_doi_xml_string_to_metadata_xml_string,
    get_doi_xml_string_from_metadata_xml_string,
    remove_doi_element_from_metadata_xml_string,
)
from resource_management.forms import (
    UploadUpdatedDataCollectionFileForm,
    UploadUpdatedFileForm,
    UpdateDataCollectionInteractionMethodsForm
)
from resource_management.views import (
    _INDEX_PAGE_TITLE,
    _DATA_COLLECTION_MANAGEMENT_INDEX_PAGE_TITLE,
    _CATALOGUE_MANAGEMENT_INDEX_PAGE_TITLE
)
from user_management.services import get_user_id_for_login_session

# TODO: remove old code

from .pymongo_api import (
    update_interaction_method_with_pymongo_transaction_if_possible,
    update_with_pymongo_transaction_if_possible,
)

from register.xml_conversion_checks_and_fixes import (
    correct_acquisition_capability_set_xml_converted_to_dict,
    correct_acquisition_xml_converted_to_dict,
    correct_computation_capability_set_xml_converted_to_dict,
    correct_computation_xml_converted_to_dict,
    correct_data_collection_xml_converted_to_dict,
    correct_instrument_xml_converted_to_dict,
    correct_operation_xml_converted_to_dict,
    correct_platform_xml_converted_to_dict,
    correct_process_xml_converted_to_dict,
    correct_project_xml_converted_to_dict,
)
from resource_management.views import _create_manage_resource_page_title


logger = logging.getLogger(__name__)


# Create your views here.

@method_decorator(login_session_institution_required, name='dispatch')
@method_decorator(institution_ownership_required, name='dispatch')
class ResourceUpdateFormView(FormView):
    # Registration variables
    resource = None
    resource_id = ''

    # Template variables
    resource_update_page_url_name = ''
    validation_url = ''
    # resource_to_update_name = '' # Set in dispatch() function
    resource_management_list_page_breadcrumb_url_name = ''

    # Class variables
    template_name = 'update/file_upload.html'
    form_class = UploadUpdatedFileForm
    success_url = ''
    xml_file_string = None

    # TODO: remove old code
    resource_mongodb_model = None
    resource_revision_mongodb_model = None
    resource_conversion_validate_and_correct_function = None

    def dispatch(self, request, *args, **kwargs):
        self.resource_id = self.kwargs['resource_id']
        self.resource = self.model.objects.get(pk=self.resource_id)
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f'Update Scientific Metadata'
        context['form'] = self.form_class
        context['resource'] = self.resource
        context['resource_id'] = self.resource_id
        context['validation_url'] = self.validation_url
        context['post_url'] = reverse_lazy(self.resource_update_page_url_name, args=[self.resource_id])
        context['resource_management_index_page_breadcrumb_text'] = _INDEX_PAGE_TITLE
        context['resource_management_category_list_page_breadcrumb_text'] = _DATA_COLLECTION_MANAGEMENT_INDEX_PAGE_TITLE
        context['resource_management_category_list_page_breadcrumb_url_name'] = 'resource_management:data_collection_related_metadata_index'
        context['resource_management_list_page_breadcrumb_text'] = _create_manage_resource_page_title(self.model.type_plural_readable.title())
        context['resource_management_list_page_breadcrumb_url_name'] = self.resource_management_list_page_breadcrumb_url_name
        return context

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST, request.FILES)
        xml_file = request.FILES['files']
        if form.is_valid():
            try:
                if self.xml_file_string is None:
                    self.xml_file_string = xml_file.read()
                with transaction.atomic():
                    resource_id_temp = self.resource_id
                    self.model.objects.update_from_xml_string(
                        resource_id_temp,
                        self.xml_file_string,
                        get_user_id_for_login_session(request.session)
                    )

                    # TODO: remove old code
                    update_with_pymongo_transaction_if_possible(
                        resource_id_temp,
                        self.resource_mongodb_model,
                        self.resource_revision_mongodb_model,
                        xml_file_string=self.xml_file_string,
                        resource_conversion_validate_and_correct_function=self.resource_conversion_validate_and_correct_function
                    )

                messages.success(request, f'Successfully updated {xml_file.name}. It may take a few minutes for the changes to be visible in the metadata\'s details page.')
            except ExpatError as err:
                logger.exception('Could not update a resource as there was an error parsing the update XML.')
                messages.error(request, 'An error occurred whilst parsing the XML.')
            except BaseException as err:
                logger.exception(f'An unexpected error occurred whilst attempting to update resource with ID "{self.resource_id}".')
                messages.error(request, 'An unexpected error occurred.')
        else:
            messages.error(request, 'The form submitted was not valid.')

        return super().post(request, *args, **kwargs)

class OrganisationUpdateFormView(ResourceUpdateFormView):
    model = models.Organisation

    resource_management_list_page_breadcrumb_url_name = 'resource_management:organisations'
    resource_update_page_url_name = 'update:organisation'
    validation_url = reverse_lazy('validation:organisation')
    success_url = reverse_lazy('resource_management:organisations')

    # TODO: remove old code
    resource_mongodb_model = CurrentOrganisation
    resource_revision_mongodb_model = OrganisationRevision
    

class IndividualUpdateFormView(ResourceUpdateFormView):
    model = models.Individual

    resource_management_list_page_breadcrumb_url_name = 'resource_management:individuals'
    resource_update_page_url_name = 'update:individual'
    validation_url = reverse_lazy('validation:individual')
    success_url = reverse_lazy('resource_management:individuals')

    # TODO: remove old code
    resource_mongodb_model = CurrentIndividual
    resource_revision_mongodb_model = IndividualRevision

class ProjectUpdateFormView(ResourceUpdateFormView):
    model = models.Project

    resource_management_list_page_breadcrumb_url_name = 'resource_management:projects'
    resource_update_page_url_name = 'update:project'
    validation_url = reverse_lazy('validation:project')
    success_url = reverse_lazy('resource_management:projects')

    # TODO: remove old code
    resource_mongodb_model = CurrentProject
    resource_revision_mongodb_model = ProjectRevision

    def post(self, request, *args, **kwargs):
        self.resource_conversion_validate_and_correct_function = correct_project_xml_converted_to_dict
        return super().post(request, *args, **kwargs)

class PlatformUpdateFormView(ResourceUpdateFormView):
    model = models.Platform

    resource_management_list_page_breadcrumb_url_name = 'resource_management:platforms'
    resource_update_page_url_name = 'update:platform'
    validation_url = reverse_lazy('validation:platform')
    success_url = reverse_lazy('resource_management:platforms')

    # TODO: remove old code
    resource_mongodb_model = CurrentPlatform
    resource_revision_mongodb_model = PlatformRevision

    def post(self, request, *args, **kwargs):
        self.resource_conversion_validate_and_correct_function = correct_platform_xml_converted_to_dict
        return super().post(request, *args, **kwargs)

class OperationUpdateFormView(ResourceUpdateFormView):
    model = models.Operation

    resource_management_list_page_breadcrumb_url_name = 'resource_management:operations'
    resource_update_page_url_name = 'update:operation'
    validation_url = reverse_lazy('validation:operation')
    success_url = reverse_lazy('resource_management:operations')

    # TODO: remove old code
    resource_mongodb_model = CurrentOperation
    resource_revision_mongodb_model = OperationRevision

    def post(self, request, *args, **kwargs):
        self.resource_conversion_validate_and_correct_function = correct_operation_xml_converted_to_dict
        return super().post(request, *args, **kwargs)

class InstrumentUpdateFormView(ResourceUpdateFormView):
    model = models.Instrument

    resource_management_list_page_breadcrumb_url_name = 'resource_management:instruments'
    resource_update_page_url_name = 'update:instrument'
    validation_url = reverse_lazy('validation:instrument')
    success_url = reverse_lazy('resource_management:instruments')

    # TODO: remove old code
    resource_mongodb_model = CurrentInstrument
    resource_revision_mongodb_model = InstrumentRevision

    def post(self, request, *args, **kwargs):
        self.resource_conversion_validate_and_correct_function = correct_instrument_xml_converted_to_dict
        return super().post(request, *args, **kwargs)

class AcquisitionCapabilitiesUpdateFormView(ResourceUpdateFormView):
    model = models.AcquisitionCapabilities

    resource_management_list_page_breadcrumb_url_name = 'resource_management:acquisition_capability_sets'
    resource_update_page_url_name = 'update:acquisition_capability_set'
    validation_url = reverse_lazy('validation:acquisition_capability_set')
    success_url = reverse_lazy('resource_management:acquisition_capability_sets')

    # TODO: remove old code
    resource_mongodb_model = CurrentAcquisitionCapability
    resource_revision_mongodb_model = AcquisitionCapabilityRevision

    def post(self, request, *args, **kwargs):
        self.resource_conversion_validate_and_correct_function = correct_acquisition_capability_set_xml_converted_to_dict
        return super().post(request, *args, **kwargs)

class AcquisitionUpdateFormView(ResourceUpdateFormView):
    model = models.Acquisition

    resource_management_list_page_breadcrumb_url_name = 'resource_management:acquisitions'
    resource_update_page_url_name = 'update:acquisition'
    validation_url = reverse_lazy('validation:acquisition')
    success_url = reverse_lazy('resource_management:acquisitions')

    # TODO: remove old code
    resource_mongodb_model = CurrentAcquisition
    resource_revision_mongodb_model = AcquisitionRevision

    def post(self, request, *args, **kwargs):
        self.resource_conversion_validate_and_correct_function = correct_acquisition_xml_converted_to_dict
        return super().post(request, *args, **kwargs)

class ComputationCapabilitiesUpdateFormView(ResourceUpdateFormView):
    model = models.ComputationCapabilities

    resource_management_list_page_breadcrumb_url_name = 'resource_management:computation_capability_sets'
    resource_update_page_url_name = 'update:computation_capability_set'
    validation_url = reverse_lazy('validation:computation_capability_set')
    success_url = reverse_lazy('resource_management:computation_capability_sets')

    # TODO: remove old code
    resource_mongodb_model = CurrentComputationCapability
    resource_revision_mongodb_model = ComputationCapabilityRevision

    def post(self, request, *args, **kwargs):
        self.resource_conversion_validate_and_correct_function = correct_computation_capability_set_xml_converted_to_dict
        return super().post(request, *args, **kwargs)
        
class ComputationUpdateFormView(ResourceUpdateFormView):
    model = models.Computation

    resource_management_list_page_breadcrumb_url_name = 'resource_management:computations'
    resource_update_page_url_name = 'update:computation'
    validation_url = reverse_lazy('validation:computation')
    success_url = reverse_lazy('resource_management:computations')

    # TODO: remove old code
    resource_mongodb_model = CurrentComputation
    resource_revision_mongodb_model = ComputationRevision

    def post(self, request, *args, **kwargs):
        self.resource_conversion_validate_and_correct_function = correct_computation_xml_converted_to_dict
        return super().post(request, *args, **kwargs)

class ProcessUpdateFormView(ResourceUpdateFormView):
    model = models.Process

    resource_management_list_page_breadcrumb_url_name = 'resource_management:processes'
    resource_update_page_url_name = 'update:process'
    validation_url = reverse_lazy('validation:process')
    success_url = reverse_lazy('resource_management:processes')

    # TODO: remove old code
    resource_mongodb_model = CurrentProcess
    resource_revision_mongodb_model = ProcessRevision

    def post(self, request, *args, **kwargs):
        self.resource_conversion_validate_and_correct_function = correct_process_xml_converted_to_dict
        return super().post(request, *args, **kwargs)

class DataCollectionUpdateFormView(ResourceUpdateFormView):
    model = models.DataCollection

    template_name = 'update/file_upload_data_collection.html'
    form_class = UploadUpdatedDataCollectionFileForm

    resource_management_list_page_breadcrumb_url_name = 'resource_management:data_collections'
    resource_update_page_url_name = 'update:data_collection'
    validation_url = reverse_lazy('validation:data_collection')
    success_url = reverse_lazy('resource_management:data_collections')

    # TODO: remove old code
    resource_mongodb_model = CurrentDataCollection
    resource_revision_mongodb_model = DataCollectionRevision

    def post(self, request, *args, **kwargs):
        self.resource_conversion_validate_and_correct_function = correct_data_collection_xml_converted_to_dict
        return super().post(request, *args, **kwargs)

@login_session_institution_required
@institution_ownership_required
def data_collection_interaction_methods(request, resource_id):
    data_collection = get_object_or_404(models.DataCollection, pk=resource_id)
    if request.method == 'POST':
        form = UpdateDataCollectionInteractionMethodsForm(request.POST)
        if form.is_valid():
            data_collection_localid = data_collection.localid
            try:
                is_api_selected = 'api_selected' in request.POST
                api_specification_url = request.POST.get('api_specification_url')
                api_description = request.POST.get('api_description')
                
                with transaction.atomic():
                    # TODO: remove old code
                    update_interaction_method_with_pymongo_transaction_if_possible(
                        data_collection_localid,
                        api_selected=is_api_selected,
                        api_specification_url=api_specification_url,
                        api_description=api_description
                    )

                    if is_api_selected == False:
                        try:
                            models.APIInteractionMethod.objects.get(data_collection=data_collection).delete(using=os.environ['DJANGO_RW_DATABASE_NAME'])
                        except models.APIInteractionMethod.DoesNotExist:
                            pass
                        messages.success(request, f'Successfully updated interaction methods for {data_collection.name}.')
                        return redirect('update:data_collection_interaction_methods', resource_id=resource_id)

                    try:
                        api_interaction_method = models.APIInteractionMethod.objects.get(data_collection=data_collection)
                        models.APIInteractionMethod.objects.update_config(
                            api_interaction_method.pk,
                            api_specification_url,
                            api_description
                        )
                    except models.APIInteractionMethod.DoesNotExist:
                        models.APIInteractionMethod.objects.create_api_interaction_method(
                            api_specification_url,
                            api_description,
                            data_collection
                        )
                messages.success(request, f'Successfully updated interaction methods for {data_collection.name}.')
            except BaseException as err:
                logger.exception('An unexpected error occurred whilst trying to update a Data Collection interaction method.')
                messages.error(request, 'An unexpected error occurred.')
            return redirect('update:data_collection_interaction_methods', resource_id=resource_id)
        
    # request.method == 'GET'
    form = UpdateDataCollectionInteractionMethodsForm()
    form_data = {}
    try:
        api_interaction_method = models.APIInteractionMethod.objects.get(data_collection=data_collection)
        form_data['api_selected'] = True
        form_data['api_specification_url'] = api_interaction_method.specification_url
        form_data['api_description'] = api_interaction_method.description
        form = UpdateDataCollectionInteractionMethodsForm(initial=form_data)
    except models.APIInteractionMethod.DoesNotExist:
        pass
    return render(request, 'update/interaction_methods.html', {
        'data_collection': data_collection,
        'data_collection_id': data_collection.pk,
        'form': form,
        'api_specification_validation_url': reverse_lazy('validation:api_specification_url'),
        'title': 'Update Interaction Methods',
        'resource_management_index_page_breadcrumb_text': _INDEX_PAGE_TITLE,
        'resource_management_category_list_page_breadcrumb_url_name': 'resource_management:data_collection_related_metadata_index',
        'resource_management_category_list_page_breadcrumb_text': _DATA_COLLECTION_MANAGEMENT_INDEX_PAGE_TITLE,
        'resource_management_list_page_breadcrumb_url_name': 'resource_management:data_collections',
        'resource_management_list_page_breadcrumb_text': _create_manage_resource_page_title(models.DataCollection.type_plural_readable.title())
    })

class CatalogueUpdateFormView(ResourceUpdateFormView):
    model = models.Catalogue

    resource_management_list_page_breadcrumb_url_name = 'resource_management:catalogues'
    resource_update_page_url_name = 'update:catalogue'
    validation_url = reverse_lazy('validation:catalogue')
    success_url = reverse_lazy('resource_management:catalogues')

    # TODO: remove old code
    resource_mongodb_model = CurrentCatalogue
    resource_revision_mongodb_model = CatalogueRevision

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['resource_management_category_list_page_breadcrumb_text'] = _CATALOGUE_MANAGEMENT_INDEX_PAGE_TITLE
        context['resource_management_category_list_page_breadcrumb_url_name'] = 'resource_management:catalogue_related_metadata_index'
        return context

class CatalogueEntryUpdateFormView(ResourceUpdateFormView):
    model = models.CatalogueEntry

    resource_management_list_page_breadcrumb_url_name = 'resource_management:catalogue_entries'
    resource_update_page_url_name = 'update:catalogue_entry'
    validation_url = reverse_lazy('validation:catalogue_entry')
    success_url = reverse_lazy('resource_management:catalogue_entries')

    # TODO: remove old code
    resource_mongodb_model = CurrentCatalogueEntry
    resource_revision_mongodb_model = CatalogueEntryRevision

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['resource_management_category_list_page_breadcrumb_text'] = _CATALOGUE_MANAGEMENT_INDEX_PAGE_TITLE
        context['resource_management_category_list_page_breadcrumb_url_name'] = 'resource_management:catalogue_related_metadata_index'
        return context

class CatalogueDataSubsetUpdateFormView(ResourceUpdateFormView):
    model = models.CatalogueDataSubset

    resource_management_list_page_breadcrumb_url_name = 'resource_management:catalogue_data_subsets'
    resource_update_page_url_name = 'update:catalogue_data_subset'
    validation_url = reverse_lazy('validation:catalogue_data_subset')
    success_url = reverse_lazy('resource_management:catalogue_data_subsets')

    # TODO: remove old code
    resource_mongodb_model = CurrentCatalogueDataSubset
    resource_revision_mongodb_model = CatalogueDataSubsetRevision

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['resource_management_category_list_page_breadcrumb_text'] = _CATALOGUE_MANAGEMENT_INDEX_PAGE_TITLE
        context['resource_management_category_list_page_breadcrumb_url_name'] = 'resource_management:catalogue_related_metadata_index'
        return context
    
    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST, request.FILES)
        xml_file = request.FILES['files']
        if form.is_valid():
            resource_doi_xml_string = get_doi_xml_string_from_metadata_xml_string(self.resource.xml)
            if resource_doi_xml_string is None:
                return super().post(request, *args, **kwargs)
            # The DOI stored in the e-Science Centre will always be considered the
            # "right" version, so we need to replace any DOI that may have been
            # passed in the updated XML file.
            self.xml_file_string = xml_file.read()
            self.xml_file_string = remove_doi_element_from_metadata_xml_string(self.xml_file_string)
            self.xml_file_string = add_doi_xml_string_to_metadata_xml_string(self.xml_file_string, resource_doi_xml_string)
        return super().post(request, *args, **kwargs)
