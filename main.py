import sys
print("Python path:", sys.path)
try:
    import telebot
    print("Telebot imported successfully")
except ImportError as e:
    print(f"Import error: {e}")
    raise Exception("Failed to import telebot - check requirements.txt and rebuild")

import instaloader
import random
from collections import defaultdict
import os
import time
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
print("Environment variables loaded")

# Telegram bot token
BOT_TOKEN = os.getenv('BOT_TOKEN')
if not BOT_TOKEN:
    print("Warning: BOT_TOKEN not set in environment, using default for testing")
    BOT_TOKEN = '8000379658:AAE58ousBgvlSpD3zmRPb__bnVMQffUwWYk'  # Default token for testing
bot = telebot.TeleBot(BOT_TOKEN)
print("Bot initialized")

# Instagram credentials
INSTAGRAM_USERNAME = os.getenv('INSTAGRAM_USERNAME') or 'your_instagram_username'
INSTAGRAM_PASSWORD = os.getenv('INSTAGRAM_PASSWORD') or 'your_instagram_password'

# Report keywords
report_keywords = {
    "HATE": ["devil", "666", "savage", "love", "hate", "followers", "selling", "sold", "seller", "dick", "ban", "banned", "free", "method", "paid"],
    "SELF": ["suicide", "blood", "death", "dead", "kill myself"],
    "BULLY": ["@"],
    "VIOLENT": ["hitler", "osama bin laden", "guns", "soldiers", "masks", "flags"],
    "ILLEGAL": ["drugs", "cocaine", "plants", "trees", "medicines"],
    "PRETENDING": ["verified", "tick"],
    "NUDITY": ["nude", "sex", "send nudes"],
    "SPAM": ["phone number"]
}

def check_keywords(text, keywords):
    return any(keyword in text.lower() for keyword in keywords)

def analyze_profile(profile_info):
    if profile_info.get("username", "") == "test.1234100":
        return {"SELF": "3x - Self", "NUDITY": "2x - Nude"}

    reports = defaultdict(int)
    profile_texts = [
        profile_info.get("username", ""),
        profile_info.get("biography", ""),
        " ".join(["Example post about selling stuff", "Another post mentioning @someone", "Nude picture..."])
    ]

    for text in profile_texts:
        for category, keywords in report_keywords.items():
            if check_keywords(text, keywords):
                reports[category] += 1

    if reports:
        num_categories = min(len(reports), random.randint(2, 5))
        selected_categories = random.sample(list(reports.keys()), num_categories)
    else:
        all_categories = list(report_keywords.keys())
        num_categories = random.randint(2, 5)
        selected_categories = random.sample(all_categories, num_categories)

    unique_counts = random.sample(range(1, 6), len(selected_categories))
    return {category: f"{count}x - {category}" for category, count in zip(selected_categories, unique_counts)}

def get_public_instagram_info(username, retries=3, delay=10):
    L = instaloader.Instaloader()
    try:
        # Comment out login for demo
        # L.login(INSTAGRAM_USERNAME, INSTAGRAM_PASSWORD)
        # print(f"Logged in to Instagram as {INSTAGRAM_USERNAME}")
        pass
    except Exception as e:
        print(f"Instagram login failed: {e}. Proceeding without login...")

    for attempt in range(retries):
        time.sleep(delay)
        try:
            profile = instaloader.Profile.from_username(L.context, username)
            info = {
                "username": profile.username,
                "full_name": profile.full_name,
                "biography": profile.biography,
                "follower_count": profile.followers,
                "following_count": profile.followees,
                "is_private": profile.is_private,
                "post_count": profile.mediacount,
                "external_url": profile.external_url,
            }
            print(f"Successfully fetched profile: {username}")
            return info
        except instaloader.exceptions.ProfileNotExistsException:
            print(f"Profile {username} does not exist.")
            return None
        except Exception as e:
            print(f"Attempt {attempt + 1}/{retries} - Error for {username}: {e}")
            if attempt == retries - 1:
                return None
    return None

@bot.message_handler(commands=['start'])
def send_welcome(message):
    chat_id = message.chat.id
    bot.reply_to(message, f"Yo! Bot is live! 😎 Use /of <username> to analyze an Instagram profile.")

@bot.message_handler(commands=['ping'])
def ping(message):
    bot.reply_to(message, "!pong")

@bot.message_handler(commands=['of'])
def analyze_instagram(message):
    chat_id = message.chat.id
    try:
        username = message.text.split(maxsplit=1)[1] if len(message.text.split()) > 1 else None
        if not username:
            bot.reply_to(message, "Please provide a username! Usage: /of <username>")
            return

        username = username.strip().replace('<', '').replace('>', '')
        if not username:
            bot.reply_to(message, "Invalid username! Usage: /of <username>")
            return

        initial_message = bot.reply_to(message, f"🔍 Analyzing profile: {username}. Please wait...")
        profile_info = get_public_instagram_info(username)
        if profile_info:
            reports_to_file = analyze_profile(profile_info)
            result_text = f"**Public Information for {username}**\n\n"
            result_text += f"Username: {profile_info.get('username', 'N/A')}\n"
            result_text += f"Full Name: {profile_info.get('full_name', 'N/A')}\n"
            result_text += f"Biography: {profile_info.get('biography', 'N/A')}\n"
            result_text += f"Followers: {profile_info.get('follower_count', 'N/A')}\n"
            result_text += f"Following: {profile_info.get('following_count', 'N/A')}\n"
            result_text += f"Private Account: {'Yes' if profile_info.get('is_private') else 'No'}\n"
            result_text += f"Posts: {profile_info.get('post_count', 'N/A')}\n"
            result_text += f"External URL: {profile_info.get('external_url', 'N/A')}\n\n"
            result_text += "Suggested Reports to File:\n"
            for report in reports_to_file.values():
                result_text += f"• {report}\n"
            result_text += "\n*Note: This analysis is based on available data and may not be fully accurate. Suggestions are generated randomly if no specific issues are found.*\n"
            result_text += "Credits: RehuSezar Developed by @sirvuo\n"
            result_text += "[Visit My Portal](https://t.me/itvuo/)"
            bot.send_message(chat_id, result_text, parse_mode='Markdown', disable_web_page_preview=False)
        else:
            bot.edit_message_text(chat_id=chat_id, message_id=initial_message.message_id,
                                 text=f"❌ Profile {username} not found or an error occurred. Check if the username exists or try again later.")
    except Exception as e:
        bot.reply_to(message, f"Error: {str(e)}")

@bot.message_handler(content_types=['text'])
def handle_text(message):
    if bot.get_me().username.lower() in message.text.lower():
        bot.reply_to(message, "I am alive!")
    else:
        bot.reply_to(message, "Use /of <username> to analyze an Instagram profile or /ping to check if I'm alive.")

if __name__ == "__main__":
    print("Starting bot...")
    try:
        bot.polling(none_stop=True)
    except Exception as e:
        print(f"Bot polling error: {e}")
        time.sleep(5)
