import logging
from bson import ObjectId
from pymongo.errors import OperationFailure

from common.mongodb_models import (
    CurrentDataCollectionInteractionMethod,
    DataCollectionInteractionMethodRevision,
    OriginalMetadataXml,
)
from handle_management.pymongo_api import add_handle_to_url_mapping_old
from handle_management.xml_utils import (
    add_doi_xml_string_to_metadata_xml_string,
    create_doi_xml_string_from_dict,
)
from mongodb import client
from register.pymongo_api import (
    register_api_specification,
    store_xml_file_as_string_and_map_to_resource_id,
)
from register.xml_metadata_file_conversion import convert_xml_metadata_file_to_dictionary


logger = logging.getLogger(__name__)


def _update_with_pymongo(
    resource_localid,
    resource_mongodb_model,
    resource_revision_mongodb_model,
    xml_file_string=None,
    resource_conversion_validate_and_correct_function=None,
    session=None
):
    resource = resource_mongodb_model.find_one({
        'identifier.PITHIA_Identifier.localID': resource_localid
    })
    resource_id = str(resource['_id'])
    converted_xml_file = convert_xml_metadata_file_to_dictionary(xml_file_string)
    converted_xml_file = converted_xml_file[(list(converted_xml_file)[0])]
    pithia_identifier = converted_xml_file['identifier']['PITHIA_Identifier']
    resource_revision = create_revision_of_current_resource_version(
        pithia_identifier,
        resource_mongodb_model,
        resource_revision_mongodb_model,
        session=session
    )
    assign_original_xml_file_entry_to_revision_id(
        resource_id,
        resource_revision['_id'],
        session=session
    )
    update_current_version_of_resource(
        resource_id,
        xml_file_string,
        resource_mongodb_model,
        resource_conversion_validate_and_correct_function,
        session=session
    )
    store_xml_file_as_string_and_map_to_resource_id(
        xml_file_string,
        resource_id,
        OriginalMetadataXml,
        session=session
    )

def _update_interaction_method_with_pymongo(
    data_collection_localid: str,
    api_selected=False,
    api_specification_url=None,
    api_description='',
    session=None
):
    create_revision_of_data_collection_api_interaction_method(
        data_collection_localid,
        session=session
    )
    if api_selected is False:
        CurrentDataCollectionInteractionMethod.delete_one({
            'data_collection_localid': data_collection_localid,
            'interaction_method': 'api',
        }, session=session)
        return
    existing_api_interaction_method = CurrentDataCollectionInteractionMethod.find_one({
        'data_collection_localid': data_collection_localid
    })
    if existing_api_interaction_method is None:
        register_api_specification(
            api_specification_url,
            data_collection_localid,
            api_description,
            session=session
        )
    else:
        update_data_collection_api_interaction_method_specification_url(
            data_collection_localid,
            api_specification_url,
            session=session
        )
        update_data_collection_api_interaction_method_description(
            data_collection_localid,
            api_description,
            session=session
        )

def add_doi_kernel_metadata_to_xml_and_return_updated_string(
    doi_dict,
    resource_id,
    xml_file,
    resource_mongodb_model,
    resource_conversion_validate_and_correct_function=None,
    session=None
):
    doi_xml_string = create_doi_xml_string_from_dict(doi_dict)
    xml_file.seek(0)
    metadata_xml_string = xml_file.read()
    xml_string_with_doi = add_doi_xml_string_to_metadata_xml_string(metadata_xml_string, doi_xml_string)
    update_current_version_of_resource(
        resource_id,
        xml_string_with_doi,
        resource_mongodb_model,
        resource_conversion_validate_and_correct_function,
        session=session
    )
    return xml_string_with_doi

def _register_doi_with_pymongo(
    doi_dict,
    resource_id,
    xml_file,
    resource_mongodb_model,
    handle,
    data_subset_url,
    resource_conversion_validate_and_correct_function=None,
    session=None
):
    xml_string_with_doi = add_doi_kernel_metadata_to_xml_and_return_updated_string(
        doi_dict,
        resource_id,
        xml_file,
        resource_mongodb_model,
        resource_conversion_validate_and_correct_function=resource_conversion_validate_and_correct_function,
        session=session
    )
    update_original_metadata_xml_string(
        xml_string_with_doi,
        resource_id,
        session=session
    )
    add_handle_to_url_mapping_old(handle, data_subset_url, session=session)

# From update.py
def update_current_version_of_resource(
    resource_id,
    xml_file,
    current_resource_mongodb_model,
    xml_conversion_check_and_fix,
    session=None
):
    metadata_file_dictionary = convert_xml_metadata_file_to_dictionary(xml_file)
    # Remove the top-level tag - this will be just <Organisation>, for example
    metadata_file_dictionary = metadata_file_dictionary[(list(metadata_file_dictionary)[0])]
    if xml_conversion_check_and_fix:
        xml_conversion_check_and_fix(metadata_file_dictionary)
    current_resource_mongodb_model.update_one({
        '_id': ObjectId(str(resource_id))
    }, { '$set': metadata_file_dictionary }, session=session)
    return metadata_file_dictionary

