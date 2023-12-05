import logging
from django.contrib import messages
from django.db import (
    IntegrityError,
    transaction,
)
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.generic import FormView
from pyexpat import ExpatError

from .forms import (
    UploadDataCollectionFileForm,
    UploadFileForm,
    UploadCatalogueDataSubsetFileForm,
)

from common import models, mongodb_models
from common.decorators import login_session_institution_required
from handle_management.handle_api import (
    add_doi_metadata_kernel_to_handle,
    create_and_register_handle_for_resource_url,
    delete_handle,
)
from handle_management.utils import (
    add_handle_to_url_mapping,
)
from handle_management.xml_utils import (
    add_data_subset_data_to_doi_metadata_kernel_dict,
    add_doi_metadata_kernel_to_data_subset,
    add_handle_data_to_doi_metadata_kernel_dict,
    initialise_default_doi_kernel_metadata_dict,
    is_doi_element_present_in_xml_file,
)
from resource_management.views import (
    _INDEX_PAGE_TITLE,
    _DATA_COLLECTION_MANAGEMENT_INDEX_PAGE_TITLE,
    _CATALOGUE_MANAGEMENT_INDEX_PAGE_TITLE,
    _create_manage_resource_page_title
)
from user_management.services import (
    get_user_id_for_login_session,
    get_institution_id_for_login_session,
)
from utils.url_helpers import create_data_subset_detail_page_url

# TODO: remove old code
from . import xml_conversion_checks_and_fixes
from .pymongo_api import register_with_pymongo_transaction_if_possible

from common.mongodb_models import OriginalMetadataXml
from handle_management.pymongo_api import add_data_subset_data_to_doi_metadata_kernel_dict_old
from update.pymongo_api import register_doi_with_pymongo_transaction_if_possible
from validation.errors import FileRegisteredBefore


logger = logging.getLogger(__name__)


# Create your views here.

