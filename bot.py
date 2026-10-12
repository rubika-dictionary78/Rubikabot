from nicotin import Client, filters
from fonts import convert, FONTS
from database import get_user, set_user
from templates import TEMPLATES

app = Client(bot_token="CGGCJJ0AXXWMPUVNBKQXFRWHGJBLZWTRJEOCLJMUDZKOGYKABGSIYSJKYGDVGFAJ")

# ── چنل‌های اجباری برای قالب سفارشی ──
REQUIRED_CHANNELS = ["@your_channel1", "@your_channel2"]

# ── ادمین‌ها (آیدی عددی) ──
ADMINS = [123456789]


def build_tag(name, user):
    """ساخت تگ نهایی با تنظیمات کاربر"""
    converted = convert(name.strip(), user["font"])
    return f"{user['prefix']}{converted}{user['suffix']}"


# ═══════════════════════════════════════
# /start
# ═══════════════════════════════════════
@app.on_message(filters.command("start"))
async def start(client, message):
    await message.reply(
        "🎨 **ربات تگ‌ساز حرفه‌ای**\n\n"
        "اسمت رو بفرست تا تگ بسازم:\n"
        "`مریم` → 𓄂 ‌مریم ♡𝑫𝑶𝑳𝑭𓆃\n\n"
        "📋 **دستورات:**\n"
        "/fonts — لیست فونت‌ها\n"
        "/setfont [نام فونت] — تغییر فونت\n"
        "/settemplate [نام قالب] — تغییر قالب\n"
        "/templates — لیست قالب‌ها\n"
        "/mytag — تگ فعلی تو\n"
        "/premium — قالب سفارشی (نیاز به اشتراک)\n"
        "/help — راهنما"
    )


# ═══════════════════════════════════════
# /fonts — لیست فونت‌ها
# ═══════════════════════════════════════
@app.on_message(filters.command("fonts"))
async def fonts_cmd(client, message):
    sample = "Sullivan"
    lines = ["🔤 **لیست فونت‌های موجود:**\n"]
    for key in FONTS.keys():
        lines.append(f"• `{key}` → {convert(sample, key)}")
    lines.append("\n📌 برای تغییر: `/setfont bold`")
    await message.reply("\n".join(lines))


# ═══════════════════════════════════════
# /setfont — تغییر فونت
# ═══════════════════════════════════════
@app.on_message(filters.command("setfont"))
async def setfont(client, message):
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        await message.reply("❌ مثال: `/setfont bold`")
        return
    font_name = args[1].strip()
    if font_name not in FONTS:
        await message.reply(f"❌ فونت `{font_name}` وجود نداره.\nاز `/fonts` لیست رو ببین.")
        return
    user = get_user(message.sender_id)
    user["font"] = font_name
    set_user(message.sender_id, user)
    await message.reply(f"✅ فونت به `{font_name}` تغییر کرد.\nنمونه: {convert('Sullivan', font_name)}")


# ═══════════════════════════════════════
# /templates — لیست قالب‌ها
# ═══════════════════════════════════════
@app.on_message(filters.command("templates"))
async def templates_cmd(client, message):
    lines = ["🎨 **قالب‌های موجود:**\n"]
    for key, t in TEMPLATES.items():
        lock = "🔒" if t["premium"] else "✅"
        lines.append(f"{lock} `{key}` — {t['name']}")
    lines.append("\n📌 برای تغییر: `/settemplate karma`")
    await message.reply("\n".join(lines))


# ═══════════════════════════════════════
# /settemplate — تغییر قالب
# ═══════════════════════════════════════
@app.on_message(filters.command("settemplate"))
async def settemplate(client, message):
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        await message.reply("❌ مثال: `/settemplate karma`")
        return
    tpl_name = args[1].strip()
    if tpl_name not in TEMPLATES:
        await message.reply(f"❌ قالب `{tpl_name}` وجود نداره.\nاز `/templates` لیست رو ببین.")
        return

    tpl = TEMPLATES[tpl_name]

    # ── اگه قالب پرمیوم بود ──
    if tpl["premium"]:
        await message.reply(
            "🔒 این قالب **ویژه** است.\n\n"
            "برای استفاده، یکی از این کارها رو انجام بده:\n"
            "۱. در چنل‌های زیر عضو شو:\n" +
            "\n".join([f"   • {ch}" for ch in REQUIRED_CHANNELS]) +
            "\n\n۲. یا از ادمین بخواه پرمیوم بخری.\n\n"
            "بعد از عضو شدن، دستور `/check` رو بزن."
        )
        return

    user = get_user(message.sender_id)
    user["prefix"] = tpl["prefix"]
    user["suffix"] = tpl["suffix"]
    user["font"] = tpl["font"]
    set_user(message.sender_id, user)
    await message.reply(f"✅ قالب `{tpl['name']}` فعال شد.\nنمونه:\n{build_tag('Sullivan', user)}")


