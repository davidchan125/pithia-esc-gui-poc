import logging
from django.contrib import messages
from django.template.loader import render_to_string
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.utils.html import escape
from django.views.generic import FormView

from .forms import *
from .services import *
from .form_processing import *
from .view_mixins import *

from common import models
from common.decorators import login_session_institution_required
from resource_management.views import (
    _INDEX_PAGE_TITLE,
    _DATA_COLLECTION_MANAGEMENT_INDEX_PAGE_TITLE,
    _create_manage_resource_page_title
)
from user_management.services import (
    get_user_id_for_login_session,
    get_institution_id_for_login_session,
)


logger = logging.getLogger(__name__)


# Create your views here.

@method_decorator(login_session_institution_required, name='dispatch')
class ResourceEditorFormView(
    FormView,
    OrganisationSelectFormViewMixin,
    ResourceChoicesViewMixin):
    success_url = ''
    form_class = None
    template_name = ''

    model = None
    metadata_editor_class = None
    save_data_local_storage_key = ''
    file_upload_registration_url = ''
    resource_management_list_page_breadcrumb_url_name = ''
    resource_management_list_page_breadcrumb_text = ''

    institution_id = None
    owner_id = None

    def process_form(self, form_cleaned_data):
        # Make copy of cleaned data
        processed_form = form_cleaned_data
        return processed_form

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if 'form' not in kwargs:
            context['form'] = self.get_form()
        context['success_url'] = self.success_url
        context['localid_base'] = self.model.localid_base
        context['metadata_type_readable'] = self.model.type_readable.title()
        context['namespaces_by_organisation'] = {o.metadata_server_url: clean_localid_or_namespace(o.short_name) for o in models.Organisation.objects.all()}
        context['save_data_local_storage_key'] = self.save_data_local_storage_key
        if 'title' not in context:
            context['title'] = f'{self.model.type_readable.title()} Wizard'
        context['resource_management_index_page_breadcrumb_text'] = _INDEX_PAGE_TITLE
        context['resource_management_category_list_page_breadcrumb_text'] = _DATA_COLLECTION_MANAGEMENT_INDEX_PAGE_TITLE
        context['resource_management_category_list_page_breadcrumb_url_name'] = 'resource_management:data_collection_related_metadata_index'
        context['resource_management_list_page_breadcrumb_text'] = self.resource_management_list_page_breadcrumb_text
        context['resource_management_list_page_breadcrumb_url_name'] = self.resource_management_list_page_breadcrumb_url_name
        return context

    def form_invalid(self, form):
        messages.error(self.request, f'The form submitted was not valid. See the form below for details.')
        return super().form_invalid(form)
    
    def dispatch(self, request, *args, **kwargs):
        self.institution_id = get_institution_id_for_login_session(request.session)
        self.owner_id = get_user_id_for_login_session(request.session)
        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['form_metadata_type'] = self.model.type_readable.title()
        kwargs['organisation_choices'] = self.get_organisation_choices_for_form()
        return kwargs

class OrganisationEditorFormView(ResourceEditorFormView):
    form_class = OrganisationEditorForm
    template_name = 'register_with_support/organisation_editor.html'

    model = models.Organisation
    metadata_editor_class = OrganisationMetadataEditor

    resource_management_list_page_breadcrumb_text = _create_manage_resource_page_title('organisations')
    resource_management_list_page_breadcrumb_url_name = 'resource_management:organisations'

    def process_form(self, form_cleaned_data):
        processed_form = super().process_form(form_cleaned_data)

        # Hours of service
        hours_of_service = process_hours_of_service_in_form(form_cleaned_data)
        processed_form['hours_of_service'] = hours_of_service
        
        # Contact info
        processed_form['contact_info'] = process_contact_info_in_form(form_cleaned_data)

        return processed_form

class IndividualEditorFormView(ResourceEditorFormView):
    form_class = IndividualEditorForm
    template_name = 'register_with_support/individual_editor.html'

    model = models.Individual
    metadata_editor_class = IndividualMetadataEditor

    resource_management_list_page_breadcrumb_text = _create_manage_resource_page_title('individuals')
    resource_management_list_page_breadcrumb_url_name = 'resource_management:individuals'

    def process_form(self, form_cleaned_data):
        processed_form = super().process_form(form_cleaned_data)

        # Hours of service
        hours_of_service = process_hours_of_service_in_form(form_cleaned_data)
        processed_form['hours_of_service'] = hours_of_service
        
        # Contact info
        processed_form['contact_info'] = process_contact_info_in_form(form_cleaned_data)

        return processed_form

