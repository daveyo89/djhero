from django.contrib import messages
from django.contrib.auth.mixins import AccessMixin
from django.contrib.auth.views import redirect_to_login
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect, reverse
from django.views.generic.detail import SingleObjectMixin

from blog.models import CustomUser


class ActiveRequiredMixin(AccessMixin):
    def handle_inactive(self):
        if self.raise_exception or self.request.user.is_authenticated:
            redirect(reverse('reactivate'))

        messages.add_message(self.request, messages.WARNING, 'Please activate your account before proceeding.')
        return redirect(reverse('index'))

    def handle_no_permission(self):
        if self.raise_exception or self.request.user.is_authenticated:
            raise PermissionDenied(self.get_permission_denied_message())
        return redirect_to_login(self.request.get_full_path(), self.get_login_url(), self.get_redirect_field_name())

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        if not request.user.is_active:
            return self.handle_inactive()
        return super().dispatch(request, *args, **kwargs)


class ProfileObjectMixin(SingleObjectMixin):
    model = CustomUser
    fields = '__all__'

    def get_object(self, queryset=None):
        try:
            return self.request.user
        except Exception:
            raise NotImplemented("User profile not implemented yet.")

