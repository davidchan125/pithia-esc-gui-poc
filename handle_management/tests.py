import environ
import os
from django.test import (
    TestCase,
    tag
)
from pathlib import Path
from pyhandle.handleclient import RESTHandleClient
from pyhandle.clientcredentials import PIDClientCredentials

from .handle_api import (
    add_doi_metadata_kernel_to_handle,
    create_and_register_handle_for_resource,
    create_handle,
    delete_handle,
    generate_and_register_handle,
    get_date_handle_was_issued_as_string,
    get_handle_issue_number,
    get_handle_raw,
    get_handle_record,
    get_handle_url,
    get_handles_with_prefix,
    get_time_handle_was_issued_as_string,
    instantiate_client_and_load_credentials,
    register_handle,
    update_handle_url,
)
from .xml_utils import (
    add_data_subset_data_to_doi_metadata_kernel_dict,
    add_doi_metadata_kernel_to_data_subset,
    add_doi_xml_string_to_metadata_xml_string,
    add_handle_data_to_doi_metadata_kernel_dict,
    create_doi_xml_string_from_dict,
    get_doi_xml_string_from_metadata_xml_string,
    get_first_related_party_name_from_data_collection,
    get_last_source_element,
    get_last_result_time_element,
    initialise_default_doi_kernel_metadata_dict,
    is_doi_element_present_in_xml_file,
    parse_xml_string,
    remove_doi_element_from_metadata_xml_string,
)

from common.models import (
    DataCollection,
    CatalogueDataSubset,
)
from pithiaesc.settings import BASE_DIR
from utils.dict_helpers import flatten

_XML_METADATA_FILE_DIR = os.path.join(BASE_DIR, 'common', 'test_files', 'xml_metadata_files')

# For tests where ownership data is required
SAMPLE_USER_ID        = 'johndoe@example.com'
SAMPLE_INSTITUTION_ID = 'John Doe Institution'

env = environ.Env()

# Create your tests here.
@tag('manual')
class PyHandleSetupTestCase(TestCase):
    TEST_SUFFIX = 'MYTEST-HANDLE'
    VALUE_ORIGINAL = 'https://www.example.com/1'
    VALUE_AFTER = 'https://www.example.com/2'

    def setUp(self) -> None:
        # Also acts as integration test
        # for instantiate_client_and_load_credentials() function
        self.client, self.credentials = instantiate_client_and_load_credentials()
        return super().setUp()
    
    def tearDown(self) -> None:
        try:
            if hasattr(self, 'handle'):
                print('Tearing down test...')
                print('Deleting handle...')
                delete_handle(self.handle, self.client)
                print('Test tear down complete')
        except:
            print('Could not delete handle.')
        return super().tearDown()
    
    def _create_and_register_handle_for_test(self):
        self.handle = create_handle(self.credentials, self.TEST_SUFFIX)
        register_handle(self.handle, self.VALUE_ORIGINAL, self.client)


