from flask import Flask

from core import db
from sqlalchemy.dialects.postgresql import JSON

def create_tables(app: Flask):
    with app.app_context():
        db.create_all()


class DiscordUser(db.Model):
    __tablename__ = 'discord_users'
    id = db.Column(db.BigInteger, primary_key=True, nullable=False)
    username = db.Column(db.String(100), nullable=False)
    avatar = db.Column(db.String(255), nullable=True)
    discriminator = db.Column(db.String(5), nullable=False)
    public_flags = db.Column(db.Integer, nullable=True, default=0)
    flags = db.Column(db.Integer, nullable=True, default=0)
    banner = db.Column(db.String(255), nullable=True)
    accent_color = db.Column(db.Integer, nullable=True)
    global_name = db.Column(db.String(100), nullable=True)
    avatar_decoration_data = db.Column(JSON, nullable=True)
    banner_color = db.Column(db.String(7), nullable=True)
    clan = db.Column(db.String(100), nullable=True)
    mfa_enabled = db.Column(db.Boolean, nullable=False, default=False)
    locale = db.Column(db.String(10), nullable=True, default='en-US')
    premium_type = db.Column(db.Integer, nullable=True, default=0)
    is_active = db.Column(db.Boolean, nullable=False, default=True)         # 用户账号是否处于激活状态

    def __repr__(self):
        return f'<DiscordUser {self.username}#{self.discriminator}>'
