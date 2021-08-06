import logging

from aiogram.types import ChatMemberUpdated

from app.config import Config
from app.models import TelegramChannelModel

logger = logging.getLogger('channel_handler')
logger.setLevel(logging.INFO)


async def channel_handler(update: ChatMemberUpdated):
    if update.chat.type != 'channel':
        return

    is_bot_left_channel = update.new_chat_member.status == 'left'

    if not is_bot_left_channel and update.from_user.id not in Config.TELEGRAM_OWNERS_USER_IDS:
        return

    channel = await TelegramChannelModel.query.where(
        TelegramChannelModel.telegram_id == str(update.chat.id),
    ).gino.first()

    if not channel and is_bot_left_channel:
        return
    elif not channel and not is_bot_left_channel:
        channel = await TelegramChannelModel(
            telegram_id=str(update.chat.id),
            added_by=update.from_user.id,
            has_currently_membership=True,
        ).create()

    await channel.update(
        has_currently_membership=not is_bot_left_channel,
    ).apply()

    if is_bot_left_channel:
        logger.info(f'Bot kicked from channel {update.chat.title}')
    else:
        logger.info(f'Bot added to channel {update.chat.title}')
