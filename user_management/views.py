import base64
import hashlib
import json
import os
import random
import uuid
import zlib

from django.http import (
    HttpResponse,
    HttpResponseRedirect,
    JsonResponse,
)
from django.urls import reverse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods, require_POST
from functools import wraps
from pathlib import Path
from urllib.parse import unquote

from .services import (
    CREATION_URL_BASE,
    get_user_info,
    verify_if_part_of_an_organisation,
    JOIN_URL_BASE,
)


JOIN_AN_INSTITUTION_PAGE_TITLE = 'Join an Institution'


# Create your views here.

# TODO: Uncomment these functions when token-based support
# is added to Perun.

# def perun_login_required(function):
#     @wraps(function)
#     def wrap(request, *args, **kwargs):
#         auth = request.headers.get('Authorization')
# 
#         if not auth:
#             return JsonResponse({'msg': 'Please login!'}, status=400)
# 
#         username = request.session.get(auth)
# 
#         if not username:
#             JsonResponse({'msg': 'invalid token!'}, status=401)
# 
#         if not username != os.environ['PERUN_USERNAME']:
#             JsonResponse({'msg': 'The perun info has been deleted by the admin.'}, status=401)
# 
#         return function(request, *args, **kwargs)
# 
#     return wrap


# @csrf_exempt
# @require_POST
# def perun_login(request):
#     username = request.POST['username']
#     if username == os.environ['PERUN_USERNAME']:
#         password = request.POST['password']
#         hashed_password = hashlib.sha512(password.encode('utf-8')).hexdigest()
# 
#         if hashed_password == os.environ['PERUN_PASSWORD']:
#             token = str(uuid.uuid4()).replace('-', '') + str(random.randint(0, 1000))
#             request.session[token] = username
#             return JsonResponse({'msg': 'login succeed!', 'token': token}, status=200)
#         else:
#             return JsonResponse({'msg': 'The username or password for perun is wrong.'}, status=400)

# @csrf_exempt
# @perun_login_required
# def perun_login_test(request):
#     return JsonResponse({'msg': 'hello world!'}, status=200)


@require_POST
def save_perun_info(request):
    username = request.POST['username']
    password = request.POST['password']

    # Save username and password into the database
    os.environ['PERUN_USERNAME'] = username
    os.environ['PERUN_PASSWORD'] = hashlib.sha512(password.encode('utf-8')).hexdigest()

    return JsonResponse({'msg': 'ok'}, status=200)


def list_joinable_perun_organisations(request):
    # Join a group - list organisations from local JSON file
    org_list_raw = []
    org_list = []
    
    try:
        with open(os.path.join(Path.home(), 'ListOfOrganisations.json'), 'r') as org_list_file:
            org_list_raw = json.load(org_list_file)
    except FileNotFoundError:
        print('Cannot find the file. Please provide an existing file!')
    else:
        for org in org_list_raw:
            index_first_colon = org.find(':')
            index_last_colon = org.rfind(':')
            if index_first_colon == index_last_colon:
                org_list.append(org[index_first_colon + 1:])
        print(org_list)
        print('Join a group: ', JOIN_URL_BASE + org_list[0])

    return render(request, 'user_management/list_joinable_perun_organisations.html', {
        'title': JOIN_AN_INSTITUTION_PAGE_TITLE,
        'org_list': org_list,
        'join_url_base': JOIN_URL_BASE
    })

def list_joinable_perun_organisation_subgroups(request, institution_id):
    # TODO: substitute institution_id with the institution
    # display name in the JSON received from Perun.
    institution_name = institution_id

    return render(request, 'user_management/list_joinable_perun_organisation_subgroups.html', {
        'title': f'Join {institution_name}',
        'join_an_institution_breadcrumb_text': JOIN_AN_INSTITUTION_PAGE_TITLE,
        'join_an_institution_breadcrumb_url_name': 'list_joinable_perun_organisations',
        'institution_id': institution_id,
        'institution_name': institution_name,
        'join_url_base': JOIN_URL_BASE
    })


