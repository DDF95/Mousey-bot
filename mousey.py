import logging
import os
import sys
import tempfile

import clipboard
import cv2
import numpy as np
import pyautogui
from telegram import (InlineKeyboardButton, InlineKeyboardMarkup,
                      InputMediaPhoto, Update)
from telegram.ext import (ApplicationBuilder, CallbackQueryHandler,
                          CommandHandler, ContextTypes, MessageHandler,
                          filters)


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

application = ApplicationBuilder().token("BOT TOKEN GOES HERE").build()

main_remote_keyboard = [
    [
        InlineKeyboardButton("left clk", callback_data="left_click"),
        InlineKeyboardButton("up", callback_data="up"),
        InlineKeyboardButton("right clk", callback_data="right_click")
    ],
    [
        InlineKeyboardButton("left", callback_data="left"),
        InlineKeyboardButton("🦦", callback_data="null"),
        InlineKeyboardButton("right", callback_data="right")
    ],
    [
        InlineKeyboardButton("scroll up", callback_data="scroll_up"),
        InlineKeyboardButton("down", callback_data="down"),
        InlineKeyboardButton("scroll down", callback_data="scroll_down")
    ],
    [
        InlineKeyboardButton("faster", callback_data="faster"),
        InlineKeyboardButton("speed 10", callback_data="default_speed"),
        InlineKeyboardButton("slower", callback_data="slower")
    ]
]


def is_admin(user_id: int):
    if user_id == 14770193:
        return True
    else:
        return False


