from datetime import datetime
from uuid import uuid4

from app.models import db


class TelegramChannelModel(db.Model):
    __tablename__ = 'telegram_channels'
    uuid = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid4()))
    created_at = db.Column(db.DateTime(), default=datetime.utcnow, nullable=False)

    telegram_id = db.Column(db.String(), index=True, nullable=False)
    added_by = db.Column(db.Integer(), index=True, nullable=False)
    has_currently_membership = db.Column(db.Boolean(), index=True, nullable=False)
