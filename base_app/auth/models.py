from flask_login import UserMixin, AnonymousUserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer, SignatureExpired, BadSignature
import logging
import os

from base_app import db, login_manager, app_config

print(app_config)

logger = logging.getLogger(__name__)

# Should probably set this in the config
SALTY_SECRET = os.getenv('SALTY_SECRET')


#
# Permissions
#
class Permission:
    USER = 0
    QUOTE_USERS = 1
    QUOTE_ADMINS = 2


class Base(db.Model):
    """ Base table template """

    __abstract__ = True

    id = db.Column(db.Integer, primary_key=True)
    date_created = db.Column(db.DateTime, default=db.func.current_timestamp())
    date_modified = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())


#
# USER ROLES
#
class Role(Base):
    """
    Create a Role table
    """
    __tablename__ = 'roles'
    # __table_args__ = {'mysql_engine': 'InnoDB', 'mysql_charset': 'utf8'}
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    default = db.Column(db.Boolean, default=False, index=True)
    permissions = db.Column(db.Integer)
    users = db.relationship('User', backref='role', lazy='dynamic')

    def __init__(self, **kwargs):
        super(Role, self).__init__(**kwargs)
        if self.permissions is None:
            self.permissions = 0

    @staticmethod
    def insert_roles():
        roles = {
            'USER': [Permission.USER],
            'QUOTE_USERS': [Permission.QUOTE_USERS],
            'QUOTE_ADMINS': [Permission.QUOTE_ADMINS]
        }
        default_role = 'USER'
        for r in roles:
            role = Role.query.filter_by(name=r).first()
            if role is None:
                role = Role(name=r)
            role.reset_permissions()
            for perm in roles[r]:
                role.add_permission(perm)
            role.default = (role.name == default_role)
            db.session.add(role)
        db.session.commit()

    def add_permission(self, perm):
        if not self.has_permission(perm):
            self.permissions += perm

    def remove_permission(self, perm):
        if self.has_permission(perm):
            self.permissions -= perm

    def reset_permissions(self):
        self.permissions = 0

    def has_permission(self, perm):
        return self.permissions & perm == perm

    def __repr__(self):
        return f'<Role {self.name}>'


#
# User model
#
class User(UserMixin, Base):
    """ User Object and Table Model """

    __tablename__ = 'users'

    # Basics
    name = db.Column(db.String(128), nullable=False)
    email = db.Column(db.String(128), nullable=False, unique=True)
    password_hash = db.Column(db.String(192))
    token = db.Column(db.String(128))
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    is_admin = db.Column(db.Boolean, default=False)

    # Return function
    def __repr__(self):
        return f'<User {self.name}>'

    def get_id(self):
        return self.id

    @property
    def is_authenticated(self):
        return True

    @property
    def is_active(self):
        return True

    @property
    def is_anonymous(self):
        return False

    @property
    def password(self):
        """
        Prevent password from being accessed
        """
        raise AttributeError('password is not a readable attribute.')

    @password.setter
    def password(self, password):
        """
        Set password to a hashed password
        """
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        """
        Check if hashed password matches actual password
        """
        return check_password_hash(self.password_hash, password)

    def generate_auth_token(self, expiration=600):
        """
        Generate a URL safe token
        """
        s = Serializer(SALTY_SECRET, expires_in=expiration)
        self.token = s
        return s.dumps({'id': self.id})

    @staticmethod
    def verify_auth_token(token):
        s = Serializer(SALTY_SECRET)
        try:
            data = s.loads(token)
            print(data)
        except SignatureExpired:
            logger.info('valid token, but expired')
            return None
        except BadSignature:
            logger.info('invalid token entered')
            return None
        user = User.query.get(data['id'])
        return user

    def can(self, perm):
        return self.role is not None and self.role.has_permission(perm)

    def is_administrator(self):
        return self.can(Permission.QUOTE_ADMINS)


#
# Anonymous Users
#
class AnonymousUser(AnonymousUserMixin):
    def can(self, permissions):
        return False

    def is_administrator(self):
        return False


login_manager.anonymous_user = AnonymousUser


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))