# ═══════════════════════════════════════
# /check — چک عضویت چنل‌ها
# ═══════════════════════════════════════
@app.on_message(filters.command("check"))
async def check(client, message):
    try:
        for ch in REQUIRED_CHANNELS:
            member = await client.get_chat_member(ch, message.sender_id)
            if member.status in ["left", "kicked"]:
                await message.reply(f"❌ هنوز در {ch} عضو نشدی.")
                return
        # اگه همه رو عضو بود
        user = get_user(message.sender_id)
        user["paid"] = True
        set_user(message.sender_id, user)
        await message.reply("✅ عضویتت تأیید شد! حالا می‌تونی از قالب‌های ویژه استفاده کنی.")
    except Exception as e:
        await message.reply(f"⚠️ خطا: {e}")


# ═══════════════════════════════════════
# /mytag — نمایش تگ فعلی
# ═══════════════════════════════════════
@app.on_message(filters.command("mytag"))
async def mytag(client, message):
    user = get_user(message.sender_id)
    await message.reply(
        f"📌 **تنظیمات فعلی تو:**\n\n"
        f"🔤 فونت: `{user['font']}`\n"
        f"🎨 پیشوند: `{user['prefix']}`\n"
        f"🎨 پسوند: `{user['suffix']}`\n"
        f"💎 پرمیوم: {'✅' if user['paid'] else '❌'}\n\n"
        f"نمونه:\n{build_tag('مریم', user)}"
    )


# ═══════════════════════════════════════
# /premium — درخواست قالب سفارشی
# ═══════════════════════════════════════
@app.on_message(filters.command("premium"))
async def premium(client, message):
    await message.reply(
        "💎 **قالب سفارشی (Custom Template)**\n\n"
        "با پرمیوم می‌تونی:\n"
        "• پیشوند و پسوند دلخواه خودت رو بذاری\n"
        "• هر فونتی که بخوای انتخاب کنی\n"
        "• قالب اختصاصی خودت رو داشته باشی\n\n"
        "💰 **هزینه:** ۵۰ هزار تومان\n"
        "🎁 **یا رایگان:** عضویت در چنل‌های زیر:\n" +
        "\n".join([f"• {ch}" for ch in REQUIRED_CHANNELS]) +
        "\n\n📌 بعد از عضو شدن `/check` رو بزن."
    )


# ═══════════════════════════════════════
# /setcustom — تنظیم قالب سفارشی (فقط پرمیوم)
# ═══════════════════════════════════════
@app.on_message(filters.command("setcustom"))
async def setcustom(client, message):
    user = get_user(message.sender_id)
    if not user["paid"] and message.sender_id not in ADMINS:
        await message.reply("🔒 این دستور فقط برای کاربران پرمیوم است.\n/premium رو بزن.")
        return
    await message.reply(
        "✏️ قالب سفارشی رو اینطوری بفرست:\n\n"
        "`prefix | suffix | font`\n\n"
        "مثال:\n"
        "`‌⇣☻⇡ | ☾❼❽☽ | bold`\n\n"
        "📌 فونت رو از `/fonts` انتخاب کن."
    )


# ═══════════════════════════════════════
# /help
# ═══════════════════════════════════════
@app.on_message(filters.command("help"))
async def help_cmd(client, message):
    await message.reply(
        "📖 **راهنمای ربات**\n\n"
        "🎯 فقط اسمت رو بفرست تا تگ بگیری!\n\n"
        "**دستورات:**\n"
        "• /fonts — لیست فونت‌ها\n"
        "• /setfont [نام] — تغییر فونت\n"
        "• /templates — لیست قالب‌ها\n"
        "• /settemplate [نام] — تغییر قالب\n"
        "• /mytag — تگ فعلی\n"
        "• /premium — قالب سفارشی\n"
        "• /check — چک عضویت چنل\n"
        "• /setcustom — تنظیم قالب دلخواه (پرمیوم)\n"
    )


# ═══════════════════════════════════════
# دریافت متن ساده (اسم کاربر)
# ═══════════════════════════════════════
@app.on_message(filters.private & filters.text & ~filters.command([
    "start", "fonts", "setfont", "templates", "settemplate",
    "check", "mytag", "premium", "setcustom", "help"
]))
async def handle_name(client, message):
    text = message.text.strip()
    user = get_user(message.sender_id)

    # چک کن اگه فرمت `prefix | suffix | font` بود (برای پرمیوم)
    if "|" in text and (user["paid"] or message.sender_id in ADMINS):
        parts = [p.strip() for p in text.split("|")]
        if len(parts) == 3:
            user["prefix"] = parts[0]
            user["suffix"] = parts[1]
            user["font"] = parts[2] if parts[2] in FONTS else "bold"
            set_user(message.sender_id, user)
            await message.reply(f"✅ قالب سفارشی ذخیره شد.\nنمونه:\n{build_tag('مریم', user)}")
            return

    # حالت عادی: اسم رو تگ کن
    tag = build_tag(text, user)
    await message.reply(tag)


if __name__ == "__main__":
    print("🤖 ربات تگ‌ساز فعال شد...")
    app.run()
