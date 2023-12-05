import logging
from dateutil.parser import parse
from django.http import JsonResponse
from django.shortcuts import (
    get_object_or_404,
    render,
)
from django.urls import reverse
from django.views.generic import (
    ListView,
    TemplateView,
)

from .services import (
    create_readable_scientific_metadata_flattened,
    get_server_urls_from_scientific_metadata_flattened,
    map_metadata_server_urls_to_browse_urls,
    map_ontology_server_urls_to_browse_urls,
)

from common import models
from handle_management.handle_api import (
    get_handle_record,
    instantiate_client_and_load_credentials,
)
from utils.dict_helpers import flatten
from utils.mapping_functions import prepare_resource_for_template

logger = logging.getLogger(__name__)

_INDEX_PAGE_TITLE = 'All Scientific Metadata'
_DATA_COLLECTION_RELATED_RESOURCE_TYPES_PAGE_TITLE = 'Data Collection-related Metadata'
_CATALOGUE_RELATED_RESOURCE_TYPES_PAGE_TITLE = 'Catalogue-related Metadata'
_XML_SCHEMAS_PAGE_TITLE = 'Metadata Models'

# Create your views here.
def index(request):
    return render(request, 'browse/index.html', {
        'title': _INDEX_PAGE_TITLE,
        'data_collection_related_resource_types_page_title': _DATA_COLLECTION_RELATED_RESOURCE_TYPES_PAGE_TITLE,
        'catalogue_related_resource_types_page_title': _CATALOGUE_RELATED_RESOURCE_TYPES_PAGE_TITLE,
    })

def data_collection_related_resource_types(request):
    """
    Acts as a centre point to all registration list pages
    for each Data Collection-related registration (i.e.,
    all scientific metadata types up to Data Collections).
    Lists the links to these pages and the total number of
    registrations for each scientific metadata type.
    """
    num_current_organsations = models.Organisation.objects.count()
    num_current_individuals = models.Individual.objects.count()
    num_current_projects = models.Project.objects.count()
    num_current_platforms = models.Platform.objects.count()
    num_current_instruments = models.Instrument.objects.count()
    num_current_operations = models.Operation.objects.count()
    num_current_acquisition_capability_sets = models.AcquisitionCapabilities.objects.count()
    num_current_acquisitions = models.Acquisition.objects.count()
    num_current_computation_capability_sets = models.ComputationCapabilities.objects.count()
    num_current_computations = models.Computation.objects.count()
    num_current_processes = models.Process.objects.count()
    num_current_data_collections = models.DataCollection.objects.count()
    return render(request, 'browse/data_collection_related_resource_types.html', {
        'title': _DATA_COLLECTION_RELATED_RESOURCE_TYPES_PAGE_TITLE,
        'num_current_organisations': num_current_organsations,
        'num_current_individuals': num_current_individuals,
        'num_current_projects': num_current_projects,
        'num_current_platforms': num_current_platforms,
        'num_current_instruments': num_current_instruments,
        'num_current_operations': num_current_operations,
        'num_current_acquisition_capability_sets': num_current_acquisition_capability_sets,
        'num_current_acquisitions': num_current_acquisitions,
        'num_current_computation_capability_sets': num_current_computation_capability_sets,
        'num_current_computations': num_current_computations,
        'num_current_processes': num_current_processes,
        'num_current_data_collections': num_current_data_collections,
        'browse_index_page_breadcrumb_text': _INDEX_PAGE_TITLE,
    })

def catalogue_related_resource_types(request):
    """
    Acts as a centre point to all registration list pages
    for each Catalogue-related registration (i.e., all
    scientific metadata types from Catalogues to Catalogue
    Data Subsets). Lists the links to these pages and the
    total number of registrations for each scientific
    metadata type.
    """
    num_current_catalogues = models.Catalogue.objects.count()
    num_current_catalogue_entries = models.CatalogueEntry.objects.count()
    num_current_catalogue_data_subsets = models.CatalogueDataSubset.objects.count()
    return render(request, 'browse/catalogue_related_resource_types.html', {
        'title': _CATALOGUE_RELATED_RESOURCE_TYPES_PAGE_TITLE,
        'num_current_catalogues': num_current_catalogues,
        'num_current_catalogue_entries': num_current_catalogue_entries,
        'num_current_catalogue_data_subsets': num_current_catalogue_data_subsets,
        'browse_index_page_breadcrumb_text': _INDEX_PAGE_TITLE,
    })

