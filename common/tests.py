from django.test import TestCase

from .models import (
    AcquisitionCapabilities,
    ComputationCapabilities,
    Instrument,
    Organisation,
)

from common.test_setup import (
    register_acquisition_capabilities_for_test,
    register_acquisition_for_test,
    register_catalogue_data_subset_for_test,
    register_catalogue_entry_for_test,
    register_catalogue_for_test,
    register_computation_capabilities_for_test,
    register_computation_capabilities_2_for_test,
    register_computation_for_test,
    register_data_collection_for_test,
    register_individual_for_test,
    register_instrument_for_test,
    register_operation_for_test,
    register_organisation_for_test,
    register_platform_for_test,
    register_platform_with_child_platforms_for_test,
    register_process_for_test,
    register_project_for_test,
)
from common.test_xml_files import (
    ACQUISITION_CAPABILITIES_METADATA_XML,
    COMPUTATION_CAPABILITIES_METADATA_XML,
    COMPUTATION_CAPABILITIES_2_METADATA_XML,
    COMPUTATION_CAPABILITIES_3_METADATA_XML,
    COMPUTATION_CAPABILITIES_4_METADATA_XML,
    COMPUTATION_CAPABILITIES_4a_METADATA_XML,
    INSTRUMENT_METADATA_XML,
    ORGANISATION_METADATA_XML,
)


# For tests where ownership data is required
SAMPLE_USER_ID        = 'johndoe@example.com'
SAMPLE_INSTITUTION_ID = 'John Doe Institution'

# Create your tests here.
class ScientificMetadataPropertiesTestCase(TestCase):
    def test_metadata_registration_has_metadata_server_url(self):
        """
        Test that a scientific metadata registration
        has a metadata server URL.
        """
        xml_file = ORGANISATION_METADATA_XML
        xml_file.seek(0)
        xml_string = xml_file.read()
        organisation = Organisation.objects.create_from_xml_string(xml_string, SAMPLE_INSTITUTION_ID, SAMPLE_USER_ID)
        try:
            metadata_server_url = organisation.metadata_server_url
            print('metadata_server_url', metadata_server_url)
        except BaseException:
            print('Unable to get metadata server URL from registration.')


