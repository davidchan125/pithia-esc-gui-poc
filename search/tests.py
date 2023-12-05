from django.test import (
    TestCase,
)

from .services import (
    find_matching_data_collections,
    get_distinct_computation_type_urls_from_data_collections,
    get_distinct_instrument_type_urls_from_data_collections,
    find_matching_data_collections,
    setup_computation_types_for_observed_property_search_form,
    setup_instrument_types_for_observed_property_search_form,
)
from .views import (
    get_registered_observed_properties,
    get_registered_features_of_interest
)

from common.models import (
    DataCollection,
)
from common.test_setup import (
    register_acquisition_capabilities_for_test,
    register_acquisition_for_test,
    register_computation_capabilities_for_test,
    register_computation_for_test,
    register_data_collection_for_test,
    register_instrument_for_test,
    register_process_for_test,
)
from ontology.utils import (
    create_dictionary_from_pithia_ontology_component,
    categorise_observed_property_dict_by_top_level_phenomenons,
    get_nested_phenomenons_in_observed_property,
)

# For tests where ownership data is required
SAMPLE_USER_ID        = 'johndoe@example.com'
SAMPLE_INSTITUTION_ID = 'John Doe Institution'


# Create your tests here.

class SearchBehaviourTestCase(TestCase):
    def setUp(self) -> None:
        register_instrument_for_test()
        register_acquisition_capabilities_for_test()
        register_acquisition_for_test()
        register_computation_capabilities_for_test()
        register_computation_for_test()
        register_process_for_test()
        register_data_collection_for_test()
        return super().setUp()

    instrument_type_urls = [
        'https://metadata.pithia.eu/ontology/2.2/instrumentType/VerticalSounder',
    ]
    computation_type_urls = [
        'https://metadata.pithia.eu/ontology/2.2/computationType/IonogramScaling_Manual',
    ]
    observed_property_urls = [
        'https://metadata.pithia.eu/ontology/2.2/observedProperty/EM-Wave_ElectricFieldStrength',
        'https://metadata.pithia.eu/ontology/2.2/observedProperty/EM-Wave_Polarization',
        'https://metadata.pithia.eu/ontology/2.2/observedProperty/EM-Wave_DopplerFrequencyShift',
        'https://metadata.pithia.eu/ontology/2.2/observedProperty/EM-Wave_Direction',
    ]
    feature_of_interest_urls = [
        'https://metadata.pithia.eu/ontology/2.2/featureOfInterest/Earth_Ionosphere_F-Region_Bottomside',
        'https://metadata.pithia.eu/ontology/2.2/featureOfInterest/Earth_Ionosphere_E-Region',
    ]

    def test_data_collections_are_found_with_instrument_types(self):
        """
        A list of data collections matching any of the
        instrument types in the list are returned.
        """
        # Register XML files
        # Pass in instrument types
        data_collections = find_matching_data_collections(feature_of_interest_urls=self.feature_of_interest_urls)
        # Pass in computation types
        # Pass in observed properties
        print('data_collections', data_collections)
        print('len(data_collections)', len(data_collections))
        self.assertGreater(len(data_collections), 0)


class SearchFormSetupTestCase(TestCase):
    # Distinct instrument/model URLs are used as part of
    # classifying which instrument types and model types
    # are registered. The registration status of each of
    # these types are displayed in the search form.
    def test_distinct_instrument_urls_are_retrieved_from_data_collections(self):
        """
        Returns a list of unique instrument type URLs
        from all registered data collections.
        """
        register_data_collection_for_test()
        data_collections = DataCollection.objects.all()
        distinct_instrument_type_urls = get_distinct_instrument_type_urls_from_data_collections(data_collections)
        print('distinct_instrument_type_urls', distinct_instrument_type_urls)
        self.assertGreater(len(distinct_instrument_type_urls), 0)
        self.assertEqual(len(distinct_instrument_type_urls), len(set(distinct_instrument_type_urls)))

    def test_distinct_model_urls_are_retrieved_from_data_collections(self):
        """
        Returns a list of unique computation type URLs
        from all registered data collections.
        """
        register_data_collection_for_test()
        data_collections = DataCollection.objects.all()
        distinct_model_urls = get_distinct_computation_type_urls_from_data_collections(data_collections)
        print('distinct_model_urls', distinct_model_urls)
        self.assertEqual(len(distinct_model_urls), 0)
        self.assertEqual(len(distinct_model_urls), len(set(distinct_model_urls)))