class ProjectEditorFormView(
    RelatedPartiesSelectFormViewMixin,
    ResourceEditorFormView,
    StatusSelectFormViewMixin):
    form_class = ProjectEditorForm
    template_name = 'register_with_support/project_editor.html'

    model = models.Project
    metadata_editor_class = ProjectMetadataEditor

    resource_management_list_page_breadcrumb_text = _create_manage_resource_page_title(models.Project.type_plural_readable)
    resource_management_list_page_breadcrumb_url_name = 'resource_management:projects'

    def process_form(self, form_cleaned_data):
        processed_form = super().process_form(form_cleaned_data)

        processed_form['documentation'] = process_documentation(form_cleaned_data)
        # processed_form['keyword_dict_list'] = process_project_keywords(form_cleaned_data)
        processed_form['related_parties'] = process_related_parties(form_cleaned_data)

        return processed_form

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['related_party_role_choices'] = self.get_related_party_role_choices_for_form()
        kwargs['related_party_choices'] = self.get_related_party_choices_for_form()
        kwargs['status_choices'] = self.get_status_choices_for_form()
        return kwargs
        
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['citation_section_description'] = 'Reference to documentation describing the project.'
        context['related_parties_section_description'] = 'Individual or organisation related to the project.'
        return context

class PlatformEditorFormView(
    PlatformSelectFormViewMixin,
    RelatedPartiesSelectFormViewMixin,
    SrsNameSelectFormViewMixin,
    StandardIdentifiersFormViewMixin,
    ResourceEditorFormView):
    form_class = PlatformEditorForm
    template_name = 'register_with_support/platform_editor.html'

    model = models.Platform
    metadata_editor_class = PlatformMetadataEditor

    resource_management_list_page_breadcrumb_text = _create_manage_resource_page_title(models.Platform.type_plural_readable)
    resource_management_list_page_breadcrumb_url_name = 'resource_management:platforms'

    def get_type_choices_for_form(self):
        return self.get_choices_from_ontology_category('platformType')

    def get_child_platform_choices_for_form(self):
        return self.get_platform_choices_for_form()

    def process_form(self, form_cleaned_data):
        processed_form = super().process_form(form_cleaned_data)

        processed_form['documentation'] = process_documentation(form_cleaned_data)
        processed_form['related_parties'] = process_related_parties(form_cleaned_data)
        processed_form['location'] = process_location(form_cleaned_data)
        processed_form['standard_identifiers'] = form_cleaned_data['standard_identifiers_json']

        return processed_form

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['related_party_role_choices'] = self.get_related_party_role_choices_for_form()
        kwargs['related_party_choices'] = self.get_related_party_choices_for_form()
        kwargs['type_choices'] = self.get_type_choices_for_form()
        kwargs['child_platform_choices'] = self.get_child_platform_choices_for_form()
        kwargs['crs_choices'] = self.get_crs_choices_for_form()
        return kwargs
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['location_section_description'] = 'Location of the platform. Note, that it is only applicable to static platforms or geo-stationary satellites.'
        context['geo_location_description'] = f'The LAT, LON coordinates of the position of the platform. "{context.get("form").fields.get("geometry_location_point_srs_name").label}" describes the coordinate system.'
        context['citation_section_description'] = 'Reference to documentation describing the platform.'
        context['related_parties_section_description'] = 'Responsibility, identification of, and means of communication with associated person(s) and organisations. A facility owning a platform can be described here.'
        context['standard_identifier_row_content_template'] = render_to_string(
            'register_with_support/components/platform/platform_standard_identifier_row_content_template.html',
            context=context
        )
        return context


