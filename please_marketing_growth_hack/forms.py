# -*- coding: utf-8 -*-

from django import forms
from django.utils.safestring import mark_safe


# SIGNUP FORM SECTION
class SignUpForm(forms.Form):
    email = forms.EmailField(
        required=True,
        label="",
        label_suffix="",
        widget=forms.EmailInput(
            attrs={
                "class": "text-input",
                "placeholder": "✉️ Email *"
            }
        )
    )

    password = forms.CharField(
        required=True,
        label="",
        label_suffix="",
        min_length=8,
        widget=forms.PasswordInput(
            attrs={
                "class": "text-input",
                "placeholder": "🔒 Mot de passe (8 caractères, 1 majuscule + 1 chiffre min) *"
            }
        )
    )

    first_name = forms.CharField(
        required=True,
        label="",
        label_suffix="",
        widget=forms.TextInput(
            attrs={
                "class": "text-input",
                "placeholder": "👤 Prénom *"
            }
        )
    )

    last_name = forms.CharField(
        required=True,
        label="",
        label_suffix="",
        widget=forms.TextInput(
            attrs={
                "class": "text-input",
                "placeholder": "👤 Nom *"
            }
        )
    )

    COUNTRIES = (
        ('+33', 'France (+33)'),
        ('+262', 'France - La Réunion (+262)'),
        ('+596', 'France - La Martinique (+596)'),
        ('+590', 'France - La Guadeloupe (+590)'),
    )

    country_code = forms.ChoiceField(
        required=True,
        label="",
        label_suffix="",
        choices=COUNTRIES,
        widget=forms.Select(
            attrs={
                "class": "text-input",
                "placeholder": "Code Pays"
            }
        ),
    )
    phone = forms.CharField(
        required=True,
        label="",
        label_suffix="",
        max_length=10,
        min_length=10,
        widget=forms.TextInput(
            attrs={
                "class": "text-input",
                "pattern": "[0-9]*",
                "inputmode": "numeric",
                "placeholder": "📱 Téléphone (0612345678) *"
            }
        )
    )

    address = forms.CharField(
        required=True,
        label="",
        label_suffix="",
        widget=forms.TextInput(
            attrs={
                "class": "text-input",
                "id": "where",
                "placeholder": "📍 Adresse *"
            }
        )
    )

    BOOL = (
        (False, 'Je ne souhaite pas recevoir vos codes promos et bons plans 😮'),
        (True, 'Je souhaite recevoir vos codes promos et bons plans 😍'),
    )

    marketing = forms.ChoiceField(
        required=True,
        label="",
        label_suffix="",
        choices=BOOL,
        widget=forms.Select(
            attrs={
                "class": "text-input",
                "placeholder": ""
            }
        ),
    )


# SIGNUP FORM SECTION
class GameVoucherVernonForm(forms.Form):
    email = forms.EmailField(
        required=True,
        label="",
        label_suffix="",
        widget=forms.EmailInput(
            attrs={
                "class": "text-input",
                "placeholder": "✉️ Email *"
            }
        )
    )