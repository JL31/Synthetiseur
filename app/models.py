"""
    Module to handle the several models for the application
"""

# ==================================================================================================
#
# IMPORTS
#
# ==================================================================================================

from app import db, app, login
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

from datetime import datetime
from time import time
import jwt


# ==================================================================================================
#
# INITIALIZATIONS
#
# ==================================================================================================

article_keyword_association_table = db.Table("article_keyword_association_table",
                                             db.Column("article_id", db.Integer, db.ForeignKey("article.article_id")),
                                             db.Column("keyword_id", db.Integer, db.ForeignKey("keyword.keyword_id")))


# ==================================================================================================
#
# CLASSES
#
# ==================================================================================================

# ==============================
class User(UserMixin, db.Model):
    """
        Class that represents a User
    """

    user_id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(64), index = True, unique = True)
    email = db.Column(db.String(120), index = True, unique = True)
    password_hash = db.Column(db.String(128))
    articles = db.relationship("Article", backref = "author", lazy = "dynamic")

    # =================
    def __repr__(self):
        """
            Method that enables to represent the class instance

            :return: the username value
            :rtype: str
        """

        return "<User {}>".format(self.username)

    # ===============================
    def set_password(self, password):
        """
            Method to define the password

            :param password: the value of the password
            :type password: str
        """

        self.password_hash = generate_password_hash(password)

    # ===============================
    def check_password(self, password):
        """
            Method to check the password

            :param password: the value of the password
            :type password: str

            :return: return the result of the password check
            :rtype: bool
        """

        return check_password_hash(self.password_hash, password)

    # ===============
    def get_id(self):
        """
            Override of "get_id" method so that it can return the current instance "user_id" value
            Without that the "get_id" method will fail because it expects the id to be nammed "id"
            Here its nammed "user_id"
            (see https://stackoverflow.com/questions/37472870/login-user-fails-to-get-user-id)

            :return: the user id
            :rtype: int
        """

        return self.user_id

    # ===================================================
    def get_reset_password_token(self, expires_in = 600):
        """
            Method that generates a token for the reset password procedure

            :param expires_in: expiration delay (in seconds)
            :type expires_in: int

            :return: the token
            :rtype: str
        """

        return jwt.encode({"reset_password": self.user_id, "exp": time() + expires_in},
                          app.config["SECRET_KEY"],
                          algorithm = "HS256").decode("utf-8")

    # =====================================
    @staticmethod
    def verify_reset_password_token(token):
        """
            Function to check the token within the reset password procedure

            :param token: the token to be checked
            :type token: str

            :return: None if the token cannot be validated or is expired, else the associated User
            :rtype: None | app.model.User
        """

        try:

            id = jwt.decode(token, app.config["SECRET_KEY"], algorithms = ["HS256"])["reset_password"]

        except:

            return None

        return User.query.get(id)

# ======================
class Article(db.Model):
    """
        Class that represents an Article
    """

    article_id = db.Column(db.Integer, primary_key = True)
    title = db.Column(db.String(100), index = True, unique = True)
    keywords = db.relationship("Keyword", secondary = article_keyword_association_table)
    references = db.relationship("Reference", backref = "article", lazy = "dynamic")
    creation_date = db.Column(db.DateTime, index = True, default = datetime.utcnow)
    update_date = db.Column(db.DateTime, index = True, default = datetime.utcnow)
    synthesis = db.Column(db.Text())
    user_id = db.Column(db.Integer, db.ForeignKey("user.user_id"))

    # =================
    def __repr__(self):
        """
            Method that enables to represent the class instance

            :return: the username value
            :rtype: str
        """

        return "<Article {}>".format(self.title)

# ======================
class Keyword(db.Model):
    """
        Class that represents a Keyword
    """

    keyword_id = db.Column(db.Integer, primary_key = True)
    description = db.Column(db.String(40), index = True, unique = True)

    # =================
    def __repr__(self):
        """
            Method that enables to represent the class instance

            :return: the username value
            :rtype: str
        """

        return "<Keyword {}>".format(self.description)

# ========================
class Reference(db.Model):
    """
        Class that represents a Reference
    """

    reference_id = db.Column(db.Integer, primary_key = True)
    description = db.Column(db.String(100), index = True, unique = True)
    article_id = db.Column(db.Integer, db.ForeignKey("article.article_id"))

    # =================
    def __repr__(self):
        """
            Method that enables to represent the class instance

            :return: the username value
            :rtype: str
        """

        return "<Reference {}>".format(self.description)


# ==================================================================================================
#
# FUNCTIONS
#
# ==================================================================================================

# =====================
@login.user_loader
def load_user(user_id):
    """
        Function to load a user through its id

        :param user_id: the id of a user
        :type user_id: int

        :return: an instance of the User class
        :rtype: app.models.User
    """

    return User.query.get(user_id)


# ==================================================================================================
#
# USE
#
# ==================================================================================================