@method_decorator(login_session_institution_required, name='dispatch')
class ResourceRegisterFormView(FormView):
    success_url = ''
    form_class = UploadFileForm
    template_name = 'register/file_upload.html'

    resource_id = None
    new_registration = None
    xml_file_string = None
    handle = None
    handle_api_client = None
    validation_url = ''
    post_url = ''

    resource_management_list_page_breadcrumb_text = ''
    resource_management_list_page_breadcrumb_url_name = ''

    # TODO: remove old code
    resource_mongodb_model = None
    resource_conversion_validate_and_correct_function = None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Register Scientific Metadata'
        context['resource_type_plural_readable'] = self.model.type_plural_readable.title()
        context['validation_url'] = self.validation_url
        context['post_url'] = self.post_url
        context['form'] = self.form_class
        context['resource_management_index_page_breadcrumb_text'] = _INDEX_PAGE_TITLE
        context['resource_management_category_list_page_breadcrumb_text'] = _DATA_COLLECTION_MANAGEMENT_INDEX_PAGE_TITLE
        context['resource_management_category_list_page_breadcrumb_url_name'] = 'resource_management:data_collection_related_metadata_index'
        context['resource_management_list_page_breadcrumb_text'] = self.resource_management_list_page_breadcrumb_text
        context['resource_management_list_page_breadcrumb_url_name'] = self.resource_management_list_page_breadcrumb_url_name
        return context

    def post(self, request, *args, **kwargs):
        institution_id = get_institution_id_for_login_session(request.session)
        owner_id = get_user_id_for_login_session(request.session)

        # Form validation
        form = UploadFileForm(request.POST, request.FILES)
        xml_files = request.FILES.getlist('files')
        file_registered = False
        if form.is_valid():
            for xml_file in xml_files:
                # XML should have already been validated at
                # the template, and validation could take
                # place again, but takes a long time. Another
                # method which verifies validation took place
                # should be implemented.
                xml_file_string = xml_file.read()
                try:
                    with transaction.atomic():
                        self.new_registration = self.model.objects.create_from_xml_string(
                            xml_file_string,
                            institution_id,
                            owner_id,
                        )
                        is_api_selected = 'api_selected' in request.POST
                        api_specification_url = request.POST.get('api_specification_url', None)
                        api_description = request.POST.get('api_description', '')
                        if is_api_selected:
                            models.InteractionMethod.api_interaction_methods.create_api_interaction_method(
                                api_specification_url,
                                api_description,
                                self.new_registration
                            )
                        # TODO: remove old code
                        
                        register_with_pymongo_transaction_if_possible(
                            xml_file,
                            self.resource_mongodb_model,
                            OriginalMetadataXml,
                            api_selected=is_api_selected,
                            api_specification_url=api_specification_url,
                            api_description=api_description,
                            resource_conversion_validate_and_correct_function=self.resource_conversion_validate_and_correct_function
                        )
                        self.new_pymongo_registration = self.resource_mongodb_model.find_one({
                            'identifier.PITHIA_Identifier.localID': self.new_registration.localid
                        })
                    
                    file_registered = True
                    messages.success(request, f'Successfully registered {xml_file.name}.')
                except ExpatError as err:
                    logger.exception('Expat error occurred during registration process.')
                    messages.error(request, f'An error occurred whilst parsing {xml_file.name}.')
                except (FileRegisteredBefore, IntegrityError) as err:
                    logger.exception('The XML file submitted for registration has been registered before.')
                    messages.error(request, f'{xml_file.name} has been registered before.')
                except BaseException as err:
                    logger.exception('An unexpected error occurred during metadata registration.')
                    messages.error(request, 'An unexpected error occurred during metadata registration.')
                
                if file_registered == False:
                    return super().post(request, *args, **kwargs)

                try:
                    # POST RESOURCE REGISTRATION
                    # Get the DOI
                    # Update the actual "xml_file" variable by adding the DOI to the XML
                    # Perform an update on the resource
                    # Continue with registration as normal
                    if 'register_doi' in request.POST:
                        with transaction.atomic():
                            is_doi_in_file_already = is_doi_element_present_in_xml_file(xml_file)
                            if is_doi_in_file_already == True:
                                logger.exception('A DOI has already been issued for this metadata file.')
                                messages.error(request, f'A DOI has already been issued for this metadata file.')
                                return super().post(request, *args, **kwargs)
                            
                            # Create and register a handle
                            data_subset_url = create_data_subset_detail_page_url(self.new_registration.pk)
                            handle, handle_api_client, credentials = create_and_register_handle_for_resource_url(data_subset_url)
                            self.handle_api_client = handle_api_client
                            self.handle = handle

                            # Create a dict storing DOI metadata kernel information.
                            # This information in this dict will be added to the
                            # Handle to store data that a DOI would normally handle.
                            doi_dict = initialise_default_doi_kernel_metadata_dict()
                            # Add the handle metadata to the DOI dict
                            doi_dict = add_handle_data_to_doi_metadata_kernel_dict(handle, doi_dict)
                            add_data_subset_data_to_doi_metadata_kernel_dict(self.new_registration, doi_dict)
                            # TODO: remove old code
                            add_data_subset_data_to_doi_metadata_kernel_dict_old(self.new_pymongo_registration['_id'], doi_dict)

                            # Add DOI metadata kernel to Handle and Data Subset
                            add_doi_metadata_kernel_to_handle(self.handle, doi_dict, self.handle_api_client)
                            add_doi_metadata_kernel_to_data_subset(
                                self.new_registration.pk,
                                doi_dict,
                                xml_file_string,
                                owner_id
                            )
                            # Handle to Data Subset URL mapping, to be able to
                            # retrieve information from the Handle in case the
                            # Data Subset ever gets deleted.
                            add_handle_to_url_mapping(handle, data_subset_url)

                            # TODO: remove old code
                            register_doi_with_pymongo_transaction_if_possible(
                                doi_dict,
                                str(self.new_pymongo_registration['_id']),
                                xml_file,
                                self.resource_mongodb_model,
                                handle,
                                data_subset_url,
                                resource_conversion_validate_and_correct_function=self.resource_conversion_validate_and_correct_function
                            )

                        messages.success(request, f'A DOI with name "{self.handle}" has been registered for this data subset.')
                except ExpatError as err:
                    logger.exception('Expat error occurred during DOI registration process.')
                    messages.error(request, f'An error occurred whilst parsing {xml_file.name} during the DOI registration process.')
                except BaseException as err:
                    logger.exception('An unexpected error occurred during DOI registration.')
                    messages.error(request, 'An unexpected error occurred during DOI registration.')
                    if self.handle != None:
                        try:
                            delete_handle(self.handle, self.handle_api_client)
                            logger.info(f'Deleted handle {self.handle} due to an error that occurred during DOI registration.')
                        except BaseException as err:
                            logger.exception(f'Could not delete handle {self.handle} due to an error.')
                            
        else:
            messages.error(request, 'The form submitted was not valid.')
        return super().post(request, *args, **kwargs)