class ImmediateMetadataDependentsTestCase(TestCase):
    def setUp(self) -> None:
        self.organisation = register_organisation_for_test()
        self.individual = register_individual_for_test()
        self.project = register_project_for_test()
        self.platform = register_platform_for_test()
        self.operation = register_operation_for_test()
        self.instrument = register_instrument_for_test()
        self.acquisition_capabilities = register_acquisition_capabilities_for_test()
        self.acquisition = register_acquisition_for_test()
        self.computation_capabilities = register_computation_capabilities_for_test()
        self.computation = register_computation_for_test()
        self.process = register_process_for_test()
        self.data_collection = register_data_collection_for_test()
        self.catalogue = register_catalogue_for_test()
        self.catalogue_entry = register_catalogue_entry_for_test()
        self.catalogue_data_subset = register_catalogue_data_subset_for_test()
        return super().setUp()

    def test_organisation_immediate_metadata_dependents_are_correct(self):
        """
        Metadata registrations referring to an organisation
        metadata URL are correctly identified.
        """
        imds = self.organisation._immediate_metadata_dependents
        self.assertIn(self.individual, imds)
        self.assertIn(self.project, imds)
        self.assertIn(self.platform, imds)
        self.assertIn(self.operation, imds)
        self.assertIn(self.instrument, imds)
        self.assertIn(self.data_collection, imds)
        self.assertEqual(len(imds), 6)

    def test_individual_immediate_metadata_dependents_are_correct(self):
        """
        Metadata registrations referring to an individual
        metadata URL are correctly identified.
        """
        imds = self.individual._immediate_metadata_dependents
        self.assertIn(self.project, imds)
        self.assertIn(self.platform, imds)
        self.assertIn(self.operation, imds)
        self.assertIn(self.instrument, imds)
        self.assertIn(self.data_collection, imds)
        self.assertEqual(len(imds), 5)

    def test_project_immediate_metadata_dependents_are_correct(self):
        """
        Metadata registrations referring to a project
        metadata URL are correctly identified.
        """
        imds = self.project._immediate_metadata_dependents
        self.assertIn(self.data_collection, imds)
        self.assertEqual(len(imds), 1)

    def test_platform_immediate_metadata_dependents_are_correct(self):
        """
        Metadata registrations referring to a platform
        metadata URL are correctly identified.
        """
        imds = self.platform._immediate_metadata_dependents
        self.assertIn(self.operation, imds)
        self.assertIn(self.acquisition, imds)
        self.assertIn(self.computation, imds)
        self.assertEqual(len(imds), 3)

    def test_operation_immediate_metadata_dependents_are_correct(self):
        """
        Metadata registrations referring to an operation
        metadata URL are correctly identified.
        """
        imds = self.operation._immediate_metadata_dependents
        self.assertEqual(len(imds), 0)

    def test_instrument_immediate_metadata_dependents_are_correct(self):
        """
        Metadata registrations referring to an instrument
        metadata URL are correctly identified.
        """
        imds = self.instrument._immediate_metadata_dependents
        self.assertIn(self.acquisition_capabilities, imds)
        self.assertEqual(len(imds), 1)

    def test_acquisition_capabilities_immediate_metadata_dependents_are_correct(self):
        """
        Metadata registrations referring to an acquisition
        capabilities metadata URL are correctly identified.
        """
        imds = self.acquisition_capabilities._immediate_metadata_dependents
        self.assertIn(self.acquisition, imds)
        self.assertEqual(len(imds), 1)

    def test_acquisition_immediate_metadata_dependents_are_correct(self):
        """
        Metadata registrations referring to an acquisition
        metadata URL are correctly identified.
        """
        imds = self.acquisition._immediate_metadata_dependents
        self.assertIn(self.process, imds)
        self.assertEqual(len(imds), 1)

    def test_computation_capabilities_immediate_metadata_dependents_are_correct(self):
        """
        Metadata registrations referring to a computation
        capabilities metadata URL are correctly identified.
        """
        imds = self.computation_capabilities._immediate_metadata_dependents
        self.assertIn(self.computation, imds)
        self.assertEqual(len(imds), 1)

    def test_computation_immediate_metadata_dependents_are_correct(self):
        """
        Metadata registrations referring to a computation
        metadata URL are correctly identified.
        """
        imds = self.computation._immediate_metadata_dependents
        self.assertIn(self.process, imds)
        self.assertEqual(len(imds), 1)

    def test_process_immediate_metadata_dependents_are_correct(self):
        """
        Metadata registrations referring to a process
        metadata URL are correctly identified.
        """
        imds = self.process._immediate_metadata_dependents
        self.assertIn(self.data_collection, imds)
        self.assertEqual(len(imds), 1)

    def test_data_collection_immediate_metadata_dependents_are_correct(self):
        """
        Metadata registrations referring to a data
        collection metadata URL are correctly identified.
        """
        imds = self.data_collection._immediate_metadata_dependents
        self.assertIn(self.catalogue_data_subset, imds)
        self.assertEqual(len(imds), 1)

    def test_catalogue_immediate_metadata_dependents_are_correct(self):
        """
        Metadata registrations referring to a catalogue
        metadata URL are correctly identified.
        """
        imds = self.catalogue._immediate_metadata_dependents
        self.assertIn(self.catalogue_entry, imds)
        self.assertEqual(len(imds), 1)

    def test_catalogue_entry_immediate_metadata_dependents_are_correct(self):
        """
        Metadata registrations referring to a catalogue
        entry metadata URL are correctly identified.
        """
        imds = self.catalogue_entry._immediate_metadata_dependents
        self.assertIn(self.catalogue_data_subset, imds)
        self.assertEqual(len(imds), 1)

    def test_catalogue_data_subset_immediate_metadata_dependents_are_correct(self):
        """
        Metadata registrations referring to a catalogue
        data subset metadata URL are correctly identified.
        """
        imds = self.catalogue_data_subset._immediate_metadata_dependents
        self.assertEqual(len(imds), 0)

    def test_child_computation_references_are_included(self):
        """
        Check that registrations with child computation
        references are included in the list of immediate
        metadata dependents.
        """
        computation_capabilities_2 = register_computation_capabilities_2_for_test()
        imds = self.computation_capabilities._immediate_metadata_dependents
        self.assertIn(computation_capabilities_2, imds)


    def test_child_platform_references_are_included(self):
        """
        Check that registrations with child platform
        references are included in the list of immediate
        metadata dependents.
        """
        platform_with_child_platforms = register_platform_with_child_platforms_for_test()
        imds = self.platform._immediate_metadata_dependents
        self.assertIn(platform_with_child_platforms, imds)


