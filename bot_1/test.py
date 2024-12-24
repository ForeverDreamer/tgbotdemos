from telethon import TelegramClient
from telethon.tl import functions, types
import os
import json
import time

from share.constants.misc import APPS

app_info = APPS[1]
# 配置文件
API_ID = app_info[0]  # 在 my.telegram.org 获取
API_HASH = app_info[1]  # 在 my.telegram.org 获取
SESSION_NAME = f"user_backup_{app_info[-1]}"
BACKUP_FILE = "user_backup.json"

# 初始化 Telegram 客户端
client = TelegramClient(SESSION_NAME, API_ID, API_HASH)


async def backup_user_data():
    """备份用户的联系人、群组和频道信息，避免重复记录"""
    print("正在备份联系人、用户、群组和频道数据...")
    # 加载已有备份数据（如果存在）
    if os.path.exists(BACKUP_FILE):
        with open(BACKUP_FILE, "r", encoding="utf-8") as file:
            backup = json.load(file)
    else:
        backup = {
            "contacts": [],
            "users": [],
            "groups": [],
            "channels": []
        }

    # 将现有数据转换为集合，用于去重
    existing_contacts = {contact["id"] for contact in backup["contacts"]}
    existing_users = {user["id"] for user in backup["users"]}
    existing_groups = {group["id"] for group in backup["groups"]}
    existing_channels = {channel["id"] for channel in backup["channels"]}

    # 获取所有联系人
    contacts = await client(functions.contacts.GetContactsRequest(hash=0))
    for user in contacts.users:
        if user.id not in existing_contacts:
            backup["contacts"].append({
                "id": user.id,
                "username": user.username,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "phone": user.phone
            })
            existing_contacts.add(user.id)

            # 获取所有对话，包括联系人、群组和频道
            async for dialog in client.iter_dialogs():
                if isinstance(dialog.entity, types.User):  # 判断是否为联系人
                    if dialog.id not in existing_users:
                        backup["users"].append({
                            "id": dialog.id,
                            "username": dialog.entity.username,
                            "first_name": dialog.entity.first_name,
                            "last_name": dialog.entity.last_name,
                            "phone": getattr(dialog.entity, "phone", None)
                        })
                        existing_users.add(dialog.id)
                elif isinstance(dialog.entity, types.Chat):  # 判断是否为普通群组
                    if dialog.id not in existing_groups:
                        group_info = {
                            "id": dialog.id,
                            "title": dialog.name,
                            "username": getattr(dialog.entity, "username", None)
                        }
                        backup["groups"].append(group_info)
                        existing_groups.add(dialog.id)
                elif isinstance(dialog.entity, types.Channel):  # 判断是否为频道或超级群组
                    if dialog.id not in existing_channels:
                        channel_info = {
                            "id": dialog.id,
                            "title": dialog.name,
                            "username": None
                        }
                        # 检查是否有公开的 username 或 usernames 字段
                        username = getattr(dialog.entity, "username", None)
                        usernames = getattr(dialog.entity, "usernames", [])
                        if username:
                            channel_info["username"] = username
                        elif usernames:
                            # 使用 usernames 字段的第一个用户名
                            channel_info["username"] = usernames[0].username
                        backup["channels"].append(channel_info)
                        existing_channels.add(dialog.id)

    # 保存到文件
    with open(BACKUP_FILE, "w", encoding="utf-8") as file:
        json.dump(backup, file, ensure_ascii=False, indent=4)

    print("备份成功！数据已保存到本地文件。")


