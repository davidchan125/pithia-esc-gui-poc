import json
import os
import uuid
import xmltodict
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.db import models
from typing import Union


class ScientificMetadataManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().order_by('json__name')

    def _convert_xml_metadata_file_to_dictionary(self, xml_file_or_string: Union[InMemoryUploadedFile, str]) -> dict:
        xml = xml_file_or_string
        if hasattr(xml_file_or_string, 'read'):
            xml_file_or_string.seek(0)
            xml = xml_file_or_string.read()
        xml_as_dict = xmltodict.parse(xml)
        xml_as_json = json.dumps(xml_as_dict)
        # Some formatting to get rid of '\n' characters and extra
        # whitespace within strings
        xml_as_json = xml_as_json.replace('\\n', '')
        xml_as_json = ' '.join(xml_as_json.split())
        # pymongo takes dictionaries when inserting new documents,
        # so convert the JSON back to a dictionary
        return json.loads(xml_as_json)

    def _format_metadata_file_xml_for_db(self, metadata_file_xml):
        metadata_file_dict = self._convert_xml_metadata_file_to_dictionary(metadata_file_xml)
        # Remove the top-level tag - this will be just <Organisation>, for example
        metadata_file_dict = metadata_file_dict[(list(metadata_file_dict)[0])]
        return metadata_file_dict
    
    def _create_from_xml_string(
        self,
        xml_string: str,
        type: str,
        institution_id: str,
        owner_id: str
    ):
        xml_as_dict = self._format_metadata_file_xml_for_db(xml_string)
        
        try:
            xml_string = xml_string.decode()
        except (UnicodeDecodeError, AttributeError):
            pass

        scientific_metadata = self.model(
            type=type,
            xml=xml_string,
            json=xml_as_dict,
            institution_id=institution_id,
            owner_id=owner_id
        )
        scientific_metadata.id = scientific_metadata.localid
        scientific_metadata.save(using=os.environ['DJANGO_RW_DATABASE_NAME'])

        return scientific_metadata


    def create_from_xml_string(self, xml_string: str, institution_id: str, owner_id: str):
        pass


    def update_from_xml_string(self, pk, xml_string: str, owner_id: str):
        xml_as_dict = self._format_metadata_file_xml_for_db(xml_string)

        try:
            xml_string = xml_string.decode()
        except (UnicodeDecodeError, AttributeError):
            pass

        registration = self.get(pk=pk)
        registration.xml = xml_string
        registration.json = xml_as_dict
        registration.owner_id = owner_id
        registration.save(using=os.environ['DJANGO_RW_DATABASE_NAME'])
        return registration
    
    class Meta:
        abstract = True

class OrganisationManager(ScientificMetadataManager):
    def get_queryset(self):
        return super().get_queryset().filter(type=self.model.ORGANISATION)

    def create_from_xml_string(self, xml_string: str, institution_id: str, owner_id: str):
        return super()._create_from_xml_string(xml_string, self.model.ORGANISATION, institution_id, owner_id)

class IndividualManager(ScientificMetadataManager):
    def get_queryset(self):
        return super().get_queryset().filter(type=self.model.INDIVIDUAL)

    def create_from_xml_string(self, xml_string: str, institution_id: str, owner_id: str):
        return super()._create_from_xml_string(xml_string, self.model.INDIVIDUAL, institution_id, owner_id)

class ProjectManager(ScientificMetadataManager):
    def get_queryset(self):
        return super().get_queryset().filter(type=self.model.PROJECT)

    def create_from_xml_string(self, xml_string: str, institution_id: str, owner_id: str):
        return super()._create_from_xml_string(xml_string, self.model.PROJECT, institution_id, owner_id)

class PlatformManager(ScientificMetadataManager):
    def get_queryset(self):
        return super().get_queryset().filter(type=self.model.PLATFORM)

    def create_from_xml_string(self, xml_string: str, institution_id: str, owner_id: str):
        return super()._create_from_xml_string(xml_string, self.model.PLATFORM, institution_id, owner_id)

class OperationManager(ScientificMetadataManager):
    def get_queryset(self):
        return super().get_queryset().filter(type=self.model.OPERATION)

    def create_from_xml_string(self, xml_string: str, institution_id: str, owner_id: str):
        return super()._create_from_xml_string(xml_string, self.model.OPERATION, institution_id, owner_id)

