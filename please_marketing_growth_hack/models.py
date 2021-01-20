# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from django.db import models
from django.contrib.postgres.fields import ArrayField
from please_marketing_app.models import Neighborhood, Merchant, Customer


class BaseSiren(models.Model):

    # IDENTIFICATION DE L’ETABLISSEMENT
    siren = models.CharField(max_length=9, blank=True, null=True, unique=True)  # Identifiant de l'entreprise
    nic = models.CharField(max_length=5, blank=True, null=True)  # Numéro interne de classement de l'établissement

    # ADRESSE NORMALISEE
    l1_normalisee = models.CharField(max_length=300, blank=True, null=True)  # ligne de l'adressage de l'établissement
    l2_normalisee = models.CharField(max_length=300, blank=True, null=True)  # ligne de l'adressage de l'établissement
    l3_normalisee = models.CharField(max_length=300, blank=True, null=True)  # ligne de l'adressage de l'établissement
    l4_normalisee = models.CharField(max_length=300, blank=True, null=True)  # ligne de l'adressage de l'établissement
    l5_normalisee = models.CharField(max_length=300, blank=True, null=True)  # ligne de l'adressage de l'établissement
    l6_normalisee = models.CharField(max_length=300, blank=True, null=True)  # ligne de l'adressage de l'établissement
    l7_normalisee = models.CharField(max_length=300, blank=True, null=True)  # ligne de l'adressage de l'établissement

    # ADRESSE DECLAREE
    l1_declaree = models.CharField(max_length=300, blank=True, null=True)  # ligne de l'adressage déclaré pour l'établissement
    l2_declaree = models.CharField(max_length=300, blank=True, null=True)  # ligne de l'adressage déclaré pour l'établissement
    l3_declaree = models.CharField(max_length=300, blank=True, null=True)  # ligne de l'adressage déclaré pour l'établissement
    l4_declaree = models.CharField(max_length=300, blank=True, null=True)  # ligne de l'adressage déclaré pour l'établissement
    l5_declaree = models.CharField(max_length=300, blank=True, null=True)  # ligne de l'adressage déclaré pour l'établissement
    l6_declaree = models.CharField(max_length=300, blank=True, null=True)  # ligne de l'adressage déclaré pour l'établissement
    l7_declaree = models.CharField(max_length=300, blank=True, null=True)  # ligne de l'adressage déclaré pour l'établissement

    # ADRESSE GEOGRAPHIQUE
    numvoie = models.CharField(max_length=300, blank=True, null=True)  # Numéro dans la voie
    indrep = models.CharField(max_length=300, blank=True, null=True)  # Indice de répétition
    typvoie = models.CharField(max_length=300, blank=True, null=True)  # Type de voie de localisation de l'établissement
    libvoie = models.CharField(max_length=300, blank=True, null=True)  # Libellé de voie de localisation de l'établissement
    codpos = models.CharField(max_length=300, blank=True, null=True)  # Code postal
    cedex = models.CharField(max_length=300, blank=True, null=True)  # Code CEDEX

    # LOCALISATION GEOGRAPHIQUE DE L’ETABLISSEMENT
    rpet = models.CharField(max_length=300, blank=True, null=True)  # Région de localisation de l'établissement
    libreg = models.CharField(max_length=300, blank=True, null=True)  # Libellé de la région
    depet = models.CharField(max_length=300, blank=True, null=True)  # Département de localisation de l'établissement
    arronet = models.CharField(max_length=300, blank=True, null=True)  # Arrondissement de localisation de l'établissement
    ctonet = models.CharField(max_length=300, blank=True, null=True)  # Canton de localisation de l'établissement
    comet = models.CharField(max_length=300, blank=True, null=True)  # Commune de localisation de l'établissement
    libcom = models.CharField(max_length=300, blank=True, null=True)  # Libellé de la commune de localisation de l'établissement
    du = models.CharField(max_length=300, blank=True, null=True)  # Département de l'unité urbaine de la localisation de l'établissement
    tu = models.CharField(max_length=300, blank=True, null=True)  # Taille de l'unité urbaine
    uu = models.CharField(max_length=300, blank=True, null=True)  # Numéro de l'unité urbaine
    epci = models.CharField(max_length=300, blank=True, null=True)  # Localisation de l'établissement dans un établissement public de coopération intercommunale
    tcd = models.CharField(max_length=300, blank=True, null=True)  # Tranche de commune détaillée
    zemet = models.CharField(max_length=300, blank=True, null=True)  # Zone d'emploi

    # INFORMATIONS SUR L’ETABLISSEMENT
    siege = models.CharField(max_length=300, blank=True, null=True)  # Qualité de siège ou non de l'établissement
    enseigne = models.CharField(max_length=300, blank=True, null=True)  # Enseigne ou nom de l'exploitation
    ind_publio = models.CharField(max_length=300, blank=True, null=True)  # Indicateur du champ du publipostage
    diffcom = models.CharField(max_length=300, blank=True, null=True)  # Statut de diffusion de l'établissement
    amintret = models.CharField(max_length=300, blank=True, null=True)  # Année et mois d'introduction de l'établissement dans la base de diffusion

    # CARACTERISTIQUES ECONOMIQUES DE L’ETABLISSEMENT
    natetab = models.CharField(max_length=300, blank=True, null=True)  # Nature de l'établissement d'un entrepreneur individuel
    libnatetab = models.CharField(max_length=300, blank=True, null=True)  # Libellé de la nature de l'établissement
    apet700 = models.CharField(max_length=300, blank=True, null=True)  # Activité principale de l'établissement
    libapet = models.CharField(max_length=300, blank=True, null=True)  # Libellé de l'activité principale de l'établissement
    dapet = models.CharField(max_length=300, blank=True, null=True)  # Année de validité de l'activité principale de l'établissement
    tefet = models.CharField(max_length=300, blank=True, null=True)  # Tranche d'effectif salarié de l'établissement
    libtefet = models.CharField(max_length=300, blank=True, null=True)  # Libellé de la tranche d'effectif de l'établissement
    efetcent = models.CharField(max_length=300, blank=True, null=True)  # Effectif salarié de l'établissement à la centaine près
    defet = models.CharField(max_length=300, blank=True, null=True)  # Année de validité de l'effectif salarié de l'établissement
    origine = models.CharField(max_length=300, blank=True, null=True)  # Origine de la création de l'établissement
    dcret = models.CharField(max_length=300, blank=True, null=True)  # Année et mois de création de l'établissement
    ddebact = models.CharField(max_length=300, blank=True, null=True)  # Date de début d’activité
    activnat = models.CharField(max_length=300, blank=True, null=True)  # Nature de l'activité de l'établissement
    lieuact = models.CharField(max_length=300, blank=True, null=True)  # Lieu de l'activité de l'établissement
    actisurf = models.CharField(max_length=300, blank=True, null=True)  # Type de magasin
    saisonat = models.CharField(max_length=300, blank=True, null=True)  # Caractère saisonnier ou non de l'activité de l'établissement
    modet = models.CharField(max_length=300, blank=True, null=True)  # Modalité de l'activité principale de l'établissement
    prodet = models.CharField(max_length=300, blank=True, null=True)  # Caractère productif de l'établissement
    prodpart = models.CharField(max_length=300, blank=True, null=True)  # Participation particulière à la production de l'établissement
    auxilt = models.CharField(max_length=300, blank=True, null=True)  # Caractère auxiliaire de l'activité de l'établissement

    # IDENTIFICATION DE L’ENTREPRISE
    nomen_long = models.CharField(max_length=300, blank=True, null=True)  # Nom ou raison sociale de l'entreprise
    sigle = models.CharField(max_length=300, blank=True, null=True)  # Sigle de l'entreprise
    nom = models.CharField(max_length=300, blank=True, null=True)  # Nom de naissance
    prenom = models.CharField(max_length=300, blank=True, null=True)  # Prénom
    civilite = models.CharField(max_length=300, blank=True, null=True)  # Civilité des entrepreneurs individuels
    rna = models.CharField(max_length=300, blank=True, null=True)  # Numéro d’identification au répertoire national des associations

    # INFORMATIONS SUR LE SIEGE DE L’ENTREPRISE
    nicsiege = models.CharField(max_length=300, blank=True, null=True)  # Numéro interne de classement de l'établissement siège
    rpen = models.CharField(max_length=300, blank=True, null=True)  # Région de localisation du siège de l'entreprise
    depcomen = models.CharField(max_length=300, blank=True, null=True)  # Département et commune de localisation du siège de l'entreprise
    adr_mail = models.CharField(max_length=300, blank=True, null=True)  # Adresse mail

    # CARACTERISTIQUES ECONOMIQUES DE L’ENTREPRISE
    nj = models.CharField(max_length=300, blank=True, null=True)  # Nature juridique de l'entreprise
    libnj = models.CharField(max_length=300, blank=True, null=True)  # Libellé de la nature juridique
    apen700 = models.CharField(max_length=300, blank=True, null=True)  # Activité principale de l'entreprise
    libapen = models.CharField(max_length=300, blank=True, null=True)  # Libellé de l'activité principale de l'entreprise
    dapen = models.CharField(max_length=300, blank=True, null=True)  # Année de validité de l'activité principale de l'entreprise
    aprm = models.CharField(max_length=300, blank=True, null=True)  # Activité principale au registre des métiers
    ess = models.CharField(max_length=300, blank=True, null=True)  # Appartenance au champ de l’économie sociale et solidaire
    dateess = models.CharField(max_length=300, blank=True, null=True)  # Date ESS
    tefen = models.CharField(max_length=300, blank=True, null=True)  # Tranche d'effectif salarié de l'entreprise
    libtefen = models.CharField(max_length=300, blank=True, null=True)  # Libellé de la tranche d'effectif de l'entreprise
    efencent = models.CharField(max_length=300, blank=True, null=True)  # Effectif salarié de l'entreprise à la centaine près
    defen = models.CharField(max_length=300, blank=True, null=True)  # Année de validité de l'effectif salarié de l'entreprise
    categorie = models.CharField(max_length=300, blank=True, null=True)  # Catégorie d'entreprise
    dcren = models.CharField(max_length=300, blank=True, null=True)  # Année et mois de création de l'entreprise
    amintren = models.CharField(max_length=300, blank=True, null=True)  # Année et mois d'introduction de l'entreprise dans la base de diffusion
    monoact = models.CharField(max_length=300, blank=True, null=True)  # Indice de monoactivité de l'entreprise
    moden = models.CharField(max_length=300, blank=True, null=True)  # Modalité de l'activité principale de l'entreprise
    proden = models.CharField(max_length=300, blank=True, null=True)  # Caractère productif de l'entreprise
    essaann = models.CharField(max_length=300, blank=True, null=True)  # Année de validité des rubriques de niveau entreprise en provenance de l'ESA*
    tca = models.CharField(max_length=300, blank=True, null=True)  # Tranche de chiffre d'affaires pour les entreprises enquêtées par l'ESA*
    esaapen = models.CharField(max_length=300, blank=True, null=True)  # Activité principale de l'entreprise issue de l'ESA*
    esasec1n = models.CharField(max_length=300, blank=True, null=True)  # Première activité secondaire déclarée dans l'ESA*
    esasec2n = models.CharField(max_length=300, blank=True, null=True)  # Deuxième activité secondaire déclarée dans l'ESA*
    esasec3n = models.CharField(max_length=300, blank=True, null=True)  # Troisième activité secondaire déclarée dans l'ESA*
    esasec4n = models.CharField(max_length=300, blank=True, null=True)  # Quatrième activité secondaire déclarée dans l'ESA*

    # DONNEES SPECIFIQUES AUX MISES À JOUR
    vmaj = models.CharField(max_length=300, blank=True, null=True)  # Nature de la mise à jour (création, suppression, modification)
    vmaj1 = models.CharField(max_length=300, blank=True, null=True)  # Indicateur de mise à jour n°1
    vmaj2 = models.CharField(max_length=300, blank=True, null=True)  # Indicateur de mise à jour n°2
    vmaj3 = models.CharField(max_length=300, blank=True, null=True)  # Indicateur de mise à jour n°3
    datemaj = models.CharField(max_length=300, blank=True, null=True)  # Date de traitement de la mise à jour

    def __str__(self):
        return self.siren


