import base64
import hashlib
import json
import os
import random
import requests
import uuid
import zlib

from django.http import (
    HttpResponse,
    HttpResponseRedirect,
    JsonResponse,
)
from django.shortcuts import render
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods, require_POST

from functools import wraps
from pathlib import Path
from urllib.parse import unquote

from utils.user_info_api import get_user_info


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

def logout(request):
    ID_TOKEN_HINT = request.META.get('OIDC_id_token')
    # Logout
    logout_response = requests.get(f'https://aai-demo.egi.eu/auth/realms/egi/protocol/openid-connect/logout?id_token_hint={ID_TOKEN_HINT}')
#    return HttpResponseRedirect(f'https://aai-demo.egi.eu/auth/realms/egi/protocol/openid-connect/logout?id_token_hint={ID_TOKEN_HINT}')
    url = 'https://aai-demo.egi.eu/auth/realms/egi/protocol/openid-connect/userinfo'
    request_meta = request.META.items()
    ACCESS_TOKEN = request.META.get('OIDC_access_token')

    user_info_response = get_user_info(url, ACCESS_TOKEN)
    user_info = json.loads(user_info_response.text)
    error_in_user_info = 'error' in user_info

    return render(request, 'index.html', {
        'title': f'PITHIA e-Science Centre Home',
        'logout_response': logout_response,
        'ID_TOKEN_HINT': ID_TOKEN_HINT,
        'error_in_user_info': error_in_user_info,
    })

def index(request):
    return render(request, 'index.html', {
        'title': 'PITHIA e-Science Centre Home',
    })

def index_admin(request):
    return render(request, 'index.html', {
        'title': 'Admin Dashboard',
        'create_perun_organisation_url': 'https://perun.egi.eu/egi/registrar/?vo=vo.esc.pithia.eu&group=organizationRequests',
    })


@require_POST
def save_perun_info(request):
    username = request.POST['username']
    password = request.POST['password']

    # Save username and password into the database
    os.environ['PERUN_USERNAME'] = username
    os.environ['PERUN_PASSWORD'] = hashlib.sha512(password.encode('utf-8')).hexdigest()

    return JsonResponse({'msg': 'ok'}, status=200)

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

def join_perun_organisation(request):
    # join a group
    # i. list organisations from local json files
    BASE_URL = 'https://perun.egi.eu/egi/registrar/?vo=vo.esc.pithia.eu&group=organizations:'
    org_list = []
    groups = {
        'Organisations': []
    }
    try:
        with open(os.path.join(Path.home(), 'ListOfOrganisations.json'), 'r') as org_list_file:
            groups = json.load(org_list_file)
    except FileNotFoundError:
        print('Cannot find the file. Please provide an exist file!')
    else:
        org_list = []
        for org in groups:
            index = org.find(':')
            index1 = org.rfind(':')
            if index == index1:
                org_list.append(org[index+1:])
        print(org_list)
        print('Join a group: ', BASE_URL + org_list[0])

    return render(request, 'join_perun_organisation.html', {
        'org_list': org_list,
        'join_url_base': BASE_URL
    })

def join_perun_organisation_subgroup(request, organisation_id):
    BASE_URL = 'https://perun.egi.eu/egi/registrar/?vo=vo.esc.pithia.eu&group=organizations:'
    return render(request, 'join_perun_organisation_subgroup.html', {
        'organisation_id': organisation_id,
        'join_url_base': BASE_URL
    })


@csrf_exempt
@require_http_methods(["PUT"])
def update_perun_organisation_list(request):
    authorisation_header = request.headers.get('Authorization')
    encoded_credentials = authorisation_header.split(' ')[1]  # Removes "Basic " to isolate credentials
    decoded_credentials = base64.b64decode(encoded_credentials).decode("utf-8").split(':')
    username = decoded_credentials[0]
    password = decoded_credentials[1]
    if username != os.environ['PERUN_USERNAME']:
        return JsonResponse({'msg': 'The username or password for perun is wrong.'}, status=400)
    hashed_password = hashlib.sha512(password.encode('utf-8')).hexdigest()
    print('password', password)
    print('hashed_password', hashed_password)
    if hashed_password != os.environ['PERUN_PASSWORD']:
        return JsonResponse({'msg': 'The username or password for perun is wrong.'}, status=400)

    decompressed_data = zlib.decompress(request.body, 16+zlib.MAX_WBITS)
    decompressed_data_string = decompressed_data.replace(b'\x00', b'').decode('ascii')
    index_first_square_bracket = decompressed_data_string.index('[')
    index_last_square_bracket = decompressed_data_string.index(']') 
    update_data = json.loads(decompressed_data_string[index_first_square_bracket:index_last_square_bracket + 1])
    with open(os.path.join(Path.home(), 'ListOfOrganisations.json'), 'w') as organisation_list_file:
        json.dump(update_data, organisation_list_file)
    return HttpResponse(status=200)

def select_institution_subgroup(request):
    print("request.session.get('selected_org')", request.session.get('selected_org'))
    if request.method == 'POST':
        subgroup_name = request.POST['subgroup-name']
        request.session['selected_org'] = subgroup_name
        return HttpResponseRedirect(reverse('select_institution_subgroup'))
    # url = 'https://aai-demo.egi.eu/auth/realms/egi/protocol/openid-connect/userinfo'

    # request_meta = request.META.items()
    # ACCESS_TOKEN = request.META.get('OIDC_access_token')

    # user_info_response = get_user_info(url, ACCESS_TOKEN)
    # user_info = json.loads(user_info_response.text)
    # error_in_user_info = 'error' in user_info
    # institution_details = user_info.get('eduperson_entitlement')
    # is_part_of_an_institution = institution_details is not None

    # TEMP
    is_part_of_an_institution = True
    institution_details = [
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
    if is_part_of_an_institution:
        # type of t: <class 'str'>
        for t in institution_details:
            print(t)
        print()

        # find organizations
        organisations = []
        for t in institution_details:
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
        
        # find the sub groups
        subgroups = []
        for o in organisations:
            index = o.find(':')
            if index == -1:
                continue
            subgroups.append(unquote(o[:]))
        print('subgroups: ', subgroups)

    return render(request, 'subgroup_selection.html', {
        # 'request_meta': request_meta,
        # 'user_info_text': user_info,
        'create_perun_organisation_url': 'https://perun.egi.eu/egi/registrar/?vo=vo.esc.pithia.eu&group=organizationRequests',
        'is_part_of_an_institution': is_part_of_an_institution,
        # 'error_in_user_info': error_in_user_info,
        'subgroups': subgroups, 
    })