import json
import traceback
from urllib.error import HTTPError
from django.http import HttpResponse, HttpResponseServerError
from django.views.decorators.http import require_POST
from django.views.generic import View
from lxml import etree
from openapi_spec_validator import validate_spec_url

from common.mongodb_models import CurrentAcquisition, CurrentAcquisitionCapability, CurrentComputation, CurrentComputationCapability, CurrentDataCollection, CurrentIndividual, CurrentInstrument, CurrentOperation, CurrentOrganisation, CurrentPlatform, CurrentProcess, CurrentProject
from validation.forms import ApiSpecificationUrlValidationForm
from validation.metadata_validation import ACQUISITION_CAPABILITY_XML_ROOT_TAG_NAME, ACQUISITION_XML_ROOT_TAG_NAME, COMPUTATION_CAPABILITY_XML_ROOT_TAG_NAME, COMPUTATION_XML_ROOT_TAG_NAME, DATA_COLLECTION_XML_ROOT_TAG_NAME, INDIVIDUAL_XML_ROOT_TAG_NAME, INSTRUMENT_XML_ROOT_TAG_NAME, OPERATION_XML_ROOT_TAG_NAME, ORGANISATION_XML_ROOT_TAG_NAME, PLATFORM_XML_ROOT_TAG_NAME, PROCESS_XML_ROOT_TAG_NAME, PROJECT_XML_ROOT_TAG_NAME, validate_xml_metadata_file

# Create your views here.
class ResourceXmlMetadataFileValidationFormView(View):
    mongodb_model = None
    expected_root_tag_name = ''

    def post(self, request, *args, **kwargs):
        xml_file = request.FILES['file']
        check_file_is_unregistered = 'validate_is_not_registered' in request.POST
        check_xml_file_localid_matches_existing_resource_localid = 'validate_xml_file_localid_matches_existing_resource_localid' in request.POST
        existing_resource_id = ''
        if 'resource_id' in request.POST:
            existing_resource_id = request.POST['resource_id']
        validation_results = validate_xml_metadata_file(xml_file, self.expected_root_tag_name, mongodb_model=self.mongodb_model, check_file_is_unregistered=check_file_is_unregistered, check_xml_file_localid_matches_existing_resource_localid=check_xml_file_localid_matches_existing_resource_localid, existing_resource_id=existing_resource_id)
        if 'error' not in validation_results:
            return HttpResponse(json.dumps({
                'result': 'valid'
            }), content_type='application/json')
        if validation_results['error']['type'] == etree.DocumentInvalid or validation_results['error']['type'] == etree.XMLSyntaxError:
            return HttpResponse(json.dumps({ 'error': validation_results['error'] }), status=422, content_type='application/json')
        return HttpResponseServerError(json.dumps({ 'error': validation_results['error'] }), content_type='application/json')

class OrganisationXmlMetadataFileValidationFormView(ResourceXmlMetadataFileValidationFormView):
    mongodb_model = CurrentOrganisation
    expected_root_tag_name = ORGANISATION_XML_ROOT_TAG_NAME
    
class IndividualXmlMetadataFileValidationFormView(ResourceXmlMetadataFileValidationFormView):
    mongodb_model = CurrentIndividual
    expected_root_tag_name = INDIVIDUAL_XML_ROOT_TAG_NAME

class ProjectXmlMetadataFileValidationFormView(ResourceXmlMetadataFileValidationFormView):
    mongodb_model = CurrentProject
    expected_root_tag_name = PROJECT_XML_ROOT_TAG_NAME

class PlatformXmlMetadataFileValidationFormView(ResourceXmlMetadataFileValidationFormView):
    mongodb_model = CurrentPlatform
    expected_root_tag_name = PLATFORM_XML_ROOT_TAG_NAME

class InstrumentXmlMetadataFileValidationFormView(ResourceXmlMetadataFileValidationFormView):
    mongodb_model = CurrentInstrument
    expected_root_tag_name = INSTRUMENT_XML_ROOT_TAG_NAME

class OperationXmlMetadataFileValidationFormView(ResourceXmlMetadataFileValidationFormView):
    mongodb_model = CurrentOperation
    expected_root_tag_name = OPERATION_XML_ROOT_TAG_NAME

class AcquisitionCapabilitiesXmlMetadataFileValidationFormView(ResourceXmlMetadataFileValidationFormView):
    mongodb_model = CurrentAcquisitionCapability
    expected_root_tag_name = ACQUISITION_CAPABILITY_XML_ROOT_TAG_NAME

class AcquisitionXmlMetadataFileValidationFormView(ResourceXmlMetadataFileValidationFormView):
    mongodb_model = CurrentAcquisition
    expected_root_tag_name = ACQUISITION_XML_ROOT_TAG_NAME

class ComputationCapabilitiesXmlMetadataFileValidationFormView(ResourceXmlMetadataFileValidationFormView):
    mongodb_model = CurrentComputationCapability
    expected_root_tag_name = COMPUTATION_CAPABILITY_XML_ROOT_TAG_NAME

class ComputationXmlMetadataFileValidationFormView(ResourceXmlMetadataFileValidationFormView):
    mongodb_model = CurrentComputation
    expected_root_tag_name = COMPUTATION_XML_ROOT_TAG_NAME

class ProcessXmlMetadataFileValidationFormView(ResourceXmlMetadataFileValidationFormView):
    mongodb_model = CurrentProcess
    expected_root_tag_name = PROCESS_XML_ROOT_TAG_NAME

class DataCollectionXmlMetadataFileValidationFormView(ResourceXmlMetadataFileValidationFormView):
    mongodb_model = CurrentDataCollection
    expected_root_tag_name = DATA_COLLECTION_XML_ROOT_TAG_NAME

@require_POST
def api_specification_url(request):
    response_body = {
        'valid': False
    }
    form = ApiSpecificationUrlValidationForm(request.POST)
    if form.is_valid():
        api_specification_url = request.POST['api_specification_url']
        try:
            validate_spec_url(api_specification_url)
            response_body['valid'] = True
        except HTTPError as err:
            print(err)
            print(traceback.format_exc())
            response_body['error'] = 'The URL was not found'
        except BaseException as err:
            print(err)
            print(traceback.format_exc())
            response_body['error'] = 'The URL does not link to a valid OpenAPI specification'
            response_body['details'] = str(err)
    else:
        response_body['error'] = 'Please enter a URL'
    return HttpResponse(json.dumps(response_body), content_type='application/json')