def schemas(request):
    """
    A list of links to the XML metadata schemas.
    """
    return render(request, 'browse/schemas.html', {
        'title': _XML_SCHEMAS_PAGE_TITLE
    })

class ResourceListView(ListView):
    """
    A list of detail page links of scientific metadata
    registrations for one given type. E.g., a list of
    all registered Data Collections.

    This view is intended to be subclassed and to not
    be called directly.
    """
    template_name = 'browse/resource_list_by_type.html'
    context_object_name = 'resources'

    description = ''
    resource_detail_page_url_name = ''
    
    def get_queryset(self):
        return self.model.objects.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = self.model.type_plural_readable.title()
        context['description'] = self.description
        context['empty_resource_list_text'] = f'No {self.model.type_plural_readable.lower()} were found.'
        context['resource_detail_page_url_name'] = self.resource_detail_page_url_name
        context['browse_index_page_breadcrumb_text'] = _INDEX_PAGE_TITLE
        context['resource_type_list_page_breadcrumb_text'] = _DATA_COLLECTION_RELATED_RESOURCE_TYPES_PAGE_TITLE
        context['resource_type_list_page_breadcrumb_url_name'] = 'browse:data_collection_related_resource_types'
        return context

    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class OrganisationListView(ResourceListView):
    """
    A subclass of ResourceListView.

    Lists the detail page links for each Organisation
    registration.
    """
    model = models.Organisation
    resource_detail_page_url_name = 'browse:organisation_detail'
    description = 'Data Provider/Owner organisation'

class IndividualListView(ResourceListView):
    """
    A subclass of ResourceListView.

    Lists the detail page links for each Individual
    registration.
    """
    model = models.Individual
    resource_detail_page_url_name = 'browse:individual_detail'
    description = 'An individual, acting in a particular role and associated with an Organisation'

class ProjectListView(ResourceListView):
    """
    A subclass of ResourceListView.

    Lists the detail page links for each Project
    registration.
    """
    model = models.Project
    resource_detail_page_url_name = 'browse:project_detail'
    description = 'An identifiable activity designed to accomplish a set of objectives'

class PlatformListView(ResourceListView):
    """
    A subclass of ResourceListView.

    Lists the detail page links for each Platform
    registration.
    """
    model = models.Platform
    resource_detail_page_url_name = 'browse:platform_detail'
    description = 'An identifiable object that brings the acquisition instrument(s) to the appropriate environment (e.g., satellite, ground observatory)'

class InstrumentListView(ResourceListView):
    """
    A subclass of ResourceListView.

    Lists the detail page links for each Instrument
    registration.
    """
    model = models.Instrument
    resource_detail_page_url_name = 'browse:instrument_detail'
    description = 'An object responsible for interacting with the Feature of Interest in order to acquire Observed Property values'

class OperationListView(ResourceListView):
    """
    A subclass of ResourceListView.

    Lists the detail page links for each Operation
    registration.
    """
    model = models.Operation
    resource_detail_page_url_name = 'browse:operation_detail'
    description = 'Description of how a platform operates in order to support data acquisition by the instrument'

class AcquisitionCapabilitiesListView(ResourceListView):
    """
    A subclass of ResourceListView.

    Lists the detail page links for each Acquisition
    Capabilities registration.
    """
    model = models.AcquisitionCapabilities
    resource_detail_page_url_name = 'browse:acquisition_capability_set_detail'
    description = ''

class AcquisitionListView(ResourceListView):
    """
    A subclass of ResourceListView.

    Lists the detail page links for each Acquisition
    registration.
    """
    model = models.Acquisition
    resource_detail_page_url_name = 'browse:acquisition_detail'
    description = 'Interaction of the Instrument with the Feature of Interest to obtain its Observed Properties'

class ComputationCapabilitiesListView(ResourceListView):
    """
    A subclass of ResourceListView.

    Lists the detail page links for each Computation
    Capabilities registration.
    """
    model = models.ComputationCapabilities
    resource_detail_page_url_name = 'browse:computation_capability_set_detail'
    description = ''

class ComputationListView(ResourceListView):
    """
    A subclass of ResourceListView.

    Lists the detail page links for each Computation
    registration.
    """
    model = models.Computation
    resource_detail_page_url_name = 'browse:computation_detail'
    description = 'Numerical calculation without interacting with the Feature of Interest; characterised by its numerical input and output'