@tag('manual')
class PyHandleTestCase(PyHandleSetupTestCase):
    @tag('fast', 'handles', 'instantiate_client_and_load_credentials')
    def test_instantiate_client_and_load_credentials(self):
        """
        instantiate_client_and_load_credentials() returns a tuple containing a client of type "RESTHandleClient "and credentials of type "PIDClientCredentials"
        """
        client, credentials = instantiate_client_and_load_credentials()

        self.assertIsInstance(client, RESTHandleClient)
        self.assertIsInstance(credentials, PIDClientCredentials)

        print('Passed instantiate_client_and_load_credentials() test.')

    @tag('fast', 'handles')
    def test_create_handle(self):
        """
        create_handle() returns a string with format "{handle_prefix}/{handle_suffix}"
        """
        self.handle = create_handle(self.credentials, self.TEST_SUFFIX)

        self.assertIsInstance(self.handle, str)
        self.assertEqual(self.handle, f'{self.credentials.get_prefix()}/{self.TEST_SUFFIX}')

        print('Passed create_handle() test.')

    @tag('fast', 'handles', 'register_handle')
    def test_register_handle(self):
        """
        register_handle() returns the handle data passed into it and raises no exceptions.
        """
        self.handle = create_handle(self.credentials, self.TEST_SUFFIX)
        register_result = register_handle(self.handle, self.VALUE_ORIGINAL, self.client)

        self.assertEqual(register_result, self.handle)

        print('Passed register_handle() test.')

    @tag('fast', 'handles', 'get_handle_record')
    def test_get_handle_record(self):
        """
        get_handle_record() returns the record for the handle data and raises no exceptions.
        """
        self._create_and_register_handle_for_test()

        handle_record = get_handle_record(self.handle, self.client)
        print('handle_record', handle_record)

        self.assertIsInstance(handle_record, dict)

        print('Passed get_handle_record() test.')

    @tag('fast', 'handles', 'get_handle_url')
    def test_get_handle_url(self):
        """
        get_handle_url() returns the URL for the handle and raises no exceptions.
        """
        self._create_and_register_handle_for_test()

        handle_url = get_handle_url(self.handle, self.client)
        print('handle_url', handle_url)

        self.assertEqual(handle_url, self.VALUE_ORIGINAL)
        self.assertIsInstance(handle_url, str)

        print('Passed get_handle_url() test.')

    @tag('fast', 'handles', 'get_handle_raw')
    def test_get_handle_raw(self):
        """
        get_handle_raw() returns the handle without being formatted by the API.
        """
        self._create_and_register_handle_for_test()
        handle_raw = get_handle_raw(self.handle)
        print('handle_raw', handle_raw)

        self.assertIsInstance(handle_raw, dict)

        print('Passed get_handle_raw() test.')

    @tag('fast', 'handles', 'get_time_handle_was_issued_as_string')
    def test_get_time_handle_was_issued_as_string(self):
        """
        get_time_handle_was_issued_as_string() returns the time the handle was issued in str format.
        """
        self._create_and_register_handle_for_test()
        issue_time_string = get_time_handle_was_issued_as_string(self.handle)
        print('issue_time_string', issue_time_string)

        self.assertIsInstance(issue_time_string, str)

        print('Passed get_time_handle_was_issued_as_string() test.')

    @tag('fast', 'handles', 'get_date_handle_was_issued_as_string')
    def test_get_date_handle_was_issued_as_string(self):
        """
        get_date_handle_was_issued_as_string() returns the date the handle was issued.
        """
        self._create_and_register_handle_for_test()
        issue_date_as_string = get_date_handle_was_issued_as_string(self.handle)
        print('issue_date_as_string', issue_date_as_string)

        self.assertIsInstance(issue_date_as_string, str)

        print('Passed get_date_handle_was_issued_as_string() test.')

    @tag('fast', 'handles', 'delete_handle')
    def test_delete_handle(self):
        """
        delete_handle() returns the handle of the deleted record and raises no exceptions.
        """
        self._create_and_register_handle_for_test()
        delete_result = delete_handle(self.handle, self.client)

        self.assertEqual(self.handle, delete_result)

        print('Passed delete_handle() test.')

    @tag('fast', 'handles', 'update_handle_url')
    def test_update_handle_url(self):
        """
        update_handle_url() raises no exception.
        """
        doi_dict = initialise_default_doi_kernel_metadata_dict()
        flat_doi_dict = flatten(doi_dict)
        self.handle = create_handle(self.credentials, self.TEST_SUFFIX)
        register_handle(self.handle, self.VALUE_ORIGINAL, self.client, initial_doi_dict_values=flat_doi_dict)
        update_result = update_handle_url(self.handle, self.VALUE_AFTER, self.client)
        handle_url = get_handle_url(self.handle, self.client)
        handle_issue_number = get_handle_issue_number(self.handle, self.client)

        self.assertEqual(update_result, self.handle)
        self.assertEqual(handle_url, self.VALUE_AFTER)
        self.assertEqual(int(handle_issue_number), 2)

        print('handle_url', handle_url)
        print('handle_issue_number', handle_issue_number)
        print('Passed update_handle_url() test.')

    @tag('fast', 'get_handles_with_prefix')
    def test_get_handles_with_prefix(self):
        """
        get_handles_with_prefix() returns all handles under a given prefix.
        """
        prefix = env('HANDLE_PREFIX')
        handles = get_handles_with_prefix(prefix)
        print('handles', handles)

    @tag('fast', 'add_doi_dict_to_handle')
    def test_add_doi_dict_to_handle(self):
        """
        add_doi_metadata_kernel_to_handle() adds the DOI metadata kernel properties to a handle.
        """
        with open(os.path.join(_XML_METADATA_FILE_DIR, 'DataSubset_Test-2023-01-01_DataCollectionTest.xml')) as xml_file:
            catalogue_data_subset = CatalogueDataSubset.objects.create_from_xml_string(xml_file.read(), SAMPLE_INSTITUTION_ID, SAMPLE_USER_ID)
            self.catalogue_data_subset_id = catalogue_data_subset.pk
        doi_dict = initialise_default_doi_kernel_metadata_dict()
        add_data_subset_data_to_doi_metadata_kernel_dict(
            catalogue_data_subset,
            doi_dict,
            data_collection_model=DataCollection
        )
        self.handle, client, credentials = create_and_register_handle_for_resource(self.catalogue_data_subset_id)
        add_handle_data_to_doi_metadata_kernel_dict(self.handle, doi_dict)
        flat_doi_dict = flatten(doi_dict, number_list_items=False)
        add_doi_metadata_kernel_to_handle(self.handle, flat_doi_dict, self.client)

        print('Passed DOI dict configuration test.')

    @tag('fast', 'generate_and_register_handle')
    def test_generate_and_register_handle(self):
        """
        generate_and_register_handle() returns a handle name
        with a randomly generated suffix.
        """
        self.handle = generate_and_register_handle('https://www.example.com', self.credentials, self.client)

        self.assertIsInstance(self.handle, str)

        print('Passed generate and register handle test.')


