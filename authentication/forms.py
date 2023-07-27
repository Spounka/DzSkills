from allauth.account.adapter import get_adapter
from allauth.account.forms import default_token_generator
from allauth.account.utils import user_pk_to_url_str
from dj_rest_auth.forms import AllAuthPasswordResetForm, default_url_generator
from django.contrib.sites.shortcuts import get_current_site


class PasswordResetForm(AllAuthPasswordResetForm):
    def save(self, request, **kwargs):
        current_site = get_current_site(request)
        email = self.cleaned_data['email']
        token_generator = kwargs.get('token_generator', default_token_generator)

        for user in self.users:
            temp_key = token_generator.make_token(user)

            # save it to the password reset model
            # password_reset = PasswordReset(user=user, temp_key=temp_key)
            # password_reset.save()

            # send the password reset email
            url_generator = kwargs.get('url_generator', default_url_generator)
            url = url_generator(request, user, temp_key)

            context = {
                'current_site': current_site,
                'user': user,
                'password_reset_url': url,
                'request': request,
                'u': user_pk_to_url_str(user),
                'key': temp_key
            }

            get_adapter(request).send_mail(
                'account/email/password_reset_key', email, context, True
            )
        return self.cleaned_data['email']
