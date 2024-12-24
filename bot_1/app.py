import os
import json

from telegram.error import TelegramError
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

from constants import BOT_TOKEN

# 配置文件路径
BACKUP_FILE = "telegram_backup.json"
import logging

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
# set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """启动命令，告诉用户如何使用备份和恢复功能"""
    start_message = (
        "欢迎使用备份恢复机器人！\n\n"
        "以下是可用命令：\n"
        "/backup - 备份您的联系人、群组和频道数据\n"
        "/restore - 恢复您的联系人、群组和频道数据\n\n"
        "请确保您的机器人有足够的权限来执行这些操作！"
    )
    await update.message.reply_text(start_message)

async def backup_data(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """备份用户联系人和所在群组、频道信息"""
    bot = context.bot
    user_id = update.message.from_user.id

    try:
        # 模拟获取联系人和群组数据
        updates = await bot.get_updates()
        backup = {
            "user_id": user_id,
            "contacts": [],
            "groups": [],
            "channels": []
        }

        for chat in updates:
            if chat.message and chat.message.chat:
                chat_data = {
                    "chat_id": chat.message.chat.id,
                    "title": chat.message.chat.title or "Private Chat",
                    "type": chat.message.chat.type,
                }
                if chat.message.chat.type == "group":
                    backup["groups"].append(chat_data)
                elif chat.message.chat.type == "supergroup":
                    backup["channels"].append(chat_data)
                else:
                    backup["contacts"].append(chat_data)

        # 保存备份到本地文件
        with open(BACKUP_FILE, "w", encoding="utf-8") as file:
            json.dump(backup, file, ensure_ascii=False, indent=4)

        await update.message.reply_text("备份成功！数据已保存到本地文件。")

    except TelegramError as e:
        await update.message.reply_text(f"备份失败: {str(e)}")

async def restore_data(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """恢复用户联系人和所在群组、频道信息"""
    bot = context.bot
    try:
        if not os.path.exists(BACKUP_FILE):
            await update.message.reply_text("备份文件不存在，无法恢复数据。")
            return

        # 加载备份数据
        with open(BACKUP_FILE, "r", encoding="utf-8") as file:
            backup = json.load(file)

        # 恢复联系人、群组和频道
        for contact in backup["contacts"]:
            await bot.send_message(chat_id=contact["chat_id"], text="你好！我是你的新号机器人，已恢复联系。")

        for group in backup["groups"]:
            await bot.join_chat(group["chat_id"])

        for channel in backup["channels"]:
            await bot.join_chat(channel["chat_id"])

        await update.message.reply_text("恢复成功！已添加联系人并加入所有群组和频道。")

    except TelegramError as e:
        await update.message.reply_text(f"恢复失败: {str(e)}")


async def main():
    """主函数，初始化机器人"""
    application = Application.builder().token(BOT_TOKEN).build()

    # 绑定命令
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("backup", backup_data))
    application.add_handler(CommandHandler("restore", restore_data))

    # 启动机器人
    await application.run_polling()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())