class InstrumentManager(ScientificMetadataManager):
    def get_queryset(self):
        return super().get_queryset().filter(type=self.model.INSTRUMENT)

    def create_from_xml_string(self, xml_string: str, institution_id: str, owner_id: str):
        return super()._create_from_xml_string(xml_string, self.model.INSTRUMENT, institution_id, owner_id)

class AcquisitionCapabilitiesManager(ScientificMetadataManager):
    def get_queryset(self):
        return super().get_queryset().filter(type=self.model.ACQUISITION_CAPABILITIES)

    def create_from_xml_string(self, xml_string: str, institution_id: str, owner_id: str):
        return super()._create_from_xml_string(xml_string, self.model.ACQUISITION_CAPABILITIES, institution_id, owner_id)

class AcquisitionManager(ScientificMetadataManager):
    def get_queryset(self):
        return super().get_queryset().filter(type=self.model.ACQUISITION)

    def create_from_xml_string(self, xml_string: str, institution_id: str, owner_id: str):
        return super()._create_from_xml_string(xml_string, self.model.ACQUISITION, institution_id, owner_id)

class ComputationCapabilitiesManager(ScientificMetadataManager):
    def get_queryset(self):
        return super().get_queryset().filter(type=self.model.COMPUTATION_CAPABILITIES)

    def create_from_xml_string(self, xml_string: str, institution_id: str, owner_id: str):
        return super()._create_from_xml_string(xml_string, self.model.COMPUTATION_CAPABILITIES, institution_id, owner_id)

class ComputationManager(ScientificMetadataManager):
    def get_queryset(self):
        return super().get_queryset().filter(type=self.model.COMPUTATION)

    def create_from_xml_string(self, xml_string: str, institution_id: str, owner_id: str):
        return super()._create_from_xml_string(xml_string, self.model.COMPUTATION, institution_id, owner_id)

class ProcessManager(ScientificMetadataManager):
    def get_queryset(self):
        return super().get_queryset().filter(type=self.model.PROCESS)

    def create_from_xml_string(self, xml_string: str, institution_id: str, owner_id: str):
        return super()._create_from_xml_string(xml_string, self.model.PROCESS, institution_id, owner_id)

class DataCollectionManager(ScientificMetadataManager):
    def get_queryset(self):
        return super().get_queryset().filter(type=self.model.DATA_COLLECTION)

    def create_from_xml_string(self, xml_string: str, institution_id: str, owner_id: str):
        return super()._create_from_xml_string(xml_string, self.model.DATA_COLLECTION, institution_id, owner_id)

class CatalogueManager(ScientificMetadataManager):
    def get_queryset(self):
        return super().get_queryset().filter(type=self.model.CATALOGUE)

    def create_from_xml_string(self, xml_string: str, institution_id: str, owner_id: str):
        return super()._create_from_xml_string(xml_string, self.model.CATALOGUE, institution_id, owner_id)

class CatalogueEntryManager(ScientificMetadataManager):
    def get_queryset(self):
        return super().get_queryset().filter(type=self.model.CATALOGUE_ENTRY)

    def create_from_xml_string(self, xml_string: str, institution_id: str, owner_id: str):
        return super()._create_from_xml_string(xml_string, self.model.CATALOGUE_ENTRY, institution_id, owner_id)

class CatalogueDataSubsetManager(ScientificMetadataManager):
    def get_queryset(self):
        return super().get_queryset().filter(type=self.model.CATALOGUE_DATA_SUBSET)

    def create_from_xml_string(self, xml_string: str, institution_id: str, owner_id: str):
        return super()._create_from_xml_string(xml_string, self.model.CATALOGUE_DATA_SUBSET, institution_id, owner_id)
    
class InteractionMethodManager(models.Manager):
    pass

class APIInteractionMethodManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(type=self.model.API)

    def create_api_interaction_method(self, specification_url: str, description: str, data_collection):
        config = {
            'specification_url': specification_url,
            'description': description,
        }
        interaction_method = self.model(
            id=uuid.uuid4(),
            type=self.model.API,
            data_collection=data_collection,
            config=config,
            owner=0
        )
        interaction_method.save(using=os.environ['DJANGO_RW_DATABASE_NAME'])

        return interaction_method

    def update_config(self, interaction_method_id, specification_url: str, description: str = ''):
        interaction_method = self.get_queryset().get(pk=interaction_method_id)
        interaction_method.specification_url = specification_url
        interaction_method.description = description
        interaction_method.save(using=os.environ['DJANGO_RW_DATABASE_NAME'])
        return interaction_method