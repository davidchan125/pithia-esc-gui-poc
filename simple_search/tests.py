import os
from django.test import TestCase

from .services import (
    filter_metadata_registrations_by_ontology_urls_default,
    filter_metadata_registrations_by_ontology_urls_exact,
    filter_metadata_registrations_by_name_exact,
    filter_metadata_registrations_by_text_nodes_default,
    filter_metadata_registrations_by_text_nodes_exact,
    find_data_collections_for_simple_search,
    get_and_process_text_nodes_of_ontology_url,
    get_ontology_component_name_from_ontology_url,
    get_ontology_urls_from_registration,
    get_rdfs_from_ontology_urls,
)

from common import models
from pithiaesc.settings import BASE_DIR


_XML_METADATA_FILE_DIR = os.path.join(BASE_DIR, 'common', 'test_files', 'xml_metadata_files')

# Create your tests here.
class SimpleSearchTestCase(TestCase):
    def setUp(self) -> None:
        with open(os.path.join(_XML_METADATA_FILE_DIR, 'Organisation_Test.xml')) as xml_file:
            self.organisation = models.Organisation.objects.create_from_xml_string(xml_file.read())
            
        with open(os.path.join(_XML_METADATA_FILE_DIR, 'Individual_Test.xml')) as xml_file:
            self.individual = models.Individual.objects.create_from_xml_string(xml_file.read())

        with open(os.path.join(_XML_METADATA_FILE_DIR, 'Project_Test.xml')) as xml_file:
            self.project = models.Project.objects.create_from_xml_string(xml_file.read())

        with open(os.path.join(_XML_METADATA_FILE_DIR, 'Platform_Test.xml')) as xml_file:
            self.platform = models.Platform.objects.create_from_xml_string(xml_file.read())

        with open(os.path.join(_XML_METADATA_FILE_DIR, 'Operation_Test.xml')) as xml_file:
            self.operation = models.Operation.objects.create_from_xml_string(xml_file.read())

        with open(os.path.join(_XML_METADATA_FILE_DIR, 'Instrument_Test.xml')) as xml_file:
            self.instrument = models.Instrument.objects.create_from_xml_string(xml_file.read())

        with open(os.path.join(_XML_METADATA_FILE_DIR, 'AcquisitionCapabilities_Test.xml')) as xml_file:
            self.acquisition_capabilities = models.AcquisitionCapabilities.objects.create_from_xml_string(xml_file.read())

        with open(os.path.join(_XML_METADATA_FILE_DIR, 'Acquisition_Test.xml')) as xml_file:
            self.acquisition = models.Acquisition.objects.create_from_xml_string(xml_file.read())

        with open(os.path.join(_XML_METADATA_FILE_DIR, 'Computation_Test.xml')) as xml_file:
            self.computation_capabilities = models.ComputationCapabilities.objects.create_from_xml_string(xml_file.read())

        with open(os.path.join(_XML_METADATA_FILE_DIR, 'ComputationCapabilities_Test.xml')) as xml_file:
            self.computation = models.Computation.objects.create_from_xml_string(xml_file.read())

        with open(os.path.join(_XML_METADATA_FILE_DIR, 'CompositeProcess_Test.xml')) as xml_file:
            self.process = models.Process.objects.create_from_xml_string(xml_file.read())
            
        with open(os.path.join(_XML_METADATA_FILE_DIR, 'DataCollection_Test.xml')) as xml_file:
            self.data_collection = models.DataCollection.objects.create_from_xml_string(xml_file.read())

        return super().setUp()

    
    def test_filter_metadata_registrations_by_text_nodes_default(self):
        """
        Searches only the given Model's registrations and returns
        registrations matching the query.
        """
        test_organisations = models.Organisation.objects.all()
        test_data_collections = models.DataCollection.objects.all()

        organisations_1 = filter_metadata_registrations_by_text_nodes_default(['lorem'], test_organisations)
        data_collections_1 = filter_metadata_registrations_by_text_nodes_default(['lorem'], test_data_collections)
        data_collections_2 = filter_metadata_registrations_by_text_nodes_default(['lorem', 'laborum'], test_data_collections)
        data_collections_3 = filter_metadata_registrations_by_text_nodes_default(['lorem', 'didbase'], test_data_collections)
        data_collections_4 = filter_metadata_registrations_by_text_nodes_default(['lorem', 'didbase', 'xyz'], test_data_collections)
        data_collections_5 = filter_metadata_registrations_by_text_nodes_default(['\\n'], test_data_collections)
        data_collections_6 = filter_metadata_registrations_by_text_nodes_default([''], test_data_collections)
        data_collections_7 = filter_metadata_registrations_by_text_nodes_default(['\\n\\n\\n'], test_data_collections)
        data_collections_8 = filter_metadata_registrations_by_text_nodes_default(['\\n', '\\n', '\\n'], test_data_collections)
        data_collections_9 = filter_metadata_registrations_by_text_nodes_default(['\\n', '\\n', 'DataCollection', '\\n'], test_data_collections)

        self.assertEqual(len(organisations_1), 1)
        self.assertEqual(len(data_collections_1), 1)
        self.assertEqual(len(data_collections_2), 1)
        self.assertEqual(len(data_collections_3), 0)
        self.assertEqual(len(data_collections_4), 0)
        self.assertEqual(len(data_collections_5), 0)
        self.assertEqual(len(data_collections_6), 1)
        self.assertEqual(len(data_collections_7), 0)
        self.assertEqual(len(data_collections_8), 0)
        self.assertEqual(len(data_collections_9), 0)
        

    def test_find_registrations_matching_query_exactly(self):
        """
        Searches on the given Model's registrations and returns
        registrations matching the query exactly.
        """
        test_data_collections = models.DataCollection.objects.all()

        data_collections_1 = filter_metadata_registrations_by_text_nodes_exact('Lorem', test_data_collections)
        data_collections_2 = filter_metadata_registrations_by_text_nodes_exact('lorem', test_data_collections)
        data_collections_3 = filter_metadata_registrations_by_text_nodes_exact('Lorem  ', test_data_collections)
        data_collections_4 = filter_metadata_registrations_by_text_nodes_exact('Lorem ', test_data_collections)
        data_collections_5 = filter_metadata_registrations_by_text_nodes_exact('giro . uml . edu / didbase /', test_data_collections)
        data_collections_6 = filter_metadata_registrations_by_text_nodes_exact('giro.uml.edu/didbase/', test_data_collections)

        print('len(data_collections_1)', len(data_collections_1))
        print('len(data_collections_2)', len(data_collections_2))
        print('len(data_collections_3)', len(data_collections_3))
        print('len(data_collections_4)', len(data_collections_4))
        print('len(data_collections_5)', len(data_collections_5))
        print('len(data_collections_6)', len(data_collections_6))

        self.assertEqual(len(data_collections_1), 1)
        self.assertEqual(len(data_collections_2), 0)
        self.assertEqual(len(data_collections_3), 0)
        self.assertEqual(len(data_collections_4), 1)
        self.assertEqual(len(data_collections_5), 0)
        self.assertEqual(len(data_collections_6), 1)


    def test_for_simple_search(self):
        """
        Performs a simple search returning Data Collections matching
        the query.
        """
        # Disable "using" parameter in managers.py before running test
        # Case-insensitive match
        data_collections_1 = find_data_collections_for_simple_search('lorem')

        # Partial case-insensitive match
        data_collections_2 = find_data_collections_for_simple_search('lor')

        # No match
        data_collections_3 = find_data_collections_for_simple_search('xyz')

        # (Partially) matching ontology URLs directly shouldn't work
        data_collections_4 = find_data_collections_for_simple_search('image-png')

        # Multiple matches across different elements shouldn't work.
        data_collections_5 = find_data_collections_for_simple_search('Organisation_Test 123')
        data_collections_5a = find_data_collections_for_simple_search('DataCollection_Test 00z')

        # Multiple non-consecutive matches within the same element should work.
        data_collections_6 = find_data_collections_for_simple_search('123 Suite')
        # Unordered text here as well
        data_collections_6a = find_data_collections_for_simple_search('28T15 2022')

        # Partial match
        data_collections_7 = find_data_collections_for_simple_search('Da')

        # Shouldn't match '\n'
        data_collections_8 = find_data_collections_for_simple_search('\n')

        # (Partially) matching a property corresponding to an ontology URL
        # should work
        data_collections_9 = find_data_collections_for_simple_search('image/png')

        print('len(data_collections_1)', len(data_collections_1))
        print('len(data_collections_2)', len(data_collections_2))
        print('len(data_collections_3)', len(data_collections_3))
        print('len(data_collections_4)', len(data_collections_4))
        print('len(data_collections_5)', len(data_collections_5))
        print('len(data_collections_5a)', len(data_collections_5a))
        print('len(data_collections_6)', len(data_collections_6))
        print('len(data_collections_6a)', len(data_collections_6a))
        print('len(data_collections_7)', len(data_collections_7))
        print('len(data_collections_8)', len(data_collections_8))
        print('len(data_collections_9)', len(data_collections_9))

        self.assertEqual(len(data_collections_1), 1)
        self.assertEqual(len(data_collections_2), 1)
        self.assertEqual(len(data_collections_3), 1)
        self.assertEqual(len(data_collections_4), 0)
        self.assertEqual(len(data_collections_5), 0)
        self.assertEqual(len(data_collections_5a), 0)
        self.assertEqual(len(data_collections_6), 1)
        self.assertEqual(len(data_collections_6a), 1)
        self.assertEqual(len(data_collections_7), 1)
        self.assertEqual(len(data_collections_8), 0)
        self.assertEqual(len(data_collections_9), 1)
        
    def test_get_ontology_urls_from_registration(self):
        """
        Find and return in a list all ontology URLs from a
        registration.
        """
        ontology_urls = get_ontology_urls_from_registration(self.data_collection)

        print('ontology_urls', ontology_urls)
        print('len(ontology_urls)', len(ontology_urls))

        self.assertGreaterEqual(len(ontology_urls), 1)

    def test_get_and_process_text_nodes_of_ontology_url(self):
        """
        Returns a list of text properties of an ontology
        node corresponding with a given ontology URL.
        """
        ontology_url = 'https://metadata.pithia.eu/ontology/2.2/resultDataFormat/image-png'

        ontology_rdfs = get_rdfs_from_ontology_urls([
            ontology_url,
        ])

        ontology_url_text_node_strings = get_and_process_text_nodes_of_ontology_url(
            ontology_url,
            ontology_rdfs[get_ontology_component_name_from_ontology_url(ontology_url)]
        )

        for tns in ontology_url_text_node_strings:
            self.assertTrue(type(tns) == str)

    def test_organisations_for_simple_search(self):
        """
        Returns a queryset of organisations matching
        a simple search query.
        """
        # Name matches
        organisations_1 = models.Organisation.objects.for_simple_search(['Organisation', 'Test'])
        # localID shouldn't be searched
        organisations_2 = models.Organisation.objects.for_simple_search(['Organisation_Test'])
        # Description shouldn't be searched
        organisations_3 = models.Organisation.objects.for_simple_search(['Lorem', 'ipsum'])
        # Check that text not in the metadata doesn't return any results
        organisations_4 = models.Organisation.objects.for_simple_search(['xyz'])
        # Search is case-insensitive
        organisations_5 = models.Organisation.objects.for_simple_search(['organisation', 'test'])
        # Name partially matches
        organisations_6 = models.Organisation.objects.for_simple_search(['organisation'])
        # Test with unexpected input (string)
        organisations_7 = models.Organisation.objects.for_simple_search('organisation')

        self.assertEqual(len(organisations_1), 1)
        self.assertEqual(len(organisations_2), 0)
        self.assertEqual(len(organisations_3), 0)
        self.assertEqual(len(organisations_4), 0)
        self.assertEqual(len(organisations_5), 1)
        self.assertEqual(len(organisations_6), 1)
        self.assertEqual(len(organisations_7), 1)

    def test_filter_metadata_registrations_by_name_exact(self):
        """
        Returns a list of metadata registrations with
        names containing (case-sensitive) a given query.
        """
        test_organisations = list(models.Organisation.objects.all())
        # Name matches
        organisations_1 = filter_metadata_registrations_by_name_exact('Organisation Test', test_organisations)
        # localID shouldn't be searched
        organisations_2 = filter_metadata_registrations_by_name_exact('Organisation_Test', test_organisations)
        # Description shouldn't be searched
        organisations_3 = filter_metadata_registrations_by_name_exact('Lorem ipsum', test_organisations)
        # Check that text not in the metadata doesn't return any results
        organisations_4 = filter_metadata_registrations_by_name_exact('xyz', test_organisations)
        # Search should be case-sensitive
        organisations_5 = filter_metadata_registrations_by_name_exact('organisation test', test_organisations)
        # Name should partially match
        organisations_6 = filter_metadata_registrations_by_name_exact('Organisation', test_organisations)

        self.assertEqual(len(organisations_1), 1)
        self.assertEqual(len(organisations_2), 0)
        self.assertEqual(len(organisations_3), 0)
        self.assertEqual(len(organisations_4), 0)
        self.assertEqual(len(organisations_5), 0)
        self.assertEqual(len(organisations_6), 1)