def update_data_collection_api_interaction_method_specification_url(
    data_collection_localid,
    api_specification_url,
    session=None
):
    return CurrentDataCollectionInteractionMethod.update_one(
        {
            'data_collection_localid': data_collection_localid,
            'interaction_method': 'api',
        },
        {
            '$set': {
                'interaction_url': api_specification_url
            }
        },
        session=session
    )

def update_data_collection_api_interaction_method_description(
    data_collection_localid,
    api_description,
    session=None
):
    return CurrentDataCollectionInteractionMethod.update_one(
        {
            'data_collection_localid': data_collection_localid,
            'interaction_method': 'api',
        },
        {
            '$set': {
                'interaction_method_description': api_description
            }
        },
        session=session
    )

def update_original_metadata_xml_string(updated_xml_string, resource_id, session=None):
    return OriginalMetadataXml.update_one(
        {
            'resourceId': ObjectId(resource_id),
        },
        {
            '$set': {
                'value': updated_xml_string
            }
        },
        session=session
    )


# From version_control.py
def create_revision_of_current_resource_version(
    resource_pithia_identifier,
    current_resource_mongodb_model,
    resource_revision_mongodb_model,
    session=None
):
    current_version_of_resource = current_resource_mongodb_model.find_one({
        'identifier.PITHIA_Identifier.localID': resource_pithia_identifier['localID'],
        'identifier.PITHIA_Identifier.namespace': resource_pithia_identifier['namespace'],
    })
    if not current_version_of_resource:
        logger.warning(f"Could not create a revision of the resource with a localID {resource_pithia_identifier['localID']} and namespace {resource_pithia_identifier['namespace']}, as that resource could not be found.")
        return 'Resource not found.'
    current_version_of_resource.pop('_id', None)
    resource_revision_mongodb_model.insert_one(current_version_of_resource, session=session)
    return current_version_of_resource

def assign_original_xml_file_entry_to_revision_id(old_resource_id, revision_id, session=None):
    current_orginal_xml_file = OriginalMetadataXml.find_one({
        'resourceId': ObjectId(str(old_resource_id))
    })
    if current_orginal_xml_file is None:
        logger.warning(f'Could not assign the original XML metadata string for resource with ID {old_resource_id} to the resource\'s revision, as an original XML metadata string for that resource was not found.')
        return 'The original XML metadata string for this resource was not found.'
    return OriginalMetadataXml.update_one({
        'resourceId': ObjectId(str(old_resource_id))
    }, { '$set': {
        'resourceId': ObjectId(str(revision_id))
    }}, session=session)

def create_revision_of_data_collection_api_interaction_method(data_collection_localid, session=None):
    current_version_of_api_interaction_method = CurrentDataCollectionInteractionMethod.find_one({
        'data_collection_localid': data_collection_localid,
        'interaction_method': 'api',
    })
    if current_version_of_api_interaction_method == None:
        logger.warning(f'Could not make a revision of the API interaction method for the Data Collection with localID {data_collection_localid}, as no Data Collection with that localID was found.')
        return 'No API interaction method for this data collection was found.'
    current_version_of_api_interaction_method.pop('_id', None)
    DataCollectionInteractionMethodRevision.insert_one(current_version_of_api_interaction_method, session=session)
    return current_version_of_api_interaction_method

# Use PyMongo Transactions if possible functions
def update_with_pymongo_transaction_if_possible(
    resource_localid,
    resource_mongodb_model,
    resource_revision_mongodb_model,
    xml_file_string=None,
    resource_conversion_validate_and_correct_function=None
):
    try:
        with client.start_session() as s:
            def cb(s):
                _update_with_pymongo(
                    resource_localid,
                    resource_mongodb_model,
                    resource_revision_mongodb_model,
                    xml_file_string,
                    resource_conversion_validate_and_correct_function,
                    session=s
                )
            s.with_transaction(cb)
    except OperationFailure:
        _update_with_pymongo(
            resource_localid,
            resource_mongodb_model,
            resource_revision_mongodb_model,
            xml_file_string,
            resource_conversion_validate_and_correct_function,
        )

def update_interaction_method_with_pymongo_transaction_if_possible(
    data_collection_localid: str,
    api_selected=False,
    api_specification_url=None,
    api_description='',
):
    try:
        with client.start_session() as s:
            def cb(s):
                _update_interaction_method_with_pymongo(
                    data_collection_localid,
                    api_selected,
                    api_specification_url,
                    api_description,
                    session=s
                )
            s.with_transaction(cb)
    except OperationFailure:
        _update_interaction_method_with_pymongo(
            data_collection_localid,
            api_selected,
            api_specification_url,
            api_description,
        )

def register_doi_with_pymongo_transaction_if_possible(
    doi_dict,
    resource_id,
    xml_file,
    resource_mongodb_model,
    handle,
    data_subset_url,
    resource_conversion_validate_and_correct_function=None,
):
    try:
        with client.start_session() as s:
            def cb(s):
                _register_doi_with_pymongo(
                    doi_dict,
                    resource_id,
                    xml_file,
                    resource_mongodb_model,
                    handle,
                    data_subset_url,
                    resource_conversion_validate_and_correct_function,
                    session=s
                )
            s.with_transaction(cb)
    except OperationFailure:
        _register_doi_with_pymongo(
            doi_dict,
            resource_id,
            xml_file,
            resource_mongodb_model,
            handle,
            data_subset_url,
            resource_conversion_validate_and_correct_function,
        )