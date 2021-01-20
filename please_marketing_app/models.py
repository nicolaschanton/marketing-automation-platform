# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from django.db import models
from django.contrib.postgres.fields import ArrayField
from cloudinary.models import CloudinaryField
import uuid


class Neighborhood(models.Model):

    name = models.CharField(max_length=500, blank=True, null=True)
    odoo_id = models.IntegerField(blank=True, null=True)
    mw_id = models.IntegerField(blank=True, null=True)

    # Inhabitants Number
    inhabitants_number = models.IntegerField(blank=True, null=True)

    # Zip Code
    zip_codes = ArrayField(models.CharField(max_length=5, null=True, blank=True), null=True, blank=True)

    # TimeZone
    timezone = models.CharField(max_length=500, blank=True, null=True)

    # Opening Information
    is_open = models.NullBooleanField(default=True, blank=True, null=True)
    open_date = models.DateField(blank=True, null=True)

    # Auto Timestamp Generation
    created_date = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    modified_date = models.DateTimeField(auto_now=True, blank=True, null=True)

    def __str__(self):
        return self.name


class Customer(models.Model):

    # Raw ERP Data from DB
    odoo_user_id = models.IntegerField(blank=True, null=True)
    sharable_user_id = models.CharField(max_length=500, blank=True, null=True)
    first_name = models.CharField(max_length=500, blank=True, null=True)
    last_name = models.CharField(max_length=500, blank=True, null=True)
    email = models.EmailField()
    phone = models.CharField(max_length=500, blank=True, null=True)
    street = models.CharField(max_length=500, blank=True, null=True)
    zip = models.CharField(max_length=500, blank=True, null=True)
    city = models.CharField(max_length=500, blank=True, null=True)
    w_longitude = models.FloatField(blank=True, null=True)
    w_latitude = models.FloatField(blank=True, null=True)
    neighborhood = models.ForeignKey(Neighborhood, blank=True, null=True, on_delete=models.DO_NOTHING)
    cb = ArrayField(models.CharField(max_length=200, null=True, blank=True), null=True, blank=True)
    sign_up_date = models.DateTimeField(blank=True, null=True)
    app_version = models.CharField(max_length=500, blank=True, null=True)
    os_platform = models.CharField(max_length=500, blank=True, null=True)
    os_name = models.CharField(max_length=500, blank=True, null=True)
    os_version = models.CharField(max_length=500, blank=True, null=True)

    # Raw ERP Data from DB for checking purpose
    signed_up = models.NullBooleanField()
    test_user = models.NullBooleanField()
    marketing = models.NullBooleanField()
    archived = models.NullBooleanField()

    # Enriched Data: personal info
    family = models.NullBooleanField()
    gender = models.CharField(max_length=500, blank=True, null=True)
    age = models.IntegerField(blank=True, null=True)
    profile_picture = models.CharField(max_length=10000, blank=True, null=True)
    face_analysis = models.CharField(max_length=100000, blank=True, null=True)
    profile_url_facebook = models.CharField(max_length=10000, blank=True, null=True)
    profile_url_linkedin = models.CharField(max_length=10000, blank=True, null=True)
    profile_url_google = models.CharField(max_length=10000, blank=True, null=True)
    profile_url_twitter = models.CharField(max_length=10000, blank=True, null=True)
    profile_url_instagram = models.CharField(max_length=10000, blank=True, null=True)
    social_profiles_full_contact = models.CharField(max_length=100000, blank=True, null=True)
    birth_date = models.DateField(blank=True, null=True)

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

    favourite_dish = models.CharField(
        max_length=20,
        choices=FAVOURITE_DISH,
        blank=True,
        null=True,
    )

    # Enriched Data: professional info
    company = models.CharField(max_length=500, blank=True, null=True)
    job_title = models.CharField(max_length=500, blank=True, null=True)

    # Enriched Data: orders
    orders_number = models.IntegerField(blank=True, null=True)
    average_basket = models.FloatField(blank=True, null=True)
    average_rating = models.FloatField(blank=True, null=True)
    total_spent = models.FloatField(blank=True, null=True)
    total_voucher = models.FloatField(blank=True, null=True)
    last_order_date = models.DateTimeField(blank=True, null=True)

    # Enriched Data: Intercom User
    last_seen_ip = models.CharField(max_length=500, blank=True, null=True)
    unsubscribed_from_emails = models.NullBooleanField()
    marked_email_as_spam = models.NullBooleanField()
    last_request_at = models.DateTimeField(blank=True, null=True)
    session_count = models.IntegerField(blank=True, null=True)
    user_agent_data = models.CharField(max_length=500, blank=True, null=True)
    intercom_id = models.CharField(max_length=500, blank=True, null=True)
    user_id = models.CharField(max_length=500, blank=True, null=True)
    social_profiles_intercom = models.CharField(max_length=100000, blank=True, null=True)
    counter_reset_password = models.IntegerField(blank=True, null=True)

    # Enriched Data: Intercom Event
    device_brand = models.CharField(max_length=500, blank=True, null=True)
    device_model = models.CharField(max_length=500, blank=True, null=True)
    device_manufacturer = models.CharField(max_length=500, blank=True, null=True)
    carrier = models.CharField(max_length=500, blank=True, null=True)

    # Auto Timestamp Generation
    created_date = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    modified_date = models.DateTimeField(auto_now=True, blank=True, null=True)

    # First Import
    first_import_events_done = models.NullBooleanField()

    # Referral Code
    referral_code = models.CharField(max_length=500, blank=True, null=True)
    referral_leads_counter = models.IntegerField(blank=True, null=True)
    referral_counter = models.IntegerField(blank=True, null=True)

    # User ban
    baned = models.NullBooleanField()

    def __str__(self):
        return self.email