class AcquisitionCapabilitiesQuerySetSearchTestCase(TestCase):
    def setUp(self):
        acquisition_capabilities_xml_file = ACQUISITION_CAPABILITIES_METADATA_XML
        acquisition_capabilities_xml_file.seek(0)
        acquisition_capabilities_xml_string = acquisition_capabilities_xml_file.read()
        AcquisitionCapabilities.objects.create_from_xml_string(acquisition_capabilities_xml_string, SAMPLE_INSTITUTION_ID, SAMPLE_USER_ID)
        
        instrument_xml_file = INSTRUMENT_METADATA_XML
        instrument_xml_file.seek(0)
        instrument_xml_string = instrument_xml_file.read()
        Instrument.objects.create_from_xml_string(instrument_xml_string, SAMPLE_INSTITUTION_ID, SAMPLE_USER_ID)

        return super().setUp()

    def test_correct_registrations_retrieved_for_search(self):
        """
        Verify the subset of Acquisition Capabilities retrieved
        for the ontology-based search based on some Instrument
        URLs and Observed Properties.
        """
        # Input data
        instrument_urls = ['https://metadata.pithia.eu/resources/2.2/instrument/test/Instrument_Test']
        observed_property_urls = [
            'https://metadata.pithia.eu/ontology/2.2/observedProperty/EM-Wave_ElectricFieldStrength',
            'https://metadata.pithia.eu/ontology/2.2/observedProperty/EM-Wave_Polarization',
            'https://metadata.pithia.eu/ontology/2.2/observedProperty/EM-Wave_DopplerFrequencyShift',
        ]
        acquisition_capability_sets = AcquisitionCapabilities.objects.for_search(instrument_urls, observed_property_urls)
        self.assertTrue(len(acquisition_capability_sets) > 0)

    def test_correct_registrations_retrieved_with_bad_input_data(self):
        """
        Verify that the subset of Acquisition Capabilities retrieved
        for the ontology-based search returns the correct results.
        """
        instrument_urls = ['https://metadata.pithia.eu/resources/2.2/instrument/test/Instrument_Test']
        bad_observed_property_urls = [
            'https://metadata.pithia.eu/ontology/2.2/observedProperty/bad',
        ]
        acquisition_capability_sets_empty = AcquisitionCapabilities.objects.for_search(instrument_urls, bad_observed_property_urls)
        self.assertEqual(len(acquisition_capability_sets_empty), 0)

    def test_correct_registrations_retrieved_with_instrument_urls_and_no_observed_properties(self):
        """
        Verify that the subset of Acquisition Capabilities retrieved
        for the ontology-based search returns the correct results.
        """
        instrument_urls = ['https://metadata.pithia.eu/resources/2.2/instrument/test/Instrument_Test']
        observed_property_urls = []
        acquisition_capability_sets = AcquisitionCapabilities.objects.for_search(instrument_urls, observed_property_urls)
        self.assertEqual(len(acquisition_capability_sets), 1)


