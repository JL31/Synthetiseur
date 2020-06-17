"""
    Module to handle the several routes for the application
"""

# ==================================================================================================
#
# IMPORTS
#
# ==================================================================================================

from flask import render_template, flash, redirect, url_for, request, jsonify
from flask_login import current_user, login_user, logout_user, login_required

from app import app, db
from app.models import User, Article, Keyword, Reference
from app.forms import LoginForm, UserProfileEditorForm, CreateArticle, ModifyArticle, ResetPasswordRequestForm, ResetPasswordForm
from app.email import send_password_reset_email

from werkzeug.urls import url_parse

from datetime import datetime


# ==================================================================================================
#
# INITIALIZATIONS
#
# ==================================================================================================

# ==================================================================================================
#
# CLASSES
#
# ==================================================================================================

# ==================================================================================================
#
# FUNCTIONS
#
# ==================================================================================================

# ==================
@app.route("/")
@app.route("/index")
@login_required
def index():
    """
        View function for the index page

        :return: the view to be displayed
        :rtype: str
    """

    return render_template("index.html", title = "Index")

# =============================================
@app.route("/login", methods = ["GET", "POST"])
def login():
    """
        View function to login

        :return: the view to be displayed
        :rtype: str
    """

    if current_user.is_authenticated:

        return redirect(url_for("index"))

    form = LoginForm()

    if form.validate_on_submit():

        user = User.query.filter_by(username = form.username.data).first()

        if user is None or not user.check_password(form.password.data):

            flash("Nom d'utilisateur ou mot de passe incorrect")
            return redirect(url_for("login"))

        login_user(user, remember = form.remember_me.data)
        next_page = request.args.get("next")

        if not next_page or url_parse(next_page).netloc != "":

            next_page = url_for("index")

        return redirect(next_page)

    return render_template("login.html", title = "Connexion", form = form)

# ===================
@app.route("/logout")
def logout():
    """
        View function to logout

        :return: the view to be displayed
        :rtype: str
    """

    logout_user()

    return redirect(url_for("index"))

# ============================
@app.route("/user/<username>")
@login_required
def user(username):
    """
        View function for a User to see its profile

        :param username: the current username
        :type username: str

        :return: the view to be displayed
        :rtype: str
    """

    user = User.query.filter_by(username = username).first_or_404()

    if user == current_user:

        return render_template("user.html", user = user)

    else:

        return render_template("acces_denied.html")

# ============================================================
@app.route("/user_profile_edition", methods = ["GET", "POST"])
@login_required
def user_profile_edition():
    """
        View function for a User to edit its profile

        :return: the view to be displayed
        :rtype: str
    """

    form = UserProfileEditorForm(current_user.username)

    if form.validate_on_submit():

        current_user.username = form.username.data
        current_user.email = form.email.data

        db.session.commit()

        flash("Ton profil a bien été mis-à-jour")

        return redirect(url_for("user", username = current_user.username))

    elif request.method == "GET":

        form.username.data = current_user.username
        form.email.data = current_user.email

    return render_template("user_profile_editor.html",
                           title = "Modifier mon profil",
                           form = form)

# ============================================================
@app.route("/create_article", methods = ["GET", "POST"])
@login_required
def create_article():
    """
        View function for a User to create an article

        :return: the view to be displayed
        :rtype: str
    """

    form = CreateArticle()

    if form.validate_on_submit():

        article = Article(title = form.title.data,
                          synthesis = form.synthesis.data,
                          user_id = current_user.user_id)

        db.session.add(article)
        db.session.commit()

        flash("L'article a bien été ajouté")

        return redirect(url_for("user_articles_list"))

    return render_template("create_article.html",
                           title = "Créer un article",
                           form = form,
                           user_id = current_user.user_id)

# ===============================
@app.route("/user_articles_list")
@login_required
def user_articles_list():
    """
        View function for a User to see its articles list

        :return: the view to be displayed
        :rtype: str
    """

    articles_list = User.query.filter_by(username = current_user.username).first().articles.all()

    return render_template("user_articles_list.html",
                           title = "Liste de mes articles",
                           articles_list = articles_list)

