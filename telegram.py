from telebot.async_telebot import AsyncTeleBot
import datetime
from database.db import userDB, serviceManagement, general
from price.get_price import tether
import asyncio
import aiohttp
import hashlib
import re
from telebot.async_telebot import types
from telebot.types import ReplyKeyboardRemove
from datetime import timedelta
import random
from database.db import DBPool
from dotenv import load_dotenv
import os
import math
import redis

##########################################################

load_dotenv()

TOKEN = os.getenv("TOKEN")

##########################################################

rdb = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
db_pool = DBPool.get_instance()
allUser = userDB(db_pool)
services = serviceManagement(db_pool)
services.create_table_andicator()
services.create_table_license()
services.create_table_services()
services.create_table_trial()
services.create_table_license_pro()
services.create_table_andicator_u()
generall = general(db_pool)
generall.create_table_admin()

##########################################################

async def check_expirations3():
    while True:
        try:
            expired_users = services.get_trial()
            
            today = datetime.date.today()
    #        today = jdatetime.date(1405, 10, 1)
            
            for user in expired_users:
                chat_id = user[0]
                info = allUser.get_info(chat_id)
                fullname = f"{info[0]} {info[1]}"
                phone = info[2]
                p = services.get_service(chat_id)[0]
                pu = services.get_service_u(chat_id)[0]
                # pb = services.get_service_bot(chat_id)[0]
                # pp = services.get_service_pro(chat_id)[0]
                if p == 'trial' or pu == 'trial':# or pb == 'trial':
                    user_exp_date = user[1]
                    if user_exp_date and today >= user_exp_date:
                        msg = "⚠️ مشترک گرامی،اشتراک 3 روزه شما پایان یافته است. برای خرید اشتراک از دستور /خرید استفاده کنید."
                        try:
                            res = await bot.send_message(chat_id, msg)
                        except Exception as e:
                            print(e)
                        await bot.send_message(support_group_id, f"اشتراک کاربر به پایان رسید:\nنام و نام خانوادگی:{fullname}\nشماره تلفن:{phone}\nاشتراک: {p}", reply_markup=keyboard_claim)
                        services.set_expiration_notified3(chat_id)
                        services.set_expiration_ban_u(chat_id)
                        services.set_expiration_notified_u(chat_id)
                        # services.set_expiration_ban_bot(chat_id)
                        # services.set_expiration_ban_pro(chat_id)
                        if p == 'trial':
                            services.set_service(chat_id=chat_id, service='None')
                        if pu == 'trial':
                            services.set_service_u(chat_id=chat_id, service='None')
                        try:
                            await bot.kick_chat_member(vip_id, chat_id)
                        except:
                            pass
                    await asyncio.sleep(10)
        except:
            pass
        await asyncio.sleep(10800)

async def check_expirations_ban():
    while True:
        try:
            expired_users = services.get_expired_users_to_ban()
            
            today = datetime.date.today()
    #        today = jdatetime.date(1405, 10, 1)
        
            for user in expired_users:
                chat_id = user[0]
                info = allUser.get_info(chat_id)
                fullname = f"{info[0]} {info[1]}"
                phone = info[2]
                p = services.get_service(chat_id)[0]
                user_exp_date = user[1]
                if user_exp_date and today >= user_exp_date:
                    msg = "⚠️ اشتراک شما به پایان رسید\nبرای خرید اشتراک از دستور /خرید استفاده کنید."
                    try:
                        await bot.send_message(chat_id, msg)
                    except:
                        pass
                    await bot.send_message(support_group_id, f"اشتراک کاربر به پایان رسید:\nنام و نام خانوادگی:{fullname}\nشماره تلفن:{phone}\nاشتراک:اندیکاتور {p}", reply_markup=keyboard_claim)
                    services.set_service(chat_id=chat_id, service='None')
                    services.set_expiration_ban(chat_id)
                    try:
                        await bot.kick_chat_member(vip_id, chat_id)
                    except:
                        pass
                await asyncio.sleep(10)
        except:
            pass
        await asyncio.sleep(10800)

async def check_expirations():
    while True:
        try:
            expired_users = services.get_expired_users_to_notify()
            
            today = datetime.date.today()
            
            for user in expired_users:
                chat_id = user[0]
                info = allUser.get_info(chat_id)
                fullname = f"{info[0]} {info[1]}"
                phone = info[2]
                p = services.get_service(chat_id)[0]
                user_exp_date = user[1]
                today = today - timedelta(days=3)
                if user_exp_date and today >= user_exp_date:
                    msg = "⚠️ مشترک گرامی، 3 روز از اشتراک شما باقی مانده است. برای تمدید از دستور /تمدید استفاده کنید."
                    try:
                        await bot.send_message(chat_id, msg)
                    except:
                        pass
                    await bot.send_message(support_group_id, f"سه روز از اشتراک کاربر باقی مانده:\nنام و نام خانوادگی:{fullname}\nشماره تلفن:{phone}\nاشتراک:اندیکاتور {p}", reply_markup=keyboard_claim)
                    services.set_expiration_notified(chat_id)
                await asyncio.sleep(10)
        except:
            pass
        await asyncio.sleep(10800)

async def check_expirations_ban_u():
    while True:
        try:
            expired_users = services.get_expired_users_to_ban_u()
            
            today = datetime.date.today()
    #        today = jdatetime.date(1405, 10, 1)
        
            for user in expired_users:
                chat_id = user[0]
                info = allUser.get_info(chat_id)
                fullname = f"{info[0]} {info[1]}"
                phone = info[2]
                p = services.get_service_u(chat_id)[0]
                user_exp_date = user[1]
                if user_exp_date and today >= user_exp_date:
                    msg = "⚠️ اشتراک شما به پایان رسید\nبرای خرید اشتراک از دستور /خرید استفاده کنید."
                    try:
                        await bot.send_message(chat_id, msg)
                    except:
                        pass
                    await bot.send_message(support_group_id, f"اشتراک کاربر به پایان رسید:\nنام و نام خانوادگی:{fullname}\nشماره تلفن:{phone}\nاشتراک:اندیکاتور {p}", reply_markup=keyboard_claim)
                    services.set_service_u(chat_id=chat_id, service='None')
                    services.set_expiration_ban_u(chat_id)
                    try:
                        await bot.kick_chat_member(vip_id, chat_id)
                    except:
                        pass
                await asyncio.sleep(10)
        except:
            pass
        await asyncio.sleep(10800)

async def check_expirations_u():
    while True:
        try:
            expired_users = services.get_expired_users_to_notify_u()
            
            today = datetime.date.today()
            
            for user in expired_users:
                chat_id = user[0]
                info = allUser.get_info(chat_id)
                fullname = f"{info[0]} {info[1]}"
                phone = info[2]
                p = services.get_service_u(chat_id)[0]
                user_exp_date = user[1]
                today = today - timedelta(days=3)
                if user_exp_date and today >= user_exp_date:
                    msg = "⚠️ مشترک گرامی، 3 روز از اشتراک شما باقی مانده است. برای تمدید از دستور /تمدید استفاده کنید."
                    try:
                        await bot.send_message(chat_id, msg)
                    except:
                        pass
                    await bot.send_message(support_group_id, f"سه روز از اشتراک کاربر باقی مانده:\nنام و نام خانوادگی:{fullname}\nشماره تلفن:{phone}\nاشتراک:اندیکاتور {p}", reply_markup=keyboard_claim)
                    services.set_expiration_notified_u(chat_id)
                await asyncio.sleep(10)
        except:
            pass
        await asyncio.sleep(10800)

########################################################################################################################

after_start = """به اکوسیستم معاملاتی LUXalpha خوش آمدید. 💎

ما اینجا هستیم تا به شما کمک کنیم با ابزارهایی معامله کنید که بر پایه منطق، استراتژی و دانشِ مهندسی بنا شده‌اند، نه حدس و گمان.


ما اینجا با استفاده از بروزترین متدهای اسمارت‌مانی و اندیکاتورهای اختصاصی خودمون، معاملات رو از حالت شانسی به یک بیزینس دقیق و سودده تبدیل کردیم.

برای اینکه بتونی دسترسی ۳ روزه رایگان رو دریافت کنی و نتایج لایو ما رو ببینی، لطفاً عدد 10 رو همین‌جا برام بفرست."""

