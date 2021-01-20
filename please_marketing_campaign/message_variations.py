# -*- coding: utf-8 -*-

import emoji


launch_notification_variations = (
    str(
        str("[OUVERTURE ")
        + emoji.emojize(u':sparkles:', use_aliases=True)
        + str("] ")
        + str("@merchant_name disponible dès à présent sur Please !")
    ),

    str(
        str("[OUVERTURE ")
        + emoji.emojize(u':sparkles:', use_aliases=True)
        + str("] ")
        + str("Découvrez @merchant_name dès à présent sur Please !")
    ),

    str(
        str("[OUVERTURE ")
        + emoji.emojize(u':sparkles:', use_aliases=True)
        + str("] ")
        + str("On vous met au défi de tester @merchant_name ce soir ! Prêt ? C’est parti !")
        + emoji.emojize(u':rocket:', use_aliases=True)
    ),

    str(
        str("[NOUVEAUTÉ ")
        + emoji.emojize(u':sparkles:', use_aliases=True)
        + str("] ")
        + str("Aujourd'hui @merchant_name ouvre sur Please !")
    ),

    str(
        str("[NOUVEAUTÉ ")
        + emoji.emojize(u':sparkles:', use_aliases=True)
        + str("] ")
        + str("Et si vous testiez @merchant_name aujourd’hui ? Il vient d’arriver sur l’App !")
    ),

    str(
        str("[NOUVEAUTÉ ")
        + emoji.emojize(u':sparkles:', use_aliases=True)
        + str("] ")
        + str("@merchant_name est disponible en livraison dès aujourd’hui sur Please !")
    ),

    str(
        str("[NOUVEAUTÉ ")
        + emoji.emojize(u':sparkles:', use_aliases=True)
        + str("] ")
        + str("Découvrez la carte de @merchant_name disponible en livraison sur Please !")
    ),

    str(
        str("[OUVERTURE ")
        + str("@merchant_name ")
        + emoji.emojize(u':sparkles:', use_aliases=True)
        + str("] ")
        + str("En livraison dès à présent sur Please !")
    ),

    str(
        str("[OUVERTURE ")
        + str("@merchant_name ")
        + emoji.emojize(u':sparkles:', use_aliases=True)
        + str("] ")
        + str("Disponible en commande dès aujourd’hui !")
    ),
)

launch_email_variations = (

    str("Découvrez dès aujourd’hui @merchant_name en livraison avec Please !\n"
        "Nous vous offrons 3€ pour tester ce nouveau commerce avec le code @voucher_code (valable 7 jours) 🎁"),

    str("En exclusivité, découvrez @merchant_name en livraison avec Please ✨ !\n"
        "Bénéficiez de 3€ offerts avec le code @voucher_code valable pendant 7 jours. 🎁"),

    str("Please vous fait découvrir @merchant_name !\n"
        "Commandez et faites vous livrer dès ce soir et bénéficiez de 3€ OFFERTS "
        "avec le code @voucher_code (valable pendant 7 jours)"),

    str("Découverte du jour : @merchant_name ✨ !\nDisponible dès à présent en livraison sur Please. "
        "Pour le tester, nous vous offrons 3€ avec le code @voucher_code (valable pendant 7 jours) 🎁"),

)

launch_email_subject_variations = (

    str("@first_name, venez découvrir @merchant_name dans Please !"),

    str("@first_name, @merchant_name disponible dans Please !"),

    str("@first_name, @merchant_name en livraison dans Please !"),

    str("@first_name, @merchant_name ouvre dans Please !"),

    str("@first_name, venez (re)découvrir @merchant_name grâce à Please !"),

    str("[OUVERTURE] @first_name, @merchant_name débarque dans Please !"),

    str("[OUVERTURE] @merchant_name arrive dans Please !"),

    str("[OUVERTURE] @first_name, commandez @merchant_name dès maintenant !"),

)
