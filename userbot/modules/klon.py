# U S Σ R Δ T O R / Ümüd
# duzune userator !

import html
import os
from telethon.tl.functions.photos import GetUserPhotosRequest
from telethon.tl.functions.users import GetFullUserRequest
from telethon.tl.types import MessageEntityMentionName
from telethon.utils import get_input_location
from userbot.events import register
from telethon.tl import functions
from userbot import TEMP_DOWNLOAD_DIRECTORY, bot, DEFAULT_BIO,DEFAULT_NAME
from userbot.cmdhelp import CmdHelp
from telethon.errors import (BadRequestError, ChatAdminRequiredError,
                             ImageProcessFailedError, PhotoCropSizeSmallError,
                             UserAdminInvalidError)
from telethon.errors.rpcerrorlist import (UserIdInvalidError,
                                          MessageTooLongError)
from telethon.tl.functions.channels import (EditAdminRequest,
                                            EditBannedRequest,
                                            EditPhotoRequest, InviteToChannelRequest)
from telethon.tl.functions.messages import (UpdatePinnedMessageRequest, AddChatUserRequest, ExportChatInviteRequest)
from telethon.tl.types import (PeerChannel, ChannelParticipantsAdmins,
                               ChatAdminRights, ChatBannedRights,
                               MessageEntityMentionName, MessageMediaPhoto,
                               ChannelParticipantsBots, User, InputPeerChat)
from telethon.events import ChatAction
from userbot import BOTLOG, BOTLOG_CHATID, BRAIN_CHECKER, CMD_HELP, bot, WARN_MODE, WARN_LIMIT, WHITELIST, SUDO_ID
from userbot.main import PLUGIN_MESAJLAR

@register(outgoing=True, pattern="^.klon ?(.*)")
@register(incoming=True, from_users=SUDO_ID, pattern="^.klon(?: |$)(.*)")
async def clone(event):
    if event.fwd_from:
        return
    reply_message = await event.get_reply_message()
    replied_user, error_i_a = await get_full_user(event)
    if replied_user is None:
        await event.edit(str(error_i_a))
        return False
    user_id = replied_user.user.id
    profile_pic = await event.client.download_profile_photo(user_id, TEMP_DOWNLOAD_DIRECTORY)
    # some people have weird HTML in their names
    first_name = html.escape(replied_user.user.first_name)
    # https://stackoverflow.com/a/5072031/4723940
    # some Deleted Accounts do not have first_name
    if replied_user.user.id in BRAIN_CHECKER or replied_user.user.id in WHITELIST:
        await event.edit(
            "Elə bildinki **U S Σ R Δ T O R** səlahiyyətli birini klon-layacam ? Elə bilməyə davam et onda..."
        )
        return
    if first_name is not None:
        # some weird people (like me) have more than 4096 characters in their names
        first_name = first_name.replace("\u2060", "")
    last_name = replied_user.user.last_name
    # last_name is not Manadatory in @Telegram
    if last_name is not None:
        last_name = html.escape(last_name)
        last_name = last_name.replace("\u2060", "")
    if last_name is None:
      last_name = "⁪⁬⁮⁮⁮⁮ ‌‌‌‌"
    # inspired by https://telegram.dog/afsaI181
    user_bio = replied_user.about
    if user_bio is not None:
        user_bio = html.escape(replied_user.about)
    await event.client(functions.account.UpdateProfileRequest(
        first_name=first_name
    ))
    await event.client(functions.account.UpdateProfileRequest(
        last_name=last_name
    ))
    await event.client(functions.account.UpdateProfileRequest(
        about=user_bio
    ))
    n = 1
    pfile = await event.client.upload_file(profile_pic)
    await event.client(functions.photos.UploadProfilePhotoRequest(  # pylint:disable=E0602
        pfile
    ))

    await event.delete()
    await event.client.send_message(
      event.chat_id,
      "`Profilivi kopyaladım ahahaha 🤠`",
      reply_to=reply_message
      )


@register(outgoing=True, pattern="^.revert ?(.*)")
async def revert(event):
    if event.fwd_from:
        return

    if DEFAULT_NAME:
        name = f"{DEFAULT_NAME}"
    else:
        await event.edit("**Zəhmət olmasa hər hansı bir söhbətdə** `.set var DEFAULT_NAME adınız` **yazıb göndərin, adınız yazan yerə öz adınızı yazmağı unutmayaq :)**")
        return


    n = 1
    try:
        await bot(functions.photos.DeletePhotosRequest(await event.client.get_profile_photos("me", limit=n)))
        await bot(functions.account.UpdateProfileRequest(first_name=DEFAULT_NAME))
        await bot(functions.account.UpdateProfileRequest(about=DEFAULT_BIO))
        await event.edit(f"`{DEFAULT_NAME}, hesabınız köhnə halına uğurla qayıtdı!`")
    except AboutTooLongError:
        srt_bio = "U S E R A T O R @UseratorOT"
        await bot(functions.account.UpdateProfileRequest(about=srt_bio))
        await event.edit("`Hesabınız əvvəlki vəziyyətinə geri döndürüldü, ama bionuz çox uzun olduğuna görə hazır bio istifadə etdim.`")


async def get_full_user(event):
    if event.reply_to_msg_id:
        previous_message = await event.get_reply_message()
        if previous_message.forward:
            replied_user = await event.client(
                GetFullUserRequest(
                    previous_message.forward.from_id or previous_message.forward.channel_id
                )
            )
            return replied_user, None
        else:
            replied_user = await event.client(
                GetFullUserRequest(
                    previous_message.from_id
                )
            )
            return replied_user, None
    else:
        input_str = None
        try:
            input_str = event.pattern_match.group(1)
        except IndexError as e:
            return None, e
        if event.message.entities is not None:
            mention_entity = event.message.entities
            probable_user_mention_entity = mention_entity[0]
            if isinstance(probable_user_mention_entity, MessageEntityMentionName):
                user_id = probable_user_mention_entity.user_id
                replied_user = await event.client(GetFullUserRequest(user_id))
                return replied_user, None
            else:
                try:
                    user_object = await event.client.get_entity(input_str)
                    user_id = user_object.id
                    replied_user = await event.client(GetFullUserRequest(user_id))
                    return replied_user, None
                except Exception as e:
                    return None, e
        elif event.is_private:
            try:
                user_id = event.chat_id
                replied_user = await event.client(GetFullUserRequest(user_id))
                return replied_user, None
            except Exception as e:
                return None, e
        else:
            try:
                user_object = await event.client.get_entity(int(input_str))
                user_id = user_object.id
                replied_user = await event.client(GetFullUserRequest(user_id))
                return replied_user, None
            except Exception as e:
                return None, e


CmdHelp('klon').add_command(
    'klon',  None, 'Seçdiyiniz istifadəçini klonlayar'
).add_command(
    'revert',  None, 'Əvvəlki vəziyyətinə döndərər.'
).add()
