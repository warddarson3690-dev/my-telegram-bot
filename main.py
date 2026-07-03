import telebot
from telebot import types
import sqlite3

bot = telebot.TeleBot("8719481648:AAEJ7_6Bjox6ECNb-0a3enSMkoJ92HzSlcE")
ADMIN_ID = 8719481648  
SHAM_CASH_ACC = "99eaacf1e6155505f1368efdbf48ee4a"

def init_db():
    conn = sqlite3.connect("bot_data.db")
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY, balance INTEGER DEFAULT 0)''')
    conn.commit()
    conn.close()

def get_balance(user_id):
    conn = sqlite3.connect("bot_data.db")
    cursor = conn.cursor()
    cursor.execute("SELECT balance FROM users WHERE user_id = ?", (user_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return row[0]
    return 0

def update_balance(user_id, amount):
    conn = sqlite3.connect("bot_data.db")
    cursor = conn.cursor()
    cursor.execute("INSERT OR IGNORE INTO users (user_id, balance) VALUES (?, 0)", (user_id,))
    cursor.execute("UPDATE users SET balance = balance + ? WHERE user_id = ?", (amount, user_id))
    conn.commit()
    conn.close()

init_db()

def main_menu():
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    markup.add(types.KeyboardButton("🔐 حساب آيشانسي وشحنه"), types.KeyboardButton("💰 شحن البوت"))
    markup.add(types.KeyboardButton("✨ إيشانسي"), types.KeyboardButton("📞 الدعم"))
    return markup

def ichance_menu():
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    markup.add(types.KeyboardButton("➕ إنشاء حساب آيشانسي"), types.KeyboardButton("⚡ شحن حسابي"))
    markup.add(types.KeyboardButton("💸 سحب رصيد من الحساب"), types.KeyboardButton("🔙 العودة للقائمة الرئيسية"))
    return markup

def bot_charge_menu():
    markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    markup.add(types.KeyboardButton("📱 شام كاش ليرة سورية"), types.KeyboardButton("🔙 العودة للقائمة الرئيسية"))
    return markup

@bot.message_handler(commands=['start'])
def welcome(message):
    user_id = message.chat.id
    current_bal = get_balance(user_id)
    bot.send_message(user_id, f"أهلاً بك! رصيدك الحالي في البوت: {current_bal} ليرة", reply_markup=main_menu())

@bot.message_handler(func=lambda message: True)
def handle_buttons(message):
    user_id = message.chat.id
    current_bal = get_balance(user_id)

    if message.text == "🔐 حساب آيشانسي وشحنه":
        bot.send_message(user_id, "قائمة حساب آيشانسي:", reply_markup=ichance_menu())
        
    elif message.text == "➕ إنشاء حساب آيشانسي":
        msg = bot.send_message(user_id, "أدخل اسم المستخدم  👇")
        bot.register_next_step_handler(msg, process_create_account)
        
    elif message.text == "💸 سحب رصيد من الحساب":
        msg = bot.send_message(user_id, "أدخل المبلغ المراد سحبه  👇\n\nيرجى الانتباه الى ضرورة إدخال الارقام باللغة الانكليزية فقط")
        bot.register_next_step_handler(msg, process_withdraw_amount)
        
    elif message.text == "⚡ شحن حسابي":
        msg = bot.send_message(user_id, f"رصيدك المتوفر بالبوت: {current_bal} ليرة.\nأدخل المبلغ المراد شحنه إلى حساب آيشانسي  👇\n\nيرجى الانتباه الى ضرورة إدخال الارقام باللغة الانكليزية فقط")
        bot.register_next_step_handler(msg, process_ichance_charge)
        
    elif message.text == "💰 شحن البوت":
        bot.send_message(user_id, "اخــتــر أحــد طــرق الــشــحــن:", reply_markup=bot_charge_menu())
        
    elif message.text == "📱 شام كاش ليرة سورية":
        msg = (f"لشحن رصيدك عبر شام كاش:\n\n"
               f"1. حول المبلغ إلى الحساب: {SHAM_CASH_ACC}\n"
               f"2. بعد التحويل، أرسل لقطة شاشة للعملية هنا فورا.")
        bot.send_message(user_id, msg)
        bot.register_next_step_handler(message, process_sham_cash_screenshot)
        
    elif message.text == "📞 الدعم":
        msg = bot.send_message(user_id, "أهلاً بك اترك رسالة وسوف نرد عليك في أقرب وقت  👇")
        bot.register_next_step_handler(msg, process_support_message)
        
    elif message.text == "🔙 العودة للقائمة الرئيسية":
        bot.send_message(user_id, f"رجعت للقائمة الرئيسية:\nرصيدك الحالي: {current_bal} ليرة", reply_markup=main_menu())

def process_create_account(message):
    username_requested = message.text
    bot.send_message(ADMIN_ID, f"🆕 طلب إنشاء حساب آيشانسي جديد\nمن العميل: {message.from_user.first_name}\nاسم المستخدم المطلوب: `{username_requested}`")
    bot.send_message(message.chat.id, "تم إرسال طلب إنشاء الحساب للإدارة. سيتم التواصل معك فور تجهيزه.")

def process_support_message(message):
    support_text = message.text
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("💬 تواصل مع العميل", url=f"tg://user?id={message.chat.id}"))
    bot.send_message(ADMIN_ID, f"📞 رسالة دعم فني جديدة\nمن: {message.from_user.first_name}\nالرسالة:\n{support_text}", reply_markup=markup)
    bot.send_message(message.chat.id, "تم إرسال رسالتك للدعم بنجاح. سيتم الرد عليك في أقرب وقت.")

def process_sham_cash_screenshot(message):
    if message.content_type == 'photo':
        photo_id = message.photo[-1].file_id
        msg = bot.send_message(message.chat.id, "يرجى كتابة المبلغ الذي قمت بتحويله باللغة الإنجليزية:")
        bot.register_next_step_handler(msg, lambda m: forward_screenshot_to_admin(m, photo_id))
    else:
        bot.send_message(message.chat.id, "خطأ: يرجى إرسال صورة لقطة الشاشة.")

def forward_screenshot_to_admin(message, photo_id):
    amount = message.text
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("✅ موافقة", callback_data=f"app_bot_{message.chat.id}_{amount}"))
    markup.add(types.InlineKeyboardButton("❌ رفض", callback_data=f"rej_bot_{message.chat.id}"))
    bot.send_photo(ADMIN_ID, photo_id, caption=f"📥 طلب شحن رصيد البوت\nمن المستخدم: {message.from_user.first_name}\nالمبلغ المذكور: {amount} ليرة", reply_markup=markup)
    bot.send_message(message.chat.id, "تم إرسال طلب الشحن ولقطة الإشعار للإدارة. جاري المراجعة...")

def process_ichance_charge(message):
    user_id = message.chat.id
    current_bal = get_balance(user_id)
    try:
        amount = int(message.text)
        if amount <= 0:
            bot.send_message(user_id, "يرجى إدخال مبلغ صحيح.")
            return
        if current_bal < amount:
            bot.send_message(user_id, "عذراً، رصيدك في البوت غير كافي لإتمام هذه العملية.")
            return
            
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("✅ موافقة ويتم الخصم", callback_data=f"app_ich_{user_id}_{amount}"))
        markup.add(types.InlineKeyboardButton("❌ رفض", callback_data=f"rej_ich_{user_id}"))
        
        bot.send_message(ADMIN_ID, f"🔔 طلب شحن حساب آيشانسي\nالعميل: {message.from_user.first_name}\nالمبلغ المطلوب: {amount} ليرة من رصيده بالبوت.", reply_markup=markup)
        bot.send_message(user_id, "تم إرسال طلب شحن حساب آيشانسي للإدارة. يرجى الانتظار لحين تأكيد الشحن.")
    except ValueError:
        bot.send_message(user_id, "خطأ: يرجى إدخال الأرقام باللغة الإنجليزية فقط.")

def process_withdraw_amount(message):
    bot.send_message(message.chat.id, "تم استلام طلب السحب، سيتم التواصل معك من قبل الإدارة.")

@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    data = call.data.split('_')
    action = data[0]
    target = data[1]
    client_id = int(data[2])
    
    if action == "app" and target == "bot":
        amount = int(data[3])
        update_balance(client_id, amount)
        bot.answer_callback_query(call.id, "تمت الموافقة وشحن الرصيد!")
        bot.edit_message_caption(chat_id=ADMIN_ID, message_id=call.message.message_id, caption=call.message.caption + "\n\n✅ [تمت الموافقة والشحن]")
        bot.send_message(client_id, f"🎉 تم تأكيد دفعتك! تم إضافة {amount} ليرة لرصيدك في البوت بنجاح.")
        
    elif action == "rej" and target == "bot":
        bot.answer_callback_query(call.id, "تم رفض الطلب")
        bot.edit_message_caption(chat_id=ADMIN_ID, message_id=call.message.message_id, caption=call.message.caption + "\n\n❌ [تم رفض الطلب]")
        bot.send_message(client_id, "❌ عذراً، تم رفض طلب شحن الرصيد من قبل الإدارة. يرجى التواصل مع الدعم.")
        
    elif action == "app" and target == "ich":
        amount = int(data[3])
        current_bal = get_balance(client_id)
        if current_bal >= amount:
            update_balance(client_id, -amount)
            bot.answer_callback_query(call.id, "تم شحن آيشانسي وخصم الرصيد!")
            bot.edit_message_text(chat_id=ADMIN_ID, message_id=call.message.message_id, text=call.message.text + "\n\n✅ [تم الشحن والخصم]")
            bot.send_message(client_id, f"⚡ تم شحن حسابك آيشانسي بمبلغ {amount} ليرة بنجاح، وتم خصمها من رصيد البوت الخاص بك.")
            
    elif action == "rej" and target == "ich":
        bot.answer_callback_query(call.id, "تم رفض شحن آيشانسي")
        bot.edit_message_text(chat_id=ADMIN_ID, message_id=call.message.message_id, text=call.message.text + "\n\n❌ [تم رفض الطلب]")
        bot.send_message(client_id, "❌ تم رفض طلب شحن حساب آيشانسي الخاص بك من قبل الإدارة.")

bot.polling()
  