@tag('manual')
class DOIDictTestCase(PyHandleSetupTestCase):
    @tag('fast', 'doi_dict_configuration')
    def test_doi_configuration_process(self):
        """
        All properties in the DOI dict are set successfully.
        """
        with open(os.path.join(_XML_METADATA_FILE_DIR, 'DataSubset_Test-2023-01-01_DataCollectionTest.xml')) as xml_file:
            catalogue_data_subset = CatalogueDataSubset.objects.create_from_xml_string(xml_file.read(), SAMPLE_INSTITUTION_ID, SAMPLE_USER_ID)
            self.catalogue_data_subset_id = catalogue_data_subset.pk
        doi_dict = initialise_default_doi_kernel_metadata_dict()
        add_data_subset_data_to_doi_metadata_kernel_dict(
            catalogue_data_subset,
            doi_dict,
            data_collection_model=DataCollection
        )
        self.handle, client, credentials = create_and_register_handle_for_resource(self.catalogue_data_subset_id)
        add_handle_data_to_doi_metadata_kernel_dict(self.handle, doi_dict)
        print(doi_dict)

        print('Passed DOI dict configuration test.')

    @tag('fast', 'flatten_doi_dict')
    def test_flatten_doi_dict(self):
        """
        Nested dicts in the DOI dict use dot notation when flattened.
        """
        with open(os.path.join(_XML_METADATA_FILE_DIR, 'DataSubset_Test-2023-01-01_DataCollectionTest.xml')) as xml_file:
            catalogue_data_subset = CatalogueDataSubset.objects.create_from_xml_string(xml_file.read(), SAMPLE_INSTITUTION_ID, SAMPLE_USER_ID)
            self.catalogue_data_subset_id = catalogue_data_subset.pk
        doi_dict = initialise_default_doi_kernel_metadata_dict()
        add_data_subset_data_to_doi_metadata_kernel_dict(
            catalogue_data_subset,
            doi_dict,
            data_collection_model=DataCollection
        )
        self.handle, client, credentials = create_and_register_handle_for_resource(self.catalogue_data_subset_id)
        add_handle_data_to_doi_metadata_kernel_dict(self.handle, doi_dict)
        flat_doi_dict = flatten(doi_dict, number_list_items=False)
        print('flat_doi_dict', flat_doi_dict)

        print('Passed flatten DOI dict test.')