class Lead(models.Model):
    email = models.CharField(max_length=150, blank=True, null=True)
    first_name = models.CharField(max_length=100, blank=True, null=True)
    last_name = models.CharField(max_length=100, blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    raw_address = models.CharField(max_length=150, blank=True, null=True)
    street = models.CharField(max_length=100, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    zip = models.CharField(max_length=5, blank=True, null=True)
    merchant = models.ForeignKey(Merchant, blank=True, null=True, on_delete=models.DO_NOTHING)

    signed_up_please = models.BooleanField(default=False)
    odoo_user_id = models.IntegerField(blank=True, null=True)

    # Auto Timestamp Generation
    created_date = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    modified_date = models.DateTimeField(auto_now=True, blank=True, null=True)

    def __str__(self):
        return self.email


class GameVoucher(models.Model):
    customer = models.ForeignKey(Customer, blank=True, null=True, on_delete=models.DO_NOTHING)
    merchant = models.ForeignKey(Merchant, blank=True, null=True, on_delete=models.DO_NOTHING)
    voucher_code = models.CharField(max_length=10, blank=True, null=True)
    voucher_value = models.IntegerField(blank=True, null=True)

    # Auto Timestamp Generation
    created_date = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    modified_date = models.DateTimeField(auto_now=True, blank=True, null=True)

    def __str__(self):
        return self.customer.email


class GameVoucherVernon(models.Model):
    email = models.CharField(max_length=150, blank=True, null=True)
    merchant = models.ForeignKey(Merchant, blank=True, null=True, on_delete=models.DO_NOTHING)
    voucher_code = models.CharField(max_length=10, blank=True, null=True)
    voucher_value = models.IntegerField(blank=True, null=True)

    # Auto Timestamp Generation
    created_date = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    modified_date = models.DateTimeField(auto_now=True, blank=True, null=True)

    def __str__(self):
        return self.email