class ObservedPropertyCategorisationForSearchFormTestCase(TestCase):
    def test_phenomenons_are_retrieved_from_observed_property_child_terms(self):
        """
        Returns a flat list of the phenomenons of an observed property
        and the observed properties child terms.
        """
        instrument_types_grouped_by_observed_property = setup_instrument_types_for_observed_property_search_form()
        computation_types_grouped_by_observed_property = setup_computation_types_for_observed_property_search_form()
        observed_property_dict = create_dictionary_from_pithia_ontology_component(
            'observedProperty',
            instrument_types_grouped_by_observed_property=instrument_types_grouped_by_observed_property,
            computation_types_grouped_by_observed_property=computation_types_grouped_by_observed_property
        )
        first_observed_property = list(observed_property_dict.values())[0]
        phenomenons = get_nested_phenomenons_in_observed_property(first_observed_property)
        print('phenomenons', phenomenons)
        self.assertIsInstance(phenomenons, list)
    
    def test_observed_properties_are_categorised_by_top_level_phenomenons(self):
        """
        Returns a dict of observed properties where each dict
        key is a top-level phenomenon that each observed property
        corresponds to.
        """
        # The Observed Properties search form is broken up
        # into sections by headings. These headings are the
        # highest level phenomenons (e.g. Field, Particle).
        instrument_types_grouped_by_observed_property = setup_instrument_types_for_observed_property_search_form()
        computation_types_grouped_by_observed_property = setup_computation_types_for_observed_property_search_form()
        observed_property_dict = create_dictionary_from_pithia_ontology_component(
            'observedProperty',
            instrument_types_grouped_by_observed_property=instrument_types_grouped_by_observed_property,
            computation_types_grouped_by_observed_property=computation_types_grouped_by_observed_property
        )
        categorised_observed_property_dict = categorise_observed_property_dict_by_top_level_phenomenons(observed_property_dict)
        self.assertIsInstance(categorised_observed_property_dict, dict)


class ObservedPropertySearchFormSetupTestCase(TestCase):
    def test_instrument_types_are_grouped_by_observed_property(self):
        """
        Returns a dict of instrument types correctly
        grouped by their observed properties.
        """
        instrument_types_grouped_by_observed_property = setup_instrument_types_for_observed_property_search_form()
        # print('instrument_types_grouped_by_observed_property', instrument_types_grouped_by_observed_property)
        self.assertTrue(isinstance(instrument_types_grouped_by_observed_property, dict))

    def test_computation_types_are_grouped_by_observed_property(self):
        """
        Returns a dict of computation types correctly
        grouped by their observed properties.
        """
        computation_types_grouped_by_observed_property = setup_computation_types_for_observed_property_search_form()
        # print('computation_types_grouped_by_observed_property', computation_types_grouped_by_observed_property)
        self.assertTrue(isinstance(computation_types_grouped_by_observed_property, dict))


class RegisteredOntologyTermsTestCase(TestCase):
    def test_registered_observed_properties_are_correct(self):
        """
        Returns a list of observed properties mentioned
        in registered metadata.
        """
        registered_observed_properties = get_registered_observed_properties()
        # print('registered_observed_properties', registered_observed_properties)
        self.assertTrue(isinstance(registered_observed_properties, list))

    def test_registered_features_of_interest_are_correct(self):
        """
        Returns a list of features of interest mentioned
        in registered metadata.
        """
        registered_observed_property_ids = get_registered_observed_properties()
        registered_features_of_interest = get_registered_features_of_interest(registered_observed_property_ids)
        # print('registered_features_of_interest', registered_features_of_interest)
        self.assertTrue(isinstance(registered_features_of_interest, list))
