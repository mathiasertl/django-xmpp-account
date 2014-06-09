# -*- coding: utf-8 -*-
#
# This file is part of django-xmpp-register (https://account.jabber.at/doc).
#
# django-xmpp-register is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your option) any
# later version.
#
# django-xmpp-register is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for
# more details.
#
# You should have received a copy of the GNU General Public License along with
# django-xmpp-register.  If not, see <http://www.gnu.org/licenses/>.

from __future__ import unicode_literals

from django import forms
from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import IntegrityError
from django.http import Http404
from django.forms.util import ErrorList
from django.utils.translation import ugettext as _
from django.views.generic import FormView

from brake.decorators import ratelimit

from recaptcha import RecaptchaUnreachableError

from backends.base import UserExists
from backends.base import UserNotFound

from core.exceptions import RateException
from core.exceptions import TemporaryError
from core.models import Address
from core.models import Confirmation
from core.models import UserAddresses

User = get_user_model()


class AntiSpamFormView(FormView):
    def dispatch(self, request, *args, **kwargs):
        # create a dummy function and dynamically set its name. This way,
        # the ratelimit decorator is specific to the method in each class.
        def func(request):
            pass
        func.__name__ = str('%s_dispatch' % self.__class__.__name__)
        func = ratelimit(method='POST', rate='10/m')(func)
        ratelimit(method='GET', rate='30/m')(func)(request)

        if getattr(request, 'limited', False):
            raise RateException()

        try:
            return super(AntiSpamFormView, self).dispatch(request, *args, **kwargs)
        except RecaptchaUnreachableError as e:
            raise TemporaryError(_("The ReCAPTCHA server was unreacheable."))
        except KeyError as e:
            raise TemporaryError(_("The ReCAPTCHA didn't work properly."))

    def get_form_kwargs(self):
        kwargs = super(AntiSpamFormView, self).get_form_kwargs()
        if settings.RECAPTCHA_CLIENT is not None:
            kwargs['request'] = self.request
        return kwargs

    def form_valid(self, form):
        return self.render_to_response(self.get_context_data(form=form))


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
        default_error = _("User not found (or false password provided)!")
        try:
            user = self.get_user(form.cleaned_data)
            self.handle_valid(form, user)
        except User.DoesNotExist:
            errors = form._errors.setdefault(forms.forms.NON_FIELD_ERRORS, ErrorList())
            errors.append(default_error)
            return self.form_invalid(form)
        except UserNotFound as e:
            errors = form._errors.setdefault(forms.forms.NON_FIELD_ERRORS, ErrorList())
            if str(e):
                errors.append(str(e))
            else:
                errors.append(default_error)
            return self.form_invalid(form)
        except (IntegrityError, UserExists):
            errors = form._errors.setdefault(forms.forms.NON_FIELD_ERRORS, ErrorList())
            errors.append(_("User already exists."))
            return self.form_invalid(form)

        # log user address:
        address = Address.objects.get_or_create(address=self.request.META['REMOTE_ADDR'])[0]
        UserAddresses.objects.create(address=address, user=user, purpose=self.purpose)

        # create a confirmation key before returning the response
        key = Confirmation.objects.create(user=user, purpose=self.purpose)
        key.send(
            request=self.request, template_base=self.email_template,
            subject=self.email_subject % {'domain': user.domain, },
            confirm_url_name=self.confirm_url_name
        )

        return super(ConfirmationView, self).form_valid(form)


class ConfirmedView(AntiSpamFormView):
    user = None

    def after_delete(self, data):
        pass

    def get_context_data(self, **kwargs):
        context = super(ConfirmedView, self).get_context_data(**kwargs)
        if self.user is not None:
            context['username'] = self.user.username
            context['domain'] = self.user.domain
            context['jid'] = self.user.jid
        return context

    def form_valid(self, form):
        try:
            key = Confirmation.objects.valid().filter(
                purpose=self.purpose).get(key=self.kwargs['key'])
        except Confirmation.DoesNotExist:
            raise Http404
        self.user = key.user

        try:
            self.handle_key(key, form)
            key.delete()
            self.after_delete(form.cleaned_data)
        except UserNotFound:
            errors = form._errors.setdefault(forms.forms.NON_FIELD_ERRORS, ErrorList())
            errors.append(_("User not found!"))
            return self.form_invalid(form)
        except UserExists:
            errors = form._errors.setdefault(forms.forms.NON_FIELD_ERRORS, ErrorList())
            errors.append(_("User already exists!"))
            return self.form_invalid(form)

        return super(ConfirmedView, self).form_valid(form)
