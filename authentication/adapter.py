from allauth.account.adapter import DefaultAccountAdapter
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.conf import settings


class AccountAdapter(DefaultAccountAdapter):
    def send_mail(self, template_prefix, email, context, is_password=False):
        if is_password:
            activation_url = f'{self.request.scheme}://{settings.HOSTNAME}{settings.PASSWOR_RESET_URL}' \
                             f'?u={context["u"]}&t={context["key"]}'
            context['password_reset_url'] = activation_url
        else:
            activation_url = f'{self.request.scheme}://{settings.HOSTNAME}{settings.EMAIL_ACTIVATION_URL}{context["key"]}'
            context['activate_url'] = activation_url
        super().send_mail(template_prefix, email, context)

    def save_user(self, request, user, form, commit=True):
        user = super().save_user(request, user, form, commit)
        return user


class SocialAdapter(DefaultSocialAccountAdapter):
    def save_user(self, request, sociallogin, form=None):
        return super().save_user(request, sociallogin, form)

    def populate_user(self, request, sociallogin, data):
        # TODO: Implement this method to populate user with data
        # user = super().populate_user(request, sociallogin, data)
        return self.save_user(request, sociallogin)
