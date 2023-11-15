from django.contrib import messages
from django.http import HttpResponseRedirect
from django.shortcuts import redirect
from django.urls import reverse
from functools import wraps

from .models import ScientificMetadata

from user_management.services import (
    get_institution_id_for_login_session,
)

def login_session_institution_required(function):
    @wraps(function)
    def wrap(request, *args, **kwargs):
        institution_id_for_login_session = get_institution_id_for_login_session(request.session)
        if not institution_id_for_login_session:
            messages.warning(request, 'The page you were trying to access requires an active login session with an institution.')
            return HttpResponseRedirect(reverse('home'))
        return function(request, *args, **kwargs)

    return wrap

def institution_ownership_required(function):
    @wraps(function)
    def wrap(request, resource_id, *args, **kwargs):
        institution_id_for_login_session = get_institution_id_for_login_session(request.session)
        resource = ScientificMetadata.objects.get(pk=resource_id)
        if resource.institution_id != institution_id_for_login_session:
            messages.error(request, f'You must be a member of the PITHIA institution that owns registration "{resource_id}" to perform this action.')
            return redirect(reverse('resource_management:index'))
        return function(request, resource_id, *args, **kwargs)

    return wrap