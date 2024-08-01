import json
import logging
from .editor_dataclasses import (
    CapabilityLinkMetadataUpdate,
    InputOutputMetadataUpdate,
    ProcessCapabilityMetadataUpdate,
    RelatedPartyMetadataUpdate,
    StandardIdentifierMetadataUpdate,
    TimeSpanMetadataUpdate,
)


logger = logging.getLogger(__name__)


# Contact info fields
def _format_time_to_12_hour_format(time_unformatted):
    return time_unformatted.strftime('%I:%M%p').lstrip('0').lower()

def get_hours_of_service_from_form(form_cleaned_data):
    try:
        time_start_parsed = form_cleaned_data.get('hours_of_service_start')
        time_end_parsed = form_cleaned_data.get('hours_of_service_end')

        time_start_formatted = _format_time_to_12_hour_format(time_start_parsed)
        time_end_formatted = _format_time_to_12_hour_format(time_end_parsed)
        return f'{time_start_formatted}-{time_end_formatted}'
    except BaseException:
        logger.exception('An error occurred when trying to process hours of service.')
        return ''

def get_phone_field_string_value(form_cleaned_data):
    phone = form_cleaned_data.get('phone', '')
    if phone:
        phone = phone.as_international
    return phone

# Capabilities field
def map_process_capabilities_to_dataclasses(form_cleaned_data):
    return [
        ProcessCapabilityMetadataUpdate(
            name=pc.get('name'),
            observed_property=pc.get('observedProperty'),
            dimensionality_instance=pc.get('dimensionalityInstance'),
            dimensionality_timeline=pc.get('dimensionalityTimeline'),
            cadence=pc.get('cadence'),
            cadence_unit=pc.get('cadenceUnits'),
            vector_representation=pc.get('vectorRepresentation'),
            coordinate_system=pc.get('coordinateSystem'),
            units=pc.get('units'),
            qualifier=pc.get('qualifier'),
        )
    for pc in form_cleaned_data.get('capabilities_json')]

# Capability Links
def map_capability_links_to_dataclasses(form_cleaned_data):
    return [
        CapabilityLinkMetadataUpdate(
            platforms=cap_link.get('platforms', []),
            capabilities=cap_link.get('capabilities'),
            standard_identifiers=[StandardIdentifierMetadataUpdate(**si) for si in json.loads(cap_link.get('standardIdentifiers', []))],
            time_spans=[TimeSpanMetadataUpdate(
                begin_position=ts.get('beginPosition'),
                end_position=ts.get('endPosition')
            ) for ts in json.loads(cap_link.get('timeSpans', []))]
        )
    for cap_link in form_cleaned_data.get('capability_links_json')]

# Processing inputs
def map_processing_inputs_to_dataclasses(form_cleaned_data):
    return [
        InputOutputMetadataUpdate(
            name=proc_input.get('name'),
            description=proc_input.get('description')
        )
    for proc_input in form_cleaned_data.get('processing_inputs_json')]

# Related parties
def map_related_parties_to_dataclasses(form_cleaned_data):
    return [
        RelatedPartyMetadataUpdate(
            role=rp.get('role'),
            parties=rp.get('parties')
        )
    for rp in form_cleaned_data.get('related_parties_json')]