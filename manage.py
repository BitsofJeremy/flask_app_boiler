# manage.py

# Options:
# create the data:  python manage.py --create_db
# drop the data:  python manage.py --drop_db
# create the admin:  python manage.py --create_admin

import argparse
import sys
import os

from run import application
from base_app import db
from base_app.auth.models import User, Role, Permission


def main(**kwargs):
    if kwargs['create_db']:
        print("Creating Database, one moment")
        with application.app_context():
            # Init the DB
            db.create_all()
            # Add Roles
            Role.insert_roles()
            roles = Role.query.all()
        print(roles)

    if kwargs['create_admin']:
        print("Creating Admin, one moment")
        if os.getenv('ADMIN_EMAIL'):
            # User at least followed the README.md
            with application.app_context():
                user = User(
                    email=os.getenv('ADMIN_EMAIL'),
                    name=os.getenv('ADMIN_USER'),
                    password=os.getenv('ADMIN_PASSWORD')
                )
                user.is_admin = True
                user.role_id = Permission.QUOTE_ADMINS
                user.token = user.generate_auth_token()
                db.session.add(user)
                db.session.commit()

    if kwargs['drop_db']:
        print("Dropping DB, one moment")
        with application.app_context():
            db.drop_all()

    print("FIN")


if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument(
        '--create_db',
        help='Create the DB',
        action="store_true",
        required=False
    )

    parser.add_argument(
        '--drop_db',
        help='Drop the DB',
        action="store_true",
        required=False
    )

    parser.add_argument(
        '--create_admin',
        help='Create the admin',
        action="store_true",
        required=False
    )

    args = parser.parse_args()

    # Convert the argparse.Namespace to a dictionary: vars(args)
    arg_dict = vars(args)
    # pass dictionary to main
    main(**arg_dict)
    sys.exit(0)