class Order(models.Model):
    odoo_order_id = models.IntegerField(blank=True, null=True)
    odoo_user_id = models.IntegerField(blank=True, null=True)
    neighborhood = models.ForeignKey(Neighborhood, blank=True, null=True, on_delete=models.DO_NOTHING)
    email = models.EmailField(blank=True, null=True)
    customer = models.ForeignKey(Customer, blank=True, null=True, on_delete=models.DO_NOTHING)

    odoo_order_state = models.CharField(max_length=500, blank=True, null=True)
    order_date = models.DateTimeField(blank=True, null=True)

    supplier_name = models.CharField(max_length=500, blank=True, null=True)
    mw_supplier_id = models.IntegerField(blank=True, null=True)
    odoo_supplier_id = models.IntegerField(blank=True, null=True)
    universe_name = models.CharField(max_length=500, blank=True, null=True)
    mw_universe_id = models.IntegerField(blank=True, null=True)
    odoo_universe_id = models.IntegerField(blank=True, null=True)
    offer_name = models.CharField(max_length=500, blank=True, null=True)
    mw_offer_id = models.IntegerField(blank=True, null=True)
    odoo_offer_id = models.IntegerField(blank=True, null=True)

    click_and_collect = models.NullBooleanField()
    delivery_amount = models.FloatField(blank=True, null=True)
    basket_amount = models.FloatField(blank=True, null=True)
    please_amount = models.FloatField(blank=True, null=True)
    partner_amount = models.FloatField(blank=True, null=True)
    paid_amount = models.FloatField(blank=True, null=True)

    delivery_street = models.CharField(max_length=500, blank=True, null=True)
    delivery_zip = models.CharField(max_length=500, blank=True, null=True)
    delivery_city = models.CharField(max_length=500, blank=True, null=True)

    rating = models.IntegerField(blank=True, null=True)
    comments = models.CharField(max_length=500, blank=True, null=True)

    voucher_code = models.CharField(max_length=500, blank=True, null=True)
    voucher_amount = models.FloatField(blank=True, null=True)
    voucher_name = models.CharField(max_length=500, blank=True, null=True)

    # First Order
    first_order = models.NullBooleanField()

    # Auto Timestamp Generation
    created_date = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    modified_date = models.DateTimeField(auto_now=True, blank=True, null=True)

    def __str__(self):
        return str(self.odoo_order_id)


