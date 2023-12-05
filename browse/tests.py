from django.test import (
    SimpleTestCase,
    TestCase,
)

from .services import (
    map_ontology_server_urls_to_browse_urls,
    map_metadata_server_urls_to_browse_urls,
)

from common.test_setup import (
    register_catalogue_data_subset_for_test,
    register_individual_for_test,
    register_instrument_for_test,
    register_organisation_for_test,
    register_project_for_test,
    register_process_for_test,
)

# Create your tests here.
class BulkOntologyUrlMappingTestCase(SimpleTestCase):
    def test_bulk_ontology_url_mapping_with_real_and_fake_urls(self):
        """
        Returns a list of dicts containing a mapping of the original
        ontology URL to the corresponding page URL in the eSC.
        """
        ontology_server_urls = [
            'https://metadata.pithia.eu/ontology/2.2/featureOfInterest/Earth_Ionosphere_F-Region_Bottomside',
            'https://metadata.pithia.eu/ontology/2.2/featureOfInterest/Earth_Ionosphere_E-Region',
            'https://metadata.pithia.eu/ontology/2.2/instrumentType/VerticalSounder',
            'https://metadata.pithia.eu/ontology/2.2/relatedPartyRole/PointOfContact',
            'https://metadata.pithia.eu/ontology/2.2/test/test',
        ]
        converted_ontology_server_urls = map_ontology_server_urls_to_browse_urls(ontology_server_urls)
        self.assertTrue(any(mapping['original_server_url'] == mapping['converted_url'] for mapping in converted_ontology_server_urls))


class BulkMetadataUrlMappingTestCase(TestCase):
    def test_bulk_metadata_url_mapping_with_real_and_fake_urls(self):
        """
        Returns a list of dicts containing a mapping of the original
        metadata URL to the corresponding page URL in the eSC.
        """
        # Register the test metadata first.
        register_organisation_for_test()
        register_individual_for_test()
        register_project_for_test()
        register_process_for_test()

        resource_server_urls = [
            'https://metadata.pithia.eu/resources/2.2/process/test/CompositeProcess_Test',
            'https://metadata.pithia.eu/resources/2.2/project/test/Project_Test',
            'https://metadata.pithia.eu/resources/2.2/individual/test/Individual_Test',
            'https://metadata.pithia.eu/resources/2.2/organisation/test/Organisation_Test',
            'https://metadata.pithia.eu/ontology/2.2/test/test',
        ]
        converted_resource_server_urls = map_metadata_server_urls_to_browse_urls(resource_server_urls)
        self.assertNotEqual(converted_resource_server_urls[0]['original_server_url'], converted_resource_server_urls[0]['converted_url'])
        self.assertNotEqual(converted_resource_server_urls[1]['original_server_url'], converted_resource_server_urls[1]['converted_url'])
        self.assertNotEqual(converted_resource_server_urls[2]['original_server_url'], converted_resource_server_urls[2]['converted_url'])
        self.assertNotEqual(converted_resource_server_urls[3]['original_server_url'], converted_resource_server_urls[3]['converted_url'])
        self.assertEqual(converted_resource_server_urls[4]['original_server_url'], converted_resource_server_urls[4]['converted_url'])

    def test_bulk_metadata_url_mapping_with_mix_of_valid_url_types(self):
        """
        Returns a list of dicts containing a successful mapping
        of all the metadata URLs for this test.
        """
        # Register the test metadata first.
        register_instrument_for_test()
        register_process_for_test()
        register_catalogue_data_subset_for_test()

        # Test data
        instrument_resource_url_with_op_mode = 'https://metadata.pithia.eu/resources/2.2/instrument/test/Instrument_Test#instrumentoperationalmode1'
        process_metadata_url = 'https://metadata.pithia.eu/resources/2.2/process/test/CompositeProcess_Test'
        catalogue_related_resource_url = 'https://metadata.pithia.eu/resources/2.2/catalogue/test/Test/DataSubset_Test-2023-01-01_DataCollectionTest'

        # Operational mode URL
        converted_instrument_resource_url_with_op_mode = map_metadata_server_urls_to_browse_urls([instrument_resource_url_with_op_mode])[0]
        # Data Collection-related metadata URL
        converted_process_metadata_url = map_metadata_server_urls_to_browse_urls([process_metadata_url])[0]
        # Catalogue-related metadata URL
        converted_catalogue_related_resource_url = map_metadata_server_urls_to_browse_urls([catalogue_related_resource_url])[0]

        # converted_instrument_resource_url_with_op_mode
        self.assertNotEqual(converted_instrument_resource_url_with_op_mode['original_server_url'], '')
        self.assertNotEqual(converted_instrument_resource_url_with_op_mode['converted_url'], '')
        self.assertNotEqual(converted_instrument_resource_url_with_op_mode['converted_url_text'], '')
        self.assertNotEqual(converted_instrument_resource_url_with_op_mode['original_server_url'], converted_instrument_resource_url_with_op_mode['converted_url'])

        # converted_process_metadata_url
        self.assertNotEqual(converted_process_metadata_url['original_server_url'], '')
        self.assertNotEqual(converted_process_metadata_url['converted_url'], '')
        self.assertNotEqual(converted_process_metadata_url['converted_url_text'], '')
        self.assertNotEqual(converted_process_metadata_url['original_server_url'], converted_process_metadata_url['converted_url'])

        # converted_catalogue_related_resource_url
        self.assertNotEqual(converted_catalogue_related_resource_url['original_server_url'], '')
        self.assertNotEqual(converted_catalogue_related_resource_url['converted_url'], '')
        self.assertNotEqual(converted_catalogue_related_resource_url['converted_url_text'], '')
        self.assertNotEqual(converted_catalogue_related_resource_url['original_server_url'], converted_catalogue_related_resource_url['converted_url'])