"""Prepares cleaned form data for XML conversion.
"""
from unidecode import unidecode

# Contact info
def process_contact_info_in_form(form_cleaned_data):
    return {
        'phone': form_cleaned_data.get('phone'),
        'address': {
            'delivery_point': form_cleaned_data.get('delivery_point'),
            'city': form_cleaned_data.get('city'),
            'administrative_area': form_cleaned_data.get('administrative_area'),
            'postal_code': form_cleaned_data.get('postal_code'),
            'country': unidecode(form_cleaned_data.get('country')),
            'electronic_mail_address': form_cleaned_data.get('email_address'),
        },
        'online_resource': form_cleaned_data.get('online_resource'),
        'hours_of_service': form_cleaned_data.get('hours_of_service'),
        'contact_instructions': form_cleaned_data.get('contact_instructions'),
    }

# Hours of service
def _format_time_to_12_hour_format(time_unformatted):
    return time_unformatted.strftime('%I:%M%p').lstrip('0').lower()

def process_hours_of_service_in_form(form_cleaned_data):
    try:
        time_start_parsed = form_cleaned_data.get('hours_of_service_start')
        time_end_parsed = form_cleaned_data.get('hours_of_service_end')

        time_start_formatted = _format_time_to_12_hour_format(time_start_parsed)
        time_end_formatted = _format_time_to_12_hour_format(time_end_parsed)
        return f'{time_start_formatted}-{time_end_formatted}'
    except BaseException:
        print('An error occurred when trying to process hours of service.')
        return ''

def process_documentation(form_cleaned_data):
    return {
        'citation_title': form_cleaned_data.get('citation_title'),
        'citation_date': form_cleaned_data.get('citation_publication_date'),
        # CI_DateTypeCode values are normally the values
        # used below.
        'ci_date_type_code': 'Publication Date',
        'ci_date_type_code_code_list': '',
        'ci_date_type_code_code_list_value': '',
        'ci_linkage_url': form_cleaned_data.get('citation_linkage_url'),
        'other_citation_details': form_cleaned_data.get('other_citation_details'),
        'doi': form_cleaned_data.get('citation_doi'),
    }

def process_project_keywords(form_cleaned_data):
    keywords_from_form = form_cleaned_data.get('keywords_json')
    keyword_dict_list = []
    for keyword_dict in keywords_from_form:
        keywords = keyword_dict.get('keywords')
        code_list = keyword_dict.get('type', {}).get('codeList')
        code_list_value = keyword_dict.get('type', {}).get('codeListValue')
        if any(not x for x in (keywords, code_list, code_list_value)):
            continue
        keyword_dict_list.append({
            'keywords': keywords,
            'type': {
                'code_list': code_list,
                'code_list_value': code_list_value,
            }
        })
    return keyword_dict_list

def process_related_parties(form_cleaned_data):
    related_parties_from_form = form_cleaned_data.get('related_parties_json')
    related_party_dict_list = []
    for related_party_dict in related_parties_from_form:
        role = related_party_dict.get('role')
        party = related_party_dict.get('parties')
        if any(not x for x in (role, party)):
            continue
        related_party_dict_list.append({
            'role': role,
            'parties': party,
        })
    return related_party_dict_list

def process_geometry_location_point_pos(form_cleaned_data):
    pos_point_1_from_form = form_cleaned_data.get('geometry_location_point_pos_1')
    pos_point_2_from_form = form_cleaned_data.get('geometry_location_point_pos_2')
    if (not pos_point_1_from_form
        or not pos_point_2_from_form):
        return ''
    return f'{pos_point_1_from_form} {pos_point_2_from_form}'

def process_location(form_cleaned_data):
    return {
        'geometry_location': {
            'point': {
                'id': form_cleaned_data.get('geometry_location_point_id'),
                'srs_name': form_cleaned_data.get('geometry_location_point_srs_name'),
                'pos': process_geometry_location_point_pos(form_cleaned_data),
            },
        },
        'name_location': {
            'code': form_cleaned_data.get('location_name')
        },
    }

def _process_time_position(time_position):
    if not time_position:
        return ''
    return time_position.isoformat()

def process_operation_time(form_cleaned_data):
    return {
        'time_period': {
            'id': form_cleaned_data.get('time_period_id'),
            'begin': {
                'time_instant': {
                    'id': form_cleaned_data.get('time_instant_begin_id'),
                    'time_position': _process_time_position(form_cleaned_data.get('time_instant_begin_position')),
                }
            },
            'end': {
                'time_instant': {
                    'id': form_cleaned_data.get('time_instant_end_id'),
                    'time_position': _process_time_position(form_cleaned_data.get('time_instant_end_position')),
                }
            },
        },
    }

def process_workflow_data_collections(form_cleaned_data):
    return [
        form_cleaned_data['data_collection_1'],
        *form_cleaned_data['data_collection_2_and_others'],
    ]

def process_operational_modes(form_cleaned_data):
    operational_modes_from_form = form_cleaned_data.get('operational_modes_json')
    operational_mode_dict_list = []
    for om in operational_modes_from_form:
        id = om.get('id')
        name = om.get('name')
        description = om.get('description')
        if any(not value for value in (id, name, description)):
            continue
        operational_mode_dict_list.append(om)
    return operational_mode_dict_list