async def remote(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if is_admin(update.message.from_user.id):
        mouse_jump = context.user_data.get("mouse_jump", 10)
        reply_markup = InlineKeyboardMarkup(main_remote_keyboard)
        await update.message.reply_text(f"Pointer speed: {mouse_jump}", reply_markup=reply_markup)
        # img = await take_screenshot()
        # with tempfile.NamedTemporaryFile(delete=True) as file:
        #     cv2.imwrite(file.name + ".png", img)
        #     await context.bot.send_photo(update.message.chat_id, open(file.name + ".png", "rb"), f"Pointer speed: {mouse_jump}", reply_markup=reply_markup)


async def remote_button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    reply_markup = InlineKeyboardMarkup(main_remote_keyboard)

    if "mouse_jump" not in context.user_data:
        context.user_data["mouse_jump"] = 10

    if query.data == "up":
        pyautogui.move(0, -context.user_data["mouse_jump"], 0.2)
    if query.data == "down":
        pyautogui.move(0, context.user_data["mouse_jump"], 0.2)
    if query.data == "left":
        pyautogui.move(-context.user_data["mouse_jump"], 0, 0.2)
    if query.data == "right":
        pyautogui.move(context.user_data["mouse_jump"], 0, 0.2)
    if query.data == "scroll_up":
        pyautogui.scroll(1)
    if query.data == "scroll_down":
        pyautogui.scroll(-1)
    if query.data == "left_click":
        pyautogui.click(button='left')
    if query.data == "right_click":
        pyautogui.click(button='right')
    if query.data == "faster":
        context.user_data["mouse_jump"] = int(context.user_data["mouse_jump"] ** 1.5)
        mouse_jump = context.user_data["mouse_jump"]
        await query.edit_message_text(f"Pointer speed: {mouse_jump}", reply_markup=reply_markup)
        # await query.edit_message_caption(f"Pointer speed: {mouse_jump}", reply_markup=reply_markup)
    if query.data == "slower":
        context.user_data["mouse_jump"] = max(10, context.user_data["mouse_jump"] // 2)
        mouse_jump = context.user_data["mouse_jump"]
        await query.edit_message_text(f"Pointer speed: {mouse_jump}", reply_markup=reply_markup)
        # await query.edit_message_caption(f"Pointer speed: {mouse_jump}", reply_markup=reply_markup)
    if query.data == "default_speed":
        context.user_data["mouse_jump"] = 10
        mouse_jump = context.user_data["mouse_jump"]
        await query.edit_message_text(f"Pointer speed: {mouse_jump}", reply_markup=reply_markup)
        # await query.edit_message_caption(f"Pointer speed: {mouse_jump}", reply_markup=reply_markup)

    await query.answer()
    # mouse_jump = context.user_data["mouse_jump"]
    # img = await take_screenshot()
    # with tempfile.NamedTemporaryFile(delete=True) as file:
    #     cv2.imwrite(file.name + ".png", img)
    #     await query.edit_message_media(InputMediaPhoto(open(file.name + ".png", "rb")), reply_markup=reply_markup)
    #     await query.edit_message_caption(f"Pointer speed: {mouse_jump}", reply_markup=reply_markup)


async def text_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if is_admin(update.message.from_user.id) and update.message.text:
        if not update.message.text.startswith("/"):
            clipboard.copy(update.message.text)
            pyautogui.hotkey('command', 'v')
        
        if update.message.text == "/enter":
            pyautogui.press('enter')

        if update.message.text == "/space":
            pyautogui.press('space')
        
        if update.message.text == "/delete" or update.message.text == "/del":
            pyautogui.press('backspace')
            
        if update.message.text == "/get":
            if clipboard.paste():
                await update.message.reply_text(clipboard.paste())
            else:
                await update.message.reply_text("Clipboard is empty")
        
        if update.message.text.startswith("/set"):
            clipboard.copy(update.message.text[5:])
            await update.message.reply_text("Copied to clipboard")
    else:
        await context.bot.forward_message(chat_id=14770193, from_chat_id=update.message.chat_id, message_id=update.message.message_id)

        if update.message.from_user.last_name:
            last_name = f" {update.message.from_user.last_name} "
        else:
            last_name = ""
        if update.message.from_user.username:
            username = f" (@{update.message.from_user.username}) "
        else:
            username = ""

        await context.bot.send_message(chat_id=14770193, text=f"From: {update.message.from_user.first_name}{last_name}{username}(<code>{update.message.from_user.id}</code>)", parse_mode="HTML")


async def take_screenshot() -> np.ndarray:
    screenshot = pyautogui.screenshot()
    x, y = pyautogui.position()
    x = x * 2
    y = y * 2
    img = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
    cv2.circle(img, (x, y), 15, (0, 0, 255), -1)
    return img


async def send_screenshot(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if is_admin(update.message.from_user.id):
        img = await take_screenshot()
        with tempfile.NamedTemporaryFile(delete=True) as file:
            cv2.imwrite(file.name + ".png", img)
            await context.bot.send_photo(chat_id=update.message.chat_id, photo=open(file.name + ".png", 'rb'))


async def help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if is_admin(update.message.from_user.id):
        await update.message.reply_text(
            "<b>Commands</b>\n"
            "/remote - remote control\n"
            "/screenshot - take screenshot\n"
            "/get - get clipboard\n"
            "/set - set clipboard\n"
            "/enter - press enter\n"
            "/space - press space\n"
            "/delete - press backspace\n"
            "/restart - restart bot",
            parse_mode="HTML"
        )
    

async def restart_bot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if is_admin(update.message.from_user.id):
        await update.message.reply_text("Restarting...")
        args = sys.argv[:]
        args.insert(0, sys.executable)
        os.chdir(os.getcwd())
        os.execv(sys.executable, args)


if __name__ == '__main__':
    remote_handler = CommandHandler('remote', remote)
    application.add_handler(remote_handler, 0)

    remote_button_handler = CallbackQueryHandler(remote_button)
    application.add_handler(remote_button_handler, 1)

    text_input_handler = MessageHandler(filters.TEXT, text_input)
    application.add_handler(text_input_handler)

    send_screenshot_handler = CommandHandler('screenshot', send_screenshot)
    application.add_handler(send_screenshot_handler, 2)

    help_handler = CommandHandler('help', help)
    application.add_handler(help_handler, 3)

    restart_handler = CommandHandler('restart', restart_bot)
    application.add_handler(restart_handler, 99)

    application.run_polling(drop_pending_updates=True)
