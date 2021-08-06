from gino import Gino

db = Gino()

from .telegram_channels import TelegramChannelModel
from .telegram_channels_scans import TelegramChannelScanModel