@csrf_exempt
@require_http_methods(["PUT"])
def update_perun_organisation_list(request):
    """
    Decodes a JSON payload of organisations sent by Perun and
    overwrites the locally stored version of these organisations
    which are stored in a JSON file.
    """
    # Retrieve the authorisation details from the request.
    authorisation_header = request.headers.get('Authorization')
    encoded_credentials = authorisation_header.split(' ')[1]  # Removes "Basic " to isolate credentials
    decoded_credentials = base64.b64decode(encoded_credentials).decode("utf-8").split(':')
    username = decoded_credentials[0]
    password = decoded_credentials[1]

    # Check the details are correct.
    if username != os.environ['PERUN_USERNAME']:
        return JsonResponse({'msg': 'The username or password for perun is wrong.'}, status=400)
    hashed_password = hashlib.sha512(password.encode('utf-8')).hexdigest()
    if hashed_password != os.environ['PERUN_PASSWORD']:
        return JsonResponse({'msg': 'The username or password for perun is wrong.'}, status=400)

    # If the details are correct, decode the data.
    decompressed_data = zlib.decompress(request.body, 16+zlib.MAX_WBITS)
    decompressed_data_string = decompressed_data.replace(b'\x00', b'').decode('ascii')
    index_first_square_bracket = decompressed_data_string.index('[')
    index_last_square_bracket = decompressed_data_string.index(']') 
    update_data = json.loads(decompressed_data_string[index_first_square_bracket:index_last_square_bracket + 1])
    
    # Store the update by overwriting the locally stored JSON file.
    with open(os.path.join(Path.home(), 'ListOfOrganisations.json'), 'w') as organisation_list_file:
        json.dump(update_data, organisation_list_file)
    return HttpResponse(status=200)


def choose_perun_organisation_subgroup_for_session(request):
    if request.method == 'POST':
        subgroup_name = request.POST['subgroup-name']
        request.session['selected_institution_subgroup'] = subgroup_name
        return HttpResponseRedirect(reverse('choose_perun_organisation_subgroup_for_session'))

    # TODO: Uncomment once deployed to production
    # ACCESS_TOKEN = request.META.get('OIDC_access_token')
    # user_info = get_user_info(ACCESS_TOKEN)
    # is_part_of_an_organisation = verify_if_part_of_an_organisation(user_info)

    # TEMP - Used for testing
    # request_meta = request.META.items()
    is_part_of_an_organisation = True
    organisation_details = [
        'urn:mace:egi.eu:group:vo.abc.test.eu:members:role=member#aai.egi.eu',
        'urn:mace:egi.eu:group:vo.abc.test.eu:organizations:abc-test:admins:role=member#aai.egi.eu',
        'urn:mace:egi.eu:group:vo.abc.test.eu:organizations:abc-test:members:role=member#aai.egi.eu',
        'urn:mace:egi.eu:group:vo.abc.test.eu:organizations:abc-test:role=member#aai.egi.eu',
        'urn:mace:egi.eu:group:vo.abc.test.eu:organizations:role=member#aai.egi.eu',
        'urn:mace:egi.eu:group:vo.abc.test.eu:organizations:abc:role=member#aai.egi.eu',
        'urn:mace:egi.eu:group:vo.abc.test.eu:role=member#aai.egi.eu'
    ]

    # One user has multiple organisations, but we need to select
    # one organisation per session.

    # Find the organisation and then do the following things (David's work)
    if is_part_of_an_organisation:
        # type of t: <class 'str'>
        for t in organisation_details:
            print(t)

        # find organizations
        organisations = []
        for t in organisation_details:
            index = t.rfind('organizations', 0, -1)

            if index == -1:
                continue

            index1 = t.rfind('role', 0, -1)
            new_string = t[index: index1 - 1]

            if len(new_string) <= len('organizations'):
                continue

            index2 = new_string.find(':', 0, -1)
            organisations.append(new_string[index2 + 1:])

        print(organisations)
        
        # Find the subgroups
        subgroups = []
        for o in organisations:
            index = o.find(':')
            if index == -1:
                continue
            subgroups.append(unquote(o[:]))
        print('subgroups: ', subgroups)

    return render(request, 'user_management/subgroup_selection_for_session.html', {
        'create_perun_organisation_url': CREATION_URL_BASE,
        'is_part_of_an_organisation': is_part_of_an_organisation,
        'subgroups': subgroups,
        # 'request_meta': request_meta,
        # 'user_info_text': user_info,
    })