questions = """
سوالات متداول:
۱. اندیکاتور روی گوشی (موبایل) نصب میشه؟
پاسخ: اندیکاتورهای ما به‌طور اختصاصی برای پلتفرم TradingView طراحی شده‌اند. شما می‌توانید تریدینگ‌ویو را روی موبایل (اندروید/آیفون) نصب کنید و از اندیکاتور ما استفاده کنید. اما برای تحلیل دقیق‌تر و مدیریت بهتر ترید، استفاده از لپ‌تاپ یا کامپیوتر (نسخه تحت وب تریدینگ‌ویو) پیشنهاد می‌شود.

۲. آیا سود این اندیکاتور تضمین شده است؟
پاسخ: در بازارهای مالی هیچ‌چیز تضمین ۱۰۰٪ ندارد. سیستم LUXalpha یک «ابزار هوشمند تحلیل» است که بر اساس پرایس‌اکشن و اسمارت‌مانی (SMC) به شما نقاط ورود و خروج می‌دهد. وین‌ریت (نرخ برد) ما ۷۰٪ است، اما موفقیت نهایی به «مدیریت سرمایه» خودِ شما بستگی دارد. ما به شما ابزار موفقیت می‌دهیم، نه ضمانت سود بدونِ دانش.

۳. اگر ضرر کنم چی؟ سیستم گارانتی داره؟
پاسخ: ما به قدرت سیستم‌مان ایمان داریم. اگر در طول یک ماه تقویمی، با رعایت «مدیریت ریسک استاندارد» (۱٪ ریسک در هر معامله)، برآیند حساب شما منفی بود، کل مبلغ اشتراک ماهانه شما تمام و کمال استرداد می‌شود. (تأکید: رعایت مدیریت ریسک شرط اصلی این ضمانت است).

۴. برای کار با این اندیکاتور چقدر دانش باید داشته باشم؟
پاسخ: ما برای شما ویدیوهای آموزشی اختصاصی ارسال می‌کنیم که صفر تا صد کار با اندیکاتور را توضیح داده است. برای شروع، آشنایی مقدماتی با نحوه ثبت سفارش (Order) در صرافی یا بروکر کافی است.

۵. از کجا بدونم کلاهبرداری نیست؟
پاسخ: اعتماد شما سرمایه ماست. به همین دلیل ما «تست رایگان ۳ روزه» داریم تا خودتان با چشمان خودتان عملکرد سیستم را در محیط لایو (گروه سیگنال) مشاهده کنید. همچنین دفتر ما در تهران پاسخگوی شماست و فعالیت ما کاملاً رسمی است.

۶. هزینه اشتراک چقدره و چطور باید پرداخت کنم؟
پاسخ: ما پلن‌های مختلفی (پایه، پیشرفته، حرفه‌ای) داریم. قیمت‌ها بسته به نوع پلن و قابلیت‌های اندیکاتور متفاوت است. جهت دریافت قیمت دقیق و شماره کارت/تتر، لطفاً در پیام‌رسان (بله/روبیکا) پیام دهید تا لیست کامل پکیج‌ها برایتان ارسال شود.

۷. میشه اندیکاتور رو روی سیستم خودم داشته باشم؟ (کپی‌برداری)
پاسخ: اندیکاتورهای LUXalpha دارای قفل امنیتی هستند و روی اکانت تریدینگ‌ویوِ شخصی شما فعال می‌شوند. این یعنی شما فقط «مجوز استفاده» دارید و امکان کپی‌برداری یا اشتراک‌گذاری با دیگران به دلیل لایسنس‌های امنیتی وجود ندارد.

۸. بهترین تایم‌فریم و نماد معاملاتی برای این اندیکاتور چیه؟
پاسخ: اندیکاتورهای ما بر اساس سشن معاملاتی نیویورک بهینه‌سازی شده‌اند. به وقت ایران، بهترین زمان برای استفاده از این ابزار و انجام معاملات، بازه زمانی ۱۳:۳۰ الی ۲۲:۰۰ است. ما این بازه زمانی را به مشتریانمان توصیه می‌کنیم، زیرا این کار باعث می‌شود معامله‌گری شما از حالت «شلوغ و پراکنده» خارج شده و با ایجاد یک نظم مشخص، در بهترین زمانِ نقدینگی بازار ترید کنید. جزئیات مربوط به تایم‌فریم‌های اختصاصی نیز در ویدیوی آموزشی که پس از خرید دریافت می‌کنید، به صورت کامل تشریح شده است.

۹.آیا برای استفاده از اندیکاتورهای LUXalpha حتماً باید اکانت پریمیوم (پولی) تریدینگ‌ویو داشته باشم؟

پاسخ: خیر، اصلاً نیازی به تهیه اکانت پریمیوم نیست. اندیکاتورهای ما به‌گونه‌ای بهینه‌سازی شده‌اند که روی نسخه رایگان (Free Plan) تریدینگ‌ویو هم بدون هیچ مشکلی کار می‌کنند. تنها نکته این است که در نسخه رایگان، شما محدود به استفاده از تعداد محدودی اندیکاتور به‌صورت همزمان هستید که سیستم ما با این محدودیت کاملاً سازگار است. بنابراین شما می‌توانید بدون پرداخت هیچ هزینه اضافی به تریدینگ‌ویو، از قدرت کامل ابزارهای ما بهره‌مند شوید
"""

wellcome_msg = """سلام دوست عزیز! به LUXalpha خوش اومدی. 💎

خیلی خوشحالم که برای ارتقای سطح تریدینگت، ما رو انتخاب کردی.

ما اینجا با استفاده از بروزترین متدهای اسمارت‌مانی و اندیکاتورهای اختصاصی خودمون، معاملات رو از حالت شانسی به یک بیزینس دقیق و سودده تبدیل کردیم.

برای اینکه بتونی دسترسی ۳ روزه رایگان رو دریافت کنی و نتایج لایو ما رو ببینی، لطفاً عدد 10 رو همین‌جا برام بفرست."""

#####################################################################################################################################

bot = AsyncTeleBot(
    TOKEN
)

session = None
allUser.create_table()

######################################################################################################################################

keyboard_claim = types.InlineKeyboardMarkup()
buttonc1 = types.InlineKeyboardButton(text="claim", callback_data="claimed")
keyboard_claim.add(buttonc1)

keyboard_plan = types.InlineKeyboardMarkup()
button1 = types.InlineKeyboardButton(text="یک ماهه", callback_data="یک ماهه")
button2 = types.InlineKeyboardButton(text="سه ماهه", callback_data="سه ماهه")
button3 = types.InlineKeyboardButton(text="شش ماهه", callback_data="شش ماهه")
keyboard_plan.add(button1, button2, button3)

keyboard_plan_au = types.InlineKeyboardMarkup()
buttonu1 = types.InlineKeyboardButton(text="یک ماهه", callback_data="یک ماهه الترا")
buttonu2 = types.InlineKeyboardButton(text="سه ماهه", callback_data="سه ماهه الترا")
buttonu3 = types.InlineKeyboardButton(text="شش ماهه", callback_data="شش ماهه الترا")
keyboard_plan_au.add(buttonu1, buttonu2, buttonu3)

keyboard_wallet = types.InlineKeyboardMarkup()
buttonw1 = types.InlineKeyboardButton(text="trc20", callback_data="t")
buttonw2 = types.InlineKeyboardButton(text="bep20", callback_data="b")
keyboard_wallet.add(buttonw1, buttonw2)

keyboard_pay = types.InlineKeyboardMarkup()
buttonpay1 = types.InlineKeyboardButton(text="ریالی", callback_data="ri")
buttonpay2 = types.InlineKeyboardButton(text="ارز دیجیتال", callback_data="di")
keyboard_pay.add(buttonpay1, buttonpay2)

keyboard_admin = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
buttona1 = types.KeyboardButton("ارسال پیام گروهی")
keyboard_admin.add(buttona1)

keyboard_manager = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
buttonm1 = types.KeyboardButton("امار کاربران")
buttonm2 = types.KeyboardButton("افزودن ادمین")
buttonm3 = types.KeyboardButton("حذف ادمین")
buttonm4 = types.KeyboardButton("دریافت چت ایدی")
buttonm5 = types.KeyboardButton("خروجی کاربران")
buttonm6 = types.KeyboardButton("خروجی کاربران جدید")
keyboard_manager.add(buttonm1, buttonm2)
keyboard_manager.add(buttonm3, buttonm4)
keyboard_manager.add(buttonm5, buttonm6)

