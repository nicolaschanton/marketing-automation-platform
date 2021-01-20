# coding: utf-8

import requests
import json
import sys
from please_marketing_app.models import Merchant
from please_marketing_pictures.models import MerchantPictureSource
from datetime import datetime, timedelta
from please_marketing_script_execution.log_script import log_script
from google.cloud import translate
import requests
from django.conf import settings
import cloudinary
from bs4 import BeautifulSoup
import os
import urllib.request


# from please_marketing_app.main_scripts.enrich_image_merchants import *
def query_unsplash(merchant, query):

    for page in [1, 2, 3, 4]:

        url = "https://unsplash.com/napi/search"

        querystring = {"query": str(query), "xp": "", "per_page": "20", "page": str(page)}

        headers = {
            'cache-control': "no-cache",
        }

        response = requests.request("GET", url, headers=headers, params=querystring).json()

        image_tuples = []
        ranking = 0

        print(response)

        for picture in response.get("photos").get("results"):
            ranking = ranking + 1
            if picture.get("likes") > 25:
                if "food" in json.dumps(picture.get("photo_tags")):
                    if ("person" not in str(json.dumps(picture.get("photo_tags"))).lower()) and ("people" not in str(json.dumps(picture.get("photo_tags"))).lower()) and ("person" not in str(picture.get("description")).lower()) and ("person" not in str(picture.get("description")).lower()):
                        image_tuples.append(
                            (
                                merchant,
                                query,
                                picture.get("id"),
                                picture.get("urls").get("regular"),
                                picture.get("likes"),
                                picture.get("description"),
                                json.dumps(picture.get("photo_tags")),
                                "safe_match" if (query.replace("food ", "") in str(json.dumps(picture.get("photo_tags"))).lower()) or (query.replace("food ", "") in str(picture.get("description")).lower()) else "risky_match",
                                ranking
                            )
                        )
                        picture_tags = []
                        for tag in picture.get("photo_tags"):
                            picture_tags.append(tag.get("title"))

                        if MerchantPictureSource.objects.filter(merchant=merchant, unsplash_id=picture.get("id")).count() == 0:
                            MerchantPictureSource(
                                merchant=merchant,
                                unsplash_id=picture.get("id"),
                                query=query,
                                url=picture.get("urls").get("regular"),
                                likes=picture.get("likes"),
                                description=picture.get("description"),
                                picture_tags=picture_tags,
                                match_type="sm" if (query.replace("food ", "") in str(json.dumps(picture.get("photo_tags"))).lower()) or (query.replace("food ", "") in str(picture.get("description")).lower()) else "rm",
                                ranking_search=ranking,
                            ).save()
    return


def google_translate(query):

    # Instantiate Client
    translate_client = translate.Client.from_service_account_json("please_marketing/google/PleaseMarketing-180914ffed4f.json")

    # The text to translate
    text = str(query)

    # The target language
    target = 'en'

    # Translation
    translation = translate_client.translate(
        text,
        target_language=target)

    translated = format(translation['translatedText'])

    return translated


def enrich_image_merchants():

    log_script(name="enrich_image_merchants", status="s")

    for merchant in Merchant.objects.filter():

        # Merchant Image Enrichment Part of the Script
        for tag in merchant.tags:
            if "€" not in tag:
                if len(tag) > 3:
                    s = google_translate(query=tag)
                    translated_query = str("food " + s)
                    query_unsplash(query=translated_query, merchant=merchant)

    log_script(name="enrich_image_merchants", status="d")

    return


def set_merchant_picture(merchant_picture_source):
    try:
        cloudinary.config(
            cloud_name=str(settings.CLOUDINARY_CLOUD_NAME),
            api_key=str(settings.CLOUDINARY_API_KEY),
            api_secret=str(settings.CLOUDINARY_API_SECRET)
        )

        merchant = merchant_picture_source.merchant
        img = cloudinary.uploader.upload(merchant_picture_source.url)
        merchant.picture_raw = img.get("public_id")
        merchant.save()

        merchant_picture_source.active = True
        merchant_picture_source.save()

    except:
        print(sys.exc_info())

    return


