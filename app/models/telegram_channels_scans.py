from datetime import datetime
from uuid import uuid4

from app.models import db


class TelegramChannelScanModel(db.Model):
    __tablename__ = 'telegram_channel_scans'
    uuid = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid4()))
    created_at = db.Column(db.DateTime(), default=datetime.utcnow, nullable=False)

    channel_uuid = db.Column(db.String(36), db.ForeignKey('telegram_channels.uuid'), nullable=False)
    dogs_count = db.Column(db.Integer())
    detected_kick = db.Column(db.Boolean(), nullable=False, default=False)