class OperationEditorFormView(
    PlatformSelectFormViewMixin,
    RelatedPartiesSelectFormViewMixin,
    SrsNameSelectFormViewMixin,
    ResourceEditorFormView,
    StatusSelectFormViewMixin,
    ResourceChoicesViewMixin):
    form_class = OperationEditorForm
    template_name = 'register_with_support/operation_editor.html'

    model = models.Operation
    metadata_editor_class = OperationMetadataEditor

    resource_management_list_page_breadcrumb_text = _create_manage_resource_page_title(models.Operation.type_plural_readable)
    resource_management_list_page_breadcrumb_url_name = 'resource_management:operations'

    def get_child_operation_choices_for_form(self):
        return self.get_resource_choices_with_model(models.Operation)

    def process_form(self, form_cleaned_data):
        processed_form = super().process_form(form_cleaned_data)

        processed_form['documentation'] = process_documentation(form_cleaned_data)
        processed_form['related_parties'] = process_related_parties(form_cleaned_data)
        processed_form['location'] = process_location(form_cleaned_data)
        processed_form['operation_time'] = process_operation_time(form_cleaned_data)

        return processed_form

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['citation_section_description'] = 'Reference to documentation describing the operation.'
        context['related_parties_section_description'] = 'Individual or organisation related to platform operation.'
        context['location_section_description'] = 'Location of the platform operation.'
        context['location_section_example'] = 'A flight line or a ship track for a platform such as an aircraft or a ship respectively.'
        return context

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['platform_choices'] = self.get_platform_choices_for_form()
        kwargs['child_operation_choices'] = self.get_child_operation_choices_for_form()
        kwargs['related_party_role_choices'] = self.get_related_party_role_choices_for_form()
        kwargs['related_party_choices'] = self.get_related_party_choices_for_form()
        kwargs['crs_choices'] = self.get_crs_choices_for_form()
        kwargs['status_choices'] = self.get_status_choices_for_form()
        return kwargs


class InstrumentEditorFormView(
    InstrumentTypeSelectFormViewMixin,
    RelatedPartiesSelectFormViewMixin,
    ResourceEditorFormView):
    form_class = InstrumentEditorForm
    template_name = 'register_with_support/instrument_editor.html'

    model = models.Instrument
    metadata_editor_class = InstrumentMetadataEditor

    resource_management_list_page_breadcrumb_text = _create_manage_resource_page_title(models.Instrument.type_plural_readable)
    resource_management_list_page_breadcrumb_url_name = 'resource_management:instruments'

    def get_member_choices_for_form(self):
        return self.get_resource_choices_with_model(models.Instrument)

    def process_form(self, form_cleaned_data):
        processed_form = super().process_form(form_cleaned_data)

        processed_form['documentation'] = process_documentation(form_cleaned_data)
        processed_form['related_parties'] = process_related_parties(form_cleaned_data)
        processed_form['operational_modes'] = process_operational_modes(form_cleaned_data)

        return processed_form

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['related_parties_section_description'] = 'Information regarding organisations and/or individuals related to instrument.'
        context['citation_section_description'] = 'Reference to documentation describing the instrument.'
        context['operational_mode_row_content_template'] = render_to_string(
            'register_with_support/components/instrument/operational_mode_row_content_template.html',
            context=context
        )
        return context

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['instrument_type_choices'] = self.get_instrument_type_choices_for_form()
        kwargs['member_choices'] = self.get_member_choices_for_form()
        kwargs['related_party_choices'] = self.get_related_party_choices_for_form()
        kwargs['related_party_role_choices'] = self.get_related_party_role_choices_for_form()
        return kwargs