class ProcessListView(ResourceListView):
    """
    A subclass of ResourceListView.

    Lists the detail page links for each Process
    registration.
    """
    model = models.Process
    resource_detail_page_url_name = 'browse:process_detail'
    description = 'A designated procedure used to assign a number, term, or other symbols to a Phenomenon generating the Result; consists of Acquisitions and Computations'

class DataCollectionListView(ResourceListView):
    """
    A subclass of ResourceListView.

    Lists the detail page links for each Data
    Collection registration.
    """
    model = models.DataCollection
    resource_detail_page_url_name = 'browse:data_collection_detail'
    description = 'Top-level definition of a collection of the model or measurement data, with CollectionResults pointing to its URL(s) for accessing the data. Note: data collections do not include begin and end times, please see Catalogue'

class CatalogueRelatedResourceListView(ResourceListView):
    """
    A subclass of ResourceListView.

    Maps Data Collection-related features (e.g., breadcrumbs)
    to Catalogue-related features.
    """
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['resource_type_list_page_breadcrumb_text'] = _CATALOGUE_RELATED_RESOURCE_TYPES_PAGE_TITLE
        context['resource_type_list_page_breadcrumb_url_name'] = 'browse:catalogue_related_resource_types'
        return context

class CatalogueListView(CatalogueRelatedResourceListView):
    """
    A subclass of CatalogueRelatedResourceListView.

    Lists the detail page links for each Catalogue
    registration.
    """
    model = models.Catalogue
    resource_detail_page_url_name = 'browse:catalogue_detail'
    description = ''

class CatalogueEntryListView(CatalogueRelatedResourceListView):
    """
    A subclass of CatalogueRelatedResourceListView.

    Lists the detail page links for each Catalogue
    Entry registration.
    """
    model = models.CatalogueEntry
    resource_detail_page_url_name = 'browse:catalogue_entry_detail'
    description = ''

class CatalogueDataSubsetListView(CatalogueRelatedResourceListView):
    """
    A subclass of CatalogueRelatedResourceListView.

    Lists the detail page links for each Catalogue
    Data Subset registration.
    """
    model = models.CatalogueDataSubset
    resource_detail_page_url_name = 'browse:catalogue_data_subset_detail'
    description = ''

class ResourceDetailView(TemplateView):
    """
    The detail page for a scientific metadata
    registration. The properties of a scientific
    metadata registration are displayed here.

    This view is intended to be subclassed and to not
    be called directly.
    """
    title = 'Resource Detail'
    resource = None
    resource_id = ''
    resource_flattened = None
    resource_human_readable = {}
    ontology_server_urls = []
    resource_server_urls = []
    resource_list_by_type_url_name = ''
    template_name = 'browse/detail.html'

    def get(self, request, *args, **kwargs):
        self.resource = get_object_or_404(self.model, pk=self.resource_id)
        self.scientific_metadata = prepare_resource_for_template(self.resource.json)
        self.scientific_metadata_flattened = flatten(self.scientific_metadata)
        self.ontology_server_urls, self.resource_server_urls = get_server_urls_from_scientific_metadata_flattened(self.scientific_metadata_flattened)
        self.scientific_metadata_readable = create_readable_scientific_metadata_flattened(self.scientific_metadata_flattened)
        self.title = self.resource.name
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = self.title
        context['browse_index_page_breadcrumb_text'] = _INDEX_PAGE_TITLE
        context['resource_type_list_page_breadcrumb_text'] = _DATA_COLLECTION_RELATED_RESOURCE_TYPES_PAGE_TITLE
        context['resource_type_list_page_breadcrumb_url_name'] = 'browse:data_collection_related_resource_types'
        context['resource_list_page_breadcrumb_text'] = self.model.type_plural_readable.title()
        context['resource_list_page_breadcrumb_url_name'] = self.resource_list_by_type_url_name
        context['resource'] = self.resource
        context['scientific_metadata_flattened'] = self.scientific_metadata_flattened
        context['ontology_server_urls'] = self.ontology_server_urls
        context['resource_server_urls'] = self.resource_server_urls
        context['scientific_metadata_readable'] = self.scientific_metadata_readable
        context['scientific_metadata_creation_date_parsed'] = parse(self.resource.creation_date_json)
        context['scientific_metadata_last_modification_date_parsed'] = parse(self.resource.last_modification_date_json)
        context['server_url_conversion_url'] = reverse('browse:convert_server_urls')
        return context

