# U S Σ R Δ T O R / Ümüd

import io
import math
import urllib.request
from os import remove
from PIL import Image
import random
from telethon.tl.types import DocumentAttributeFilename, MessageMediaPhoto
from userbot import bot
from userbot.events import register
from telethon.tl.functions.messages import GetStickerSetRequest
from telethon.tl.types import InputStickerSetID
from telethon.tl.types import DocumentAttributeSticker
from userbot.cmdhelp import CmdHelp

@register(outgoing=True, pattern="^.sinfo$")
async def get_pack_info(event):
    if not event.is_reply:
        return await event.edit("`Heç birşey haqqında məlumat verə bilmərəm :/`")

    rep_msg = await event.get_reply_message()
    if not rep_msg.document:
        return await event.edit("`Yalnız stickerlər haqqında məlumat verə bilirəm...`")

    try:
        stickerset_attr = rep_msg.document.attributes[1]
        await event.edit(
            "`Məlumatlar gətirilir...`")
    except BaseException:
        return await event.edit("`Bu bir sticker deyil. Bir stickerə cavab verin`")

    if not isinstance(stickerset_attr, DocumentAttributeSticker):
        return await event.edit("`Bu bir sticker deyil. Bir stickerə cavab verin`")

    get_stickerset = await bot(
        GetStickerSetRequest(
            InputStickerSetID(
                id=stickerset_attr.stickerset.id,
                access_hash=stickerset_attr.stickerset.access_hash)))
    pack_emojis = []
    for document_sticker in get_stickerset.packs:
        if document_sticker.emoticon not in pack_emojis:
            pack_emojis.append(document_sticker.emoticon)

    OUTPUT = (
        f"**Paket Başlığı:** `{get_stickerset.set.title}\n`"
        f"**Paketin Qısa adı:** `{get_stickerset.set.short_name}`\n"
        f"**Rəsmi:** `{get_stickerset.set.official}`\n"
        f"**Arxiv:** `{get_stickerset.set.archived}`\n"
        f"**Paketdəki emojili sticker sayı:** `{len(get_stickerset.packs)}`\n"
        f"**Paketdəki emojilər:**\n{' '.join(pack_emojis)}"
    )

    await event.edit(OUTPUT)


@register(outgoing=True, pattern="^.spng$")
async def sticker_to_png(sticker):
    if not sticker.is_reply:
        await sticker.edit("`NULL information to fetch...`")
        return False

    img = await sticker.get_reply_message()
    if not img.document:
        await sticker.edit("`Bir stickerə cavab verin`")
        return False

    try:
        img.document.attributes[1]
    except Exception:
        await sticker.edit("`Bu bir sticker deyil`")
        return

    with io.BytesIO() as image:
        await sticker.client.download_media(img, image)
        image.name = 'sticker.png'
        image.seek(0)
        try:
            await img.reply(file=image, force_document=True)
        except Exception:
            await sticker.edit("**Xəta:** `faylı göndərə bilmədim...`")
        else:
            await sticker.delete()
    return

CmdHelp('sinfo').add_command(
    'sinfo', None, 'Stiker haqqında məlumat verər.'
).add_command(
    'spng', None, 'Stikeri png kimi göndərər.'
).add()