class AcquisitionCapabilitiesEditorFormView(
    CapabilitiesSelectFormViewMixin,
    DataLevelSelectFormViewMixin,
    QualityAssessmentSelectFormViewMixin,
    RelatedPartiesSelectFormViewMixin,
    ResourceEditorFormView):
    form_class = AcquisitionCapabilitiesEditorForm
    template_name = 'register_with_support/acquisition_capabilities_editor.html'

    model = models.AcquisitionCapabilities
    metadata_editor_class = AcquisitionCapabilitiesMetadataEditor

    resource_management_list_page_breadcrumb_text = _create_manage_resource_page_title(models.AcquisitionCapabilities.type_plural_readable)
    resource_management_list_page_breadcrumb_url_name = 'resource_management:acquisition_capability_sets'

    def get_instrument_choices_with_oms_for_form(self):
        instruments = self.get_resources_with_model_ordered_by_name(models.Instrument)
        return (
            ('', ''),
            *[(instrument.metadata_server_url, instrument.name) for instrument in instruments if instrument.operational_modes],
        )

    def get_instrument_operational_modes_for_form(self):
        instruments = self.get_resources_with_model_ordered_by_name(models.Instrument)
        operational_modes_by_instrument = []
        for instrument in instruments:
            operational_modes = instrument.operational_modes
            if not operational_modes:
                continue
            operational_modes_by_instrument.append((
                instrument.name,
                [(f'{instrument.metadata_server_url}#{om.get("id")}', om.get('name')) for om in operational_modes]
            ))

        return (
            ('', ''),
            *operational_modes_by_instrument,
        )

    def process_form(self, form_cleaned_data):
        processed_form = super().process_form(form_cleaned_data)

        processed_form['documentation'] = process_documentation(form_cleaned_data)
        processed_form['related_parties'] = process_related_parties(form_cleaned_data)
        processed_form['capabilities'] = process_capabilities(form_cleaned_data)
        processed_form['instrument_mode_pair'] = process_instrument_mode_pair(form_cleaned_data)
        processed_form['quality_assessment'] = process_quality_assessment(form_cleaned_data)

        return processed_form

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['citation_section_description'] = 'Reference to documentation describing the component.'
        context['related_parties_section_description'] = 'Individual or organisation related to acquisition.'
        context['capabilities_tab_content_template'] = render_to_string(
            'register_with_support/components/capabilities_tab_content_template.html',
            context=context
        )
        return context

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['data_level_choices'] = self.get_data_level_choices_for_form()
        kwargs['data_quality_flag_choices'] = self.get_data_quality_flag_choices_for_form()
        kwargs['metadata_quality_flag_choices'] = self.get_metadata_quality_flag_choices_for_form()
        # Capabilities
        kwargs['coordinate_system_choices'] = self.get_coordinate_system_choices_for_form()
        kwargs['dimensionality_instance_choices'] = self.get_dimensionality_instance_choices_for_form()
        kwargs['dimensionality_timeline_choices'] = self.get_dimensionality_timeline_choices_for_form()
        kwargs['observed_property_choices'] = self.get_observed_property_choices_for_form()
        kwargs['qualifier_choices'] = self.get_qualifier_choices_for_form()
        kwargs['unit_choices'] = self.get_unit_choices_for_form()
        kwargs['vector_representation_choices'] = self.get_vector_representation_choices_for_form()
        # Instrument mode pairs
        kwargs['instrument_choices'] = self.get_instrument_choices_with_oms_for_form()
        kwargs['operational_mode_choices'] = self.get_instrument_operational_modes_for_form()
        # Related parties
        kwargs['related_party_role_choices'] = self.get_related_party_role_choices_for_form()
        kwargs['related_party_choices'] = self.get_related_party_choices_for_form()
        return kwargs


class AcquisitionEditorFormView(
    PlatformSelectFormViewMixin,
    ResourceEditorFormView):
    form_class = AcquisitionEditorForm
    template_name = 'register_with_support/acquisition_editor.html'

    model = models.Acquisition
    metadata_editor_class = AcquisitionMetadataEditor

    resource_management_list_page_breadcrumb_text = _create_manage_resource_page_title(models.Acquisition.type_plural_readable)
    resource_management_list_page_breadcrumb_url_name = 'resource_management:acquisitions'

    def get_acquisition_capability_sets_for_form(self):
        return self.get_resource_choices_with_model(models.AcquisitionCapabilities)

    def process_form(self, form_cleaned_data):
        processed_form = super().process_form(form_cleaned_data)

        processed_form['capability_links'] = process_acquisition_capability_links(form_cleaned_data)

        return processed_form

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['capability_links_tab_pane_content_template'] = render_to_string(
            'register_with_support/components/capability_links_tab_pane_content_template.html',
            context=context
        )
        context['capability_link_standard_identifier_row_content_template'] = render_to_string(
            'register_with_support/components/acquisition_and_computation/capability_link_standard_identifier_row_content_template.html',
            context=context
        )
        context['capability_link_time_span_row_content_template'] = render_to_string(
            'register_with_support/components/acquisition_and_computation/capability_link_time_span_row_content_template.html',
            context=context
        )
        return context

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['capability_set_choices'] = self.get_acquisition_capability_sets_for_form()
        kwargs['platform_choices'] = self.get_platform_choices_for_form()
        return kwargs


