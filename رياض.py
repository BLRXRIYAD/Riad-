#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import telebot
from telebot import types
import json
import time
from datetime import datetime, timedelta
import os
import requests
import threading
import asyncio

# استيراد الوظائف من main.py
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# استيراد المستلزمات من main.py
try:
    from byte import *
    from important_zitado import *
except ImportError:
    # في حالة عدم توفر هذه الملفات، سنستخدم الدوال المحلية
    print("⚠️ تحذير: لم يتم العثور على ملفات byte.py أو important_zitado.py")

# إعدادات البوت
TELEGRAM_TOKEN = "8024394383:AAGLlQqhJr_AhomCOMgbGMOcVLNdM3xTkMI"
ADMIN_ID = 8415652042
def load_telegram_settings():
    try:
        with open('telegram_settings.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        # إنشاء ملف الإعدادات الافتراضي
        default_settings = {
            "allowed_chat": None,
            "admins": [ADMIN_ID],
            "dev_id": ADMIN_ID
        }
        with open('telegram_settings.json', 'w', encoding='utf-8') as f:
            json.dump(default_settings, f, indent=4, ensure_ascii=False)
        return default_settings

# استخدام نفس ملف قاعدة البيانات من main.py
USERS_DATA_FILE = "bot_users.json"
ADMIN_JWT_TOKEN = None

# دوال إدارة المستخدمين من main.py
def Encrypt_ID(number):
    """تشفير معرف اللاعب لاستخدامه في طلبات الصداقة"""
    number = int(number)
    encoded_bytes = []
    while True:
        byte = number & 0x7F
        number >>= 7
        if number:
            byte |= 0x80
        encoded_bytes.append(byte)
        if not number:
            break
    return bytes(encoded_bytes).hex()

def encrypt_api(plain_text):
    """تشفير البيانات للـ API"""
    from Crypto.Cipher import AES
    from Crypto.Util.Padding import pad
    plain_text = bytes.fromhex(plain_text)
    key = bytes([89, 103, 38, 116, 99, 37, 68, 69, 117, 104, 54, 37, 90, 99, 94, 56])
    iv = bytes([54, 111, 121, 90, 68, 114, 50, 50, 69, 51, 121, 99, 104, 106, 77, 37])
    cipher = AES.new(key, AES.MODE_CBC, iv)
    cipher_text = cipher.encrypt(pad(plain_text, AES.block_size))
    return cipher_text.hex()

def load_bot_users():
    """تحميل قاعدة بيانات المستخدمين المضافين"""
    if os.path.exists(USERS_DATA_FILE):
        with open(USERS_DATA_FILE, "r", encoding="utf-8") as file:
            try:
                data = json.load(file)
                if isinstance(data, dict):
                    return data
            except json.JSONDecodeError:
                pass
    return {}

def save_bot_users(bot_users):
    """حفظ قاعدة بيانات المستخدمين"""
    with open(USERS_DATA_FILE, "w", encoding="utf-8") as file:
        json.dump(bot_users, file, ensure_ascii=False, indent=4)

def format_remaining_time(expiry_time):
    """تنسيق الوقت المتبقي"""
    remaining = int(expiry_time - time.time())
    if remaining <= 0:
        return "⛔ انتهت الصلاحية"
    days = remaining // 86400
    hours = (remaining % 86400) // 3600
    return f"{days} يوم / {hours} ساعة"

def fetch_jwt_token():
    """جلب JWT token من الخادم"""
    url = ("https://protective-vere-blackkk805-4c844f10.koyeb.app/GeneRate-Jwt?"
           "Uid=هنا تحط ايدي بوتك&Pw=هنا تحط باسسورد بوتك")
    try:
        resp = requests.get(url, timeout=10)
        if resp.status_code == 200 and resp.text.strip():
            response_text = resp.text.strip()
            if response_text.startswith("- ToKen :"):
                return response_text.split(":")[1].strip()
            return response_text
    except Exception as e:
        print(f"⚠️ JWT ERROR: {e}")
    return None

def send_friend_request(player_id):
    """إرسال طلب صداقة للاعب"""
    global ADMIN_JWT_TOKEN
    if not ADMIN_JWT_TOKEN:
        ADMIN_JWT_TOKEN = fetch_jwt_token()
    
    if not ADMIN_JWT_TOKEN:
        return "⚠️ التوكن غير متاح حاليًا، حاول لاحقًا."
    
    enc_id = Encrypt_ID(player_id)
    payload = f"08a7c4839f1e10{enc_id}1801"
    encrypted_payload = encrypt_api(payload)
    url = "https://clientbp.ggblueshark.com/RequestAddingFriend"
    headers = {
        "Authorization": f"Bearer {ADMIN_JWT_TOKEN}",
        "X-Unity-Version": "2018.4.11f1",
        "X-GA": "v1 1",
        "ReleaseVersion": "OB50",
        "Content-Type": "application/x-www-form-urlencoded",
        "Content-Length": str(len(encrypted_payload)),
        "User-Agent": "Dalvik/2.1.0 (Linux; Android 9)",
        "Connection": "close",
    }
    try:
        r = requests.post(url, headers=headers, data=bytes.fromhex(encrypted_payload), timeout=10)
        if r.status_code == 200:
            return "✅ تم إرسال طلب الصداقة بنجاح!"
        return f"⚠️ فشل إرسال الطلب. كود الخطأ: {r.status_code}"
    except Exception as e:
        return f"⚠️ حدث خطأ أثناء إرسال الطلب: {e}"

def remove_friend(player_id):
    """حذف صديق من قائمة الأصدقاء"""
    global ADMIN_JWT_TOKEN
    if not ADMIN_JWT_TOKEN:
        ADMIN_JWT_TOKEN = fetch_jwt_token()
    
    if not ADMIN_JWT_TOKEN:
        return "⚠️ التوكن غير متاح حاليًا، حاول لاحقًا."
    
    enc_id = Encrypt_ID(player_id)
    payload = f"08a7c4839f1e10{enc_id}1801"
    encrypted_payload = encrypt_api(payload)
    url = "https://clientbp.ggblueshark.com/RemoveFriend"
    headers = {
        "Authorization": f"Bearer {ADMIN_JWT_TOKEN}",
        "X-Unity-Version": "2018.4.11f1",
        "X-GA": "v1 1",
        "ReleaseVersion": "OB50",
        "Content-Type": "application/x-www-form-urlencoded",
        "Content-Length": str(len(encrypted_payload)),
        "User-Agent": "Dalvik/2.1.0 (Linux; Android 9)",
        "Connection": "close",
    }
    try:
        r = requests.post(url, headers=headers, data=bytes.fromhex(encrypted_payload), timeout=10)
        if r.status_code == 200:
            return "✅ تم الحذف بنجاح!"
        return f"⚠️ فشل حذف الصديق. كود الخطأ: {r.status_code}"
    except Exception as e:
        return f"⚠️ حدث خطأ أثناء الحذف: {e}"

def get_player_info_for_add(uid):
    """الحصول على معلومات اللاعب لإضافته"""
    try:
        res = requests.get(f"https://info-api-murex.vercel.app/accinfo?key=OnyxOverlord1&uid={uid}", timeout=10)
        if res.status_code == 200:
            data = res.json()
            if "basicInfo" in data:
                basic_info = data["basicInfo"]
                name = basic_info.get("nickname", "غير معروف")
                region = basic_info.get("region", "Unknown")
                level = basic_info.get("level", 0)
                return name, region, level
    except Exception as e:
        print(f"⚠️ Error fetching info for {uid}: {e}")
    return "غير معروف", "N/A", "N/A"

def fix_num(num):
    """تنسيق الأرقام بإضافة فواصل"""
    fixed = ""
    count = 0
    num_str = str(num)
    
    for char in num_str:
        if char.isdigit():
            count += 1
        fixed += char
        if count == 3:
            fixed += "[c]"
            count = 0  
    return fixed

def remove_expired_users():
    """حذف المستخدمين منتهي الصلاحية تلقائياً"""
    bot_users = load_bot_users()
    now = time.time()
    expired = [uid for uid, d in bot_users.items() if d.get("expiry", 0) <= now]
    for uid in expired:
        try:
            remove_friend(uid)
            del bot_users[uid]
        except:
            continue
    if expired:
        save_bot_users(bot_users)
    return len(expired)

# تهيئة JWT Token
def init_jwt_token():
    global ADMIN_JWT_TOKEN
    print("🔄 جاري تهيئة JWT Token...")
    for _ in range(5):
        ADMIN_JWT_TOKEN = fetch_jwt_token()
        if ADMIN_JWT_TOKEN:
            print("✅ تم جلب JWT Token بنجاح")
            return True
        print("⚠️ محاولة أخرى لجلب JWT Token...")
        time.sleep(3)
    
    print("⚠️ تحذير: لم يتم الحصول على JWT Token")
    return False

# إعداد البوت
settings = load_telegram_settings()
bot_users = load_bot_users()

bot = telebot.TeleBot(TELEGRAM_TOKEN)

# دالة للتحقق من الصلاحيات
def is_admin(user_id):
    return user_id in settings["admins"] or user_id == settings["dev_id"]

def is_dev(user_id):
    return user_id == settings["dev_id"]

# التحقق من المحادثة المسموحة أو الخاص للمطور/الإدمن
def check_chat_permission(message):
    # إذا كانت رسالة خاصة، تسمح فقط للمطور والإدمن
    if message.chat.type == 'private':
        return is_admin(message.from_user.id)
    
    # إذا كانت في مجموعة، تحقق من المحادثة المسموحة
    if settings["allowed_chat"]:
        return message.chat.id == settings["allowed_chat"]
    
    return False  # منع العمل في المجموعات غير المحددة

# دالة لتنظيف المستخدمين منتهيي الصلاحية
def cleanup_expired_users():
    global bot_users
    expired_count = remove_expired_users()
    if expired_count > 0:
        bot_users = load_bot_users()  # إعادة تحميل البيانات
        print(f"🧹 تم حذف {expired_count} مستخدم منتهي الصلاحية")
    return expired_count

# أمر /start
@bot.message_handler(commands=['start'])
def start_command(message):
    """رسالة الترحيب"""
    user = message.from_user
    
    if not check_chat_permission(message):
        bot.reply_to(message, "⚠️ لا يمكنك استخدام البوت هنا. استخدم المحادثة المسموحة فقط.")
        return
    
    welcome_text = f"""🎮 مرحباً {user.first_name}!

📋 قائمة الأوامر المتاحة:

👥 أوامر المستخدمين:
/add - إضافة معرف للبوت (24 ساعة فقط)
/help - عرض قائمة الأوامر"""
    
    if is_admin(user.id):
        welcome_text += """

🛡️ أوامر الإدمن:
/add - إضافة معرف بمدة مخصصة
/remove - حذف معرف من البوت
/list - عرض قائمة المستخدمين
/sync - مزامنة قاعدة البيانات
/status - حالة النظام"""
    
    welcome_text += """

ℹ️ ملاحظات:
• يعمل فقط في المحادثات المخصصة
• المستخدمون العاديون: /add فقط (24 ساعة)
• الإدمن: جميع الأوامر
• الرسائل الخاصة: للمطور والإدمن فقط
""" + "اي واحد يريد اي خدمة زيادة لفل بوتات اي شيء في راسوا يحيني @BLRXH4RDIXX".replace("_", "\\_").replace("*", "\\*").replace("`", "\\`")
    
    bot.send_message(message.chat.id, welcome_text)

# أمر /help
@bot.message_handler(commands=['help'])
def help_command(message):
    """عرض قائمة الأوامر"""
    
    if not check_chat_permission(message):
        bot.reply_to(message, "⚠️ لا يمكنك استخدام الأوامر هنا. استخدم المحادثة المسموحة فقط.")
        return
    
    help_text = """📋 قائمة الأوامر
بوت إدارة المستخدمين - متصل مع النظام الرئيسي

👥 أوامر المستخدمين:
/add - بوت مجاني
/help - عرض هذه القائمة"""
    
    if is_admin(message.from_user.id):
        help_text += """

🛡️ أوامر الإدمن:
/add - إضافة معرف بمدة مخصصة
/remove - حذف معرف من البوت
/list - عرض قائمة المستخدمين
/sync - مزامنة قاعدة البيانات
/status - حالة النظام"""
    
    bot.send_message(message.chat.id, help_text)

# أمر /add للمستخدمين العاديين (يوم واحد فقط)
@bot.message_handler(commands=['add'])
def add_user_command(message):
    """إضافة مستخدم للبوت"""
    global bot_users
    
    # التحقق من المحادثة المسموحة
    if not check_chat_permission(message):
        bot.reply_to(message, "⚠️ لا يمكنك استخدام الأوامر هنا. استخدم المحادثة المسموحة فقط.")
        return
    
    args = message.text.split()[1:]  # إزالة /add من النص
    
    if len(args) < 1:
        bot.reply_to(message, "❌ **استخدام خاطئ**\n\nالاستخدام: `/add <uid> [hours]`\n\nمثال: `/add 123456789`", parse_mode='Markdown')
        return
    
    uid = args[0]
    hours = 24  # افتراضي للمستخدمين العاديين
    
    # التحقق من صحة UID
    if not uid.isdigit() or len(uid) < 8:
        bot.reply_to(message, "❌ **خطأ في المعرف**\n\nيرجى إدخال UID صحيح (أرقام فقط، على الأقل 8 أرقام)", parse_mode='Markdown')
        return
    
    # إذا كان هناك معامل ثاني (الساعات)
    if len(args) >= 2:
        try:
            hours = int(args[1])
        except ValueError:
            bot.reply_to(message, "❌ **خطأ في عدد الساعات**\n\nيرجى إدخال رقم صحيح للساعات", parse_mode='Markdown')
            return
    
    # المستخدمون العاديون يمكنهم إضافة يوم واحد فقط
    if not is_admin(message.from_user.id) and hours != 24:
        hours = 24
    
    # الإدمن يمكنه تحديد المدة
    if is_admin(message.from_user.id) and hours > 8760:  # أقصى سنة واحدة
        hours = 8760
    
    # تنظيف المستخدمين منتهيي الصلاحية أولاً
    cleanup_expired_users()
    
    # إعادة تحميل البيانات
    bot_users = load_bot_users()
    
    # التحقق من وجود المستخدم مسبقاً
    if uid in bot_users:
        user_data = bot_users[uid]
        remaining_time = format_remaining_time(user_data.get('expiry', 0))
        
        response_text = f"""
⚠️ **المستخدم موجود مسبقاً**

المعرف `{uid}` مضاف بالفعل في قاعدة البيانات

⏰ **الوقت المتبقي:** {remaining_time}
👤 **تم الإضافة بواسطة:** {user_data.get('added_by', 'غير معروف')}
"""
        bot.send_message(message.chat.id, response_text, parse_mode='Markdown')
        return
    
    # رسالة المعالجة
    processing_msg = bot.send_message(message.chat.id, f"🔄 **جاري المعالجة...**\n\nجاري إضافة المعرف `{uid}` للبوت", parse_mode='Markdown')
    
    # الحصول على معلومات اللاعب
    name, region, level = get_player_info_for_add(uid)
    
    # إضافة المستخدم الجديد
    expiry_time = time.time() + (hours * 60 * 60)
    
    bot_users[uid] = {
        'name': name,
        'region': region,
        'level': level,
        'expiry': expiry_time,
        'added_by': f"{message.from_user.first_name} (@{message.from_user.username})" if message.from_user.username else message.from_user.first_name,
        'added_time': time.time()
    }
    
    save_bot_users(bot_users)
    
    # إرسال طلب صداقة
    friend_result = send_friend_request(uid)
    
    # حساب تاريخ الانتهاء
    expiry_date = datetime.fromtimestamp(expiry_time).strftime('%Y-%m-%d %H:%M:%S')
    
    response_text = f"""
✅ **تم إضافة المستخدم بنجاح**

🆔 **المعرف:** `{uid}`
👤 **اسم اللاعب:** {name}
🎖️ **المستوى:** {level}
🌍 **السيرفر:** {region}
⏰ **مدة الصلاحية:** {hours} ساعة
👤 **تم الإضافة بواسطة:** {message.from_user.first_name}
📅 **تاريخ الانتهاء:** {expiry_date}

🤝 **طلب الصداقة:** {friend_result}
"""
    
    bot.edit_message_text(response_text, message.chat.id, processing_msg.message_id, parse_mode='Markdown')

# أمر /remove للإدمن فقط
@bot.message_handler(commands=['remove'])
def remove_user_command(message):
    """حذف مستخدم من قاعدة البيانات (للإدمن فقط)"""
    global bot_users
    
    # التحقق من المحادثة المسموحة
    if not check_chat_permission(message):
        bot.reply_to(message, "⚠️ لا يمكنك استخدام الأوامر هنا. استخدم المحادثة المسموحة فقط.")
        return
    
    # التحقق من صلاحيات الإدمن
    if not is_admin(message.from_user.id):
        bot.reply_to(message, "❌ **ليس لديك صلاحية**\n\nهذا الأمر للإدمن فقط", parse_mode='Markdown')
        return
    
    args = message.text.split()[1:]  # إزالة /remove من النص
    
    if len(args) < 1:
        bot.reply_to(message, "❌ **استخدام خاطئ**\n\nالاستخدام: `/remove <uid>`\n\nمثال: `/remove 123456789`", parse_mode='Markdown')
        return
    
    uid = args[0]
    
    # تنظيف المستخدمين منتهيي الصلاحية أولاً
    cleanup_expired_users()
    
    # إعادة تحميل البيانات
    bot_users = load_bot_users()
    
    # التحقق من وجود المستخدم
    if uid not in bot_users:
        bot.reply_to(message, f"❌ **المستخدم غير موجود**\n\nالمعرف `{uid}` غير موجود في قاعدة البيانات", parse_mode='Markdown')
        return
    
    # رسالة المعالجة
    processing_msg = bot.send_message(message.chat.id, f"🔄 **جاري المعالجة...**\n\nجاري حذف المعرف `{uid}` من البوت", parse_mode='Markdown')
    
    # الحصول على بيانات المستخدم قبل الحذف
    user_data = bot_users[uid]
    
    # حذف الصديق من اللعبة
    friend_result = remove_friend(uid)
    
    # حذف المستخدم
    del bot_users[uid]
    save_bot_users(bot_users)
    
    response_text = f"""
✅ **تم حذف المستخدم**

🆔 **المعرف:** `{uid}`
👤 **اسم اللاعب:** {user_data.get('name', 'غير معروف')}
👤 **كان مضاف بواسطة:** {user_data.get('added_by', 'غير معروف')}
🗑️ **تم الحذف بواسطة:** {message.from_user.first_name}

🤝 **حذف من الأصدقاء:** {friend_result}
"""
    
    bot.edit_message_text(response_text, message.chat.id, processing_msg.message_id, parse_mode='Markdown')

# أمر /list للإدمن فقط
@bot.message_handler(commands=['list'])
def list_users_command(message):
    """عرض قائمة المستخدمين (للإدمن فقط)"""
    global bot_users
    
    # التحقق من المحادثة المسموحة
    if not check_chat_permission(message):
        bot.reply_to(message, "⚠️ لا يمكنك استخدام الأوامر هنا. استخدم المحادثة المسموحة فقط.")
        return
    
    # التحقق من صلاحيات الإدمن
    if not is_admin(message.from_user.id):
        bot.reply_to(message, "❌ **ليس لديك صلاحية**\n\nهذا الأمر للإدمن فقط", parse_mode='Markdown')
        return
    
    # تنظيف المستخدمين منتهيي الصلاحية أولاً
    cleanup_expired_users()
    
    # إعادة تحميل البيانات
    bot_users = load_bot_users()
    
    if not bot_users:
        bot.reply_to(message, "📋 **قائمة المستخدمين**\n\nلا يوجد مستخدمين مسجلين حالياً", parse_mode='Markdown')
        return
    
    # تقسيم القائمة إلى صفحات (5 مستخدمين لكل رسالة)
    users_per_page = 5
    total_users = len(bot_users)
    users_list = list(bot_users.items())
    
    response_text = f"📋 **قائمة المستخدمين**\nإجمالي المستخدمين: {total_users}\n\n"
    
    for i, (uid, user_data) in enumerate(users_list[:users_per_page], 1):
        remaining_time = format_remaining_time(user_data.get('expiry', 0))
        name = user_data.get('name', 'غير معروف')
        level = user_data.get('level', 'N/A')
        region = user_data.get('region', 'N/A')
        added_by = user_data.get('added_by', 'غير معروف')
        
        # تهريب الرموز الخاصة في النص
        name = name.replace("_", "\\_").replace("*", "\\*").replace("`", "\\`")
        region = region.replace("_", "\\_").replace("*", "\\*").replace("`", "\\`")
        added_by = added_by.replace("_", "\\_").replace("*", "\\*").replace("`", "\\`")
        remaining_time = remaining_time.replace("_", "\\_").replace("*", "\\*").replace("`", "\\`")
        
        response_text += f"""
**{i}. 🆔** `{fix_num(uid)}`
👤 {name} | 🎖️ Lv.{level} | 🌍 {region}
⏰ {remaining_time}
👤 أضافه: {added_by}
"""
        response_text += "─" * 30 + "\n"
    
    if total_users > users_per_page:
        response_text += f"\n*عرض أول {users_per_page} من {total_users} مستخدم*"
    
    # إرسال الرسالة بدون وضع التحليل Markdown
    bot.send_message(message.chat.id, response_text)

# أمر /status لحالة النظام
@bot.message_handler(commands=['status'])
def system_status_command(message):
    """عرض حالة النظام"""
    global bot_users
    
    if not check_chat_permission(message):
        bot.reply_to(message, "⚠️ لا يمكنك استخدام الأوامر هنا. استخدم المحادثة المسموحة فقط.")
        return
    
    if not is_admin(message.from_user.id):
        bot.reply_to(message, "❌ هذا الأمر للإدمن فقط")
        return
    
    # إعادة تحميل البيانات
    bot_users = load_bot_users()
    
    # فحص JWT Token
    token_status = "✅ متاح" if ADMIN_JWT_TOKEN else "❌ غير متاح"
    
    # حساب المستخدمين
    total_users = len(bot_users)
    active_users = sum(1 for user_data in bot_users.values() if user_data.get('expiry', 0) > time.time())
    expired_users = total_users - active_users
    
    response_text = f"""
📊 **حالة النظام**
إحصائيات بوت إدارة المستخدمين

🔐 **JWT Token:** {token_status}
👥 **إجمالي المستخدمين:** {total_users}
✅ **المستخدمين النشطين:** {active_users}
⏰ **المستخدمين منتهيي الصلاحية:** {expired_users}
📁 **ملف قاعدة البيانات:** {"✅ موجود" if os.path.exists(USERS_DATA_FILE) else "❌ غير موجود"}
🤖 **حالة البوت:** 🟢 متصل
"""
    
    bot.send_message(message.chat.id, response_text, parse_mode='Markdown')

# أمر /allow لتحديد المحادثة المسموحة (للإدمن فقط)
@bot.message_handler(commands=['allow'])
def set_allowed_chat_command(message):
    """تحديد المحادثة المسموحة للأوامر (للإدمن فقط)"""
    
    if not is_admin(message.from_user.id):
        bot.reply_to(message, "❌ ليس لديك صلاحية\n\nهذا الأمر للإدمن فقط")
        return
    
    # إذا كان الأمر في مجموعة، قم بتعيين هذه المجموعة كمسموحة
    if message.chat.type in ['group', 'supergroup']:
        settings["allowed_chat"] = message.chat.id
        
        # حفظ الإعدادات
        with open('telegram_settings.json', 'w', encoding='utf-8') as f:
            json.dump(settings, f, indent=4, ensure_ascii=False)
        
        response_text = f"""✅ تم تحديث المحادثة المسموحة

📍 تم تحديد هذه المجموعة كمحادثة مسموحة للأوامر
🆔 معرف المحادثة: {message.chat.id}
👤 تم التحديث بواسطة: {message.from_user.first_name}

البوت سيعمل الآن فقط في هذه المجموعة والرسائل الخاصة للمشرفين."""
        
        bot.send_message(message.chat.id, response_text)
    
    elif message.chat.type == 'private':
        # عرض المحادثة الحالية المسموحة
        current_chat = settings.get("allowed_chat")
        if current_chat:
            response_text = f"""📍 المحادثة المسموحة الحالية

🆔 معرف المحادثة: {current_chat}

لتغيير المحادثة المسموحة، استخدم الأمر /allow في المجموعة الجديدة."""
        else:
            response_text = """📍 المحادثة المسموحة

لم يتم تحديد محادثة مسموحة حالياً.
البوت يعمل فقط في الرسائل الخاصة للمشرفين.

لتحديد مجموعة مسموحة، استخدم الأمر /allow في المجموعة."""
        
        bot.send_message(message.chat.id, response_text)

# أمر /sync لمزامنة قاعدة البيانات
@bot.message_handler(commands=['sync'])
def sync_database_command(message):
    """مزامنة قاعدة البيانات مع النظام الرئيسي"""
    global bot_users
    
    if not check_chat_permission(message):
        bot.reply_to(message, "⚠️ لا يمكنك استخدام الأوامر هنا. استخدم المحادثة المسموحة فقط.")
        return
    
    if not is_admin(message.from_user.id):
        bot.reply_to(message, "❌ هذا الأمر للإدمن فقط")
        return
    
    # تنظيف المنتهية الصلاحية
    expired_count = cleanup_expired_users()
    
    # إعادة تحميل البيانات
    bot_users = load_bot_users()
    
    response_text = f"""
🔄 **تمت المزامنة**

تم تحديث قاعدة البيانات
المستخدمين الحاليين: {len(bot_users)}
"""
    
    if expired_count > 0:
        response_text += f"\n🧹 **تنظيف:** تم حذف {expired_count} مستخدم منتهي الصلاحية"
    
    bot.send_message(message.chat.id, response_text, parse_mode='Markdown')

# تشغيل مهام دورية في الخلفية
def background_tasks():
    """مهام تعمل في الخلفية"""
    while True:
        try:
            # تنظيف المستخدمين منتهيي الصلاحية كل 5 دقائق
            cleanup_expired_users()
            
            # تحديث JWT Token كل ساعة
            global ADMIN_JWT_TOKEN
            if not ADMIN_JWT_TOKEN:
                init_jwt_token()
            
        except Exception as e:
            print(f"خطأ في المهام الخلفية: {e}")
        
        # انتظار 5 دقائق
        time.sleep(300)

# تشغيل البوت
if __name__ == "__main__":
    print(f'✅ Telegram Bot جاهز!')
    print(f'🔧 الإعدادات المحملة: {len(settings)} إعدادات')
    print(f'👥 المستخدمين المسجلين: {len(bot_users)} مستخدم')
    
    # تهيئة JWT Token في الخلفية
    def init_token_background():
        init_jwt_token()
    
    token_thread = threading.Thread(target=init_token_background, daemon=True)
    token_thread.start()
    
    # تشغيل المهام الخلفية
    background_thread = threading.Thread(target=background_tasks, daemon=True)
    background_thread.start()
    
    try:
        # بدء استقبال الرسائل
        bot.polling(non_stop=True, interval=0)
    except Exception as e:
        print(f"❌ خطأ في تشغيل البوت: {e}")