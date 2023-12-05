from bson import ObjectId
from django.core.files.uploadedfile import InMemoryUploadedFile
from mongodb import client
from pymongo.errors import OperationFailure
from typing import Union

from .xml_metadata_file_conversion import convert_xml_metadata_file_to_dictionary

from common.mongodb_models import (
    CurrentDataCollectionInteractionMethod,
    OriginalMetadataXml,
)
from validation.errors import FileRegisteredBefore


# From register.py
def register_metadata_xml_file(xml_file, mongodb_model, xml_conversion_check_and_fix, session=None):
    converted_metadata_file_dictionary = convert_xml_metadata_file_to_dictionary(xml_file)
    # Remove the top-level tag - this will be just <Organisation>, for example
    converted_metadata_file_dictionary = converted_metadata_file_dictionary[(list(converted_metadata_file_dictionary)[0])]
    existing_registration = mongodb_model.find_one({
        'identifier.PITHIA_Identifier.namespace': converted_metadata_file_dictionary['identifier']['PITHIA_Identifier']['namespace'],
        'identifier.PITHIA_Identifier.localID': converted_metadata_file_dictionary['identifier']['PITHIA_Identifier']['localID'],
    })
    if existing_registration is not None:
        raise FileRegisteredBefore('This XML metadata file has been registered before.',)
    if xml_conversion_check_and_fix:
        xml_conversion_check_and_fix(converted_metadata_file_dictionary)
    mongodb_model.insert_one(converted_metadata_file_dictionary, session=session)
    return converted_metadata_file_dictionary

def store_xml_file_as_string_and_map_to_resource_id(
    xml_file_or_string: Union[InMemoryUploadedFile, str],
    resource_id,
    original_metadata_xml_model,
    session=None
):
    xml_file_string = xml_file_or_string
    if hasattr(xml_file_or_string, 'read'):
        xml_file_or_string.seek(0)
        xml_file_string = xml_file_or_string.read()
    if isinstance(xml_file_string, bytes):
        xml_file_string = xml_file_string.decode()
    original_metadata_xml = {
        'resourceId': ObjectId(resource_id),
        'value': xml_file_string
    }
    original_metadata_xml_model.insert_one(original_metadata_xml, session=session)

# From register_api_specification.py
def register_api_specification(api_specification_url, data_collection_localid, api_description='', session=None):
    return CurrentDataCollectionInteractionMethod.insert_one({
        'interaction_method': 'api',
        'interaction_url': api_specification_url,
        'interaction_method_description': api_description, 
        'data_collection_localid': data_collection_localid
    }, session=session)

# From views.py
def _register_with_pymongo(
    xml_file,
    resource_mongodb_model,
    original_metadata_xml_model,
    api_selected=False,
    api_specification_url=None,
    api_description='',
    resource_conversion_validate_and_correct_function=None,
    session=None
):
    registration_results = register_metadata_xml_file(
        xml_file,
        resource_mongodb_model,
        resource_conversion_validate_and_correct_function,
        session=session
    )

    store_xml_file_as_string_and_map_to_resource_id(
        xml_file,
        registration_results['_id'],
        original_metadata_xml_model,
        session=session
    )
    if api_selected is True:
        register_api_specification(
            api_specification_url,
            registration_results['identifier']['PITHIA_Identifier']['localID'],
            api_description=api_description,
            session=session
        )

def register_with_pymongo_transaction_if_possible(
    xml_file,
    resource_mongodb_model,
    original_metadata_xml_model,
    api_selected=False,
    api_specification_url=None,
    api_description='',
    resource_conversion_validate_and_correct_function=None,
):
    try:
        with client.start_session() as s:
            def cb(s):
                _register_with_pymongo(
                    xml_file,
                    resource_mongodb_model,
                    original_metadata_xml_model,
                    api_selected=api_selected,
                    api_specification_url=api_specification_url,
                    api_description=api_description,
                    resource_conversion_validate_and_correct_function=resource_conversion_validate_and_correct_function,
                    session=s
                )
            s.with_transaction(cb)
    except OperationFailure:
        _register_with_pymongo(
            xml_file,
            resource_mongodb_model,
            original_metadata_xml_model,
            api_selected=api_selected,
            api_specification_url=api_specification_url,
            api_description=api_description,
            resource_conversion_validate_and_correct_function=resource_conversion_validate_and_correct_function
        )