class ComputationCapabilitiesEditorFormView(
    CapabilitiesSelectFormViewMixin,
    ComputationTypeSelectFormViewMixin,
    DataLevelSelectFormViewMixin,
    QualityAssessmentSelectFormViewMixin,
    RelatedPartiesSelectFormViewMixin,
    ResourceEditorFormView):
    form_class = ComputationCapabilitiesEditorForm
    template_name = 'register_with_support/computation_capabilities_editor.html'

    model = models.ComputationCapabilities
    metadata_editor_class = ComputationCapabilitiesMetadataEditor

    resource_management_list_page_breadcrumb_text = _create_manage_resource_page_title(models.ComputationCapabilities.type_plural_readable)
    resource_management_list_page_breadcrumb_url_name = 'resource_management:computation_capability_sets'

    def get_child_computation_choices_for_form(self):
        return self.get_resource_choices_with_model(models.ComputationCapabilities)

    def process_form(self, form_cleaned_data):
        processed_form = super().process_form(form_cleaned_data)
        
        processed_form['documentation'] = process_documentation(form_cleaned_data)
        processed_form['related_parties'] = process_related_parties(form_cleaned_data)
        processed_form['capabilities'] = process_capabilities(form_cleaned_data)
        processed_form['quality_assessment'] = process_quality_assessment(form_cleaned_data)
        processed_form['processing_inputs'] = process_processing_inputs(form_cleaned_data)
        processed_form['software_reference'] = process_software_reference(form_cleaned_data)
        
        return processed_form

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['related_parties_section_description'] = 'Individual or organisation related to Computation.'
        context['citation_section_description'] = 'Reference to documentation describing the component.'
        context['capabilities_tab_content_template'] = render_to_string(
            'register_with_support/components/capabilities_tab_content_template.html',
            context=context
        )
        context['processing_input_row_content_template'] = render_to_string(
            'register_with_support/components/computation_capabilities/processing_input_row_content_template.html',
            context=context
        )
        return context

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['data_level_choices'] = self.get_data_level_choices_for_form()
        kwargs['data_quality_flag_choices'] = self.get_data_quality_flag_choices_for_form()
        kwargs['metadata_quality_flag_choices'] = self.get_metadata_quality_flag_choices_for_form()
        kwargs['child_computation_choices'] = self.get_child_computation_choices_for_form()
        kwargs['computation_type_choices'] = self.get_computation_type_choices_for_form()
        # Capabilities
        kwargs['coordinate_system_choices'] = self.get_coordinate_system_choices_for_form()
        kwargs['dimensionality_instance_choices'] = self.get_dimensionality_instance_choices_for_form()
        kwargs['dimensionality_timeline_choices'] = self.get_dimensionality_timeline_choices_for_form()
        kwargs['observed_property_choices'] = self.get_observed_property_choices_for_form()
        kwargs['qualifier_choices'] = self.get_qualifier_choices_for_form()
        kwargs['unit_choices'] = self.get_unit_choices_for_form()
        kwargs['vector_representation_choices'] = self.get_vector_representation_choices_for_form()
        # Related parties
        kwargs['related_party_role_choices'] = self.get_related_party_role_choices_for_form()
        kwargs['related_party_choices'] = self.get_related_party_choices_for_form()
        return kwargs


class ComputationEditorFormView(
    PlatformSelectFormViewMixin,
    ResourceEditorFormView):
    form_class = ComputationEditorForm
    template_name = 'register_with_support/computation_editor.html'

    model = models.Computation
    metadata_editor_class = ComputationMetadataEditor

    resource_management_list_page_breadcrumb_text = _create_manage_resource_page_title(models.Computation.type_plural_readable)
    resource_management_list_page_breadcrumb_url_name = 'resource_management:computations'

    def get_computation_capability_set_choices_for_form(self):
        return self.get_resource_choices_with_model(models.ComputationCapabilities)

    def process_form(self, form_cleaned_data):
        processed_form = super().process_form(form_cleaned_data)

        processed_form['capability_links'] = process_computation_capability_links(form_cleaned_data)

        return processed_form

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['capability_links_tab_pane_content_template'] = render_to_string(
            'register_with_support/components/capability_links_tab_pane_content_template.html',
            context=context
        )
        context['capability_link_standard_identifier_row_content_template'] = render_to_string(
            'register_with_support/components/acquisition_and_computation/capability_link_standard_identifier_row_content_template.html',
            context=context
        )
        context['capability_link_time_span_row_content_template'] = render_to_string(
            'register_with_support/components/acquisition_and_computation/capability_link_time_span_row_content_template.html',
            context=context
        )
        return context

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['platform_choices'] = self.get_platform_choices_for_form()
        kwargs['capability_set_choices'] = self.get_computation_capability_set_choices_for_form()
        return kwargs