class OrganisationRegisterFormView(ResourceRegisterFormView):
    model = models.Organisation
    success_url = reverse_lazy('register:organisation')

    validation_url = reverse_lazy('validation:organisation')
    post_url = reverse_lazy('register:organisation')
    resource_management_list_page_breadcrumb_url_name = 'resource_management:organisations'
    resource_management_list_page_breadcrumb_text = _create_manage_resource_page_title('organisations')

    # TODO: remove old code
    resource_mongodb_model = mongodb_models.CurrentOrganisation

class IndividualRegisterFormView(ResourceRegisterFormView):
    model = models.Individual
    success_url = reverse_lazy('register:individual')

    validation_url = reverse_lazy('validation:individual')
    post_url = reverse_lazy('register:individual')
    resource_management_list_page_breadcrumb_url_name = 'resource_management:individuals'
    resource_management_list_page_breadcrumb_text = _create_manage_resource_page_title('individuals')

    # TODO: remove old code
    resource_mongodb_model = mongodb_models.CurrentIndividual

class ProjectRegisterFormView(ResourceRegisterFormView):
    model = models.Project
    success_url = reverse_lazy('register:project')

    validation_url = reverse_lazy('validation:project')
    post_url = reverse_lazy('register:project')
    resource_management_list_page_breadcrumb_url_name = 'resource_management:projects'
    resource_management_list_page_breadcrumb_text = _create_manage_resource_page_title('projects')

    # TODO: remove old code
    resource_mongodb_model = mongodb_models.CurrentProject

    def post(self, request, *args, **kwargs):
        self.resource_conversion_validate_and_correct_function = xml_conversion_checks_and_fixes.correct_project_xml_converted_to_dict
        return super().post(request, *args, **kwargs)

class PlatformRegisterFormView(ResourceRegisterFormView):
    model = models.Platform
    success_url = reverse_lazy('register:platform')

    validation_url = reverse_lazy('validation:platform')
    post_url = reverse_lazy('register:platform')
    resource_management_list_page_breadcrumb_url_name = 'resource_management:platforms'
    resource_management_list_page_breadcrumb_text = _create_manage_resource_page_title('platforms')

    # TODO: remove old code
    resource_mongodb_model = mongodb_models.CurrentPlatform

    def post(self, request, *args, **kwargs):
            self.resource_conversion_validate_and_correct_function = xml_conversion_checks_and_fixes.correct_platform_xml_converted_to_dict
            return super().post(request, *args, **kwargs)

class OperationRegisterFormView(ResourceRegisterFormView):
    model = models.Operation
    success_url = reverse_lazy('register:operation')

    validation_url = reverse_lazy('validation:operation')
    post_url = reverse_lazy('register:operation')
    resource_management_list_page_breadcrumb_url_name = 'resource_management:operations'
    resource_management_list_page_breadcrumb_text = _create_manage_resource_page_title('operations')

    # TODO: remove old code
    resource_mongodb_model = mongodb_models.CurrentOperation

    def post(self, request, *args, **kwargs):
        self.resource_conversion_validate_and_correct_function = xml_conversion_checks_and_fixes.correct_operation_xml_converted_to_dict
        return super().post(request, *args, **kwargs)