class OrganisationDetailView(ResourceDetailView):
    """
    A subclass of ResourceDetailView.

    A detail page displaying the properties of
    an Organisation registration.
    """
    model = models.Organisation
    resource_list_by_type_url_name = 'browse:list_organisations'

    def get(self, request, *args, **kwargs):
        self.resource_id = self.kwargs['organisation_id']
        return super().get(request, *args, **kwargs)

class IndividualDetailView(ResourceDetailView):
    """
    A subclass of ResourceDetailView.

    A detail page displaying the properties of
    an Individual registration.
    """
    model = models.Individual
    resource_list_by_type_url_name = 'browse:list_individuals'

    def get(self, request, *args, **kwargs):
        self.resource_id = self.kwargs['individual_id']
        return super().get(request, *args, **kwargs)

class ProjectDetailView(ResourceDetailView):
    """
    A subclass of ResourceDetailView.

    A detail page displaying the properties of
    a Project registration.
    """
    model = models.Project
    resource_list_by_type_url_name = 'browse:list_projects'

    def get(self, request, *args, **kwargs):
        self.resource_id = self.kwargs['project_id']
        return super().get(request, *args, **kwargs)

class PlatformDetailView(ResourceDetailView):
    """
    A subclass of ResourceDetailView.

    A detail page displaying the properties of
    a Platform registration.
    """
    model = models.Platform
    resource_list_by_type_url_name = 'browse:list_platforms'

    def get(self, request, *args, **kwargs):
        self.resource_id = self.kwargs['platform_id']
        return super().get(request, *args, **kwargs)

class InstrumentDetailView(ResourceDetailView):
    """
    A subclass of ResourceDetailView.

    A detail page displaying the properties of
    an Instrument registration.
    """
    model = models.Instrument
    resource_list_by_type_url_name = 'browse:list_instruments'

    def get(self, request, *args, **kwargs):
        self.resource_id = self.kwargs['instrument_id']
        return super().get(request, *args, **kwargs)

class OperationDetailView(ResourceDetailView):
    """
    A subclass of ResourceDetailView.

    A detail page displaying the properties of
    an Operation registration.
    """
    model = models.Operation
    resource_list_by_type_url_name = 'browse:list_operations'

    def get(self, request, *args, **kwargs):
        self.resource_id = self.kwargs['operation_id']
        return super().get(request, *args, **kwargs)

class AcquisitionCapabilitiesDetailView(ResourceDetailView):
    """
    A subclass of ResourceDetailView.

    A detail page displaying the properties of
    an Acquisition Capabilities registration.
    """
    model = models.AcquisitionCapabilities
    resource_list_by_type_url_name = 'browse:list_acquisition_capability_sets'

    def get(self, request, *args, **kwargs):
        self.resource_id = self.kwargs['acquisition_capability_set_id']
        return super().get(request, *args, **kwargs)

class AcquisitionDetailView(ResourceDetailView):
    """
    A subclass of ResourceDetailView.

    A detail page displaying the properties of
    an Acquisition registration.
    """
    model = models.Acquisition
    resource_list_by_type_url_name = 'browse:list_acquisitions'

    def get(self, request, *args, **kwargs):
        self.resource_id = self.kwargs['acquisition_id']
        return super().get(request, *args, **kwargs)

class ComputationCapabilitiesDetailView(ResourceDetailView):
    """
    A subclass of ResourceDetailView.

    A detail page displaying the properties of
    a Computation Capabilities registration.
    """
    model = models.ComputationCapabilities
    resource_list_by_type_url_name = 'browse:list_computation_capability_sets'

    def get(self, request, *args, **kwargs):
        self.resource_id = self.kwargs['computation_capability_set_id']
        return super().get(request, *args, **kwargs)

class ComputationDetailView(ResourceDetailView):
    """
    A subclass of ResourceDetailView.

    A detail page displaying the properties of
    a Computation registration.
    """
    model = models.Computation
    resource_list_by_type_url_name = 'browse:list_computations'

    def get(self, request, *args, **kwargs):
        self.resource_id = self.kwargs['computation_id']
        return super().get(request, *args, **kwargs)

class ProcessDetailView(ResourceDetailView):
    """
    A subclass of ResourceDetailView.

    A detail page displaying the properties of
    a Process registration.
    """
    model = models.Process
    resource_list_by_type_url_name = 'browse:list_processes'

    def get(self, request, *args, **kwargs):
        self.resource_id = self.kwargs['process_id']
        return super().get(request, *args, **kwargs)

