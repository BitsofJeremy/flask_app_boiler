from flask import Blueprint, render_template
from flask_login import login_required
import logging
import random

# Local imports
from base_app.data.models import Quotes

logger = logging.getLogger(__name__)

home = Blueprint('home', __name__)


# Basic site routes
@home.route('/')
def index():
    # Send a random quote to the index page
    num_quotes = Quotes.query.order_by(Quotes.id.asc()).count()
    if num_quotes == 0:
        # We have no quotes, oh noes
        quote = {
            'quote': 'no_quotes',
            'character': 'admin'
        }
        return render_template(
            'index.html',
            quote=quote
        )
    else:
        r = random.randint(1, num_quotes)
        q = Quotes.query.filter_by(id=r).first_or_404()
        logger.info(q.serialize)
        quote = {
            'quote': q.quote_text,
            'character': q.character
        }
        return render_template(
            'index.html',
            quote=quote
        )


@home.route('/about')
def about():
    return render_template('about.html')


@home.route('/contact')
def contact():
    return render_template('contact.html')


@home.route('/test')
@login_required
def test():
    # Just a test page that requires login
    secret_data = "This is a secret page"
    return render_template('test.html', secret_data=secret_data)
