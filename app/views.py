from flask import render_template, request, redirect, url_for, flash
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, HiddenField, SubmitField, DateField
from wtforms.validators import DataRequired, Email, Regexp
from . import app  # ou import app si app est défini dans __init__.py
from app.models import *

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

@app.route('/inscription')
def inscription():
    form = InscriptionForm()
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

@app.route('/login')

@app.route('/calendrier')
def calendrier():
    emploi_du_temps = get_cours()
    return render_template('calendrier.html', emploi_du_temps=emploi_du_temps[0], horaires=emploi_du_temps[1])

@app.route('/club')
def club():
    return render_template('club.html')

@app.route('/profil')
def profil():
    return render_template('profil.html')

@app.route('/mes_cours')
def mes_cours():
    """Affiche les cours réservés par l'utilisateur connecté."""
    user_id = 1
    cours = cours_reserves(user_id)
    return render_template('mesCours.html', cours=cours)