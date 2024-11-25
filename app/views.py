from flask import render_template, request, redirect, url_for, flash
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, HiddenField, SubmitField, DateField
from wtforms.validators import DataRequired, Email, Regexp
from . import app  # ou import app si app est défini dans __init__.py
from .models import *
from flask_login import current_user, login_required, login_user, logout_user
from werkzeug.security import generate_password_hash, check_password_hash

@app.route('/')
def home():
    return render_template('home.html')

class InscriptionForm(FlaskForm):
    nomM = StringField('Nom', validators=[DataRequired()])
    prenomM = StringField('Prénom', validators=[DataRequired()])
    dateNaissance = DateField('Date de naissance', format='%Y-%m-%d', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    motDePasse = PasswordField('Mot de passe', validators=[DataRequired()])
    telephone = StringField('Téléphone', validators=[DataRequired(), Regexp(r'^\+?1?\d{9,15}$', message="Le numéro de téléphone est invalide.")])
    submit = StringField('Inscrire')

@app.route('/inscription',methods=['GET','POST'])
def inscription():
    form = InscriptionForm()
    if form.validate_on_submit():
        existing_user = get_email_membre(form.email.data)
        if existing_user:
            #flash("Un utilisateur avec cette adresse email existe déjà")
            return render_template('inscription.html', error="L'email est déjà pris", form=form)
        hashed_password = generate_password_hash(form.motDePasse.data)
        insert_membre(form.nomM.data, form.prenomM.data, form.dateNaissance.data, form.email.data, hashed_password, form.telephone.data)
        new_user = get_all_user_info(form.email.data)
        if new_user:

            login_user(new_user)
        return redirect(url_for('home'))
    return render_template('inscription.html', form=form)

class LoginForm(FlaskForm):
    email = StringField("Adresse email", validators=[DataRequired()])
    motdepasse = PasswordField("Mot de passe", validators=[DataRequired()])
    next = HiddenField()
    submit = SubmitField("Se connecter")

@app.route('/connexion')
def connexion():
    form = LoginForm()
    if not form.is_submitted():
        form.next.data = request.args.get("next")
    elif form.validate_on_submit():
        # if mdp incorrect:
        #     return render_template('connexion.html', error="Nom d'utilisateur ou mot de passe incorrect", form=form)
        # next_page = form.next.data or url_for('home')
        # return redirect(next_page)
        return redirect(url_for('home'))
    return render_template('connexion.html', form=form)

@app.route('/calendrier')
def calendrier():
    emploi_du_temps = get_cours()
    return render_template('calendrier.html', emploi_du_temps=emploi_du_temps[0], horaires=emploi_du_temps[1])

@app.route('/club')
def club():
    return render_template('club.html')