@tag('manual')
class DOIXMLRegistrationTestCase(PyHandleSetupTestCase):
    @tag('fast', 'register_handle_and_add_to_metadata')
    def test_register_handle_and_add_to_metadata(self):
        """
        register_handle_and_add_to_metadata() raises no exceptions.
        """
        with open(os.path.join(_XML_METADATA_FILE_DIR, 'DataSubset_Test-2023-01-01_DataCollectionTest.xml')) as xml_file:
            xml_file_string = xml_file.read()
            catalogue_data_subset = CatalogueDataSubset.objects.create_from_xml_string(xml_file_string, SAMPLE_INSTITUTION_ID, SAMPLE_USER_ID)
            catalogue_data_subset_id = catalogue_data_subset.pk
            self.handle, client, credentials = create_and_register_handle_for_resource(catalogue_data_subset_id)
            print('xml_file', xml_file)
            doi_dict = initialise_default_doi_kernel_metadata_dict()
            add_doi_metadata_kernel_to_data_subset(
                catalogue_data_subset_id,
                doi_dict,
                xml_file_string,
                SAMPLE_USER_ID
            )

        print(f'Passed handle registration for {Path(xml_file.name).name}.')

    @tag('fast', 'add_doi_xml_string_to_metadata_xml_string')
    def test_add_doi_xml_string_to_metadata_xml_string(self):
        """
        add_doi_xml_string_to_metadata_xml_string() adds a filled out <doi> element to the XML string.
        """
        self._create_and_register_handle_for_test()
        doi_dict = initialise_default_doi_kernel_metadata_dict()
        doi_xml_string = create_doi_xml_string_from_dict(doi_dict)
        with open(os.path.join(_XML_METADATA_FILE_DIR, 'DataSubset_Test-2023-01-01_DataCollectionTest.xml')) as xml_file:
            xml_string = xml_file.read()
            updated_xml_string = add_doi_xml_string_to_metadata_xml_string(xml_string, doi_xml_string)
            print('updated_xml_string', updated_xml_string)

        print(f'Passed new DOI element addition for {Path(xml_file.name).name}.')

    @tag('fast', 'get_last_result_time_element')
    def test_get_last_result_time_element(self):
        """
        Gets the last <resultTime> element in a Data Subset XML string.
        """
        with open(os.path.join(_XML_METADATA_FILE_DIR, 'DataSubset_Test-2023-01-01_DataCollectionTest.xml')) as xml_file:
            xml_string = xml_file.read()
            xml_string_parsed = parse_xml_string(xml_string)
            last_result_time_element = get_last_result_time_element(xml_string_parsed)
            print('last_result_time_element', last_result_time_element)

    @tag('fast', 'get_last_source_element')
    def test_get_last_source_element(self):
        """
        Gets the last <source> element in a Data Subset XML string.
        """
        with open(os.path.join(_XML_METADATA_FILE_DIR, 'DataSubset_Test-2023-01-01_DataCollectionTest.xml')) as xml_file:
            xml_string = xml_file.read()
            xml_string_parsed = parse_xml_string(xml_string)
            last_source_element = get_last_source_element(xml_string_parsed)
            print('last_source_element', last_source_element)

    @tag('fast', 'doi_element_is_not_present_in_xml_file', 'is_doi_element_present_in_xml_file')
    def test_doi_element_is_not_present_in_xml_file(self):
        """
        is_doi_element_present_in_xml_file() returns False for the given XML file.
        """
        with open(os.path.join(_XML_METADATA_FILE_DIR, 'DataSubset_Test-2023-01-01_DataCollectionTest.xml')) as xml_file:
            result = is_doi_element_present_in_xml_file(xml_file)
            print('result', result)

            self.assertEqual(result, False)

    @tag('fast', 'doi_element_is_present_in_xml_file', 'is_doi_element_present_in_xml_file')
    def test_doi_element_is_present_in_xml_file(self):
        """
        is_doi_element_present_in_xml_file() returns True for the given XML file.
        """
        with open(os.path.join(_XML_METADATA_FILE_DIR, 'DataSubset_Test-2023-01-01_DataCollectionTest_with_DOI.xml')) as xml_file:
            result = is_doi_element_present_in_xml_file(xml_file)
            print('result', result)

            self.assertEqual(result, True)


