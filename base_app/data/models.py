# base_app/data/models.py

# Add random data to store here
from base_app import db
from base_app.auth.models import Base


# ## QUOTES ###
class Quotes(Base):
    """ Individual Quote data """
    __tablename__ = 'quotes'

    """
    {
    "id": "Integer",  # created by DB
    "quote_text": "string",
    "character": "string"  
    }
    """

    quote_text = db.Column(db.String(256))
    character = db.Column(db.String(64))

    def __init__(self, quote_text, character):
        self.quote_text = quote_text
        self.character = character

    def __repr__(self):
        return "{0} - {1}".format(
            self.quote_text,
            self.character
        )

    def update(self, **kwargs):
        """ Updates a Quote """
        for key, value in kwargs.items():
            setattr(self, key, value)

    @property
    def serialize(self):
        """ Returns a dictionary of the quote information """
        return {
            "id": self.id,
            "quote_text": self.quote_text,
            "character": self.character
        }