class InstrumentRegisterFormView(ResourceRegisterFormView):
    model = models.Instrument
    success_url = reverse_lazy('register:instrument')

    validation_url = reverse_lazy('validation:instrument')
    post_url = reverse_lazy('register:instrument')
    resource_management_list_page_breadcrumb_url_name = 'resource_management:instruments'
    resource_management_list_page_breadcrumb_text = _create_manage_resource_page_title('instruments')

    # TODO: remove old code
    resource_mongodb_model = mongodb_models.CurrentInstrument

    def post(self, request, *args, **kwargs):
        self.resource_conversion_validate_and_correct_function = xml_conversion_checks_and_fixes.correct_instrument_xml_converted_to_dict
        return super().post(request, *args, **kwargs)

class AcquisitionCapabilitiesRegisterFormView(ResourceRegisterFormView):
    model = models.AcquisitionCapabilities
    success_url = reverse_lazy('register:acquisition_capability_set')

    validation_url = reverse_lazy('validation:acquisition_capability_set')
    post_url = reverse_lazy('register:acquisition_capability_set')
    resource_management_list_page_breadcrumb_url_name = 'resource_management:acquisition_capability_sets'
    resource_management_list_page_breadcrumb_text = _create_manage_resource_page_title('acquisition capabilities')

    # TODO: remove old code
    resource_mongodb_model = mongodb_models.CurrentAcquisitionCapability

    def post(self, request, *args, **kwargs):
        self.resource_conversion_validate_and_correct_function = xml_conversion_checks_and_fixes.correct_acquisition_capability_set_xml_converted_to_dict
        return super().post(request, *args, **kwargs)

class AcquisitionRegisterFormView(ResourceRegisterFormView):
    model = models.Acquisition
    success_url = reverse_lazy('register:acquisition')

    validation_url = reverse_lazy('validation:acquisition')
    post_url = reverse_lazy('register:acquisition')
    resource_management_list_page_breadcrumb_url_name = 'resource_management:acquisitions'
    resource_management_list_page_breadcrumb_text = _create_manage_resource_page_title('acquisitions')

    # TODO: remove old code
    resource_mongodb_model = mongodb_models.CurrentAcquisition

    def post(self, request, *args, **kwargs):
        self.resource_conversion_validate_and_correct_function = xml_conversion_checks_and_fixes.correct_acquisition_xml_converted_to_dict
        return super().post(request, *args, **kwargs)

class ComputationCapabilitiesRegisterFormView(ResourceRegisterFormView):
    model = models.ComputationCapabilities
    success_url = reverse_lazy('register:computation_capability_set')

    validation_url = reverse_lazy('validation:computation_capability_set')
    post_url = reverse_lazy('register:computation_capability_set')
    resource_management_list_page_breadcrumb_url_name = 'resource_management:computation_capability_sets'
    resource_management_list_page_breadcrumb_text = _create_manage_resource_page_title('computation capabilities')

    # TODO: remove old code
    resource_mongodb_model = mongodb_models.CurrentComputationCapability

    def post(self, request, *args, **kwargs):
        self.resource_conversion_validate_and_correct_function = xml_conversion_checks_and_fixes.correct_computation_capability_set_xml_converted_to_dict
        return super().post(request, *args, **kwargs)

class ComputationRegisterFormView(ResourceRegisterFormView):
    model = models.Computation
    success_url = reverse_lazy('register:computation')

    validation_url = reverse_lazy('validation:computation')
    post_url = reverse_lazy('register:computation')
    resource_management_list_page_breadcrumb_url_name = 'resource_management:computations'
    resource_management_list_page_breadcrumb_text = _create_manage_resource_page_title('computations')

    # TODO: remove old code
    resource_mongodb_model = mongodb_models.CurrentComputation

    def post(self, request, *args, **kwargs):
        self.resource_conversion_validate_and_correct_function = xml_conversion_checks_and_fixes.correct_computation_xml_converted_to_dict
        return super().post(request, *args, **kwargs)

class ProcessRegisterFormView(ResourceRegisterFormView):
    model = models.Process
    success_url = reverse_lazy('register:process')

    validation_url = reverse_lazy('validation:process')
    post_url = reverse_lazy('register:process')
    resource_management_list_page_breadcrumb_url_name = 'resource_management:processes'
    resource_management_list_page_breadcrumb_text = _create_manage_resource_page_title('processes')

    # TODO: remove old code
    resource_mongodb_model = mongodb_models.CurrentProcess

    def post(self, request, *args, **kwargs):
        self.resource_conversion_validate_and_correct_function = xml_conversion_checks_and_fixes.correct_process_xml_converted_to_dict
        return super().post(request, *args, **kwargs)

