from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import uuid

db = SQLAlchemy()

class BlacklistEmail(db.Model):
    __tablename__ = 'blacklist_emails'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), nullable=False, unique=True)
    app_uuid = db.Column(db.String(36), nullable=False, default=lambda: str(uuid.uuid4()))
    blocked_reason = db.Column(db.String(255), nullable=True)
    request_ip = db.Column(db.String(45), nullable=False)  # IPv4 / IPv6
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __init__(self, email, app_uuid, blocked_reason, request_ip):
        self.email = email
        self.app_uuid = app_uuid
        self.blocked_reason = blocked_reason
        self.request_ip = request_ip

    def to_dict(self):
        return {
            'email': self.email,
            'app_uuid': self.app_uuid,
            'blocked_reason': self.blocked_reason,
            'request_ip': self.request_ip,
            'created_at': self.created_at
        }