async def restore_user_data():
    """恢复用户的联系人、用户、群组和频道信息"""
    try:
        if not os.path.exists(BACKUP_FILE):
            print("备份文件不存在，无法恢复数据。")
            return

        print("正在恢复联系人、用户、群组和频道数据...")
        with open(BACKUP_FILE, "r", encoding="utf-8") as file:
            backup = json.load(file)

        # # 单向添加联系人
        # for contact in backup["contacts"]:
        #     username = contact["username"]
        #     user_id = contact["id"]
        #     first_name = contact["first_name"]
        #     last_name = contact["last_name"]
        #     try:
        #         # 如果提供了 username，则通过 username 获取实体
        #         if username:
        #             user_entity = await client.get_entity(username)
        #         elif user_id:
        #             # 如果提供了 user_id，则直接获取实体
        #             user_entity = await client.get_entity(user_id)
        #         else:
        #             print("需要提供 username 或 user_id 才能添加联系人。")
        #             return
        #
        #         # 确保实体是有效的用户
        #         if not isinstance(user_entity, types.User):
        #             print(f"目标 {username or user_id} 不是有效的用户实体，无法添加为联系人。")
        #             return
        #
        #         # 添加联系人，不分享电话号码
        #         await client(functions.contacts.AddContactRequest(
        #             id=user_id,
        #             first_name=first_name or "",  # 获取用户的名字或备用名字
        #             last_name=last_name or "",  # 获取用户的姓氏或备用姓氏
        #             phone="",  # 不需要提供电话号码
        #             add_phone_privacy_exception=False  # 不分享你的电话号码
        #         ))
        #         print(
        #             f"成功添加联系人：{first_name} {last_name} ({username or user_id})")
        #
        #     except Exception as e:
        #         print(f"无法添加联系人 {username or user_id}: {e}")

        # # 恢复用户（非直接联系人但有记录）
        # for user in backup["users"]:
        #     try:
        #         # 如果有用户名，尝试通过用户名打开会话
        #         if user["username"]:
        #             user_entity = await client.get_entity(user["username"])
        #             await client.send_message(user_entity, "你好！我是你的新号机器人，已恢复联系。")  # 向用户发送消息
        #             print(f"已通过用户名恢复用户会话: {user['first_name']} {user['last_name']} ({user['username']})")
        #         else:
        #             # 如果没有用户名，尝试通过用户 ID 获取实体
        #             user_entity = await client.get_entity(user["id"])
        #             await client.send_message(user_entity, "你好！我是你的新号机器人，已恢复联系。")
        #             print(f"已恢复用户会话: {user['first_name']} {user['last_name']}")
        #     except Exception as e:
        #         print(f"无法恢复用户会话 {user['first_name']} {user['last_name']}: {e}")
        #
        # # 恢复群组
        # for group in backup["groups"]:
        #     try:
        #         group_entity = await client.get_entity(group["id"])
        #         if isinstance(group_entity, types.Chat) or isinstance(group_entity, types.Channel):
        #             await client(functions.channels.JoinChannelRequest(group_entity))
        #             print(f"已通过 ID 加入群组: {group['title']}")
        #         else:
        #             print(f"群组 {group['title']} 无法加入，因为无法解析实体。")
        #         # if group["invite_link"]:
        #         #     # 如果有邀请链接，通过邀请链接加入
        #         #     invite_hash = group["invite_link"].split("/")[-1]
        #         #     await client(functions.messages.ImportChatInviteRequest(hash=invite_hash))
        #         #     print(f"已加入群组: {group['title']}")
        #         # else:
        #         #     # 如果没有邀请链接，尝试通过 ID 加入
        #         #     group_entity = await client.get_entity(group["id"])
        #         #     if isinstance(group_entity, types.Chat) or isinstance(group_entity, types.Channel):
        #         #         await client(functions.channels.JoinChannelRequest(group_entity))
        #         #         print(f"已通过 ID 加入群组: {group['title']}")
        #         #     else:
        #         #         print(f"群组 {group['title']} 无法加入，因为无法解析实体。")
        #     except Exception as e:
        #         print(f"无法加入群组 {group['title']}: {e}")

        # 恢复频道
        for channel in backup["channels"]:
            try:
                channel_id = channel["username"] or channel["id"]
                channel_entity = await client.get_entity(channel_id)
                if isinstance(channel_entity, types.Channel):
                    await client(functions.channels.JoinChannelRequest(channel_entity))
                    print(f"已通过 {channel_id} 加入频道: {channel['title']}")
                    # 设置静音
                    mute_until = int(time.time()) + 10 * 365 * 24 * 60 * 60  # 静音 10 年
                    await client(functions.account.UpdateNotifySettingsRequest(
                        peer=channel_entity,
                        settings=types.InputPeerNotifySettings(mute_until=mute_until)
                    ))
                    # print(f"已静音频道: {channel_entity.title}")
                else:
                    print(f"频道 {channel['title']} 无法加入，因为无法解析实体。")
                # if channel["invite_link"]:
                #     # 如果有邀请链接，通过邀请链接加入
                #     invite_hash = channel["invite_link"].split("/")[-1]
                #     await client(functions.messages.ImportChatInviteRequest(hash=invite_hash))
                #     print(f"已加入频道: {channel['title']}")
                # else:
                #     # 如果没有邀请链接，尝试通过 ID 加入
                #     channel_entity = await client.get_entity(channel["id"])
                #     if isinstance(channel_entity, types.Channel):
                #         await client(functions.channels.JoinChannelRequest(channel_entity))
                #         print(f"已通过 ID 加入频道: {channel['title']}")
                #     else:
                #         print(f"频道 {channel['title']} 无法加入，因为无法解析实体。")
            except Exception as e:
                print(f"无法加入频道 {channel['title']}: {e}")

        print("恢复完成！")
    except Exception as e:
        print(f"恢复失败: {e}")


async def main():
    """主函数"""
    print("欢迎使用 Telegram 备份恢复工具！")
    print("请选择操作：")
    print("1. 备份数据")
    print("2. 恢复数据")
    choice = input("请输入 1 或 2: ").strip()

    if choice == "1":
        await backup_user_data()
    elif choice == "2":
        await restore_user_data()
    else:
        print("无效选项，请重试。")

if __name__ == "__main__":
    client.start(app_info[-1])  # 启动客户端
    client.loop.run_until_complete(main())  # 运行主函数