keyboard_service = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
buttonb2 = types.KeyboardButton("اندیکاتور لوکس الفا📊📈")
buttonb4 = types.KeyboardButton("اندیکاتور لوکس الفا الترا مخصوص طلا📊📈")
keyboard_service.add(buttonb2)
keyboard_service.add(buttonb4)

keyboard_service_re = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
buttonre2 = types.KeyboardButton("تمدید اندیکاتور لوکس الفا📊📈")
buttonre4 = types.KeyboardButton("تمدید اندیکاتور لوکس الفا الترا مخصوص طلا📊📈")
keyboard_service_re.add(buttonre2)
keyboard_service_re.add(buttonre4)

keyboard_learn_an = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
buttonla1 = types.KeyboardButton("دریافت اموزش اندیکاتور لوکس الفا📚")
buttonla2 = types.KeyboardButton("ادامه خرید اندیکاتور لوکس الفا🛒")
keyboard_learn_an.add(buttonla1)
keyboard_learn_an.add(buttonla2)

keyboard_learn_au = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
buttonlau1 = types.KeyboardButton("دریافت اموزش اندیکاتور لوکس الفا الترا مخصوص طلا📚")
buttonlau2 = types.KeyboardButton("ادامه خرید اندیکاتور لوکس الفا الترا مخصوص طلا🛒")
keyboard_learn_au.add(buttonlau1)
keyboard_learn_au.add(buttonlau2)


learn_keyboard = types.ReplyKeyboardMarkup(row_width=4, resize_keyboard=True)
buttonlk1 = types.KeyboardButton("اندیکاتور لوکس الفا📊📈")
buttonlk2 = types.KeyboardButton("اندیکاتور لوکس الفا الترا مخصوص طلا📊📈")
learn_keyboard.add(buttonlk1) 
learn_keyboard.add(buttonlk2)

keyboard_filter = types.ReplyKeyboardMarkup(row_width=5, resize_keyboard=True)
buttonm1 = types.KeyboardButton("کاربران فعال")
buttonm2 = types.KeyboardButton("کاربران تستی")
buttonm3 = types.KeyboardButton("کاربران یک ماهه")
buttonm4 = types.KeyboardButton("کاربران سه ماهه")
buttonm5 = types.KeyboardButton("کاربران شش ماهه")
buttonm6 = types.KeyboardButton("کاربران یک ماهه الترا")
buttonm7 = types.KeyboardButton("کاربران سه ماهه الترا")
buttonm8 = types.KeyboardButton("کاربران شش ماهه الترا")
buttonm9 = types.KeyboardButton("کاربران بدون اشتراک")
keyboard_filter.add(buttonm1, buttonm2)
keyboard_filter.add(buttonm3, buttonm4)
keyboard_filter.add(buttonm5, buttonm6)
keyboard_filter.add(buttonm7, buttonm8)
keyboard_filter.add(buttonm9)

keyboard_help = types.ReplyKeyboardMarkup(row_width=5, resize_keyboard=True)
buttonh1 = types.KeyboardButton("10")
buttonh2 = types.KeyboardButton("/خرید")
buttonh3 = types.KeyboardButton("/تمدید")
buttonh4 = types.KeyboardButton("/ویرایش")
buttonh5 = types.KeyboardButton("/پروفایل")
buttonh6 = types.KeyboardButton("/سوالات")
buttonh7 = types.KeyboardButton("/عکس")
buttonh9 = types.KeyboardButton("/مدیر")
buttonh10 = types.KeyboardButton("/ادمین")
keyboard_help.add(buttonh1)
keyboard_help.add(buttonh2, buttonh3)
keyboard_help.add(buttonh4, buttonh5)
keyboard_help.add(buttonh6, buttonh7)
keyboard_help.add(buttonh9, buttonh10)

#######################################################################################################################################

photo_group_id = os.getenv("PHOTO_GROUP_ID")
support_group_id = os.getenv("SUPPORT_GROUP_ID")
vip_id = os.getenv("VIP_ID")
manager_chat_id = os.getenv("MANAGER_CHAT_ID")
me_chat_id = os.getenv("ME_CHAT_ID")
manager_users = [me_chat_id, manager_chat_id]
photo_id = os.getenv("PHOTO_ID")
andu_photo_id = os.getenv("ANDU_PHOTO_ID")
bot_photo_id = os.getenv("BOT_PHOTO_ID")
pro_bot_photo_id = os.getenv("PRO_BOT_PHOTO_ID")
video_id = os.getenv("VIDEO_ID")
u_v_id = os.getenv("U_VIDEO_ID")
andpdf = os.getenv("ANDPDF")
bot_video_id = os.getenv("BOT_VIDEO_ID")
voice_id = os.getenv("VOICE_ID")
ex_id_pro = os.getenv("EX_ID_PRO")
ex_id = os.getenv("EX_ID")
card = os.getenv("CARD_PHOTO_ID")

#######################################################################################################################################

def save_to_txt(data, filename="output.txt"):
    with open(filename, "w", encoding="utf-8") as f:
        for row in data:
            f.write(str(row) + "\n")

async def broadcast_message(user_ids, text):
    for chat_id in user_ids:
        try:
            await bot.send_message(chat_id, text)
            await asyncio.sleep(random.uniform(2.0, 4.8))
        except Exception as e:
            print(f"{chat_id}: {e}")
            await asyncio.sleep(10)

async def cod(chat_id):
    chat_id = str(chat_id).encode('utf-8')
    c = hashlib.sha256(chat_id)
    return c.hexdigest()[:6].upper()

async def create_license(chat_id, counter):
    chat_id = str(chat_id) + str(counter)
    chat_id = str(chat_id).encode('utf-8')
    c = hashlib.sha256(chat_id)
    c = c.hexdigest()[:21].upper()
    c = 'MT5LUXALPHA'+str(c)
    return c

async def set_redis(key, updates):
    rdb.hset(key, mapping=updates)

async def del_user(key):
    rdb.delete(key)

async def get_state(key):
    state = rdb.hget(key, "step")
    return state

async def get_command(key):
    command = rdb.hget(key, "commands")
    return command

async def set_ids(key, value):
    rdb.rpush(key, *value)

async def get_ids(key):
    ids = rdb.lrange(key, 0, -1)
    return ids

async def get_info(key):
    info = rdb.hgetall(key)
    return info

#######################################################################################################################################

@bot.message_handler('start')
async def send_welcome(message):
    await bot.reply_to(message, after_start, reply_markup=keyboard_help)

