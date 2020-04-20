import asyncio
import json
import io
from telethon import events
from telethon.tl import functions, types
from userbot.plugins.sql_helper.pmpermit_sql import pmpermit_sql
from userbot.utils import admin_cmd


PM_WARNS = {}
PREV_REPLY_MESSAGE = {}


BAALAJI_TG_USER_BOT = "`I Haven't Approved You To PM! Please Don't Spam!`"
TG_COMPANION_USER_BOT = "`Please Wait For My Response And Don't Spam!`"
UNIBORG_USER_BOT_WARN_ZERO = "`I Am Currently Offline! Don't Spam!`"
UNIBORG_USER_BOT_NO_WARN = "`Hi! I'll Respond To You ASAP! Please Don't Spam!`"


@borg.on(events.NewMessage(incoming=True, func=lambda e: e.is_private))
async def monito_p_m_s(event):
    sender = await event.get_sender()
    current_message_text = event.message.message.lower()
    if current_message_text == BAALAJI_TG_USER_BOT or \
        current_message_text == TG_COMPANION_USER_BOT or \
        current_message_text == UNIBORG_USER_BOT_NO_WARN:
        # userbot's should not reply to other userbot's
        # https://core.telegram.org/bots/faq#why-doesn-39t-my-bot-see-messages-from-other-bots
        return False
    if Config.PRIVATE_GROUP_ID and not sender.bot:
        chat = await event.get_chat()
        if not is_approved(chat.id) and chat.id != borg.uid:
            logger.info(chat.stringify())
            logger.info(PM_WARNS)
            if chat.id not in PM_WARNS:
                PM_WARNS.update({chat.id: 0})
            if PM_WARNS[chat.id] == Config.MAX_FLOOD_IN_P_M_s:
                r = await event.reply(UNIBORG_USER_BOT_WARN_ZERO)
                await asyncio.sleep(3)
                await borg(functions.contacts.BlockRequest(chat.id))
                if chat.id in PREV_REPLY_MESSAGE:
                    await PREV_REPLY_MESSAGE[chat.id].delete()
                PREV_REPLY_MESSAGE[chat.id] = r
                return
            r = await event.reply(UNIBORG_USER_BOT_NO_WARN)
            PM_WARNS[chat.id] += 1
            if chat.id in PREV_REPLY_MESSAGE:
                await PREV_REPLY_MESSAGE[chat.id].delete()
            PREV_REPLY_MESSAGE[chat.id] = r


@borg.on(admin_cmd("pm ?(.*)"))
async def approve_p_m(event):
    if event.fwd_from:
        return
    reason = event.pattern_match.group(1)
    chat = await event.get_chat()
    if Config.PRIVATE_GROUP_ID:
        if event.is_private:
            if not is_approved(chat.id):
                if chat.id in PM_WARNS:
                    del PM_WARNS[chat.id]
                if chat.id in PREV_REPLY_MESSAGE:
                    await PREV_REPLY_MESSAGE[chat.id].delete()
                    del PREV_REPLY_MESSAGE[chat.id]
                approve(chat.id, reason)
                await event.edit("`User Approved!`")
                await asyncio.sleep(3)
                await event.delete()


@borg.on(admin_cmd("block ?(.*)"))
async def approve_p_m(event):
    if event.fwd_from:
        return
    reason = event.pattern_match.group(1)
    chat = await event.get_chat()
    if Config.PRIVATE_GROUP_ID:
        if event.is_private:
            if is_approved(chat.id):
                disapprove(chat.id)
                await event.edit("`User Blocked!`")
                await asyncio.sleep(3)
                await borg(functions.contacts.BlockRequest(chat.id))
                
                
@borg.on(admin_cmd("dis ?(.*)"))
async def approve_p_m(event):
    if event.fwd_from:
        return
    reason = event.pattern_match.group(1)
    chat = await event.get_chat()
    if Config.PRIVATE_GROUP_ID:
        if event.is_private:
            if is_approved(chat.id):
                disapprove(chat.id)
                await event.edit("`PM Disapproved!`")
                await asyncio.sleep(3)
                await event.delete()



@borg.on(admin_cmd("listpms"))
async def approve_p_m(event):
    if event.fwd_from:
        return
    approved_users = get_all_approved()
    APPROVED_PMs = "Current Approved PMs\n"
    for a_user in approved_users:
        if a_user.reason:
            APPROVED_PMs += f"👉 [{a_user.chat_id}](tg://user?id={a_user.chat_id}) for {a_user.reason}\n"
        else:
            APPROVED_PMs += f"👉 [{a_user.chat_id}](tg://user?id={a_user.chat_id})\n"
    if len(APPROVED_PMs) > Config.MAX_MESSAGE_SIZE_LIMIT:
        with io.BytesIO(str.encode(APPROVED_PMs)) as out_file:
            out_file.name = "approved.pms.text"
            await borg.send_file(
                event.chat_id,
                out_file,
                force_document=True,
                allow_cache=False,
                caption="Current Approved PMs",
                reply_to=event
            )
            await event.delete()
    else:
        await event.edit(APPROVED_PMs)