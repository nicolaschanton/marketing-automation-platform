# -*- coding: utf-8 -*-

import django
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "please_marketing.settings")
django.setup()
from please_marketing_app.models import *
from apscheduler.schedulers.blocking import BlockingScheduler
from rq import Queue
from worker_background_tasks import conn_background_tasks
from worker_urgent_tasks import conn_urgent_tasks
from worker_mid_urgent_tasks import conn_mid_urgent_tasks
from worker_etl import conn_etl

from please_marketing_app.main_scripts.intercom import executor_save_intercom_events_2, \
    executor_save_intercom_events_30, executor_update_intercom_users, executor_update_local_users
from please_marketing_app.main_scripts.erp import update_total_voucher, update_total_spent, update_orders_number, \
    update_last_order_date, update_counter_password, update_user_device, update_average_mark, update_average_basket,\
    update_address, update_gender, update_no_orders_done, executor_update_intercom_events_ip, \
    update_intercom_events_neighborhood, update_paid_order_events, executor_update_paid_amount, \
    update_marketing_archived, update_user_device_30

from please_marketing_app.main_scripts.wish_feast import wish_feast

from please_marketing_app.main_scripts.amplitude import executor_update_amplitude_events, \
    executor_update_amplitude_users

from please_marketing_app.main_scripts.abandoned_cart import abandoned_cart_voucher, abandoned_cart

from please_marketing_app.main_scripts.deduplicate import deduplicate_events, deduplicate_nps

from please_marketing_app.main_scripts.best_merchants import elect_best_merchants

from please_marketing_recommendation.cos_sim import executor_cos_sim_all, create_all_vector_booking

from please_marketing_referral_program.referral_program import executor_retrieve_used_referral_codes, \
    create_referral_code, send_leads_to_intercom
from please_marketing_app.promo_campaigns.one_book_one_voucher import executor_one_book_one_voucher
from please_marketing_leaderboard.leaderboard_referral_city_manager import retrieve_voucher_code_leaderboard, send_leaderboard_results
from please_marketing_extra_user_enrichment.address_enrichment import executor_get_prices, get_data_from_sl
from please_marketing_extra_user_enrichment.ban_user import executor_ban_user
from please_marketing_app.main_scripts.first_order import executor_flag_first_order
from please_marketing_etl.etl_update_delivery_men_leads import import_update_delivery_men_leads
from please_marketing_etl.etl_regular import import_etl_regular
from please_marketing_etl.etl_update_customers import import_etl_update_customers, import_etl_update_customers_phone
from please_marketing_etl.etl_update_merchants import import_etl_update_merchant, import_etl_update_merchant_open
from please_marketing_etl.etl_aip_orders import execute_aip_orders
from please_marketing_campaign.send_launch_campaign import send_launch_campaign
from please_marketing_campaign.send_notification_campaign import send_notification_campaign
from please_marketing_campaign.send_sms_campaign import send_sms_campaign
from please_marketing_app.main_scripts.non_activated_users_15_days import launch_non_activated_users_15_days
from please_marketing_app.main_scripts.enrich_image_merchants import set_merchant_picture_from_please
from please_marketing_campaign.send_cron_campaigns import send_cron_campaigns
from please_marketing_app.main_scripts.kpis import send_weekly_report, executor_analyze_merchant, send_landing_pages_report
import logging
import sys
import random
logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)


sched = BlockingScheduler()

q_background = Queue(connection=conn_background_tasks)
q_urgent_tasks = Queue(connection=conn_urgent_tasks)
q_mid_urgent_tasks = Queue(connection=conn_mid_urgent_tasks)
q_etl = Queue(connection=conn_etl)