@bot.message_handler(regexp="^10$")
async def register_trial(message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    key = f"user:{user_id}"
    exist = allUser.check_user(chat_id)
    if exist:
        date = services.get_date_3(chat_id)
        await bot.reply_to(message, f"شما در طرح سه روزه عضو هستید.\nپایان: {date[0]}")
    else:
        updates = {
            "step":"GET_NAME",
            "commands":"10"
        }
        await set_redis(key, updates)
        await bot.reply_to(message, "نام خود را وارد کنید:")

@bot.message_handler(commands=['مدیر'])
async def managerp(message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    key = f"user:{user_id}"
    exist = allUser.check_user(chat_id)
    if str(chat_id) not in manager_users:
        await bot.send_message(chat_id, "شما به این بخش دسترسی ندارید.")
    else:
        await bot.send_message(chat_id, "یکی از گزینه ها را انتخاب کنید\nبرای خروج از پنل مدیریت دستور /exit را وارد کنید.", reply_markup=keyboard_manager)
        updates = {
            "step":"choose_operation"
        }
        await set_redis(key, updates)

@bot.message_handler(commands=["ادمین"])
async def adminp(message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    key = f"user:{user_id}"
    res = generall.get_admins()
    ress=[r[0] for r in res]
    if str(chat_id) not in ress:
        await bot.send_message(chat_id, "شما به این بخش دسترسی ندارید.")
    else:
        await bot.send_message(chat_id, "یکی از گزینه ها را انتخاب کنید\nبرای خروج از پنل ادمین دستور /exit را وارد کنید.", reply_markup=keyboard_admin)
        updates = {
            "step":"SELECT_OPERATION"
        }
        await set_redis(key, updates)

@bot.message_handler(commands=["عکس"])
async def getPhoto(message):
    await bot.reply_to(message, "عکس واریزی خود را ارسال کنید")

@bot.message_handler(commands=['خرید'])
async def buy(message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    k = allUser.check_user(chat_id)
    if not k:
        await bot.send_message(chat_id, "قبل از خرید با ارسال عدد 10 اطلاعات خود را ثبت کنید")
    else:
        await bot.send_message(chat_id, "محصول خود را انتخاب کنید:", reply_markup=keyboard_service)

@bot.message_handler(regexp="^اندیکاتور لوکس الفا📊📈$")
async def andic(message):
    chat_id = message.chat.id
    await bot.send_message(chat_id, """📚 لطفاً قبل از هر خرید یا استفاده، حتماً آموزش‌ها را مشاهده کنید تا بتوانید بهترین نتیجه را بگیرید و بدون مشکل از خدمات استفاده کنید.
""", reply_markup=keyboard_learn_an)

@bot.message_handler(regexp="^اندیکاتور لوکس الفا الترا مخصوص طلا📊📈$")
async def andic(message):
    chat_id = message.chat.id
    await bot.send_message(chat_id, """📚 لطفاً قبل از هر خرید یا استفاده، حتماً آموزش‌ها را مشاهده کنید تا بتوانید بهترین نتیجه را بگیرید و بدون مشکل از خدمات استفاده کنید.
""", reply_markup=keyboard_learn_au)
    
@bot.message_handler(regexp="^دریافت اموزش اندیکاتور لوکس الفا الترا مخصوص طلا📚$")
async def la(message):
    chat_id = message.chat.id
    #send video
    await bot.send_video(chat_id, u_v_id)

@bot.message_handler(regexp="^ادامه خرید اندیکاتور لوکس الفا الترا مخصوص طلا🛒$")
async def candicc(message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    key = f"user:{user_id}"
    k = allUser.check_user(chat_id)
    try:
        ser = services.get_service_u(chat_id)[0]
    except:
        ser = "None"
    if not k:
        await bot.send_message(chat_id, "قبل از خرید با ارسال عدد 10 اطلاعات خود را ثبت کنید")
    elif ser != "None" and ser != "trial" and ser != None:
        await bot.send_message(chat_id, "شما اشتراک فعال دارید.برای تمدید از دستور /تمدید استفاده کنید.")
    else:
        await bot.send_photo(chat_id, andu_photo_id)
        await bot.send_message(chat_id, "لطفا پلن خود را انتخاب کنید", reply_markup=keyboard_plan_au)
        updates = {
            "step":"pl"
        }
        await set_redis(key, updates)

@bot.message_handler(regexp="^دریافت اموزش اندیکاتور لوکس الفا📚$")
async def la(message):
    chat_id = message.chat.id
    await bot.send_video(chat_id, video=video_id)

@bot.message_handler(regexp="^ادامه خرید اندیکاتور لوکس الفا🛒$")
async def candic(message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    key = f"user:{user_id}"
    k = allUser.check_user(chat_id)
    try:
        ser = services.get_service(chat_id)[0]
    except:
        ser = "None"
    if not k:
        await bot.send_message(chat_id, "قبل از خرید با ارسال عدد 10 اطلاعات خود را ثبت کنید")
    elif ser != "None" and ser != "trial" and ser != None:
        await bot.send_message(chat_id, "شما اشتراک فعال دارید.برای تمدید از دستور /تمدید استفاده کنید.")
    else:
        await bot.send_photo(chat_id, photo_id)
        await bot.send_message(chat_id, "لطفا پلن خود را انتخاب کنید", reply_markup=keyboard_plan)
        updates = {
            "step":"pl"
        }
        await set_redis(key, updates)

@bot.message_handler(commands=['تمدید'])
async def ren(message):
    chat_id = message.chat.id
    await bot.send_message(chat_id, "محصول خود را انتخاب کنید:", reply_markup=keyboard_service_re)

@bot.message_handler(regexp="^تمدید اندیکاتور لوکس الفا📊📈$")
async def crean(message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    key = f"user:{user_id}"
    try:
        ser = services.get_service(chat_id)[0]
    except:
        ser = None
    k = allUser.check_user(chat_id)
    if not k:
        await bot.send_message(chat_id, "قبل از خرید با ارسال عدد 10 اطلاعات خود را ثبت کنید")
    elif ser == "None" or ser == "trial" or ser == None or ser == []:
        await bot.send_message(chat_id, "شما اشتراک فعال ندارید.برای خرید از دستور /خرید استفاده")
    else:
        await bot.send_photo(chat_id, photo_id)
        await bot.send_message(chat_id, "لطفا پلن خود را انتخاب کنید", reply_markup=keyboard_plan)
        updates = {
            "step":"pl"
        }
        await set_redis(key, updates)

@bot.message_handler(regexp="^تمدید اندیکاتور لوکس الفا الترا مخصوص طلا📊📈$")
async def creann(message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    key = f"user:{user_id}"
    try:
        ser = services.get_service_u(chat_id)[0]
    except:
        ser = None
    k = allUser.check_user(chat_id)
    if not k:
        await bot.send_message(chat_id, "قبل از خرید با ارسال عدد 10 اطلاعات خود را ثبت کنید")
    elif ser == "None" or ser == "trial" or ser == None or ser == []:
        await bot.send_message(chat_id, "شما اشتراک فعال ندارید.برای خرید از دستور /خرید استفاده")
    else:
        await bot.send_photo(chat_id, andu_photo_id)
        await bot.send_message(chat_id, "لطفا پلن خود را انتخاب کنید", reply_markup=keyboard_plan_au)
        updates = {
            "step":"pl"
        }
        await set_redis(key, updates)

@bot.message_handler(commands=['help'])
async def get_help(message):
    await bot.reply_to(message, """
                           

🔹 خرید اشتراک ▫️▫️▫️▫️▫️ /خرید
🔹 مشاهده پروفایل ▫️▫️▫️ /پروفایل
🔸 ویرایش پروفایل ▫️▫️▫️ /ویرایش
🔹 سوالات متداول ▫️▫️▫️ /سوالات
🔹 ارسال عکس واریزی ▫️▫️ /عکس
🔸 ثبت اطلاعات ▫️▫️▫️▫️▫️10
➖➖➖➖➖➖➖➖➖➖
🔑 ورود به پنل ادمین ▫️▫️ /ادمین
🔑 ورود به پنل مدیریت ▫️ /مدیر
                           
            
                           """)

@bot.message_handler(commands=['پروفایل'])
async def get_profile(message):
    chat_id = message.chat.id
    info = allUser.get_info(chat_id)
    try:
        id1, id2u = services.get_ids(chat_id)
    except:
        id1, id2u = ['ندارد', 'ندارد']
    if not id1:
        id1 = 'ندارد'
    try:
        date3 = services.get_date_3(chat_id)[0]
    except:
        date3 = ''
    try:
        date_and = services.get_date(chat_id)[0]
    except Exception as e:
        date_and = ''

    try:
        id1u, id2 = services.get_ids_u(chat_id)
    except:
        id1u, id2 = ['ندارد', 'ندارد']
    if not id1u:
        id1u = 'ندارد'
    try:
        date_andu = services.get_date_u(chat_id)[0]
    except Exception as e:
        date_andu = ''

    try:
        service = services.get_service(chat_id)[0]
    except:
        service = 'None'

    try:
        serviceu = services.get_service_u(chat_id)[0]
    except:
        serviceu = 'None'

    if not info:
        await bot.send_message(chat_id, "اطلاعات شما ثبت نشده.")

    else:
        if service != 'trial' and serviceu != 'trial':
            profile_text = (
                f"👤 نام: {info[0]} {info[1]}\n"
                f"📞 شماره: {info[2]}\n\n"
                f"💹اشتراک: {service}\n"
                f"🆔 تریدینگ‌ویو: {id1}\n"
                f"📅 تاریخ انقضا: {date_and}\n\n"
                f"💹اشتراک الترا: {serviceu}\n"
                f"🆔 تریدینگ‌ویو: {id1u}\n"
                f"📅 تاریخ انقضا: {date_andu}"
            )
            await bot.send_message(chat_id, profile_text)
        elif service == "trial" and serviceu != "trial":
            profile_text = (
                f"👤 نام: {info[0]} {info[1]}\n"
                f"📞 شماره: {info[2]}\n\n"
                f"💹اشتراک: {service}\n"
                f"🆔 تریدینگ‌ویو: {id1}\n"
                f"📅 تاریخ انقضا: {date3}\n\n"
                f"💹اشتراک الترا: {serviceu}\n"
                f"🆔 تریدینگ‌ویو: {id1u}\n"
                f"📅 تاریخ انقضا: {date_andu}"
            )
            await bot.send_message(chat_id, profile_text)
        elif service != "trial" and serviceu == "trial":
            profile_text = (
                f"👤 نام: {info[0]} {info[1]}\n"
                f"📞 شماره: {info[2]}\n\n"
                f"💹اشتراک: {service}\n"
                f"🆔 تریدینگ‌ویو: {id1}\n"
                f"📅 تاریخ انقضا: {date_and}\n\n"
                f"💹اشتراک الترا: {serviceu}\n"
                f"🆔 تریدینگ‌ویو: {id1u}\n"
                f"📅 تاریخ انقضا: {date3}"
            )
            await bot.send_message(chat_id, profile_text)
        elif service == "trial" and serviceu == "trial":
            profile_text = (
                f"👤 نام: {info[0]} {info[1]}\n"
                f"📞 شماره: {info[2]}\n\n"
                f"💹اشتراک: {service}\n"
                f"🆔 تریدینگ‌ویو: {id1}\n"
                f"📅 تاریخ انقضا: {date3}\n\n"
                f"💹اشتراک الترا: {serviceu}\n"
                f"🆔 تریدینگ‌ویو: {id1u}\n"
                f"📅 تاریخ انقضا: {date3}"
            )
            await bot.send_message(chat_id, profile_text)

@bot.message_handler(commands=["ویرایش"])
async def edit_p(message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    key = f"user:{user_id}"
    exist = allUser.check_user(chat_id)
    if not exist:
        await bot.send_message(chat_id, "اطلاعات شما ثبت نشده.")
    else:
        await bot.send_message(chat_id, "نام خود را وارد کنید:")
        updates = {
            "step":"GET_NAME",
            "commands":"edit"
        }
        await set_redis(key, updates)

@bot.message_handler(commands=["سوالات"])
async def get_ask(message):
    global questions
    await bot.reply_to(message, questions)

######################################################################text handler#######################################################

@bot.callback_query_handler(func=lambda call: True)
async def plan(call):
    activate = re.search(r'^activate_', call.data)
    accept = re.search(r'^accept_', call.data)
    rejet = re.search(r'^reject_', call.data)
    acceptu = re.search(r'^acceptu_', call.data)
    chat_id = call.message.chat.id
    user_id = call.from_user.id
    key = f"user:{user_id}"
    command = await get_command(key)
    msg_id = call.message.message_id
    admin_name = call.from_user.first_name
    if call.data in ["یک ماهه", "سه ماهه", "شش ماهه"]:
        services.update_temp_service(call.data, chat_id)
        updates = {
            "step":"BUY",
            "commands":"and"
        }
        await set_redis(key, updates)
        await bot.answer_callback_query(call.id, f"پلن {call.data} انتخاب شد.")
        res = await bot.send_message(chat_id, "نحوه پرداخت را انتخاب کنید", reply_markup=keyboard_pay)

    elif call.data in ["یک ماهه الترا", "سه ماهه الترا", "شش ماهه الترا"]:
        services.update_temp_service_u(call.data, chat_id)
        updates = {
            "step":"BUY",
            "commands":"andu"
        }
        await set_redis(key, updates)
        await bot.answer_callback_query(call.id, f"پلن {call.data} انتخاب شد.")
        res = await bot.send_message(chat_id, "نحوه پرداخت را انتخاب کنید", reply_markup=keyboard_pay)

    elif call.data == 'ri':
        t = tether()
        price = t.get_price()
        if not price:
            await bot.send_message(chat_id, "مشکلی در دریافت قیمت پیش امده.لطفا بعدا تلاش کنید.")
        else:
            if command == 'andu':
                s = services.get_temp_u(chat_id)[0]
                if s == 'یک ماهه الترا':
                    c = 38
                elif s == 'سه ماهه الترا':
                    c = 99
                else:
                    c = 149
            else:
                s = services.get_temp(chat_id)[0]
                if s == 'یک ماهه':
                    c = 28
                elif s == 'سه ماهه':
                    c = 79
                else:
                    c = 139
            
            price2 = price*c
            finall_price = math.floor(price2/100000)*100000
            await bot.send_photo(chat_id, card)
            await bot.send_message(
            chat_id, 
            f"💵 *تومان نهایی:* `{finall_price:,}`\n"
            f"🟢 *مبنا:* `{price:,}`\n"
            f"────────────────\n"
            f"🕒 *اعتبار تراکنش:* ۱ ساعت\n"
        )
            await bot.send_message(chat_id, "بعد از انجام واریز، فقط کافیست اسکرین‌شاتِ موفقیت‌آمیز بودنِ تراکنش را برای ما بفرستید.همکارانِ من در بخشِ فنی بلافاصله واریزی شما را بررسی و دسترسی‌تان را فعال می‌کنند.\nبرای ارسال عکس از دستور /عکس استفاده کنید.")


    elif call.data == 'di':
        await bot.send_message(chat_id, "شبکه مورد نظر را انتخاب کنید", reply_markup=keyboard_wallet)

    elif call.data == "b":
        await bot.send_message(chat_id, "0x5d6b8c8c1577f2b71b9cca4492a2cbec57fd51a9")
        await bot.send_message(chat_id, "بعد از انجام واریز، فقط کافیست اسکرین‌شاتِ موفقیت‌آمیز بودنِ تراکنش را برای ما بفرستید.همکارانِ من در بخشِ فنی بلافاصله واریزی شما را بررسی و دسترسی‌تان را فعال می‌کنند.\nبرای ارسال عکس از دستور /عکس استفاده کنید.")

    elif call.data == "t":
        await bot.send_message(chat_id, "TK6ybs7iALN7n5GqE5kagu7JBRfFUQkcT8")
        await bot.send_message(chat_id, "بعد از انجام واریز، فقط کافیست اسکرین‌شاتِ موفقیت‌آمیز بودنِ تراکنش را برای ما بفرستید.همکارانِ من در بخشِ فنی بلافاصله واریزی شما را بررسی و دسترسی‌تان را فعال می‌کنند.\nبرای ارسال عکس از دستور /عکس استفاده کنید.")

    elif call.data == "claimed":
        text = ""
        if call.message.content_type == "text" and call.message.text:
            text += call.message.text
            t = text + f"\n\nکارشناس:{admin_name}"
            await bot.edit_message_text(chat_id=support_group_id, message_id=msg_id, text=t)
        elif call.message.content_type == "photo" and call.message.caption:
            text += call.message.caption
            t = text + f"\n\nکارشناس:{admin_name}"
            await bot.edit_message_caption(chat_id=support_group_id, message_id=msg_id, caption=t)

    elif activate:
        action, ta_c_id = call.data.split("_")
        await bot.send_message(ta_c_id, """
        دسترسیِ شما به اندیکاتور در اکانتِ تریدینگ‌ویو فعال شد.

        برای مشاهده و استفاده، کافیست:

        1. واردِ سایتِ TradingView شوید.

        2. از منوی بالا به بخش Indicators بروید.

        3. در تبِ Invite-only scripts، اندیکاتور LUXalpha برای شما ظاهر شده است؛ آن را روی نمودار فعال کنید

        4.توافق‌نامه سلب مسئولیت:

        شما می‌پذیرید که اندیکاتورهای LUXalpha و ربات های luxalpha صرفاً ابزارهای کمکی جهت تحلیل بوده و مسئولیت نهایی تمامی معاملات، مدیریت سرمایه و حد ضرر، مستقیماً بر عهده تریدر است. ما هیچ‌گونه تعهدی نسبت به نتایج معاملات شخصی شما نداریم
        
        """, reply_markup=keyboard_help)
        await bot.edit_message_text(chat_id=manager_chat_id, message_id=msg_id, text="فعال شد!")

    elif accept:
        action, t_c_id = call.data.split("_")
        plann = services.get_temp(t_c_id)
        c = allUser.get_invited(t_c_id)
        tc = int(t_c_id)
        key = f"user:{tc}"
        updates = {
            "step":"GET_TID"
        }
        await set_redis(key, updates)
        if c != "None":
            allUser.add_person(c[0])
        services.set_expiration_notified3(t_c_id)
        await bot.edit_message_caption(chat_id=photo_group_id, message_id=msg_id, caption=f"توسط کارشناس {admin_name} تایید شد.")
        await bot.send_document(t_c_id, document=andpdf)
        await bot.send_message(t_c_id, """
        فعال‌سازیِ دسترسی شما ✅

«واریزیِ شما توسطِ تیم فنی تأیید شد. به تیمِ حرفه‌ای LUXalpha خوش آمدید! 💎
لطفا جهت دریافت اندیکاتور ایدی تریدیگ ویو خودتونو کامل باری ما ارسال کنین تا بتونیم لایسنس شمارو متصل کنیم.
        """, reply_markup=ReplyKeyboardRemove())

    elif acceptu:
        action, t_c_id = call.data.split("_")
        plann = services.get_temp_u(t_c_id)
        c = allUser.get_invited(t_c_id)
        tc = int(t_c_id)
        key = f"user:{tc}"
        updates = {
            "step":"GET_TIDU"
        }
        await set_redis(key, updates)
        if c != "None":
            allUser.add_person(c[0])
        services.set_expiration_notified3(t_c_id)
        await bot.edit_message_caption(chat_id=photo_group_id, message_id=msg_id, caption=f"توسط کارشناس {admin_name} تایید شد.")
        await bot.send_document(t_c_id, document=andpdf)
        await bot.send_message(t_c_id, """
        فعال‌سازیِ دسترسی شما ✅

«واریزیِ شما توسطِ تیم فنی تأیید شد. به تیمِ حرفه‌ای LUXalpha خوش آمدید! 💎
لطفا جهت دریافت اندیکاتور ایدی تریدیگ ویو خودتونو کامل باری ما ارسال کنین تا بتونیم لایسنس شمارو متصل کنیم.
        """, reply_markup=ReplyKeyboardRemove())
        
    elif rejet:
        msg_id = call.message.message_id
        await bot.edit_message_caption(chat_id=photo_group_id, message_id=msg_id, caption=f"توسط کارشناس {admin_name} رد شد.")
        action, target_chat_id = call.data.split("_")
        await bot.send_message(target_chat_id, """واریز شما توسط کارشناس مربوطه رد شد.""", reply_markup=keyboard_help)

################################################################callback hndler##################################################

@bot.message_handler(content_types=['new_chat_members'])
async def kick(message):
    group_id = message.chat.id
    print(group_id)
    if str(group_id) == str(vip_id):
        new_members = message.new_chat_members
        
        for user in new_members:
            user_id = user.id
            print(f"Checking user: {user_id}")
           
            has_subscription = allUser.check_user(user_id)
           
            try:
                if not has_subscription:
                    print(f"User {user_id} is NOT VIP. Attempting to ban...")
                    result = await bot.kick_chat_member(vip_id, user_id)
                    print(f"Ban Result: {result}")
            except:
                pass

##########################################################new chat member handler######################################################

@bot.message_handler(content_types=['photo'])
async def handle_photo(message):
    chat_id = message.chat.id
    file_id = message.photo[-1].file_id
    user_id = message.from_user.id
    key= f"user:{user_id}"
    command = await get_command(key)
    if command and command == 'andu':
        p = services.get_temp_u(chat_id)
    else:
        p = services.get_temp(chat_id)
    file_id = message.photo[-1].file_id
    full_caption = f"📸 عکس ارسالی از: {message.from_user.first_name}\nID:{chat_id}\nplan:{p[0]}"
    if command and command == "and":
        check_keyboard = types.InlineKeyboardMarkup()
        button1 = types.InlineKeyboardButton(text="accept✅", callback_data=f"accept_{chat_id}")
        button2 = types.InlineKeyboardButton(text="reject❌", callback_data=f"reject_{chat_id}")
        check_keyboard.add(button1, button2)

    elif command and command == "andu":
        check_keyboard = types.InlineKeyboardMarkup()
        button1 = types.InlineKeyboardButton(text="accept✅", callback_data=f"acceptu_{chat_id}")
        button2 = types.InlineKeyboardButton(text="reject❌", callback_data=f"reject_{chat_id}")
        check_keyboard.add(button1, button2)
    await bot.send_photo(chat_id=photo_group_id, photo=file_id, reply_markup=check_keyboard, caption=full_caption)
    await bot.send_message(chat_id, "✅ تصویر شما با موفقیت به مجموعه کارشناسان LUXalpha ارسال شد و پس از تایید دسترسی شما فعال میشود ", reply_markup=None)
    await del_user(key)

# @bot.message_handler(content_types=['video'])
# async def get_document_file_id(message):
#     if message.video:
#         file_id = message.video.file_id
#         print(f"📄 File ID:\n{file_id}")
    
######################################################################photo handler####################################################

@bot.message_handler(func=lambda message: True)
async def handle_steps(message):
    chat_id = message.chat.id
    text = message.text if message.text else None
    user_id = message.from_user.id
    key = f"user:{user_id}"
    step = await get_state(key)
    command = await get_command(key)
    if step == "GET_TID":
        services.set_ids(chat_id, text, "allTimeFull")
        await del_user(key)
        await bot.send_message(chat_id, "دریافت شد.")
        keyboard_activate = types.InlineKeyboardMarkup()
        buttonac1 = types.InlineKeyboardButton(text="فعال شد", callback_data=f"activate_{chat_id}")
        keyboard_activate.add(buttonac1)
        plann = services.get_temp(chat_id)[0]
        ids = services.get_ids(chat_id)
        try:
            serv = services.get_service(chat_id)[0]
        except:
            serv = 'None'
        if serv == "None" or serv == [] or not serv or serv == "trial":
            await bot.send_message(manager_chat_id, f"activate service for user:\n\ntrading view id => {ids[0]}\nplan={plann}", reply_markup=keyboard_activate)
            services.set_service(service=plann, chat_id=chat_id)
            services.set_date_buy(chat_id, plann)
        else:
            await bot.send_message(manager_chat_id, f"renewal service for user:\n\ntrading view id => {ids[0]}\nplan={plann}", reply_markup=keyboard_activate)
            services.set_service(service=plann, chat_id=chat_id)
            services.set_date(chat_id, plann)

    elif step == "GET_TIDU":
        services.set_ids_u(chat_id, text, "allTimeFull")
        await del_user(key)
        await bot.send_message(chat_id, "دریافت شد.")
        keyboard_activate = types.InlineKeyboardMarkup()
        buttonac1 = types.InlineKeyboardButton(text="فعال شد", callback_data=f"activate_{chat_id}")
        keyboard_activate.add(buttonac1)
        plann = services.get_temp_u(chat_id)[0]
        ids = services.get_ids_u(chat_id)
        try:
            serv = services.get_service_u(chat_id)[0]
        except:
            serv = 'None'
        if serv == "None" or serv == [] or not serv or serv == "trial":
            await bot.send_message(manager_chat_id, f"activate service for user:\n\ntrading view id => {ids[0]}\nplan={plann}", reply_markup=keyboard_activate)
            services.set_service_u(service=plann, chat_id=chat_id)
            services.set_date_buy_u(chat_id, plann)
        else:
            await bot.send_message(manager_chat_id, f"renewal service for user:\n\ntrading view id => {ids[0]}\nplan={plann}", reply_markup=keyboard_activate)
            services.set_service_u(service=plann, chat_id=chat_id)
            services.set_date_u(chat_id, plann)

    elif step == "GET_NAME":
        updates = {
            'name' : text,
            'step' : "GET_FNAME"
        }
        await set_redis(key, updates)
        await bot.reply_to(message, "نام خانوادگی خود را وارد کنید:")

    elif step == "GET_FNAME":
        updates = {
            'fname' : text,
            'step' : "GET_PHONE"
        }
        await set_redis(key, updates)
        await bot.reply_to(message, "شماره تلفن خود را وارد کنید:")

    elif step == "GET_PHONE":
        info = await get_info(key)
        if info:
            name = info.get("name")
            fname = info.get("fname")
        updates = {
            'phone' : text,
            'step' : "GET_PHONE"
        }
        await set_redis(key, updates)
        summary = (f"✅ اطلاعات شما ثبت شد:\n"
            f"👤 نام: {name} {fname}\n"
            f"📞 شماره: {text}\n"
        )
        summary2 = (f"✅ اطلاعات شما ویرایش شد:\n"
            f"👤 نام: {name} {fname}\n"
            f"📞 شماره: {text}\n"
        )
        
        if command:
            if command == "10":
                await bot.send_message(chat_id, summary)
                await bot.send_message(chat_id, f"""بسیار عالی! خوش‌آمدی به جمع تریدرهای هوشمند LUXalpha. 🚀
اگر میخوای تست 3 روزه رو دریافت کنی کافیه به من پیام بدی تا دسترسی رو 3 روز رایگان بهت بدم
    @luxalphafxx
                
اگر هم قصد خرید لایسنس رو داری از قسمت پایین اندیکاتوری که مد نظرته رو انتخاب کن و خریدتو کامل کن.
هر سوالی داشتی من کنارتم😉
https://t.me/+7vOZgpnSZmw5Y2Q0""", reply_markup=learn_keyboard)
                allUser.register_user(name, fname, text, "Empty", chat_id, "tel", 'Empty', user_id)
                services.set_service(chat_id, "trial")
                services.set_service_u(chat_id, 'trial')
                services.set_date_3(chat_id)
                services.set_date_3_u(chat_id)
                services.set_expiration_ban_u(chat_id)
                services.set_expiration_notified_u(chat_id)
                await del_user(key)
            elif command == "edit":
                allUser.update_info(name, fname, text, chat_id)
                await bot.send_message(chat_id, summary2)
                await del_user(key)

    elif step == "choose_operation":
        if text == "/exit":
            await bot.send_message(chat_id, "از پنل ادمین خارج شدید", reply_markup=keyboard_help)
            await del_user(key)

        elif text == "امار کاربران":
            await bot.send_message(chat_id, """در این بخش، نمای کاملی از جمعیت کاربری پلتفرم ارائه شده است. این آمار به شما کمک می‌کند تا روند جذب و رضایت مشتریان را به صورت دقیق پایش نمایید""")

            amar = services.get_user_status()
            if 'None' not in amar:
                amar['None'] = 0
            if 'trial' not in amar:
                amar['trial'] = 0
            if 'یک ماهه' not in amar:
                amar['یک ماهه'] = 0
            if 'سه ماهه' not in amar:
                amar["سه ماهه"] = 0
            if 'شش ماهه' not in amar:
                amar["شش ماهه"] = 0
            
            await bot.send_message(chat_id, "اندیکاتور")
            await bot.send_message(chat_id, f"""📊 خلاصه وضعیت کلی:
- کل کاربران ثبت‌نامی: {amar['trial']+amar['یک ماهه']+amar['سه ماهه']+amar['شش ماهه']+amar['None']} نفر
- کاربران فعال (اشتراک‌دار): {amar['یک ماهه']+amar['سه ماهه']+amar['شش ماهه']} نفر""")
            
            await bot.send_message(chat_id, f"""
- نرخ تبدیل تستی به پولی: {(amar['یک ماهه']+amar['سه ماهه']+amar['شش ماهه'])/(amar['trial']+amar['یک ماهه']+amar['سه ماهه']+amar['شش ماهه']+amar['None'])*100}

👥 جزئیات تفکیکی کاربران:
1.  کاربران بدون اشتراک : {amar['None']} نفر
1.  کاربران تستی: {amar['trial']} نفر (دوره آشنایی رایگان)
2.  اشتراک ماهانه: {amar['یک ماهه']} نفر
3.  اشتراک سه‌ماهه: {amar['سه ماهه']} نفر
4.  اشتراک شش‌ماهه: {amar['شش ماهه']} نفر
""")

            amar2 = services.get_user_status_u()
            if 'None' not in amar2:
                amar2['None'] = 0
            if 'trial' not in amar2:
                amar2['trial'] = 0
            if 'یک ماهه الترا' not in amar2:
                amar2['یک ماهه الترا'] = 0
            if 'سه ماهه الترا' not in amar2:
                amar2["سه ماهه الترا"] = 0
            if 'شش ماهه الترا' not in amar2:
                amar2["شش ماهه الترا"] = 0
            
            await bot.send_message(chat_id, "اندیکاتور الترا")
            await bot.send_message(chat_id, f"""📊 خلاصه وضعیت کلی:
- کل کاربران ثبت‌نامی: {amar2['trial']+amar2['یک ماهه الترا']+amar2['سه ماهه الترا']+amar2['شش ماهه الترا']+amar2['None']} نفر
- کاربران فعال (اشتراک‌دار): {amar2['یک ماهه الترا']+amar2['سه ماهه الترا']+amar2['شش ماهه الترا']} نفر""")
            
            await bot.send_message(chat_id, f"""
- نرخ تبدیل تستی به پولی: {(amar2['یک ماهه الترا']+amar2['سه ماهه الترا']+amar2['شش ماهه الترا'])/(amar2['trial']+amar2['یک ماهه الترا']+amar2['سه ماهه الترا']+amar2['شش ماهه الترا']+amar2['None'])*100}

👥 جزئیات تفکیکی کاربران:
1.  کاربران بدون اشتراک : {amar2['None']} نفر
1.  کاربران تستی: {amar2['trial']} نفر (دوره آشنایی رایگان)
2.  اشتراک ماهانه: {amar2['یک ماهه الترا']} نفر
3.  اشتراک سه‌ماهه: {amar2['سه ماهه الترا']} نفر
4.  اشتراک شش‌ماهه: {amar2['شش ماهه الترا']} نفر
""")

            await bot.send_message(chat_id, "یکی از گزینه ها را انتخاب کنید\nبرای خروج از پنل مدیریت دستور /exit را وارد کنید.", reply_markup=keyboard_manager)
            updates = {
                "step":"choose_operation"
            }
            await set_redis(key, updates)

        elif text == "افزودن ادمین":
            await bot.send_message(chat_id, "برای افزودن ادمین ایدی عددی کاربر را وارد کنید:")
            updates = {
                "step":"add_admin"
            }
            await set_redis(key, updates)
        elif text == "حذف ادمین":
            await bot.send_message(chat_id, "برای حذف ادمین ایدی عددی کاربر را وارد کنید")
            updates = {
                "step":"remove_admin"
            }
            await set_redis(key, updates)
        elif text == "دریافت چت ایدی":
            await bot.send_message(chat_id, "برای دریافت چت ایدی یک پیام دلخواه ارسال کنید\nبرای دریافت چت ایدی یک کاربر دیگر کافیست یک پیام از ان شخص برای من ارسال کنید")
            updates = {
                "step":"chat_id"
            }
            await set_redis(key, updates)
        elif text == "خروجی کاربران":
            users = allUser.export_users()
            txt = ""
            for first_name, last_name, phone in users:
                users_info = (
                    f"نام: {first_name}\n"
                    f"نام خانوادگی: {last_name}\n"
                    f"شماره: {phone}\n"
                    "============================\n")
                if len(txt)+len(users_info) > 4000:
                    await bot.send_message(chat_id, txt)
                    txt = ""
                txt += users_info
            if txt:
                await bot.send_message(chat_id, txt)
            await bot.send_message(chat_id, "برای خروج از بخش مدیریت دستور /exit را وارد کنید.")
            updates = {
                "step":"choose_operation"
            }
            await set_redis(key, updates)
        elif text == "خروجی کاربران جدید":
            users = allUser.export_new_users()
            if not users:
                await bot.send_message(chat_id, "کاربر جدیدی وجود ندارد.")
            else:
                txt = ""
                for first_name, last_name, phone in users:
                    users_info = (
                        f"نام: {first_name}\n"
                        f"نام خانوادگی: {last_name}\n"
                        f"شماره: {phone}\n"
                        "============================\n")
                    if len(txt)+len(users_info) > 4000:
                        await bot.send_message(chat_id, txt)
                        txt = ""
                    txt += users_info
                if txt:
                    await bot.send_message(chat_id, txt)
            allUser.set_new_member()
            await bot.send_message(chat_id, "برای خروج از بخش مدیریت دستور /exit را وارد کنید.")
            updates = {
                "step":"choose_operation"
            }
            await set_redis(key, updates)
    
    elif step == "add_admin":
        if text == "/exit":
            await bot.send_message(chat_id, "از پنل مدیریت خارج شدید", reply_markup=keyboard_help)
            await del_user(key)
        else:
            generall.register_admin(text)
            await bot.send_message(chat_id, "ادمین استخدام شد.")
            await bot.send_message(chat_id, "یکی از گزینه ها را انتخاب کنید\nبرای خروج از پنل مدیریت دستور /exit را وارد کنید.", reply_markup=keyboard_manager)
            updates = {
                "step":"choose_operation"
            }
            await set_redis(key, updates)
    
    elif step == "remove_admin":
        if text == "/exit":
            await bot.send_message(chat_id, "از پنل مدیریت خارج شدید", reply_markup=keyboard_help)
            await del_user(key)
        else:
            res = generall.get_admins()
            ress = [r[0] for r in res]
            if text in ress:
                generall.delete_admin(text)
                await bot.send_message(chat_id, "ادمین حذف شد.")
            else:
                await bot.send_message(chat_id, "ادمین وجود ندارد")
                await bot.send_message(chat_id, "یکی از گزینه ها را انتخاب کنید\nبرای خروج از پنل مدیریت دستور /exit را وارد کنید.", reply_markup=keyboard_manager)
            updates = {
                "step":"choose_operation"
            }
            await set_redis(key, updates)

    elif step == "chat_id":
        if text == "/exit":
            await bot.send_message(chat_id, "از پنل مدیریت خارج شدید", reply_markup=keyboard_help)
            await del_user(key)
        else:
            if message.forward_from != None:
                forward_id = message.forward_from.id
                await bot.send_message(chat_id, f"forwarded caht-id -> {forward_id}")
                await bot.send_message(chat_id, "یکی از گزینه ها را انتخاب کنید\nبرای خروج از پنل مدیریت دستور /exit را وارد کنید.", reply_markup=keyboard_manager)
            else:
                user_id = message.from_user.id
                await bot.send_message(chat_id, f"your caht-id -> {user_id}")
                await bot.send_message(chat_id, "یکی از گزینه ها را انتخاب کنید\nبرای خروج از پنل مدیریت دستور /exit را وارد کنید.", reply_markup=keyboard_manager)
            updates = {
                "step":"choose_operation"
            }
            await set_redis(key, updates)
    
    elif step == "SELECT_OPERATION":
        if text == "/exit":
            await bot.send_message(chat_id, "از پنل ادمین خارج شدید", reply_markup=keyboard_help)
            await del_user(key)
        elif text == "ارسال پیام گروهی":
            await bot.send_message(chat_id, "فیلتر کاربران را انتخاب کنید", reply_markup=keyboard_filter)
            updates = {
                "step":"FILTER"
            }
            await set_redis(key, updates)
        else:
            await bot.send_message(chat_id, "پیام یافت نشد.عملیات را به درستی انتخاب کنید", reply_markup=keyboard_admin)
    elif step == "FILTER":
        if text == "/exit":
            await bot.send_message(chat_id, "از پنل ادمین خارج شدید", reply_markup=keyboard_help)
            await del_user(key)
        elif text in ["کاربران تستی", "کاربران فعال", "کاربران یک ماهه", "کاربران سه ماهه", "کاربران شش ماهه", "کاربران بدون اشتراک", "کاربران یک ماهه الترا", "کاربران سه ماهه الترا", "کاربران شش ماهه الترا"]:
            if text == 'کاربران تستی':
                ids = services.get_trial_user_ids()
                ids2 = services.get_trial_user_ids_u()
                finall_ids = [x for x in ids if x in ids2]
                updates = {
                    "step":"SEND_MESSAGE"
                }
                await set_redis(key, updates)
                await bot.send_message(chat_id, "پیام خود را بنویسید:\nدر صورت انصراف دستور /exit را وارد کنید.")
            elif text == "کاربران فعال":
                ids = services.get_active_user_ids()
                ids2 = services.get_active_user_ids_u()
                finall_ids = ids+ids2
                finall_ids = set(finall_ids)
                updates = {
                    "step":"SEND_MESSAGE"
                }
                await set_redis(key, updates)
                await bot.send_message(chat_id, "پیام خود را بنویسید:\nدر صورت انصراف دستور /exit را وارد کنید.")
            elif text == 'کاربران بدون اشتراک':
                ids = services.get_deactive_user_ids()
                ids2 = services.get_deactive_user_ids_u()
                finall_ids = [x for x in ids if x in ids2]
                updates = {
                    "step":"SEND_MESSAGE"
                }
                await set_redis(key, updates)
                await bot.send_message(chat_id, "پیام خود را بنویسید:\nدر صورت انصراف دستور /exit را وارد کنید.")
            elif text == "کاربران یک ماهه":
                finall_ids = services.get_basic_user_ids()
                updates = {
                    "step":"SEND_MESSAGE"
                }
                await set_redis(key, updates)
                await bot.send_message(chat_id, "پیام خود را بنویسید:\nدر صورت انصراف دستور /exit را وارد کنید.")
            elif text == "کاربران سه ماهه":
                finall_ids = services.get_pro_user_ids()
                updates = {
                    "step":"SEND_MESSAGE"
                }
                await set_redis(key, updates)
                await bot.send_message(chat_id, "پیام خود را بنویسید:\nدر صورت انصراف دستور /exit را وارد کنید.")
            elif text == "کاربران شش ماهه":
                finall_ids = services.get_elite_user_ids()
                updates = {
                    "step":"SEND_MESSAGE"
                }
                await set_redis(key, updates)
                await bot.send_message(chat_id, "پیام خود را بنویسید:\nدر صورت انصراف دستور /exit را وارد کنید.")
            elif text == "کاربران یک ماهه الترا":
                finall_ids = services.get_basic_user_ids_u()
                updates = {
                    "step":"SEND_MESSAGE"
                }
                await set_redis(key, updates)
                await bot.send_message(chat_id, "پیام خود را بنویسید:\nدر صورت انصراف دستور /exit را وارد کنید.")
            elif text == "کاربران سه ماهه الترا":
                finall_ids = services.get_pro_user_ids_u()
                updates = {
                    "step":"SEND_MESSAGE"
                }
                await set_redis(key, updates)
                await bot.send_message(chat_id, "پیام خود را بنویسید:\nدر صورت انصراف دستور /exit را وارد کنید.")
            elif text == "کاربران شش ماهه الترا":
                finall_ids = services.get_elite_user_ids_u()
                updates = {
                    "step":"SEND_MESSAGE"
                }
                await set_redis(key, updates)
                await bot.send_message(chat_id, "پیام خود را بنویسید:\nدر صورت انصراف دستور /exit را وارد کنید.")
            ids_key = f"user:{user_id}ids"
            await set_ids(ids_key, finall_ids)
        else:
            await bot.send_message(chat_id, "پیام یافت نشد.فیلتر کاربران را به درستی انتخاب کنید", reply_markup=keyboard_filter)
    
    elif step == "SEND_MESSAGE":
        if text == "/exit":
            await bot.send_message(chat_id, "از پنل ادمین خارج شدید", reply_markup=keyboard_help)
            await del_user(key)
        else:
            ids_key = f"user:{user_id}ids"
            ids = await get_ids(ids_key)
            await bot.send_message(chat_id, "⏳ ارسال پیام گروهی در پس‌زمینه شروع شد")
            if ids:
                asyncio.create_task(broadcast_message(ids, text))
            await bot.send_message(chat_id, "یکی از گزینه ها را انتخاب کنید\nبرای خروج از پنل ادمین دستور /exit را وارد کنید.", reply_markup=keyboard_admin)
            updates = {
                "step":"SELECT_OPERATION"
            }
            await set_redis(key, updates)

##########################################################################state handler#################################################################

async def run_bot():
    global session
    session = aiohttp.ClientSession()
    
    asyncio.create_task(check_expirations3())
    asyncio.create_task(check_expirations())
    asyncio.create_task(check_expirations_ban())
    asyncio.create_task(check_expirations_u())
    asyncio.create_task(check_expirations_ban_u())

    
    try:
        await bot.infinity_polling()
    finally:
        await session.close()


if __name__ == '__main__':
    asyncio.run(run_bot())