class DataCollectionDetailView(ResourceDetailView):
    """
    A subclass of ResourceDetailView.

    A detail page displaying the properties of
    a Data Collection registration.
    """
    model = models.DataCollection
    resource_list_by_type_url_name = 'browse:list_data_collections'
    template_name = 'browse/detail_interaction_methods.html'
    interaction_methods = []
    link_interaction_methods = []

    def get(self, request, *args, **kwargs):
        self.resource_id = self.kwargs['data_collection_id']
        self.resource = get_object_or_404(self.model, pk=self.resource_id)
        # API Interaction methods
        self.api_interaction_methods = models.APIInteractionMethod.objects.filter(data_collection=self.resource)
        # Link interaction methods
        self.link_interaction_methods = self.resource.link_interaction_methods

        return super().get(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['api_interaction_methods'] = list(self.api_interaction_methods)
        context['link_interaction_methods'] = list(self.link_interaction_methods)
        context['data_collection_id'] = self.resource_id
        
        return context

class CatalogueRelatedResourceDetailView(ResourceDetailView):
    """
    A subclass of ResourceDetailView.

    Maps Data Collection-related features (e.g., breadcrumbs)
    to Catalogue-related features.

    This view is intended to be subclassed and to not
    be called directly.
    """
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['resource_type_list_page_breadcrumb_text'] = _CATALOGUE_RELATED_RESOURCE_TYPES_PAGE_TITLE
        context['resource_type_list_page_breadcrumb_url_name'] = 'browse:catalogue_related_resource_types'
        return context

class CatalogueDetailView(CatalogueRelatedResourceDetailView):
    """
    A subclass of CatalogueRelatedResourceDetailView.

    A detail page displaying the properties of
    a Catalogue registration.
    """
    model = models.Catalogue
    resource_list_by_type_url_name = 'browse:list_catalogues'

    def get(self, request, *args, **kwargs):
        self.resource_id = self.kwargs['catalogue_id']
        return super().get(request, *args, **kwargs)

class CatalogueEntryDetailView(CatalogueRelatedResourceDetailView):
    """
    A subclass of CatalogueRelatedResourceDetailView.

    A detail page displaying the properties of
    a Catalogue Entry registration.
    """
    model = models.CatalogueEntry
    resource_list_by_type_url_name = 'browse:list_catalogue_entries'

    def get(self, request, *args, **kwargs):
        self.resource_id = self.kwargs['catalogue_entry_id']
        return super().get(request, *args, **kwargs)

class CatalogueDataSubsetDetailView(CatalogueRelatedResourceDetailView):
    """
    A subclass of CatalogueRelatedResourceDetailView.

    A detail page displaying the properties of
    a Catalogue Data Subset registration.
    """
    model = models.CatalogueDataSubset
    resource_list_by_type_url_name = 'browse:list_catalogue_data_subsets'

    def get(self, request, *args, **kwargs):
        self.resource_id = self.kwargs['catalogue_data_subset_id']
        self.handle = None
        self.handle_data = None

        try:
            self.client, self.credentials = instantiate_client_and_load_credentials()
        except BaseException as e:
            logger.exception('An unexpected error occurred whilst instantiating the PyHandle client.')
            return super().get(request, *args, **kwargs)
        
        try:
            handle_url_mapping = models.HandleURLMapping.objects.for_url(request.get_full_path())
            self.handle = handle_url_mapping.handle_name
            self.handle_data = get_handle_record(self.handle, self.client)
        except models.HandleURLMapping.DoesNotExist:
            pass
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['handle'] = self.handle
        context['handle_data'] = None
        if self.handle_data is not None:
            context['handle_data'] = create_readable_scientific_metadata_flattened(self.handle_data)
        return context

def get_esc_url_templates_for_ontology_server_urls_and_resource_server_urls(request):
    """
    Used for mapping ontology server URLs and
    metadata server URLs to their corresponding
    detail pages. Mappings are displayed in 
    scientific metadata detail pages.
    """
    ontology_server_urls = []
    resource_server_urls = []
    if 'ontology-server-urls' in request.GET:
        ontology_server_urls = request.GET['ontology-server-urls'].split(',')
    if 'resource-server-urls' in request.GET:
        resource_server_urls = request.GET['resource-server-urls'].split(',')
    esc_ontology_urls = map_ontology_server_urls_to_browse_urls(ontology_server_urls)
    esc_resource_urls = map_metadata_server_urls_to_browse_urls(resource_server_urls)
    
    return JsonResponse({
        'ontology_urls': esc_ontology_urls,
        'resource_urls': esc_resource_urls,
    })
