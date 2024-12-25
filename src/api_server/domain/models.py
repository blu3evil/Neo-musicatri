from sqlalchemy.dialects.mysql import JSON
from api_server.app_context import db
from flask import Flask

def init(app: Flask):
    with app.app_context():
        db.create_all()

class DiscordUser(db.Model):
    __tablename__ = 'discord_users'
    # __table_args__ = {'extend_existing': True}
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

    roles = db.relationship('Role', backref='users', secondary='user_roles')

    def __repr__(self):
        return f'<DiscordUser {self.username}#{self.discriminator}>'

class Role(db.Model):
    """ 角色表，例如管理员，用户，访客 """
    __tablename__ = 'roles'
    # __table_args__ = {'extend_existing': True}
    id = db.Column(db.BigInteger, primary_key=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(255), nullable=True)

    def __repr__(self):
        return f'<Role {self.name}>'

    def __hash__(self):
        return hash(self.id)

    def __eq__(self, other):
        if isinstance(other, Role):
            return self.id == other.id
        return False


class UserRole(db.Model):
    __tablename__ = 'user_roles'
    # __table_args__ = {'extend_existing': True}
    user_id = db.Column(db.BigInteger, db.ForeignKey('discord_users.id'), primary_key=True)
    role_id = db.Column(db.BigInteger, db.ForeignKey('roles.id'), primary_key=True)


def init_roles():
    def ensure_role(name, desc):
        role = Role.query.filter_by(name=name).first()
        if not role:
            role = Role(name=name, description=desc)
            db.session.add(role)

    ensure_role('admin', 'Administrator role')
    ensure_role('user', 'Normal user role')
    ensure_role('anonymous', 'Anonymous user role')
    db.session.commit()


def copy_properties(data, instance):
    """ 属性拷贝 """
    if isinstance(data, dict):
        # 如果是字典，则按键值对赋值
        for key, value in data.items():
            if hasattr(instance, key):
                setattr(instance, key, value)
    elif hasattr(data, '__dict__'):
        # 如果是对象，则按属性名称赋值
        for key, value in data.__dict__.items():
            if hasattr(instance, key) and not key.startswith('_'):
                setattr(instance, key, value)


def to_dict(instance) -> dict:
    if isinstance(instance, db.Model):
        data = {}
        for column in instance.__table__.columns:
            data[column.name] = getattr(instance, column.name)
        return data
    return {}