class DataCollectionRegisterFormView(ResourceRegisterFormView):
    model = models.DataCollection
    success_url = reverse_lazy('register:data_collection')

    template_name = 'register/file_upload_data_collection.html'
    form_class = UploadDataCollectionFileForm

    validation_url = reverse_lazy('validation:data_collection')
    post_url = reverse_lazy('register:data_collection')
    resource_management_list_page_breadcrumb_url_name = 'resource_management:data_collections'
    resource_management_list_page_breadcrumb_text = _create_manage_resource_page_title('data collections')

    # TODO: remove old code
    resource_mongodb_model = mongodb_models.CurrentDataCollection

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['api_specification_validation_url'] = reverse_lazy('validation:api_specification_url')
        return context
        
    def post(self, request, *args, **kwargs):
        self.resource_conversion_validate_and_correct_function = xml_conversion_checks_and_fixes.correct_data_collection_xml_converted_to_dict
        return super().post(request, *args, **kwargs)

class CatalogueRegisterFormView(ResourceRegisterFormView):
    template_name='register/file_upload_catalogue.html'
    model = models.Catalogue
    success_url = reverse_lazy('register:catalogue')

    validation_url = reverse_lazy('validation:catalogue')
    post_url = reverse_lazy('register:catalogue')
    resource_management_list_page_breadcrumb_url_name = 'resource_management:catalogues'
    resource_management_list_page_breadcrumb_text = _create_manage_resource_page_title('catalogues')

    # TODO: remove old code
    resource_mongodb_model = mongodb_models.CurrentCatalogue

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['resource_management_category_list_page_breadcrumb_text'] = _CATALOGUE_MANAGEMENT_INDEX_PAGE_TITLE
        context['resource_management_category_list_page_breadcrumb_url_name'] = 'resource_management:catalogue_related_metadata_index'
        return context

class CatalogueEntryRegisterFormView(ResourceRegisterFormView):
    template_name='register/file_upload_catalogue.html'
    model = models.CatalogueEntry
    success_url = reverse_lazy('register:catalogue_entry')

    validation_url = reverse_lazy('validation:catalogue_entry')
    post_url = reverse_lazy('register:catalogue_entry')
    resource_management_list_page_breadcrumb_url_name = 'resource_management:catalogue_entries'
    resource_management_list_page_breadcrumb_text = _create_manage_resource_page_title('catalogue entries')

    # TODO: remove old code
    resource_mongodb_model = mongodb_models.CurrentCatalogueEntry

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['resource_management_category_list_page_breadcrumb_text'] = _CATALOGUE_MANAGEMENT_INDEX_PAGE_TITLE
        context['resource_management_category_list_page_breadcrumb_url_name'] = 'resource_management:catalogue_related_metadata_index'
        return context

class CatalogueDataSubsetRegisterFormView(ResourceRegisterFormView):
    template_name='register/file_upload_catalogue_data_subset.html'
    model = models.CatalogueDataSubset
    success_url = reverse_lazy('register:catalogue_data_subset')

    form_class = UploadCatalogueDataSubsetFileForm

    validation_url = reverse_lazy('validation:catalogue_data_subset')
    post_url = reverse_lazy('register:catalogue_data_subset')
    resource_management_list_page_breadcrumb_url_name = 'resource_management:catalogue_data_subsets'
    resource_management_list_page_breadcrumb_text = _create_manage_resource_page_title('catalogue data subsets')

    # TODO: remove old code
    resource_mongodb_model = mongodb_models.CurrentCatalogueDataSubset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['resource_management_category_list_page_breadcrumb_text'] = _CATALOGUE_MANAGEMENT_INDEX_PAGE_TITLE
        context['resource_management_category_list_page_breadcrumb_url_name'] = 'resource_management:catalogue_related_metadata_index'
        return context
