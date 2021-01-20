# -*- coding: utf-8 -*-

from django import forms
from django.utils.safestring import mark_safe


# CONTACT SECTION
class SendEmailReferralForm(forms.Form):
    email = forms.EmailField(
        required=True,
        label="",
        label_suffix="",
        widget=forms.EmailInput(
            attrs={
                "class": "text-input",
                "placeholder": "mon_ami@gmail.com"
            }
        )
    )


class SendSmsReferralForm(forms.Form):
    phone = forms.CharField(
        required=True,
        label="",
        label_suffix="",
        widget=forms.TextInput(
            attrs={
                "class": "text-input",
                "placeholder": "06 12 42 13 19"
            }
        )
    )


class LoginForm(forms.Form):
    email = forms.EmailField(
        required=True,
        label="",
        label_suffix="",
        widget=forms.EmailInput(
            attrs={
                "class": "text-input",
                "placeholder": "mon_email@mail.com"
            }
        )
    )
