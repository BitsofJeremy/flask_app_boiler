# base_app/api/views.py

from flask import Blueprint, g, jsonify
from flask_httpauth import HTTPTokenAuth
from flask_restx import Resource, Api, reqparse
import logging

# Local imports
from base_app import db
from base_app.auth.models import User
from base_app.data.models import Quotes

logger = logging.getLogger(__name__)


# Build API swagger auth into headers
authorizations = {
    'apikey': {
        'type': 'apiKey',
        'in': 'header',
        'name': 'authorization'
    }
}

api_bp = Blueprint('api', __name__, url_prefix="/api/v1")
api = Api(api_bp,
          title="THE API",
          contact="admin@example.com",
          authorizations=authorizations,
          doc='/')

httpauth = HTTPTokenAuth(
    scheme='Bearer'
)
api_ns = api.namespace('quotes', description='Quote operations')
auth_ns = api.namespace('auth', description='Authentication operations')


# Helper functions
@httpauth.verify_token
def verify_password(token):
    """ Uses the Bearer token to authenticate the user """
    # try to authenticate by token
    user = User.verify_auth_token(token)
    if not user:
        logger.info(user)
        logger.info("User is not user")
        return False
    g.user = user
    logger.info(f"{user} Sent and API request.")
    return True


# Token refresh helper API route
@auth_ns.route('/renew')
class ApiToken(Resource):
    @api.doc(security='apikey')
    @httpauth.login_required
    def get(self):
        """
        Renews Current User's Token
        Returns: Token JSON
        """
        # Get current user from DB and renew the token
        user = User.query.filter(User.id == g.user.id).one()
        user.token = user.generate_auth_token()
        db.session.add(user)
        db.session.commit()
        token = g.user.token
        return jsonify({'token': token.decode('ascii')})


# API Routes
@api_ns.route('/all')
class ApiList(Resource):
    def get(self):
        """ GET a list of all quotes.
        ---
            - This endpoint returns all quotes in the DB

            Returns: JSON quotes
        """
        data_return = {"quotes": []}
        quotes = Quotes.query.order_by(Quotes.date_modified.desc()).all()
        for quote in quotes:
            data_return['quotes'].append(quote.serialize)
        return jsonify(data_return)


@api_ns.route('')
class API(Resource):
    """ Provides API resources. """
    # ##### GET QUOTE PARSER #####
    get_parser = reqparse.RequestParser()
    get_parser.add_argument(
        'quote_id',
        type=int,
        required=True,
        help="Enter the quote ID."
    )

    # ##### POST QUOTE PARSER #####
    post_parser = reqparse.RequestParser()
    # Required
    post_parser.add_argument(
        'quote_text',
        type=str,
        required=True,
        help="REQUIRED - Enter quote text"
    )
    post_parser.add_argument(
        'character',
        type=str,
        required=True,
        help="REQUIRED - Enter the character that said the quote"
    )

    # ##### PUT quote SPEC PARSER #####
    put_parser = reqparse.RequestParser()
    # Required
    put_parser.add_argument(
        'quote_id',
        type=int,
        required=True,
        help="Enter the quote ID to update."
    )
    put_parser.add_argument(
        'quote_text',
        type=str,
        required=False,
        help="Update the quote text"
    )
    put_parser.add_argument(
        'character',
        type=str,
        required=False,
        help="Update the quote character"
    )

    @api.doc(security='apikey')
    @api_ns.expect(get_parser)
    @httpauth.login_required
    def get(self):
        """
        GET one quote
        ---
            - Required: a quote ID number
            - Returns one quote in JSON format
        """
        data = API.get_parser.parse_args()
        quote_id = int(data['quote_id'])
        # Get task from DB
        data_return = {"quote": []}
        quote = Quotes.query.filter(
            Quotes.id == quote_id).order_by(
            Quotes.date_modified.desc()).all()
        if quote:
            for q in quote:
                data_return['quote'].append(q.serialize)
            return jsonify(data_return)
        else:
            logger.warning(f"Sorry, quote ID: {quote_id} Not Found")
            return {
                       "message": f"Sorry, quote ID: {quote_id} Not Found"
                   }, 404

    @api.doc(security='apikey')
    @api_ns.expect(post_parser)
    @httpauth.login_required
    def post(self):
        """ POST a quote
        ---
            - Requirements
                - A quote spec requires the quote text and character
            - Returns: quote JSON
        """
        data = API.post_parser.parse_args()
        logger.info(data)
        q = Quotes(
            quote_text=data['quote_text'],
            character=data['character']
        )
        db.session.add(q)
        db.session.commit()
        logger.info(q.serialize)
        return {"quote": f"{q.serialize}"}, 201

    @api.doc(security='apikey')
    @httpauth.login_required
    @api_ns.expect(put_parser)
    def put(self):
        """ UPDATE a quote
        ---
            - Updates: a quote
            - Returns: quote JSON
        """
        # get dictionary from parser
        data = API.put_parser.parse_args()
        quote_id = int(data['quote_id'])
        logger.info('API Data PUT')
        logger.info(data)
        # Get items to change
        # Assume if None, means user does not want to change the data
        to_update = {}
        for k, v in data.items():
            if v is not None:
                to_update.update({k: v})
            else:
                print(f"not adding: {k}: {v}")
        # Search for quote
        quote_data = Quotes.query.filter_by(id=quote_id).first()

        if quote_data:
            to_update.pop('quote_id', None)
            quote_to_update = Quotes.query.filter_by(id=quote_id).first()
            quote_to_update.update(**to_update)
            db.session.commit()

            logger.info(f"Updated Quote {quote_id} with new data")
            return {"message": f"Quote {quote_id} Updated"}, 201
        else:
            # NO QUOTE FOUND IN DB
            logger.info(f"Quote {quote_id} not found")
            return {"message": "QUOTE WAS NOT FOUND"}, 401

    @api.doc(security='apikey')
    @api_ns.expect(get_parser)
    @httpauth.login_required
    def delete(self):
        """ DELETE a Quote
        ---
            - Deletes a Quote
            - Required: a Quote ID
            - Returns: Happy message
        """
        data = API.get_parser.parse_args()

        quote_to_delete = Quotes.query.filter_by(id=data['quote_id']).first()
        db.session.delete(quote_to_delete)
        db.session.commit()

        if quote_to_delete:
            logger.info(f"Deleted Quote: {data['quote_id']}")
            return {"message": f"{data['quote_id']} Deleted"}
        else:
            logger.info("Something went wrong with delete.")
            logger.info("Check if quote_id exists?")
            return {"message": "Something went wrong. "
                               "Missing quote_id?"}, 404

