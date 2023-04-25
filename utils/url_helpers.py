from django.urls import reverse


# Resource URL component extraction functions
def divide_resource_url_into_main_components(resource_url):
    resource_url_split = resource_url.split('/')
    return {
        'url_base': '/'.join(resource_url_split[:-3]),
        'resource_type': resource_url_split[-3],
        'namespace': resource_url_split[-2],
        'localid': resource_url_split[-1],
    }

def divide_catalogue_related_resource_url_into_main_components(resource_url):
    resource_url_split = resource_url.split('/')
    return {
        'url_base': '/'.join(resource_url_split[:-4]),
        'resource_type': resource_url_split[-4],
        'namespace': resource_url_split[-3],
        'event': resource_url_split[-2],
        'localid': resource_url_split[-1],
    }

def divide_resource_url_from_op_mode_id(resource_url_with_op_mode_id):
    resource_url_with_op_mode_id_split = resource_url_with_op_mode_id.split('#')
    return {
        'resource_url': '#'.join(resource_url_with_op_mode_id_split[:-1]),
        'op_mode_id': resource_url_with_op_mode_id_split[-1],
    }

def get_namespace_and_localid_from_resource_url(resource_url: str) -> tuple[str, str]:
    resource_server_url_components = divide_resource_url_into_main_components(resource_url)
    return resource_server_url_components['namespace'], resource_server_url_components['localid']

def create_ontology_term_detail_url_from_ontology_term_server_url(ontology_term_server_url):
    ontology_term_server_url_split = ontology_term_server_url.split('/')
    ontology_category = ontology_term_server_url_split[-2]
    ontology_term_id = ontology_term_server_url_split[-1]
    return reverse('ontology:ontology_term_detail', args=[ontology_category, ontology_term_id])