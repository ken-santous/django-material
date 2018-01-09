from django import forms
from django.contrib import messages
from django.contrib.auth import views, forms as auth_forms
from django.contrib.auth.decorators import user_passes_test
from django.core.cache import cache
from django.core.cache.utils import make_template_fragment_key
from django.core.files.storage import default_storage
from django.db import models
from django.urls import path
from django.utils.decorators import method_decorator
from django.views import generic
from django.utils.translation import ugettext_lazy as _

from material import (
    Viewset, viewprop, Icon,
    MaterialTextInput, MaterialPasswordInput
)


class AuthenticationForm(auth_forms.AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['username'].widget = MaterialTextInput(
            attrs={'autofocus': True},
            prefix=Icon('account_box')
        )
        self.fields['password'].widget = MaterialPasswordInput(
            prefix=Icon('lock')
        )


@method_decorator(user_passes_test(lambda u: u.is_authenticated), name='dispatch')
class ProfileView(generic.DetailView):
    template_name = 'registration/profile.html'

    def get_object_data(self):
        for field in self.object._meta.fields:
            if field.name in ['password']:
                continue
            if isinstance(field, models.AutoField):
                continue
            elif field.auto_created:
                continue
            else:
                choice_display_attr = "get_{}_display".format(field.name)
            if hasattr(self.object, choice_display_attr):
                value = getattr(self.object, choice_display_attr)()
            else:
                value = getattr(self.object, field.name)

            if value is not None:
                yield (field, field.verbose_name.capitalize(), value)

    def get_object(self):
        return self.request.user

    def post(self, request, *args, **kwargs):
        class AvatarForm(forms.Form):
            avatar = forms.FileField(required=True)
        form = AvatarForm(request.POST, request.FILES)
        if form.is_valid():
            file_name = 'avatars/{}.png'.format(request.user.pk)
            if default_storage.exists(file_name):
                default_storage.delete(file_name)
            default_storage.save(file_name, form.cleaned_data['avatar'], max_length=512*1024)
            key = make_template_fragment_key('django-material-avatar', [request.user.pk])
            cache.delete(key)
            messages.add_message(self.request, messages.SUCCESS, _('Avatar changed'), fail_silently=True)
        else:
            messages.add_message(self.request, messages.ERROR, form.errors(), fail_silently=True)
        return self.get(request, *args, **kwargs)


class AuthViewset(Viewset):
    """
    Viewset for the `django.contrib.auth`.

    urlpatterns = [
        path('accounts/', AuthViewset(
            login_view=views.LoginView.as_view(
                authentication_form=MyAuthForm
            )
        ).urls),
    ]
    """

    def __init__(self, *, allow_password_change=True, with_profile_view=True, **kwargs):
        """
            Initialize the viewset.

            :param allow_password_change=True: enable password change/reset views
        """
        super().__init__(**kwargs)
        self.allow_password_change = allow_password_change
        self.with_profile_view = with_profile_view

    """
    Login
    """
    login_view_class = views.LoginView

    def get_login_view_kwargs(self, **kwargs):
        result = {
            'form_class': AuthenticationForm
        }
        result.update(kwargs)
        return result

    @viewprop
    def login_view(self):
        return self.login_view_class.as_view(**self.get_login_view_kwargs())

    @property
    def login_url(self):
        return path('login/', self.login_view, name='login')

    """
    Logout
    """
    logout_view_class = views.LogoutView

    def get_logout_view_kwargs(self, **kwargs):
        return kwargs

    @viewprop
    def logout_view(self):
        return self.logout_view_class.as_view(**self.get_logout_view_kwargs())

    @property
    def logout_url(self):
        return path('logout/', self.logout_view, name='logout')

    """
    Password Change
    """
    pass_change_view_class = views.PasswordChangeView

    def get_pass_change_view_kwargs(self, **kwargs):
        return kwargs

    @viewprop
    def pass_change_view(self):
        return self.pass_change_view_class.as_view(**self.get_pass_change_view_kwargs())

    @property
    def pass_change_url(self):
        if self.allow_password_change:
            return path(
                'password_change/', self.pass_change_view,
                name='password_change')

    """
    Password Change Done
    """
    pass_change_done_view_class = views.PasswordChangeDoneView

    def get_pass_change_done_view_kwargs(self, **kwargs):
        return kwargs

    @viewprop
    def pass_change_done_view(self):
        return self.pass_change_done_view_class.as_view(**self.get_pass_change_done_view_kwargs())

    @property
    def pass_change_done_url(self):
        if self.allow_password_change:
            return path(
                'password_change/done/', self.pass_change_done_view,
                name='password_change_done')

    """
    Password Reset Request
    """
    pass_reset_view_class = views.PasswordResetView

    def get_pass_reset_view_kwargs(self, **kwargs):
        return kwargs

    @viewprop
    def pass_reset_view(self):
        return self.pass_reset_view_class.as_view(**self.get_pass_reset_view_kwargs())

    @property
    def pass_reset_url(self):
        if self.allow_password_change:
            return path(
                'password_reset/', self.pass_reset_view,
                name='password_reset')

    """
    Password Reset Request Done
    """
    pass_reset_done_view_class = views.PasswordResetDoneView

    def get_pass_reset_done_view_kwargs(self, **kwargs):
        return kwargs

    @viewprop
    def pass_reset_done_view(self):
        return self.pass_reset_done_view_class.as_view(**self.get_pass_reset_done_view_kwargs())

    @property
    def pass_reset_done_url(self):
        if self.allow_password_change:
            return path(
                'password_reset/done/', self.pass_reset_done_view,
                name='password_reset_done')

    """
    Password Reset Request Confirm
    """
    pass_reset_confirm_view_class = views.PasswordResetConfirmView

    def get_pass_reset_confirm_view_kwargs(self, **kwargs):
        return kwargs

    @viewprop
    def pass_reset_confirm_view(self):
        return self.pass_reset_confirm_view_class.as_view(**self.get_pass_reset_confirm_view_kwargs())

    @property
    def pass_reset_confirm_url(self):
        if self.allow_password_change:
            return path(
                'reset/<uidb64>/<token>/', self.pass_reset_confirm_view,
                name='password_reset_confirm')

    """
    Password Request Request Confirmed
    """
    pass_reset_complete_view_class = views.PasswordResetCompleteView

    def get_pass_reset_complete_view_kwargs(self, **kwargs):
        return kwargs

    @viewprop
    def pass_reset_complete_view(self):
        return self.pass_reset_complete_view_class.as_view(**self.get_pass_reset_complete_view_kwargs())

    @property
    def pass_reset_complete_url(self):
        if self.allow_password_change:
            return path(
                'reset/done/', self.pass_reset_complete_view,
                name='password_reset_complete')
    """
    Profile
    """
    profile_view_class = ProfileView

    def get_profile_view_kwargs(self, **kwargs):
        return kwargs

    @viewprop
    def profile_view(self):
        return self.profile_view_class.as_view(**self.get_profile_view_kwargs())

    @property
    def profile_url(self):
        if self.with_profile_view:
            return path('profile/', self.profile_view, name='profile')
