from app import app, db
from app.models import User, Article, Keyword, Reference

@app.shell_context_processor
def make_shell_context():
    """
        Function to configure the shell context

        :return: the context
        :rtype: dict
    """

    return {"db":db,
            "User": User,
            "Article": Article,
            "Keyword": Keyword,
            "Reference": Reference}