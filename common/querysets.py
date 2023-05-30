from django.db import models
from django.db.models import Q

from .core import *

class OrganisationQuerySet(models.QuerySet, AbstractOrganisationDatabaseQueries):
    pass

class IndividualQuerySet(models.QuerySet, AbstractIndividualDatabaseQueries):
    pass

class ProjectQuerySet(models.QuerySet, AbstractProjectDatabaseQueries):
    pass

class PlatformQuerySet(models.QuerySet, AbstractPlatformDatabaseQueries):
    pass

class OperationQuerySet(models.QuerySet, AbstractOperationDatabaseQueries):
    pass

class InstrumentQuerySet(models.QuerySet, AbstractInstrumentDatabaseQueries):
    def referencing_instrument_type_urls(self, instrument_type_urls: list):
        query = Q()
        for url in instrument_type_urls:
            query |= Q(**{'json__type__@xlink:href__contains': url})
        return self.filter(query)

    def for_search(self, instrument_type_urls: list):
        return self.referencing_instrument_type_urls(instrument_type_urls)

class AcquisitionCapabilitiesQuerySet(models.QuerySet, AbstractAcquisitionCapabilitiesDatabaseQueries):
    def referencing_instrument_urls(self, instrument_urls: list):
        query = Q()
        for url in instrument_urls:
            query |= Q(**{'json__instrumentModePair__InstrumentOperationalModePair__instrument__@xlink:href': url})
        return self.filter(query)

    def referencing_observed_property_urls(self, observed_property_urls: list):
        query = Q()
        for url in observed_property_urls:
            query |= Q(**{'json__capabilities__processCapability__contains': [{'observedProperty': {'@xlink:href': url}}]})
        return self.filter(query)

    def for_search(self, instrument_urls: list, observed_property_urls: list):
        return self.referencing_instrument_urls(instrument_urls) & self.referencing_observed_property_urls(observed_property_urls)

class AcquisitionQuerySet(models.QuerySet, AbstractAcquisitionDatabaseQueries):
    def referencing_acquisition_capability_set_urls(self, acquisition_capability_set_urls: list):
        pass

    def for_search(self, acquisition_capability_set_urls: list):
        pass

class ComputationCapabilitiesQuerySet(models.QuerySet, AbstractComputationCapabilitiesDatabaseQueries):
    def referencing_computation_type_urls(self, computation_type_urls: list):
        pass

    def referencing_observed_property_urls(self, observed_property_urls: list):
        pass

    def for_search(self, computation_type_urls: list, observed_property_urls: list):
        pass

class ComputationQuerySet(models.QuerySet, AbstractComputationDatabaseQueries):
    def referencing_computation_capability_set_urls(self, computation_capability_set_urls: list):
        pass

    def for_search(self, computation_capability_set_urls: list):
        pass

class ProcessQuerySet(models.QuerySet, AbstractProcessDatabaseQueries):
    def referencing_acquisition_urls(self, acquisition_urls: list):
        pass

    def referencing_computation_urls(self, computation_urls: list):
        pass

    def for_search(self, acquisition_urls: list, computation_urls: list):
        pass

class DataCollectionQuerySet(models.QuerySet, AbstractDataCollectionDatabaseQueries):
    def referencing_instrument_type_urls(self, instrument_type_urls: list):
        pass

    def referencing_computation_type_urls(self, computation_type_urls: list):
        pass

    def referencing_process_urls_or_feature_of_interest_urls(self, process_urls: list, feature_of_interest_urls: list):
        pass

    def for_search(
        self,
        process_urls: list,
        feature_of_interest_urls: list,
        instrument_type_urls: list,
        computation_type_urls: list
    ):
        pass

class CatalogueQuerySet(models.QuerySet, AbstractCatalogueDatabaseQueries):
    pass

class CatalogueEntryQuerySet(models.QuerySet, AbstractCatalogueEntryDatabaseQueries):
    pass

class CatalogueDataSubsetQuerySet(models.QuerySet, AbstractCatalogueDataSubsetDatabaseQueries):
    pass