# =====================================
@app.route("/article/<article_number>")
@login_required
def article(article_number):
    """
        View function to consult a specific article

        :param article_number: selected article id
        :type article_number: str

        :return: the view to be displayed
        :rtype: str
    """

    article = Article.query.get_or_404(int(article_number))

    article_creation_date = article.creation_date.strftime("%d/%m/%Y %H:%M:%S")
    article_update_date = article.update_date.strftime("%d/%m/%Y %H:%M:%S")

    article_creation_date_for_display = article.creation_date.strftime("%d/%m/%Y")
    article_update_date_for_display = article.update_date.strftime("%d/%m/%Y")

    dates = {"article_creation_date" : article_creation_date,
             "article_update_date" : article_update_date,
             "article_creation_date_for_display" : article_creation_date_for_display,
             "article_update_date_for_display" : article_update_date_for_display
            }

    return render_template("article.html", article = article, dates = dates)

# =======================================================================
@app.route("/modify_article/<article_number>", methods = ["GET", "POST"])
@login_required
def modify_article(article_number):
    """
        View function for a User to modify an article

        :param article_number: selected article id
        :type article_number: str

        :return: the view to be displayed
        :rtype: str
    """

    article = Article.query.get_or_404(int(article_number))

    form = ModifyArticle()

    if form.validate_on_submit():

        article.title = form.title.data
        article.synthesis = form.synthesis.data
        article.update_date = datetime.utcnow()

        db.session.add(article)
        db.session.commit()

        flash("L'article a bien été modifié")

        return redirect(url_for("article", article_number = article.article_id))

    elif request.method == "GET":

        form.title.data = article.title
        form.synthesis.data = article.synthesis

    return render_template("create_article.html",
                           title = "Modifier un article",
                           form = form)

# =======================================================================
@app.route("/delete_article/<article_number>", methods = ["GET", "POST"])
@login_required
def delete_article(article_number):
    """
        View function for a User to delete an article

        :param article_number: selected article id
        :type article_number: str

        :return: the view to be displayed
        :rtype: str
    """

    article = Article.query.get_or_404(int(article_number))

    db.session.delete(article)
    db.session.commit()

    return redirect(url_for("user_articles_list"))

# ==============================================================
@app.route("/reset_password_request", methods = ["GET", "POST"])
def reset_password_request():
    """
        View function for a User to ask for a password reset

        :param article_number: selected article id
        :type article_number: str

        :return: the view to be displayed
        :rtype: str
    """

    if current_user.is_authenticated:

        return redirect(url_for("index"))

    form = ResetPasswordRequestForm()

    if form.validate_on_submit():

        user = User.query.filter_by(email = form.email.data).first()

        if user:

            send_password_reset_email(user)

        flash("Un email t'a été envoyé avec les instructions afin de réinitialiser ton mot de passe")

        return redirect(url_for("login"))

    return render_template("reset_password_request.html",
                           title = "Réinitialisation du mot de passe",
                           form = form)

# ==============================================================
@app.route("/reset_password/<token>", methods = ["GET", "POST"])
def reset_password(token):
    """
        View function for a User to reset his password

        :param token: the token generated during the password reset process
        :type token: str

        :return: the view to be displayed
        :rtype: str
    """

    if current_user.is_authenticated:

        return redirect(url_for("index"))

    user = User.verify_reset_password_token(token)

    if not user:

        flash("Jeton invalide : le lien a peut-être expiré")
        return redirect(url_for("index"))

    form = ResetPasswordForm()

    if form.validate_on_submit():

        user.set_password(form.password.data)
        db.session.commit()

        flash("Ton mot de passe a bien été réinitialisé")

        return redirect(url_for("login"))

    return render_template("reset_password.html", form = form)

# ======================================================
@app.route("/add_keyword/<user_id>", methods = ["POST"])
@login_required
def add_keyword(user_id):
    """
        View function for a User to reset his password

        :return: the view to be displayed
        :rtype: str
    """

    tmp_keyword = Keyword.query.filter_by(description = request.form["keywords"]).first()

    if tmp_keyword:

        emtpy_dict = {"already_exists": True}

        return jsonify(emtpy_dict)

    tmp_article = Article.query.filter_by(title = "TMP").first()

    if not tmp_article:

        tmp_article = Article(title = "TMP",
                              synthesis = "tmp",
                              user_id = int(user_id))

        db.session.add(tmp_article)
        db.session.commit()

        tmp_article = Article.query.filter_by(title = "TMP").first()

    keyword = Keyword(description = request.form["keywords"])

    tmp_article.keywords.append(keyword)

    db.session.commit()

    emtpy_dict = {"already_exists": False}

    return jsonify(emtpy_dict)


# ==================================================================================================
#
# USE
#
# ==================================================================================================