def elect_best_merchant_picture():

    # Clean deleted picture source
    for merchant_picture_source in MerchantPictureSource.objects.filter(deleted=True, active=True):
        merchant_picture_source.merchant.picture_raw = ''
        merchant_picture_source.merchant.save()

        merchant_picture_source.active = False
        merchant_picture_source.save()

    for merchant in Merchant.objects.filter(active=True, neighborhood__isnull=False, picture_raw=''):
        merchant_pictures_source = MerchantPictureSource.objects.filter(merchant=merchant, deleted=False)

        if merchant_pictures_source.count() > 0:
            merchant_pictures_used_in_neighborhood = MerchantPictureSource.objects.filter(
                merchant__in=Merchant.objects.filter(neighborhood=merchant.neighborhood),
                active=True
            )

            unsplash_id_list_exclusion = []
            for merchant_picture_used_in_neighborhood in merchant_pictures_used_in_neighborhood:
                unsplash_id_list_exclusion.append(merchant_picture_used_in_neighborhood.unsplash_id)

            mps_deduplicate = merchant_pictures_source.exclude(unsplash_id__in=unsplash_id_list_exclusion)

            if mps_deduplicate.filter(match_type="sm").count() == 0:
                set_merchant_picture(merchant_picture_source=mps_deduplicate.order_by("ranking_search").order_by("-likes").first())

            elif mps_deduplicate.count() > 0:
                set_merchant_picture(merchant_picture_source=mps_deduplicate.filter(match_type="sm").order_by("ranking_search").order_by("-likes").first())

    return


def clean():

    MerchantPictureSource.objects.all().update(active=False)
    Merchant.objects.all().update(picture_raw='')
    return


# from please_marketing_app.main_scripts.enrich_image_merchants import *
def set_merchant_picture_from_please():

    cloudinary.config(
        cloud_name=str(settings.CLOUDINARY_CLOUD_NAME),
        api_key=str(settings.CLOUDINARY_API_KEY),
        api_secret=str(settings.CLOUDINARY_API_SECRET)
    )

    for merchant in Merchant.objects.filter(active=True):
        if not merchant.picture_raw:
            for extension in ["jpg", "jpeg", "png"]:
                try:
                    url = str("https://mw.please-it.com/next-mw/api/public/website/services/menu/" + str(merchant.mw_offer_id))
                    response = requests.request("GET", url)

                    print(response.json())

                    if response.status_code == 200:
                        image_tag = response.json().get("imageTag")

                        url_img = str("https://mw.please-it.com/assets/Please/offers/" + str(image_tag) + "/menu/menu." + str(extension))

                        img = cloudinary.uploader.upload(url_img)
                        merchant.picture_raw = img.get("public_id")
                        merchant.save()

                    else:
                        pass

                except:
                    print(sys.exc_info())

    return


