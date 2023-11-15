import base64
import hashlib
import json
import os
import random
import uuid
import zlib

from django.contrib import messages
from django.http import (
    HttpResponse,
    HttpResponseRedirect,
    JsonResponse,
)
from django.shortcuts import render
from django.urls import (
    resolve,
    Resolver404,
    reverse,
)
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import (
    require_http_methods,
    require_POST
)
from functools import wraps

from .services import (
    get_institution_id_for_login_session,
    get_institution_memberships_of_logged_in_user,
    JOIN_URL_BASE,
    set_institution_for_login_session,
)

from common.forms import InstitutionForLoginSessionForm
from pithiaesc.settings import BASE_DIR


JOIN_AN_INSTITUTION_PAGE_TITLE = 'Join a PITHIA Institution'


# Create your views here.

# TODO: Uncomment these functions when token-based support
# is added to Perun.

def perun_login_required(function):
    @wraps(function)
    def wrap(request, *args, **kwargs):
        auth = request.headers.get('Authorization')

        if not auth:
            return JsonResponse({'msg': 'Please login!'}, status=400)
        
        if not auth.startswith('Bearer'):
            return JsonResponse({'msg': 'Header does not start with \'Bearer\'.'}, status=400)

        token = auth[7:]
        username = request.session.get(token)

        if not username:
            return JsonResponse({'msg': 'Invalid token!'}, status=401)

        if username != os.environ['PERUN_USERNAME']:
            return JsonResponse({'msg': 'The perun info has been deleted by the admin.'}, status=401)

        return function(request, *args, **kwargs)

    return wrap


@csrf_exempt
@require_POST
def perun_login(request):
    incorrect_login_msg = 'The username or password for Perun is wrong.'

    # Verify username
    username = request.POST.get('username', None)
    if username != os.environ['PERUN_USERNAME']:
        return JsonResponse({'msg': incorrect_login_msg}, status=400)
    
    # Verify password
    password = request.POST.get('password', None)
    hashed_password = hashlib.sha512(password.encode('utf-8')).hexdigest()
    if hashed_password != os.environ['PERUN_PASSWORD']:
        return JsonResponse({'msg': incorrect_login_msg}, status=400)
    
    # Set session token if login details are correct.
    token = str(uuid.uuid4()).replace('-', '') + str(random.randint(0, 1000))
    request.session[token] = username
    return JsonResponse({'msg': 'Login succeeded!', 'token': token}, status=200)

@csrf_exempt
@perun_login_required
def perun_login_test(request):
    return JsonResponse({'msg': 'hello world!'}, status=200)


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
        with open(os.path.join(BASE_DIR, 'perun', 'ListOfOrganisations.json'), 'r') as org_list_file:
            org_list_raw = [o['name'] for o in json.load(org_list_file)['organizations']]
    except FileNotFoundError:
        print('Cannot find the file. Please provide an existing file!')
    else:
        for org in org_list_raw:
            index_first_colon = org.find(':')
            index_last_colon = org.rfind(':')
            if index_first_colon == index_last_colon:
                org_list.append(org[index_first_colon + 1:])
        # Debugging
        print(org_list)
        # print('Join a group: ', JOIN_URL_BASE + org_list[0])

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
@perun_login_required
def update_perun_organisation_list(request):
    """
    Decodes a JSON payload of organisations sent by Perun and
    overwrites the locally stored version of these organisations
    which are stored in a JSON file.
    """
    # Retrieve the authorisation details from the request.
    # authorisation_header = request.headers.get('Authorization')
    # encoded_credentials = authorisation_header.split(' ')[1]  # Removes "Basic " to isolate credentials
    # decoded_credentials = base64.b64decode(encoded_credentials).decode("utf-8").split(':')
    # username = decoded_credentials[0]
    # password = decoded_credentials[1]

    # # Check the details are correct.
    # if username != os.environ['PERUN_USERNAME']:
    #     return JsonResponse({'msg': 'The username or password for perun is wrong.'}, status=400)
    # hashed_password = hashlib.sha512(password.encode('utf-8')).hexdigest()
    # if hashed_password != os.environ['PERUN_PASSWORD']:
    #     return JsonResponse({'msg': 'The username or password for perun is wrong.'}, status=400)

    # If the details are correct, decode the data.
    decompressed_data = zlib.decompress(request.body, 16+zlib.MAX_WBITS)
    decompressed_data_string = decompressed_data.replace(b'\x00', b'').decode('ascii')
    index_first_curly_bracket = decompressed_data_string.index('{')
    index_last_curly_bracket = decompressed_data_string.rfind('}') 
    update_data = json.loads(decompressed_data_string[index_first_curly_bracket:index_last_curly_bracket + 1])
    
    # Store the update by overwriting the locally stored JSON file.
    with open(os.path.join(BASE_DIR, 'perun', 'ListOfOrganisations.json'), 'w') as organisation_list_file:
        json.dump(update_data, organisation_list_file)
    return HttpResponse(status=200)


def choose_institution_for_login_session(request):
    # One user has multiple organisations, but we need to select
    # one organisation per session.
    next_url = reverse('data_provider_home')

    # Find the organisation to be able to configure views to institution.
    if request.method == 'POST':
        institution_subgroup_pair = request.POST['institutions']
        institution_subgroup_pair_split = institution_subgroup_pair.split(':')
        institution = institution_subgroup_pair_split[0]
        subgroup = institution_subgroup_pair_split[1]
        
        # Validate the next URL redirects to an eSC page
        if request.POST.get('next') is not None:
            try:
                resolve(request.POST.get('next'))
                next_url = request.POST.get('next')
            except Resolver404:
                messages.error(request, 'The "next" URL could not be resolved to a valid eSC URL.')
                return HttpResponseRedirect(reverse('data_provider_home'))

        # Validate the form
        try:
            user_memberships = get_institution_memberships_of_logged_in_user(request.session)
        except AttributeError:
            # session.get('user_memberships') will raise an AttributeError if
            # user memberships have not been stored in the session yet.
            messages.error(request, 'Could not retrieve user\'s memberships for form validation.')
            return HttpResponseRedirect(next_url)

        institution_choices = [(f'{institution}:{subgroup}', institution) for institution, subgroup in user_memberships.items()]
        form = InstitutionForLoginSessionForm(
            request.POST,
            institution_choices=institution_choices,
        )
        if form.is_valid():
            is_institution_for_login_session_set = get_institution_id_for_login_session(request.session)
            changed_or_set = 'changed' if is_institution_for_login_session_set else 'set'
            set_institution_for_login_session(request.session, institution, subgroup)
            success_msg = f'PITHIA Institution {changed_or_set} to {institution}.'
            messages.success(request, success_msg)
            if not is_institution_for_login_session_set:
                user_icon_svg = '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-person-fill" viewBox="0 0 16 16"><path d="M3 14s-1 0-1-1 1-4 6-4 6 3 6 4-1 1-1 1H3Zm5-6a3 3 0 1 0 0-6 3 3 0 0 0 0 6Z"/></svg>'
                info_msg = f'You can switch to another PITHIA institution from the {user_icon_svg} menu in the navigation bar.'
                messages.info(request, info_msg)
        else:
            messages.error(request, 'The form submitted was invalid.')

    return HttpResponseRedirect(next_url)