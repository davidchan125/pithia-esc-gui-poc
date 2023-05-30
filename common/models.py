from django.db import models

from .managers import *
from .querysets import *
from .converted_xml_correction_functions import *

# Create your models here.
class ScientificMetadata(models.Model):
    ORGANISATION = 'organisation'
    INDIVIDUAL = 'individual'
    PROJECT = 'project'
    PLATFORM = 'platform'
    OPERATION = 'operation'
    INSTRUMENT = 'instrument'
    ACQUISITION_CAPABILITIES = 'acquisition_capabilities'
    ACQUISITION = 'acquisition'
    COMPUTATION_CAPABILITIES = 'computation_capabilities'
    COMPUTATION = 'computation'
    PROCESS = 'process'
    DATA_COLLECTION = 'data_collection'
    CATALOGUE = 'catalogue'
    CATALOGUE_ENTRY = 'catalogue_entry'
    CATALOGUE_DATA_SUBSET = 'catalogue_data_subset'
    RESOURCE_TYPE_CHOICES = [
        (ORGANISATION, 'Organisation'),
        (INDIVIDUAL, 'Individual'),
        (PROJECT, 'Project'),
        (PLATFORM, 'Platform'),
        (OPERATION, 'Operation'),
        (INSTRUMENT, 'Instrument'),
        (ACQUISITION_CAPABILITIES, 'Acquisition Capabilities'),
        (ACQUISITION, 'Acquisition'),
        (COMPUTATION_CAPABILITIES, 'Computation Capabilities'),
        (COMPUTATION, 'Computation'),
        (PROCESS, 'Process'),
        (DATA_COLLECTION, 'Data Collection'),
        (CATALOGUE, 'Catalogue'),
        (CATALOGUE_ENTRY, 'Catalogue Entry'),
        (CATALOGUE_DATA_SUBSET, 'Catalogue Data Subset'),
    ]
    registration_id = models.CharField(max_length=200)
    resource_type = models.CharField(
        max_length=100,
        choices=RESOURCE_TYPE_CHOICES
    )
    xml = models.TextField()
    json = models.JSONField()
    # institution_id = models.ForeignKey()
    # registrant_id = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def identifier(self):
        return self.json['identifier']

    @property
    def pithia_identifier(self):
        return self.identifier['PITHIA_Identifier']

    @property
    def namespace(self):
        return self.pithia_identifier['namespace']

    @property
    def localid(self):
        return self.pithia_identifier['localID']
    
    @property
    def name(self):
        return self.json['name']

    @property
    def type_in_metadata_server_url(self):
        pass

    @property
    def _metadata_server_url_base(self):
        return 'https://metadata.pithia.eu/resources/2.2'

    @property
    def metadata_server_url(self):
        return f'{self._metadata_server_url_base}/{self.type_in_metadata_server_url}/{self.namespace}/{self.localid}'
    
    @property
    def converted_xml_correction_function(self):
        return None

    def save(self, *args, **kwargs):
        if self.converted_xml_correction_function is not None:
            self.json = self.converted_xml_correction_function(self.scientific_metadata)
        super().save(*args, **kwargs)

class TechnicalMetadata(models.Model):
    API = 'api'
    MICADO = 'micado'
    DOWNLOAD = 'download'
    INTERACTION_METHOD_CHOICES = [
        (API, 'API'),
        (MICADO, 'MiCADO'),
        (DOWNLOAD, 'Download'),
    ]
    # data_collection_id = models.ForeignKey()
    interaction_method = models.CharField(
        choices=INTERACTION_METHOD_CHOICES,
        default=API,
        max_length=100
    )
    json = models.JSONField()
    # institution_id = models.ForeignKey()
    # registrant_id = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Institution(models.Model):
    institution_name = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class HandleURLMapping(models.Model):
    data_subset_url = models.URLField()
    handle_name = models.CharField(max_length=100)

# Proxy models
class Organisation(ScientificMetadata):
    type_in_metadata_server_url = 'organisation'
    weight = 1
    type_readable = 'organisation'
    type_plural_readable = 'organisations'
    a_or_an = 'an'

    objects = OrganisationManager.from_queryset(OrganisationQuerySet)()

    class Meta:
        proxy = True

class Individual(ScientificMetadata):
    type_in_metadata_server_url = 'individual'
    weight = 2
    type_readable = 'individual'
    type_plural_readable = 'individuals'
    a_or_an = 'an'

    objects = IndividualManager.from_queryset(IndividualQuerySet)()

    class Meta:
        proxy = True

class Project (ScientificMetadata):
    type_in_metadata_server_url = 'project'
    weight = 3
    type_readable = 'project'
    type_plural_readable = 'projects'
    a_or_an = 'a'

    objects = ProjectManager.from_queryset(ProjectQuerySet)()

    class Meta:
        proxy = True