@tag('manual')
class DOIXMLUpdateTestCase(PyHandleSetupTestCase):
    @tag('fast', 'get_doi_xml_string_from_metadata_xml_string')
    def test_get_doi_xml_string_from_metadata_xml_string(self):
        """
        Returns the first <doi> element from an XML string.
        """
        with open(os.path.join(_XML_METADATA_FILE_DIR, 'DataSubset_Test-2023-01-01_DataCollectionTest_with_DOI.xml')) as xml_file:
            xml_string = xml_file.read()
            doi_element_string = get_doi_xml_string_from_metadata_xml_string(xml_string)
            print('doi_element_string', doi_element_string)

            self.assertIsInstance(doi_element_string, str)
            self.assertEqual(doi_element_string[:4], '<doi')

        print('Passed get_doi_xml_string_from_metadata_xml_string() test.')

    @tag('fast', 'remove_doi_element_from_metadata_xml_string')
    def test_remove_doi_element_from_metadata_xml_string(self):
        """
        Removes all <doi> elements from an XML string.
        """
        with open(os.path.join(_XML_METADATA_FILE_DIR, 'DataSubset_Test-2023-01-01_DataCollectionTest_with_DOI.xml')) as xml_file:
            xml_string = xml_file.read()
            updated_xml_string = remove_doi_element_from_metadata_xml_string(xml_string)
            print('updated_xml_string', updated_xml_string)

            self.assertIsInstance(updated_xml_string, str)
            self.assertLess(len(updated_xml_string), len(xml_string))

        print('Passed remove_doi_element_from_metadata_xml_string() test.')

    @tag('fast', 'replace_doi_element_from_metadata_xml_string')
    def test_replace_doi_element_from_metadata_xml_string(self):
        """
        Replaces all <doi> elements with a new single DOI element.
        """
        with open(os.path.join(_XML_METADATA_FILE_DIR, 'DataSubset_Test-2023-01-01_DataCollectionTest_with_DOI.xml')) as xml_file:
            xml_string = xml_file.read()
            doiless_xml_string = remove_doi_element_from_metadata_xml_string(xml_string)
            self._create_and_register_handle_for_test()
            doi_dict = initialise_default_doi_kernel_metadata_dict()
            doi_xml_string = create_doi_xml_string_from_dict(doi_dict)
            updated_xml_string = add_doi_xml_string_to_metadata_xml_string(doiless_xml_string, doi_xml_string)
            print('updated_xml_string', updated_xml_string)

        print('Passed replace_doi_element_from_metadata_xml_string() test.')


@tag('manual')
class PrincipalAgentTestCase(TestCase):
    @tag('fast', 'get_first_related_party_name_from_data_collection')
    def test_get_first_related_party_name_from_data_collection(self):
        """
        Returns the name of the organisation (or individual if organisation is
        not found) responsible for the data collection.
        """
        data_collection = None
        with open(os.path.join(_XML_METADATA_FILE_DIR, 'DataCollection_Test.xml')) as xml_file:
            data_collection = DataCollection.objects.create_from_xml_string(xml_file.read(), SAMPLE_INSTITUTION_ID, SAMPLE_USER_ID)
        principal_agent_name = get_first_related_party_name_from_data_collection(data_collection)
        print('principal_agent_name', principal_agent_name)