class ProcessEditorFormView(
    CapabilitiesSelectFormViewMixin,
    DataLevelSelectFormViewMixin,
    QualityAssessmentSelectFormViewMixin,
    RelatedPartiesSelectFormViewMixin,
    ResourceEditorFormView):
    form_class = ProcessEditorForm
    template_name = 'register_with_support/process_editor.html'

    model = models.Process
    metadata_editor_class = ProcessMetadataEditor

    resource_management_list_page_breadcrumb_text = _create_manage_resource_page_title(models.Process.type_plural_readable)
    resource_management_list_page_breadcrumb_url_name = 'resource_management:processes'

    def get_acquisition_choices_for_form(self):
        return self.get_resource_choices_with_model(models.Acquisition)

    def get_computation_choices_for_form(self):
        return self.get_resource_choices_with_model(models.Computation)

    def process_form(self, form_cleaned_data):
        processed_form = super().process_form(form_cleaned_data)
        
        processed_form['documentation'] = process_documentation(form_cleaned_data)
        processed_form['related_parties'] = process_related_parties(form_cleaned_data)
        processed_form['capabilities'] = process_capabilities(form_cleaned_data)
        processed_form['quality_assessment'] = process_quality_assessment(form_cleaned_data)

        return processed_form

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['related_parties_section_description'] = 'Individual or organisation related to composite process.'
        context['citation_section_description'] = 'Reference to documentation describing the component.'
        context['capabilities_tab_content_template'] = render_to_string(
            'register_with_support/components/capabilities_tab_content_template.html',
            context=context
        )
        return context

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        # Process
        kwargs['acquisition_choices'] = self.get_acquisition_choices_for_form()
        kwargs['computation_choices'] = self.get_computation_choices_for_form()
        # Capabilities
        kwargs['coordinate_system_choices'] = self.get_coordinate_system_choices_for_form()
        kwargs['dimensionality_instance_choices'] = self.get_dimensionality_instance_choices_for_form()
        kwargs['dimensionality_timeline_choices'] = self.get_dimensionality_timeline_choices_for_form()
        kwargs['observed_property_choices'] = self.get_observed_property_choices_for_form()
        kwargs['qualifier_choices'] = self.get_qualifier_choices_for_form()
        kwargs['unit_choices'] = self.get_unit_choices_for_form()
        kwargs['vector_representation_choices'] = self.get_vector_representation_choices_for_form()
        # Data levels
        kwargs['data_level_choices'] = self.get_data_level_choices_for_form()
        kwargs['data_quality_flag_choices'] = self.get_data_quality_flag_choices_for_form()
        # Quality assessment
        kwargs['metadata_quality_flag_choices'] = self.get_metadata_quality_flag_choices_for_form()
        # Related parties
        kwargs['related_party_role_choices'] = self.get_related_party_role_choices_for_form()
        kwargs['related_party_choices'] = self.get_related_party_choices_for_form()
        return kwargs


