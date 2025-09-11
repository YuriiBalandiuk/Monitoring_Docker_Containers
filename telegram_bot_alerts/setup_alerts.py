import sys
import os
import time
import logger_setup.logger as lc
import telebot

from telebot.types import ReplyKeyboardMarkup, KeyboardButton
from dotenv import load_dotenv

try:
    from monitoring.setup_monitoring import get_container_metrics as gcm
    from monitoring.setup_monitoring import get_container_status_real_time as gcs
except FileNotFoundError as excerr:
    lc.logger.error("Docker isn't working now!\n" + str(excerr))
    print("Docker isn't working now!")

if __name__ == "__main__":
    lc.logger.error("This file cannot be run as main!")
    print("\nThis file cannot be run as main!")
    sys.exit()

try:
    load_dotenv()
except NameError as nerr:
    lc.logger.error("Unable to load the environment!\n" + str(nerr))
    print("Unable to load the environment!")

try:
    API_TOKEN = os.getenv("API_TOKEN")
    if not API_TOKEN:
        raise ValueError
    bot = telebot.TeleBot(API_TOKEN)
except ValueError as verr:
    lc.logger.error("The API-TOKEN hasn't been found!\n" + str(verr))
    print("The API-TOKEN hasn't been found!")


def main_keyboard() -> ReplyKeyboardMarkup:
    """
    Create the main keyboard for the Telegram bot.

    Returns:
        ReplyKeyboardMarkup: Keyboard markup with buttons for Start, Help,
        Status, and Clear actions.
    """
    markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False)
    btn1 = KeyboardButton("▶️ Start")
    btn2 = KeyboardButton("🔍 Help")
    btn3 = KeyboardButton("📊 Status")
    btn4 = KeyboardButton("ℹ️ Clear")
    markup.add(btn1, btn2, btn3, btn4)
    return markup


@bot.message_handler(commands=['start'])
def send_start(message) -> None:
    """
    Send the start message to the user with the main keyboard.

    Args:
        message: Telegram message object containing chat and user info.
    """
    bot.send_message(message.chat.id, "Hi! I\'m a Docker container monitoring bot",
        reply_markup=main_keyboard())


@bot.message_handler(func=lambda message: message.text == "▶️ Start")
def send_start_instruction(message) -> None:
    """
    Trigger the start command via button press.

    Args:
        message: Telegram message object.
    """
    send_start(message)


@bot.message_handler(func=lambda message: message.text == "🔍 Help")
def send_help(message) -> None:
    """
    Send help information to the user.

    Args:
        message: Telegram message object.
    """
    bot.send_message(message.chat.id, "Help information: Use Status to "
        "get container stats, Clear to clear chat.", reply_markup=main_keyboard())


@bot.message_handler(commands=['help'])
def send_help_instruction(message) -> None:
    """
    Trigger the help command via /help command.

    Args:
        message: Telegram message object.
    """
    send_help(message)


@bot.message_handler(func=lambda message: message.text == "📊 Status")
def sen_containers_stats(message) -> None:
    """
    Send real-time Docker container statistics to the user.

    Args:
        message: Telegram message object.
    """
    count = 0

    for number in range(5):
        try:
            container_stats_text = "\n".join(gcm())
            bot.reply_to(message, container_stats_text)
            count += 1
            if count == 5:
                bot.send_message(message.chat.id,
                                 "You have received five information containers", 
                                 reply_markup=main_keyboard())
                break
        except Exception as err:
            lc.logger.error("The docker containers is not running now!\n" + str(err))
            bot.reply_to(message, "The docker containers is not running now!")
            break


@bot.message_handler(commands=['status'])
def send_status_instruction(message) -> None:
    """
    Trigger the status command via /status command.

    Args:
        message: Telegram message object.
    """
    sen_containers_stats(message)


@bot.message_handler(func=lambda message: message.text == "ℹ️ Clear")
def clear_chat(message) -> None:
    """
    Clear the last 100 messages in the chat.

    Args:
        message: Telegram message object.
    """
    chat_id = message.chat.id
    last_message_id = message.message_id

    for msg_id in range(last_message_id, last_message_id - 100, -1):
        try:
            bot.delete_message(chat_id, msg_id)
            time.sleep(0.2)
        except Exception as exc:
            pass
    bot.send_message(message.chat.id, "The chat has been cleared!", reply_markup=main_keyboard())


@bot.message_handler(commands=['clear'])
def send_clear_instruction(message) -> None:
    """
    Trigger the clear command via /clear command.

    Args:
        message: Telegram message object.
    """
    clear_chat(message)


@bot.message_handler(func=lambda message: True)
def echo_message(message) -> None:
    """
    Echo back any message and show the main keyboard.

    Args:
        message: Telegram message object.
    """
    bot.reply_to(message, message.text)
    bot.send_message(message.chat.id, "Make your choice ->", reply_markup=main_keyboard())


def update_containers_status_real_time(chat_id: int) -> None:
    """
    Continuously send real-time container status updates to the user.

    Args:
        chat_id (int): Telegram chat ID where updates will be sent.
    """
    count = 0

    while True:
        status = gcs()
        if status is None:
            count += 1
            if count % 10 == 0:
                print("Done:", count)
            else:
                print("Done:", count, end=" | ")
            time.sleep(15)
            continue
        bot.send_message(chat_id, status)
        time.sleep(15)


def start_telegram_bot() -> None:
    """
    Start the Telegram bot with infinite polling.

    Handles exceptions and retries after 15 seconds if the bot fails.

    """
    try:
        bot.infinity_polling(none_stop=True, timeout=60)
    except Exception as exc:
        lc.logger.error("The telegram bot is not running now!" + str(exc))
        time.sleep(15)