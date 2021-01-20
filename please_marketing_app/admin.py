# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from django.contrib import admin
from .models import Customer, OrderLine, Order, IntercomEvent, Fete, Neighborhood, Merchant, \
    NotificationHistory, NetPromoterScore, VoucherCode, SmsHistory, \
    DeliveryMan, CityManager, EmailHistory, DeliveryManLead, SalesAnalysis, SmsAuthorizationInProgress, Product


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    search_fields = ["first_name", "last_name", "email"]
    list_filter = ["neighborhood", "signed_up"]
    list_display = ["first_name", "last_name", "email", "neighborhood", "created_date", "modified_date"]
    pass


@admin.register(IntercomEvent)
class IntercomEventAdmin(admin.ModelAdmin):
    list_filter = ["event_name", "neighborhood", "sent_to_amplitude", "updated_ip"]
    list_display = ["event_name", "customer", "created_at", "created_date", "modified_date"]
    search_fields = ["intercom_id"]
    list_display_links = None
    pass


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_filter = ["neighborhood", "supplier_name"]
    list_display = ["customer", "supplier_name", "created_date"]
    pass


@admin.register(Neighborhood)
class NeighborhoodAdmin(admin.ModelAdmin):
    list_display = [
        "name",
        "mw_id",
        "odoo_id",
        "is_open",
        "open_date",
        "inhabitants_number"
    ]
    pass


@admin.register(Merchant)
class MerchantAdmin(admin.ModelAdmin):
    search_fields = ["name"]
    list_filter = ["neighborhood"]
    list_display = ["name", "neighborhood", "active", "five_best"]
    pass


@admin.register(Fete)
class FeteAdmin(admin.ModelAdmin):
    search_fields = ["first_name"]
    list_filter = ["first_name"]
    list_display = ["first_name", "day", "month"]
    pass


@admin.register(OrderLine)
class OrderLineAdmin(admin.ModelAdmin):
    list_filter = ["customer"]
    list_display = ["label", "odoo_order_id", "customer"]
    pass


@admin.register(NotificationHistory)
class NotificationHistoryAdmin(admin.ModelAdmin):
    list_display = ["title", "customer", "created_date"]
    list_filter = ["created_date", "title"]
    pass


@admin.register(NetPromoterScore)
class NetPromoterScoreAdmin(admin.ModelAdmin):
    list_display = ["customer", "score", "description", "created_date"]
    list_filter = ["created_date", "score"]
    pass


@admin.register(VoucherCode)
class VoucherCodeAdmin(admin.ModelAdmin):
    list_display = ["customer", "code", "name", "voucher_type", "value", "expiry_date", "notification_type"]
    list_filter = ["voucher_type", "notification_type"]
    pass


@admin.register(SmsHistory)
class SmsHistoryAdmin(admin.ModelAdmin):
    list_display = ["customer", "content", "send_date"]
    list_filter = ["sms_type", "created_date"]
    pass


@admin.register(EmailHistory)
class EmailHistoryAdmin(admin.ModelAdmin):
    list_display = ["customer", "content", "send_date"]
    list_filter = ["email_type", "created_date"]
    pass


@admin.register(DeliveryMan)
class DeliveryManAdmin(admin.ModelAdmin):
    search_fields = ["email"]
    list_filter = ["neighborhood"]
    list_display = ["first_name", "last_name", "email", "phone", "neighborhood"]
    pass


@admin.register(DeliveryManLead)
class DeliveryManLeadAdmin(admin.ModelAdmin):
    search_fields = ["email"]
    list_filter = ["city"]
    list_display = ["first_name", "last_name", "email", "phone", "city", "formatted_address", "created_date"]
    pass


@admin.register(CityManager)
class CityManagerAdmin(admin.ModelAdmin):
    search_fields = ["email"]
    list_filter = ["neighborhood"]
    list_display = ["first_name", "last_name", "email", "phone", "neighborhood"]
    pass


@admin.register(SalesAnalysis)
class SalesAnalysisAdmin(admin.ModelAdmin):
    search_fields = ["merchant__name"]
    list_filter = ["merchant__neighborhood"]
    list_display = [
        "merchant",
        "viewed_offer",
        "viewed_offer_30",
        "viewed_offer_60",
        "viewed_offer_trend",
        "po_vo_ratio",
        "po_vo_ratio_30",
        "po_vo_ratio_60",
        "po_vo_ratio_trend",
        "average_rating",
        "average_rating_30",
        "average_rating_60",
        "average_rating_trend",
        "average_basket",
        "average_basket_30",
        "average_basket_60",
        "average_basket_trend",
        "average_please_amount",
        "average_please_amount_30",
        "average_please_amount_60",
        "average_please_amount_trend",
        "average_partner_amount",
        "average_partner_amount_30",
        "average_partner_amount_60",
        "average_partner_amount_trend",
        "order_number",
        "order_number_30",
        "order_number_60",
        "order_number_trend",
    ]
    pass


@admin.register(SmsAuthorizationInProgress)
class SmsAuthorizationInProgressAdmin(admin.ModelAdmin):
    list_display = ["customer", "odoo_order_id", "sms_type", "created_date", "modified_date"]
    search_fields = ["customer__email", "customer__last_name"]
    pass


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = [
        "mw_id",
        "type",
        "name",
        "version",
        "description",
        "price",
        "unavailable",
        "deleted",
        "ingredients",
        "short_description",
        "created_date",
        "modified_date"
    ]
    list_filter = ["deleted", "unavailable", "version", "type"]
    search_fields = ["name", "mw_id"]
    pass