def transform_picture_from_please():
    cloudinary.config(
        cloud_name=str(settings.CLOUDINARY_CLOUD_NAME),
        api_key=str(settings.CLOUDINARY_API_KEY),
        api_secret=str(settings.CLOUDINARY_API_SECRET)
    )

    html = requests.request("GET", "https://mw.please-it.com/assets/Please/offers/").text
    soup = BeautifulSoup(html, "html.parser")

    merchants = soup.find_all("a")[6:]

    for merchant in merchants:

        merchant_clean = BeautifulSoup(merchant.text, "html.parser")

        main_folder_name = str(merchant_clean)

        html_2 = requests.request("GET", "https://mw.please-it.com/assets/Please/offers/" + str(merchant_clean)).text
        soup_2 = BeautifulSoup(html_2, "html.parser")

        folders = soup_2.find_all("a")[5:]

        for folder in folders:

            folder_clean = BeautifulSoup(folder.text, "html.parser")

            folder_name = str(folder_clean)

            html_3 = requests.request("GET", "https://mw.please-it.com/assets/Please/offers/" + str(merchant_clean) + str(folder_clean)).text

            soup_3 = BeautifulSoup(html_3, "html.parser")

            images = soup_3.find_all("a")[5:]

            for image in images:

                image_name = BeautifulSoup(image.text, "html.parser")

                try:
                    url_img = str("https://mw.please-it.com/assets/Please/offers/" + str(merchant_clean) + str(folder_clean) + str(image_name))

                    result = cloudinary.uploader.upload(
                        url_img,
                        use_filename=True,
                        unique_filename=False,
                        format='jpg',
                        quality=50 if "products" in folder_clean else 80,
                        folder=str("please_mw/" + str(main_folder_name) + "/" + str(folder_name)),
                        overwrite=True,
                    )

                    res = cloudinary.uploader.upload(
                        "https://mw.please-it.com/assets/Please/offers/50sdiner/products/coca_cola_cherry_33_cl_640x400.png",
                        use_filename=True,
                        unique_filename=False,
                        format='jpg',
                        quality=50,
                        folder=str("please_mw_test/"),
                        overwrite=True,
                    )

                    cloudinary.api.resources(
                        type="upload",
                        prefix="please_mw/")

                except:
                    print(sys.exc_info())

    return


def transform_all():

    cloudinary.config(
        cloud_name=str(settings.CLOUDINARY_CLOUD_NAME),
        api_key=str(settings.CLOUDINARY_API_KEY),
        api_secret=str(settings.CLOUDINARY_API_SECRET)
    )

    results = cloudinary.api.resources(
        type="upload",
        prefix="please_all/",
    )

    next_cursor = results.get("next_cursor")

    while next_cursor is not None:
        results = cloudinary.api.resources(
            type="upload",
            prefix="please_all/",
            next_cursor=next_cursor,
        )

        for result in results:
            try:
                image_url = result.get("url").replace(".png", ".jpg")

                if "products" in image_url:
                    image_url = image_url.replace("/image/upload/", "/image/upload/q_50")

                urllib.urlretrieve(
                    image_url,
                    image_url.replace(
                        "http://res.cloudinary.com/haxzc1afw/image/upload/v1553204417/",
                        "/Users/nicolaschanton/Desktop/"
                    )
                )

            except:
                print(sys.exc_info())

        next_cursor = results.get("next_cursor")

    return


# from please_marketing_app.main_scripts.enrich_image_merchants import *
# python3 manage.py shell --settings=please_marketing.settings_dev
def convert_please_images():

    cloudinary.config(
        cloud_name=str(settings.CLOUDINARY_CLOUD_NAME),
        api_key=str(settings.CLOUDINARY_API_KEY),
        api_secret=str(settings.CLOUDINARY_API_SECRET)
    )

    for root, dirs, files in os.walk(os.path.abspath("/Users/nicolaschanton/Downloads/please_all")):
        for file in files:
            try:
                file_path = os.path.join(root, file)
                folder_path = root.replace("/Users/nicolaschanton/Downloads/", "")

                result = cloudinary.uploader.upload(
                    file_path,
                    use_filename=True,
                    unique_filename=False,
                    format='jpg',
                    quality=50 if "products" in folder_path else 80,
                    folder=folder_path,
                    overwrite=True,
                )

                image_url = result.get("secure_url")

                if '.png' in file_path:
                    file_path = file_path.replace(".png", ".jpg")

                print(image_url, file_path)

                urllib.request.urlretrieve(image_url, file_path)

            except:
                print(sys.exc_info())
    return


def clean_directory():
    for root, dirs, files in os.walk(os.path.abspath("/Users/nicolaschanton/Desktop/please_all")):
        for file in files:
            try:
                if '.png' in file:
                    file_path = os.path.join(root, file)
                    print(file_path)
                    os.remove(file_path)
            except:
                print(sys.exc_info())

    return