class Platform(ScientificMetadata):
    type_in_metadata_server_url = 'platform'
    weight = 4
    type_readable = 'platform'
    type_plural_readable = 'platforms'
    a_or_an = 'a'
    converted_xml_correction_function = correct_platform_xml_converted_to_dict

    objects = PlatformManager.from_queryset(PlatformQuerySet)()

    class Meta:
        proxy = True

class Operation(ScientificMetadata):
    type_in_metadata_server_url = 'operation'
    weight = 5
    type_readable = 'operation'
    type_plural_readable = 'operations'
    a_or_an = 'an'

    objects = OperationManager.from_queryset(OperationQuerySet)()

    class Meta:
        proxy = True

class Instrument(ScientificMetadata):
    type_in_metadata_server_url = 'instrument'
    weight = 6
    type_readable = 'instrument'
    type_plural_readable = 'instruments'
    a_or_an = 'an'
    converted_xml_correction_function = correct_instrument_xml_converted_to_dict

    objects = InstrumentManager.from_queryset(InstrumentQuerySet)()

    class Meta:
        proxy = True

class AcquisitionCapabilities(ScientificMetadata):
    type_in_metadata_server_url = 'acquisitionCapabilities'
    weight = 7
    type_readable = 'acquisition capabilities'
    type_plural_readable = 'acquisition capabilities'
    a_or_an = 'an'
    converted_xml_correction_function = correct_acquisition_capability_set_xml_converted_to_dict

    objects = AcquisitionCapabilitiesManager.from_queryset(AcquisitionCapabilitiesQuerySet)()

    class Meta:
        proxy = True

class Acquisition(ScientificMetadata):
    type_in_metadata_server_url = 'acquisition'
    weight = 8
    type_readable = 'acquisition'
    type_plural_readable = 'acquisitions'
    a_or_an = 'an'
    converted_xml_correction_function = correct_acquisition_xml_converted_to_dict

    objects = AcquisitionManager.from_queryset(AcquisitionQuerySet)()

    class Meta:
        proxy = True

class ComputationCapabilities(ScientificMetadata):
    type_in_metadata_server_url = 'computationCapabilities'
    weight = 9
    type_readable = 'computation capabilities'
    type_plural_readable = 'computation capabilities'
    a_or_an = 'a'
    converted_xml_correction_function = correct_computation_capability_set_xml_converted_to_dict

    objects = ComputationCapabilitiesManager.from_queryset(ComputationCapabilitiesQuerySet)()

    class Meta:
        proxy = True

class Computation(ScientificMetadata):
    type_in_metadata_server_url = 'computation'
    weight = 10
    type_readable = 'computation'
    type_plural_readable = 'computations'
    a_or_an = 'a'
    converted_xml_correction_function = correct_computation_xml_converted_to_dict

    objects = ComputationManager.from_queryset(ComputationQuerySet)()

    class Meta:
        proxy = True

class Process(ScientificMetadata):
    type_in_metadata_server_url = 'process'
    weight = 11
    type_readable = 'process'
    type_plural_readable = 'processes'
    a_or_an = 'a'
    converted_xml_correction_function = correct_process_xml_converted_to_dict

    objects = ProcessManager.from_queryset(ProcessQuerySet)()

    class Meta:
        proxy = True

class DataCollection(ScientificMetadata):
    type_in_metadata_server_url = 'collection'
    weight = 12
    type_readable = 'data collection'
    type_plural_readable = 'data collections'
    a_or_an = 'a'
    converted_xml_correction_function = correct_data_collection_xml_converted_to_dict

    @property
    def first_related_party_url(self):
        return self.scientific_metadata['relatedParty'][0]['ResponsiblePartyInfo']['party']['@xlink:href']

    objects = DataCollectionManager.from_queryset(DataCollectionQuerySet)()

    class Meta:
        proxy = True

class Catalogue(ScientificMetadata):
    type_in_metadata_server_url = 'catalogue'
    weight = 13
    type_readable = 'catalogue'
    type_plural_readable = 'catalogues'
    a_or_an = 'a'

    objects = CatalogueManager.from_queryset(CatalogueQuerySet)()

    class Meta:
        proxy = True

class CatalogueEntry(ScientificMetadata):
    type_in_metadata_server_url = 'catalogue'
    weight = 14
    type_readable = 'catalogue entry'
    type_plural_readable = 'catalogue entries'
    a_or_an = 'a'

    objects = CatalogueEntryManager.from_queryset(CatalogueEntryQuerySet)()

    class Meta:
        proxy = True

class CatalogueDataSubset(ScientificMetadata):
    type_in_metadata_server_url = 'catalogue'
    weight = 15
    type_readable = 'catalogue data subset'
    type_plural_readable = 'catalogue data subsets'
    a_or_an = 'a'

    @property
    def data_collection_url(self):
        return self.json['dataCollection']['@xlink:href']

    objects = CatalogueDataSubsetManager.from_queryset(CatalogueDataSubsetQuerySet)()

    class Meta:
        proxy = True