class DataCollectionEditorFormView(
    ComputationTypeSelectFormViewMixin,
    DataCollectionSelectFormViewMixin,
    DataLevelSelectFormViewMixin,
    InstrumentTypeSelectFormViewMixin,
    QualityAssessmentSelectFormViewMixin,
    RelatedPartiesSelectFormViewMixin,
    ResourceEditorFormView):
    form_class = DataCollectionEditorForm
    template_name = 'register_with_support/data_collection_editor.html'

    model = models.DataCollection
    metadata_editor_class = DataCollectionMetadataEditor

    resource_management_list_page_breadcrumb_text = _create_manage_resource_page_title(models.DataCollection.type_plural_readable)
    resource_management_list_page_breadcrumb_url_name = 'resource_management:data_collections'

    def register_api_interaction_method(self, request, new_registration):
        try:
            api_specification_url = request.POST.get('api_specification_url', None)
            api_description = request.POST.get('api_description', '')
            if not api_specification_url:
                return
            models.InteractionMethod.api_interaction_methods.create_api_interaction_method(
                api_specification_url,
                api_description,
                new_registration
            )
            messages.success(request, f'<p>Added an API interaction method for {escape(new_registration.name)}.</p><p class="mb-0">It can be viewed and/or updated from the <a href="{reverse_lazy("update:data_collection_interaction_methods", kwargs={"resource_id": new_registration.pk})}">interaction methods page</a> for this data collection.</p>')
        except BaseException as err:
            logger.exception('An unexpected error occurred during API interaction method registration.')
            messages.error(request, 'An unexpected error occurred during API interaction method registration.')
    
    def run_registration_actions(self, request, xml_file, name):
        new_registration = self.register_xml_file(request, xml_file, name)
        self.register_api_interaction_method(request, new_registration)
        return new_registration

    def get_feature_of_interest_choices_for_form(self):
        return self.get_choices_from_ontology_category('featureOfInterest')

    def get_permission_choices_for_form(self):
        return self.get_choices_from_ontology_category('licence')

    def get_type_choices_for_form(self):
        instrument_type_choices = list(self.get_instrument_type_choices_for_form())
        instrument_type_choices.pop(0)
        computation_type_choices = list(self.get_computation_type_choices_for_form())
        computation_type_choices.pop(0)
        return (
            ('', ''),
            ('Instrument Types', instrument_type_choices),
            ('Computation Types', computation_type_choices),
        )

    def get_project_choices_for_form(self):
        return self.get_resource_choices_with_model(models.Project)

    def get_process_choices_for_form(self):
        return self.get_resource_choices_with_model(models.Process)

    def get_service_function_choices_for_form(self):
        return self.get_choices_from_ontology_category('serviceFunction')

    def get_data_format_choices_for_form(self):
        return self.get_choices_from_ontology_category('resultDataFormat')

    def process_form(self, form_cleaned_data):
        processed_form = super().process_form(form_cleaned_data)
        
        processed_form['related_parties'] = process_related_parties(form_cleaned_data)
        processed_form['quality_assessment'] = process_quality_assessment(form_cleaned_data)
        processed_form['collection_results'] = process_sources(form_cleaned_data)

        return processed_form

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['related_parties_section_description'] = 'Individual or organisation related to composite process.'
        context['sources_tab_pane_content_template'] = render_to_string(
            'register_with_support/components/data_collection/sources_tab_pane_content_template.html',
            context=context
        )
        return context
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['data_level_choices'] = self.get_data_level_choices_for_form()
        kwargs['type_choices'] = self.get_type_choices_for_form()
        kwargs['project_choices'] = self.get_project_choices_for_form()
        kwargs['feature_of_interest_choices'] = self.get_feature_of_interest_choices_for_form()
        kwargs['permission_choices'] = self.get_permission_choices_for_form()
        kwargs['process_choices'] = self.get_process_choices_for_form()
        # Quality assessment
        kwargs['data_quality_flag_choices'] = self.get_data_quality_flag_choices_for_form()
        kwargs['metadata_quality_flag_choices'] = self.get_metadata_quality_flag_choices_for_form()
        # Related parties
        kwargs['related_party_role_choices'] = self.get_related_party_role_choices_for_form()
        kwargs['related_party_choices'] = self.get_related_party_choices_for_form()
        # Sub collection
        kwargs['sub_collection_choices'] = self.get_data_collection_choices_for_form()
        # Collection results
        kwargs['service_function_choices'] = self.get_service_function_choices_for_form()
        kwargs['data_format_choices'] = self.get_data_format_choices_for_form()
        return kwargs

class WorkflowEditorFormView(
    DataCollectionSelectFormViewMixin,
    ResourceEditorFormView):
    form_class = WorkflowEditorForm
    template_name = 'register_with_support/workflow_editor.html'

    model = models.Workflow
    metadata_editor_class = WorkflowMetadataEditor

    resource_management_list_page_breadcrumb_text = _create_manage_resource_page_title(models.Workflow.type_plural_readable)
    resource_management_list_page_breadcrumb_url_name = 'resource_management:workflows'

    def process_form(self, form_cleaned_data):
        processed_form = super().process_form(form_cleaned_data)
        processed_form['data_collections'] = process_workflow_data_collections(form_cleaned_data)
        return processed_form

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['data_collection_choices'] = self.get_data_collection_choices_for_form()
        return kwargs