class ComputationCapabilitiesQuerySetTestCase(TestCase):
    def test_all_computation_capability_set_referers(self):
        """
        Recursively retrieve a list of Computation Capabilities
        registrations that reference other Computation Capabilities
        registrations, starting from a given Computation Capabilities
        registration.
        """
        # Register the Computation Capabilities XML files
        computation_capabilities_file_1 = COMPUTATION_CAPABILITIES_METADATA_XML
        computation_capabilities_file_1.seek(0)
        test_computation_capability_set = ComputationCapabilities.objects.create_from_xml_string(computation_capabilities_file_1.read(), SAMPLE_INSTITUTION_ID, SAMPLE_USER_ID)

        # Each file in this list references the file
        # preceding it (e.g., CC4a references CC4,
        # CC4 references CC3, and so on) so the number
        # of resultant referers should be equal to the
        # number of files in this list.
        computation_capabilities_referer_files = [
            COMPUTATION_CAPABILITIES_2_METADATA_XML,
            COMPUTATION_CAPABILITIES_3_METADATA_XML,
            COMPUTATION_CAPABILITIES_4_METADATA_XML,
            COMPUTATION_CAPABILITIES_4a_METADATA_XML,
        ]
        for xml_file in computation_capabilities_referer_files:
            xml_file.seek(0)
            ComputationCapabilities.objects.create_from_xml_string(xml_file.read(), SAMPLE_INSTITUTION_ID, SAMPLE_USER_ID)
        
        # Execute all_computation_capability_set_referers()
        ccs_referers = ComputationCapabilities.objects.all_computation_capability_set_referers(test_computation_capability_set)
        print('ccs_referers', [r.localid for r in ccs_referers])
        print('len(ccs_referers)', len(ccs_referers))
        self.assertEqual(len(ccs_referers), len(computation_capabilities_referer_files))


class ComputationCapabilitiesQuerySetSearchTestCase(TestCase):
    def setUp(self):
        # Register the Computation Capabilities XML files
        computation_capabilities_file_1 = COMPUTATION_CAPABILITIES_METADATA_XML
        computation_capabilities_file_1.seek(0)
        ComputationCapabilities.objects.create_from_xml_string(computation_capabilities_file_1.read(), SAMPLE_INSTITUTION_ID, SAMPLE_USER_ID)

        computation_capabilities_file_2 = COMPUTATION_CAPABILITIES_2_METADATA_XML
        computation_capabilities_file_2.seek(0)
        ComputationCapabilities.objects.create_from_xml_string(computation_capabilities_file_2.read(), SAMPLE_INSTITUTION_ID, SAMPLE_USER_ID)

        computation_capabilities_file_3 = COMPUTATION_CAPABILITIES_3_METADATA_XML
        computation_capabilities_file_3.seek(0)
        ComputationCapabilities.objects.create_from_xml_string(computation_capabilities_file_3.read(), SAMPLE_INSTITUTION_ID, SAMPLE_USER_ID)

        computation_capabilities_file_4 = COMPUTATION_CAPABILITIES_4_METADATA_XML
        computation_capabilities_file_4.seek(0)
        ComputationCapabilities.objects.create_from_xml_string(computation_capabilities_file_4.read(), SAMPLE_INSTITUTION_ID, SAMPLE_USER_ID)

        computation_capabilities_file_4a = COMPUTATION_CAPABILITIES_4a_METADATA_XML
        computation_capabilities_file_4a.seek(0)
        ComputationCapabilities.objects.create_from_xml_string(computation_capabilities_file_4a.read(), SAMPLE_INSTITUTION_ID, SAMPLE_USER_ID)
        
        return super().setUp()

    def test_correct_registrations_are_returned_for_search(self):
        """
        ComputationCapabilities.objects.for_search() returns
        a QuerySet of Computation Capabilities registrations.
        """
        computation_type_urls = [
            'https://metadata.pithia.eu/ontology/2.2/computationType/IonogramScaling_Manual',
        ]

        search_results = ComputationCapabilities.objects.for_search(computation_type_urls, [])
        # The number of results is the (number of registrations matching) + (number of referers).
        # In this case, it is (1) + (4).
        self.assertEqual(len(search_results), 5)

    def test_referers_for_search_works_correctly(self):
        computation_type_urls_2 = [
            'https://metadata.pithia.eu/ontology/2.2/computationType/Test',
        ]

        # Only CC_4a should match here, which has no referers.
        search_results_2 = ComputationCapabilities.objects.for_search(computation_type_urls_2, [])
        self.assertEqual(len(search_results_2), 1)
