from allauth.account.adapter import DefaultAccountAdapter
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.conf import settings


class AccountAdapter(DefaultAccountAdapter):
    def send_mail(self, template_prefix, email, context):
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
        user = super().populate_user(request, sociallogin, data)
        return self.save_user(request, sociallogin)
