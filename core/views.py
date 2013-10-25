# -*- coding: utf-8 -*-
#
# This file is part of xmppregister (https://account.jabber.at/doc).
#
# xmppregister is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# xmppregister is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with xmppregister.  If not, see <http://www.gnu.org/licenses/>.

from __future__ import unicode_literals

from django import forms
from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import IntegrityError
from django.forms.util import ErrorList
from django.utils.decorators import method_decorator
from django.utils.translation import ugettext as _
from django.views.generic import FormView

from brake.decorators import ratelimit

from backends.base import UserExists
from backends.base import UserNotFound

from core.exceptions import RateException
from core.models import Confirmation

User = get_user_model()


class AntiSpamFormView(FormView):
    @method_decorator(ratelimit(method='GET', rate='15/m'))
    @method_decorator(ratelimit(method='POST', rate='5/m'))
    def dispatch(self, request, *args, **kwargs):
        if getattr(request, 'limited', False):
            raise RateException()
        return super(AntiSpamFormView, self).dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super(AntiSpamFormView, self).get_form_kwargs()
        if settings.RECAPTCHA_CLIENT is not None:
            kwargs['request'] = self.request
        return kwargs


class ConfirmationView(AntiSpamFormView):
    """
    Keys:

    * confirm_url_name
    * email_subject
    * email_template
    * purpose
    """
    def handle_valid(self, form, user):
        pass

    def form_valid(self, form):
        try:
            user = self.get_user(form.cleaned_data)
            self.handle_valid(form, user)
        except (User.DoesNotExist, UserNotFound):
            errors = form._errors.setdefault(forms.forms.NON_FIELD_ERRORS,
                                             ErrorList())
            errors.append(_("User not found!"))
            return self.form_invalid(form)
        except (IntegrityError, UserExists):
            errors = form._errors.setdefault(forms.forms.NON_FIELD_ERRORS,
                                             ErrorList())
            errors.append(_("User already exists."))
            return self.form_invalid(form)

#TODO: Handle case were user already exists

        # create a confirmation key before returning the response
        key = Confirmation.objects.create(user=user, purpose=self.purpose)
        key.send(
            request=self.request, template_base=self.email_template,
            subject=self.email_subject % {'domain': user.domain, },
            confirm_url_name=self.confirm_url_name
        )

        return super(ConfirmationView, self).form_valid(form)


class ConfirmedView(AntiSpamFormView):
    def form_valid(self, form):
        key = Confirmation.objects.registrations().get(key=self.kwargs['key'])
        try:
            self.handle_key(key, form)
            key.delete()
        except UserNotFound:
            errors = form._errors.setdefault(forms.forms.NON_FIELD_ERRORS,
                                             ErrorList())
            errors.append(_("User not found!"))
            return self.form_invalid(form)
        except UserExists:
            errors = form._errors.setdefault(forms.forms.NON_FIELD_ERRORS,
                                             ErrorList())
            errors.append(_("User already exists!"))
            return self.form_invalid(form)

        return super(FormView, self).form_valid(form)
