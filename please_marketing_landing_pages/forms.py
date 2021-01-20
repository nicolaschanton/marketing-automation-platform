# -*- coding: utf-8 -*-

from django import forms
from django.utils.safestring import mark_safe
from django.core.validators import RegexValidator
import datetime


# SIGNUP FORMS SECTION
class SignUpFormFull(forms.Form):
    email = forms.EmailField(
        required=True,
        label="",
        label_suffix="",
        widget=forms.EmailInput(
            attrs={
                "class": "text-input-2",
                "placeholder": "Email *",
                "id": "email-input",
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
                "class": "text-input-2",
                "placeholder": "Mot de passe (8 caractères, 1 majuscule + 1 chiffre min) *"
            }
        )
    )

    first_name = forms.CharField(
        required=True,
        label="",
        label_suffix="",
        widget=forms.TextInput(
            attrs={
                "class": "text-input-2",
                "placeholder": "Prénom *",
                "id": "first-name-input",
            }
        )
    )

    last_name = forms.CharField(
        required=True,
        label="",
        label_suffix="",
        widget=forms.TextInput(
            attrs={
                "class": "text-input-2",
                "placeholder": "Nom *",
                "id": "last-name-input",
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
                "class": "text-input-2",
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
                "class": "text-input-2",
                "pattern": "[0]+[6-7]+[0-9]*",
                "inputmode": "numeric",
                "placeholder": "Téléphone (0612345678) *"
            }
        )
    )

    address = forms.CharField(
        required=True,
        label="",
        label_suffix="",
        widget=forms.TextInput(
            attrs={
                "class": "text-input-2",
                "id": "where",
                "placeholder": "Adresse *",
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
                "class": "text-input-2",
                "placeholder": ""
            }
        ),
    )


class VoucherForm(forms.Form):
    email = forms.EmailField(
        required=True,
        label="",
        label_suffix="",
        widget=forms.EmailInput(
            attrs={
                "class": "text-input",
                "placeholder": "Email *"
            }
        )
    )


class GameForm(forms.Form):
    birth_date = forms.DateField(
        initial=datetime.date.today,
        required=True,
        label="Votre date de naissance *",
        label_suffix="",
        widget=forms.DateInput(
            format="%d/%m/%Y",
            attrs={
                "class": "date-input-retro",
                "placeholder": ""
            }
        )
    )

    FAVOURITE_DISH = (
        ('Burger', 'Burger'),
        ('Tacos', 'Tacos'),
        ('Pizza', 'Pizza'),
        ('Salade', 'Salade'),
        ('Pâtes', 'Pâtes'),
        ('Kebab', 'Kebab'),
        ('Risotto', 'Risotto'),
        ('Indien', 'Indien'),
        ('Sushis', 'Sushis'),
        ('Chinois', 'Chinois'),
        ('Tex Mex', 'Tex Mex'),
    )

    favourite_dish = forms.ChoiceField(
        required=True,
        label="Votre plat favori *",
        label_suffix="",
        choices=FAVOURITE_DISH,
        widget=forms.Select(
            attrs={
                "class": "text-input-retro-gaming",
                "placeholder": ""
            }
        ),
    )