class OrderLine(models.Model):
    odoo_order_line_id = models.IntegerField(blank=True, null=True)
    odoo_order_id = models.IntegerField(blank=True, null=True)
    odoo_user_id = models.IntegerField(blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    customer = models.ForeignKey(Customer, blank=True, null=True, on_delete=models.DO_NOTHING)

    label = models.CharField(max_length=500, blank=True, null=True)
    quantity = models.FloatField(blank=True, null=True)
    total_amount = models.FloatField(blank=True, null=True)

    # Auto Timestamp Generation
    created_date = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    modified_date = models.DateTimeField(auto_now=True, blank=True, null=True)

    def __str__(self):
        return str(self.odoo_order_id)


class IntercomEvent(models.Model):

    # Updated Event Data
    updated_ip = models.NullBooleanField()

    # Core Event Data
    customer = models.ForeignKey(Customer, blank=True, null=True, on_delete=models.DO_NOTHING)
    neighborhood = models.ForeignKey(Neighborhood, blank=True, null=True, on_delete=models.DO_NOTHING)
    event_name = models.CharField(max_length=500, blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)
    user_id = models.CharField(max_length=500, blank=True, null=True)
    intercom_user_id = models.CharField(max_length=500, blank=True, null=True)
    intercom_id = models.CharField(max_length=500, blank=True, null=True)
    channel = models.CharField(max_length=500, blank=True, null=True)

    # Event Metadata: Geolocation Data
    geo_country = models.CharField(max_length=500, blank=True, null=True)
    geo_city = models.CharField(max_length=500, blank=True, null=True)
    geo_zip_code = models.CharField(max_length=500, blank=True, null=True)
    geo_lat = models.FloatField(blank=True, null=True)
    geo_long = models.FloatField(blank=True, null=True)

    # Event Metadata: what are the users on while using our App?
    app_version = models.CharField(max_length=500, blank=True, null=True)
    os_platform = models.CharField(max_length=500, blank=True, null=True)
    os_name = models.CharField(max_length=500, blank=True, null=True)
    os_version = models.CharField(max_length=500, blank=True, null=True)
    device_brand = models.CharField(max_length=500, blank=True, null=True)
    device_model = models.CharField(max_length=500, blank=True, null=True)
    device_manufacturer = models.CharField(max_length=500, blank=True, null=True)
    carrier = models.CharField(max_length=500, blank=True, null=True)
    ip_address = models.CharField(max_length=500, blank=True, null=True)
    user_agent_data = models.CharField(max_length=500, blank=True, null=True)

    # Event Metadata: where the users are coming from?
    referer_domain = models.CharField(max_length=500, blank=True, null=True)

    # Event Metadata: checkout
    odoo_order_id = models.IntegerField(blank=True, null=True)
    universe_name = models.CharField(max_length=500, blank=True, null=True)
    mw_universe_id = models.IntegerField(blank=True, null=True)
    supplier_name = models.CharField(max_length=500, blank=True, null=True)
    mw_supplier_id = models.IntegerField(blank=True, null=True)
    offer_name = models.CharField(max_length=500, blank=True, null=True)
    mw_offer_id = models.IntegerField(blank=True, null=True)
    item_name = models.CharField(max_length=500, blank=True, null=True)
    mw_item_id = models.IntegerField(blank=True, null=True)
    item_list = ArrayField(models.CharField(max_length=20000, null=True, blank=True), null=True, blank=True)
    voucher_code = models.CharField(max_length=500, blank=True, null=True)
    voucher_name = models.CharField(max_length=500, blank=True, null=True)
    voucher_value = models.FloatField(blank=True, null=True)
    voucher_type = models.CharField(max_length=50, blank=True, null=True)
    delivery_amount = models.FloatField(blank=True, null=True)
    basket_amount = models.FloatField(blank=True, null=True)
    please_amount = models.FloatField(blank=True, null=True)
    partner_amount = models.FloatField(blank=True, null=True)
    delivery_street = models.CharField(max_length=500, blank=True, null=True)
    delivery_zip = models.CharField(max_length=500, blank=True, null=True)
    delivery_city = models.CharField(max_length=500, blank=True, null=True)
    order_date = models.DateTimeField(blank=True, null=True)
    minimum_basket_amount = models.FloatField(blank=True, null=True)
    rating = models.IntegerField(blank=True, null=True)
    click_and_collect = models.NullBooleanField()

    # Event Metadata: general
    point_count = models.IntegerField(blank=True, null=True)
    link = models.CharField(max_length=500, blank=True, null=True)
    campaign_name = models.CharField(max_length=500, null=True, blank=True)
    search_term = models.CharField(max_length=500, null=True, blank=True)
    offer_list = ArrayField(models.CharField(max_length=2000, null=True, blank=True), null=True, blank=True)

    # Amplitude Data
    sent_to_amplitude = models.NullBooleanField()

    # Auto Timestamp Generation
    created_date = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    modified_date = models.DateTimeField(auto_now=True, blank=True, null=True)

    def __str__(self):
        return self.event_name


class Fete(models.Model):

    first_name = models.CharField(max_length=500)
    month = models.IntegerField()
    day = models.IntegerField()

    # Auto Timestamp Generation
    created_date = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    modified_date = models.DateTimeField(auto_now=True, blank=True, null=True)

    def __str__(self):
        return self.first_name


class Merchant(models.Model):
    name = models.CharField(max_length=500, null=True, blank=True)
    neighborhood = models.ForeignKey(Neighborhood, on_delete=models.DO_NOTHING)
    email = models.CharField(max_length=500, null=True, blank=True)
    five_best = models.NullBooleanField()
    mw_offer_id = models.CharField(max_length=2000, null=True, blank=True)
    odoo_offer_id = models.CharField(max_length=2000, null=True, blank=True)
    universe_name = models.CharField(max_length=100, null=True, blank=True)
    rating = models.FloatField(default=5)
    rating_number = models.IntegerField(default=1)
    active = models.NullBooleanField()
    open = models.NullBooleanField()
    tags = ArrayField(models.CharField(max_length=500, blank=True, null=True), null=True, blank=True)

    # Picture
    picture_raw = CloudinaryField('image')

    # Auto Timestamp Generation
    created_date = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    modified_date = models.DateTimeField(auto_now=True, blank=True, null=True)

    def __str__(self):
        merchant_name = str(self.name + " - " + self.neighborhood.name)
        return merchant_name


class NotificationHistory(models.Model):
    customer = models.ForeignKey(Customer, blank=True, null=True, on_delete=models.DO_NOTHING)
    title = models.CharField(max_length=500, null=True, blank=True)
    content = models.CharField(max_length=500, null=True, blank=True)
    send_date = models.DateTimeField(null=True, blank=True)

    # Notification Type
    abandoned_cart = models.NullBooleanField()
    abandoned_sign_up = models.NullBooleanField()
    rediscover = models.NullBooleanField()
    discover = models.NullBooleanField()

    # Auto Timestamp Generation
    created_date = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    modified_date = models.DateTimeField(auto_now=True, blank=True, null=True)

    def __str__(self):
        return self.customer.email


class VoucherCode(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.DO_NOTHING)
    code = models.CharField(max_length=15)
    name = models.CharField(max_length=200)
    voucher_type = models.CharField(max_length=200)
    value = models.IntegerField()
    expiry_date = models.DateTimeField(null=True, blank=True)

    notification_type = models.CharField(max_length=200)

    # Auto Timestamp Generation
    created_date = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    modified_date = models.DateTimeField(auto_now=True, blank=True, null=True)

    def __str__(self):
        return self.code


class NetPromoterScore(models.Model):
    customer = models.ForeignKey(Customer, blank=True, null=True, on_delete=models.DO_NOTHING)
    score = models.IntegerField(null=True, blank=True)
    description = models.TextField(max_length=5000, null=True, blank=True)

    # Auto Timestamp Generation
    created_date = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    modified_date = models.DateTimeField(auto_now=True, blank=True, null=True)

    def __str__(self):
        return self.customer.email


class SmsHistory(models.Model):
    customer = models.ForeignKey(Customer, blank=True, null=True, on_delete=models.DO_NOTHING)
    content = models.CharField(max_length=500, null=True, blank=True)
    send_date = models.DateTimeField(null=True, blank=True)

    # Notification Type
    sms_type = models.CharField(max_length=500, null=True, blank=True)

    # Auto Timestamp Generation
    created_date = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    modified_date = models.DateTimeField(auto_now=True, blank=True, null=True)

    def __str__(self):
        return self.customer.email


class EmailHistory(models.Model):
    customer = models.ForeignKey(Customer, blank=True, null=True, on_delete=models.DO_NOTHING)
    content = models.CharField(max_length=500, null=True, blank=True)
    send_date = models.DateTimeField(null=True, blank=True)

    # Notification Type
    email_type = models.CharField(max_length=500, null=True, blank=True)

    # Auto Timestamp Generation
    created_date = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    modified_date = models.DateTimeField(auto_now=True, blank=True, null=True)

    def __str__(self):
        return self.customer.email


class DeliveryMan(models.Model):
    neighborhood = models.ForeignKey(Neighborhood, on_delete=models.DO_NOTHING)
    first_name = models.CharField(max_length=500, null=True, blank=True)
    last_name = models.CharField(max_length=500, null=True, blank=True)
    phone = models.CharField(max_length=500, null=True, blank=True)
    email = models.CharField(max_length=500, null=True, blank=True)
    sent_comment_request = models.NullBooleanField()

    # Auto Timestamp Generation
    created_date = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    modified_date = models.DateTimeField(auto_now=True, blank=True, null=True)

    def __str__(self):
        return self.email


class DeliveryManLead(models.Model):
    first_name = models.CharField(max_length=500, null=True, blank=True)
    last_name = models.CharField(max_length=500, null=True, blank=True)
    phone = models.CharField(max_length=500, null=True, blank=True)
    email = models.CharField(max_length=500, null=True, blank=True)
    city = models.CharField(max_length=500, null=True, blank=True)
    formatted_address = models.CharField(max_length=500, null=True, blank=True)
    lat = models.FloatField(null=True, blank=True)
    lng = models.FloatField(null=True, blank=True)
    cv_url = models.CharField(max_length=500, null=True, blank=True)
    message = models.TextField(max_length=5000, null=True, blank=True)

    # Auto Timestamp Generation
    created_date = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    modified_date = models.DateTimeField(auto_now=True, blank=True, null=True)

    def __str__(self):
        return self.email


class CityManager(models.Model):
    neighborhood = models.ForeignKey(Neighborhood, on_delete=models.DO_NOTHING)
    customer = models.ForeignKey(Customer, blank=True, null=True, on_delete=models.DO_NOTHING)
    first_name = models.CharField(max_length=500, null=True, blank=True)
    last_name = models.CharField(max_length=500, null=True, blank=True)
    phone = models.CharField(max_length=500, null=True, blank=True)
    email = models.CharField(max_length=500, null=True, blank=True)
    sent_comment_request = models.NullBooleanField()

    # Referral Code
    referral_codes = ArrayField(models.CharField(max_length=500, blank=True, null=True), null=True, blank=True)

    # Auto Timestamp Generation
    created_date = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    modified_date = models.DateTimeField(auto_now=True, blank=True, null=True)

    def __str__(self):
        return self.email


class SalesAnalysis(models.Model):
    merchant = models.ForeignKey(Merchant, on_delete=models.DO_NOTHING)

    viewed_offer = models.FloatField(blank=True, null=True)
    viewed_offer_30 = models.FloatField(blank=True, null=True)
    viewed_offer_60 = models.FloatField(blank=True, null=True)
    viewed_offer_trend = models.FloatField(blank=True, null=True)

    po_vo_ratio = models.FloatField(blank=True, null=True)
    po_vo_ratio_30 = models.FloatField(blank=True, null=True)
    po_vo_ratio_60 = models.FloatField(blank=True, null=True)
    po_vo_ratio_trend = models.FloatField(blank=True, null=True)

    average_rating = models.FloatField(blank=True, null=True)
    average_rating_30 = models.FloatField(blank=True, null=True)
    average_rating_60 = models.FloatField(blank=True, null=True)
    average_rating_trend = models.FloatField(blank=True, null=True)

    average_basket = models.FloatField(blank=True, null=True)
    average_basket_30 = models.FloatField(blank=True, null=True)
    average_basket_60 = models.FloatField(blank=True, null=True)
    average_basket_trend = models.FloatField(blank=True, null=True)

    average_please_amount = models.FloatField(blank=True, null=True)
    average_please_amount_30 = models.FloatField(blank=True, null=True)
    average_please_amount_60 = models.FloatField(blank=True, null=True)
    average_please_amount_trend = models.FloatField(blank=True, null=True)

    average_partner_amount = models.FloatField(blank=True, null=True)
    average_partner_amount_30 = models.FloatField(blank=True, null=True)
    average_partner_amount_60 = models.FloatField(blank=True, null=True)
    average_partner_amount_trend = models.FloatField(blank=True, null=True)

    order_number = models.FloatField(blank=True, null=True)
    order_number_30 = models.FloatField(blank=True, null=True)
    order_number_60 = models.FloatField(blank=True, null=True)
    order_number_trend = models.FloatField(blank=True, null=True)

    # Auto Timestamp Generation
    created_date = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    modified_date = models.DateTimeField(auto_now=True, blank=True, null=True)

    def __str__(self):
        return self.merchant.name


class SmsAuthorizationInProgress(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.DO_NOTHING)
    odoo_order_id = models.IntegerField(blank=True, null=True)
    sms_type = models.CharField(max_length=500, null=True, blank=True)

    # Auto Timestamp Generation
    created_date = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    modified_date = models.DateTimeField(auto_now=True, blank=True, null=True)

    def __str__(self):
        return self.customer.email


class Product(models.Model):
    mw_id = models.IntegerField(blank=True, null=True)
    type = models.CharField(blank=True, null=True, max_length=500)
    name = models.CharField(blank=True, null=True, max_length=500)
    version = models.IntegerField(blank=True, null=True)
    description = models.CharField(blank=True, null=True, max_length=500)
    price = models.FloatField(blank=True, null=True)
    unavailable = models.BooleanField(default=False)
    deleted = models.BooleanField(default=False)
    ingredients = models.CharField(blank=True, null=True, max_length=500)
    short_description = models.CharField(blank=True, null=True, max_length=500)

    # Auto Timestamp Generation
    created_date = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    modified_date = models.DateTimeField(auto_now=True, blank=True, null=True)

    def __str__(self):
        return self.product.name