# BACKGROUND CRONS
@sched.scheduled_job('cron', hour=23)
def background_tasks_daily():
    q_background.enqueue(executor_save_intercom_events_2, job_timeout=36000)
    q_background.enqueue(send_leads_to_intercom, job_timeout=360)
    q_background.enqueue(set_merchant_picture_from_please, job_timeout=1200)
    q_background.enqueue(deduplicate_events, job_timeout=1200)
    q_background.enqueue(deduplicate_nps, job_timeout=1200)
    q_background.enqueue(executor_update_intercom_events_ip, job_timeout=7200)
    q_background.enqueue(update_intercom_events_neighborhood, job_timeout=3600)
    q_background.enqueue(update_paid_order_events, job_timeout=7200)
    q_background.enqueue(update_gender, job_timeout=3600)
    q_background.enqueue(update_address, job_timeout=3600)
    q_background.enqueue(update_counter_password, job_timeout=3600)
    q_background.enqueue(update_user_device, job_timeout=3600)
    # q_background.enqueue(get_data_from_sl, job_timeout=7200)
    q_background.enqueue(update_marketing_archived, job_timeout=30)
    q_background.enqueue(update_last_order_date, job_timeout=3600)
    q_background.enqueue(update_average_basket, job_timeout=3600)
    q_background.enqueue(update_average_mark, job_timeout=3600)
    q_background.enqueue(update_orders_number, job_timeout=3600)
    q_background.enqueue(update_total_spent, job_timeout=3600)
    q_background.enqueue(update_total_voucher, job_timeout=3600)
    q_background.enqueue(update_no_orders_done, job_timeout=3600)
    q_background.enqueue(executor_flag_first_order, job_timeout=3600)
    q_background.enqueue(executor_update_intercom_users, job_timeout=36000)
    q_background.enqueue(executor_update_amplitude_users, job_timeout=3600)
    q_background.enqueue(executor_update_amplitude_events, job_timeout=36000)
    q_background.enqueue(create_referral_code, job_timeout=7200)
    q_background.enqueue(elect_best_merchants, job_timeout=3600)
    q_background.enqueue(retrieve_voucher_code_leaderboard, job_timeout=600)
    q_background.enqueue(executor_update_paid_amount, job_timeout=600)


@sched.scheduled_job('cron', day_of_week=0, hour=15)
def background_tasks_weekly():
    q_background.enqueue(executor_update_local_users, job_timeout=36000)
    q_background.enqueue(send_weekly_report, job_timeout=180)
    q_background.enqueue(send_landing_pages_report, job_timeout=600)
    q_background.enqueue(executor_analyze_merchant, job_timeout=3600)
#     q_background.enqueue(create_all_vector_booking, job_timeout=7200)
#     q_background.enqueue(executor_cos_sim_all, job_timeout=7200)


@sched.scheduled_job('cron', day=1, hour=13)
def background_tasks_monthly():
    # q_background.enqueue(send_leaderboard_results, job_timeout=600)
    q_background.enqueue(executor_save_intercom_events_30, job_timeout=86400)
    q_background.enqueue(update_user_device_30, job_timeout=14400)
    q_background.enqueue(executor_ban_user, job_timeout=3600)


# ETL CRONS
@sched.scheduled_job('interval', minutes=30)
def etl_tasks_hourly():
    q_etl.enqueue(import_etl_regular, job_timeout=1500)


@sched.scheduled_job('interval', hours=6)
def etl_tasks_daily():
    q_etl.enqueue(import_etl_update_customers, job_timeout=900)
    q_etl.enqueue(import_etl_update_merchant, job_timeout=900)
    q_etl.enqueue(import_update_delivery_men_leads, job_timeout=900)
    q_etl.enqueue(import_etl_update_customers_phone, job_timeout=3600)


# MID URGENT CRONS
@sched.scheduled_job('interval', hours=1)
def mid_urgent_tasks_daily():
    q_mid_urgent_tasks.enqueue(executor_retrieve_used_referral_codes, job_timeout=900)


@sched.scheduled_job('interval', minutes=2)
def mid_urgent_tasks_send_notification_campaign():
    # q_mid_urgent_tasks.enqueue(execute_aip_orders, job_timeout=120)
    q_mid_urgent_tasks.enqueue(send_notification_campaign, job_timeout=7200)
    q_mid_urgent_tasks.enqueue(send_launch_campaign, job_timeout=7200)
    q_mid_urgent_tasks.enqueue(send_sms_campaign, job_timeout=7200)
    q_mid_urgent_tasks.enqueue(send_cron_campaigns, job_timeout=7200)
    # q_mid_urgent_tasks.enqueue(executor_one_book_one_voucher, job_timeout=600)


# URGENT CRONS
@sched.scheduled_job('interval', minutes=2)
def urgent_tasks_abandoned_cart():
    coin = random.randint(0, 1)
    if coin == 0:
        q_urgent_tasks.enqueue(abandoned_cart, job_timeout=90)
    elif coin == 1:
        q_urgent_tasks.enqueue(abandoned_cart, job_timeout=90)


sched.start()
