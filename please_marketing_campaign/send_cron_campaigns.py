# -*- coding: utf-8 -*-

from please_marketing_app.models import Merchant, Customer, Neighborhood, SmsHistory
from please_marketing_campaign.models import CronCampaign
from please_marketing_app.main_scripts.nps import send_nps
from please_marketing_app.main_scripts.comment_request import executor_send_comment_request_nps_fan
from please_marketing_referral_program.referral_remember import executor_send_sms_remember
from please_marketing_app.main_scripts.non_activated_users_15_days import launch_non_activated_users_15_days
from datetime import datetime, timedelta
import sys
from django.conf import settings


# from please_marketing_campaign.send_cron_campaigns import *
def send_cron_campaigns():

    for cron_campaign in CronCampaign.objects.filter(
            active=True,
            campaign_is_sending=False,
            script_target="RPR",
            campaign_send_time__lte=datetime.now().time(),
            campaign_send_time__gte=(datetime.now() - timedelta(minutes=2)).time()
    ):

        cron_campaign.campaign_is_sending = True
        cron_campaign.save()

        # Function to be executed
        executor_send_sms_remember(neighborhoods=cron_campaign.neighborhoods.all())

        # Update campaign status to done
        cron_campaign.campaign_is_sending = False
        cron_campaign.save()

    for cron_campaign in CronCampaign.objects.filter(
            active=True,
            campaign_is_sending=False,
            script_target="NPS",
            campaign_send_time__lte=datetime.now().time(),
            campaign_send_time__gte=(datetime.now() - timedelta(minutes=2)).time()
    ):
        cron_campaign.campaign_is_sending = True
        cron_campaign.save()

        # Function to be executed
        send_nps(neighborhoods=cron_campaign.neighborhoods.all())

        # Update campaign status to done
        cron_campaign.campaign_is_sending = False
        cron_campaign.save()

    for cron_campaign in CronCampaign.objects.filter(
            active=True,
            campaign_is_sending=False,
            script_target="FCR",
            campaign_send_time__lte=datetime.now().time(),
            campaign_send_time__gte=(datetime.now() - timedelta(minutes=2)).time()
    ):
        cron_campaign.campaign_is_sending = True
        cron_campaign.save()

        # Function to be executed
        executor_send_comment_request_nps_fan(neighborhoods=cron_campaign.neighborhoods.all())

        # Update campaign status to done
        cron_campaign.campaign_is_sending = False
        cron_campaign.save()

    for cron_campaign in CronCampaign.objects.filter(
            active=True,
            campaign_is_sending=False,
            script_target="LNA",
            campaign_send_time__lte=datetime.now().time(),
            campaign_send_time__gte=(datetime.now() - timedelta(minutes=2)).time()
    ):
        cron_campaign.campaign_is_sending = True
        cron_campaign.save()

        # Function to be executed
        launch_non_activated_users_15_days(neighborhoods=cron_campaign.neighborhoods.all())

        # Update campaign status to done
        cron_campaign.campaign_is_sending = False
        cron_campaign.save()

    return
