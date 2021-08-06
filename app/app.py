import asyncio
import logging
from typing import Optional

import sentry_sdk
from aiogram import (
    Bot,
    Dispatcher,
)
from aiogram.utils.exceptions import Unauthorized

from app.config import Config
from app.dispatchers.dispatcher import register_dispatcher
from app.models import db
from app.models import (
    TelegramChannelModel,
    TelegramChannelScanModel,
)


class App:
    def __init__(self):
        sentry_sdk.init(Config.SENTRY_DSN)
        logging.basicConfig(format=Config.LOGGER_FORMAT)
        self.logger = logging.getLogger('App')
        self.logger.setLevel(logging.INFO)
        self.is_working = False

        self.background_task: Optional[asyncio.Task] = None

        self.telegram_bot = Bot(token=Config.TELEGRAM_BOT_TOKEN)
        self.telegram_dispatcher = Dispatcher(self.telegram_bot)
        register_dispatcher(self.telegram_dispatcher)

    async def start(self):
        self.logger.info('App started!')
        self.is_working = True

        bot_user = await self.telegram_bot.me
        self.logger.info(f"The bot's name is {bot_user.username}")

        try:
            await db.set_bind(Config.DATABASE_URI)

            self.background_task = asyncio.create_task(self.wrap_task(self.scan_task()))

            await self.telegram_dispatcher.start_polling()
        except Exception as e:
            self.logger.exception(e)
        finally:
            await self.stop()

    async def stop(self):
        self.is_working = False

        if not self.background_task.done():
            self.background_task.cancel()
            try:
                await self.background_task
            except asyncio.CancelledError:
                pass

        try:
            if self.telegram_dispatcher:
                self.telegram_dispatcher.stop_polling()
        except Exception as e:
            self.logger.exception(e)

        try:
            await db.pop_bind().close()
        except Exception as e:
            self.logger.exception(e)

        self.logger.info('App stopped!')

    async def wrap_task(self, coroutine):
        try:
            await coroutine
        except Exception as e:
            self.logger.exception(e)
            await self.stop()

    async def scan_task(self):
        while self.background_task:
            db_channels = await TelegramChannelModel.query.where(
                TelegramChannelModel.has_currently_membership.is_(True)
            ).gino.all()

            send_message_tasks = []

            for db_channel in db_channels:
                current_channel_scan = TelegramChannelScanModel(channel_uuid=db_channel.uuid)

                try:
                    tg_channel = await self.telegram_bot.get_chat(int(db_channel.telegram_id))
                except Exception as e:
                    self.logger.exception(e)
                    continue

                try:
                    current_channel_scan.dogs_count = await self.telegram_bot.get_chat_members_count(tg_channel.id)
                except Unauthorized:
                    self.logger.info(f'Detected kick from channel {tg_channel.title}')

                    await db_channel.update(
                        has_currently_membership=False,
                        detected_kick=True,
                    ).apply()

                    current_channel_scan.detected_kick = True
                    await current_channel_scan.create()

                    continue

                previous_channel_scan = await TelegramChannelScanModel.query.where(
                    TelegramChannelScanModel.channel_uuid == db_channel.uuid,
                ).order_by(
                    TelegramChannelScanModel.created_at.desc(),
                ).gino.first()

                await current_channel_scan.create()

                if not previous_channel_scan:
                    continue

                dogs_count_delta = current_channel_scan.dogs_count - previous_channel_scan.dogs_count
                if dogs_count_delta == 0:
                    continue

                send_message_tasks = [
                    self.telegram_bot.send_message(
                        telegram_user_id,
                        self.get_message_text(dogs_count_delta, tg_channel.title),
                    )
                    for telegram_user_id in Config.TELEGRAM_OWNERS_USER_IDS
                ]

                self.logger.info(f'Checked channel {tg_channel.title}, dogs count delta: {dogs_count_delta}')

            if send_message_tasks:
                await asyncio.gather(*send_message_tasks)

            send_message_tasks.clear()

            await asyncio.sleep(Config.POLLING_CHANNELS_INTERVAL)

    @staticmethod
    def get_message_text(dogs_count_delta: int, channel_title: str) -> str:
        if dogs_count_delta == 1:
            return Config.MESSAGE_ONE_DOG_JOINED % channel_title
        elif 1 < dogs_count_delta < 5:
            return Config.MESSAGE_FROM_TWO_TO_FOUR_DOGS_JOINED % (-dogs_count_delta, channel_title)
        elif dogs_count_delta >= 5:
            return Config.MESSAGE_MANY_DOGS_JOINED % (-dogs_count_delta, channel_title)
        elif dogs_count_delta == -1:
            return Config.MESSAGE_ONE_DOG_LEFT % channel_title
        elif -5 < dogs_count_delta < -1:
            return Config.MESSAGE_FROM_TWO_TO_FOUR_DOGS_JOINED % (-dogs_count_delta, channel_title)
        elif dogs_count_delta <= -5:
            return Config.MESSAGE_MANY_DOGS_JOINED % (-dogs_count_delta, channel_title)
