from flask import render_template, request, redirect, url_for, flash
from flask_wtf import FlaskForm
from wtforms import FloatField, SelectField, StringField, PasswordField, HiddenField, SubmitField, DateField
from wtforms.validators import DataRequired, Email, Regexp
from . import app  # ou import app si app est défini dans __init__.py

from .models import *
from flask_login import current_user, login_required, login_user, logout_user
from werkzeug.security import generate_password_hash, check_password_hash

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
    poidsA = FloatField('Poids actuel', validators=[DataRequired()])
    niveau = SelectField('Niveau', choices=[('debutant', 'Débutant'), ('intermediaire', 'Intermédiaire'), ('avance', 'Avancé')], validators=[DataRequired()])
    submit = StringField('Inscrire')

@app.route('/inscription',methods=['GET','POST'])
def inscription():
    form = InscriptionForm()
    for input in form:
        print(input)
    if form.validate_on_submit():
        existing_user = get_email_membre(form.email.data)
        if existing_user:
            #flash("Un utilisateur avec cette adresse email existe déjà")
            return render_template('inscription.html', error="L'email est déjà pris", form=form)
        hashed_password = generate_password_hash(form.motDePasse.data)
        idT = getIdTarif(form.dateNaissance.data)
        print(idT, "Voici l'id du tarif")
        insert_membre(form.nomM.data, form.prenomM.data, form.dateNaissance.data, form.email.data, hashed_password, form.telephone.data, form.poidsA.data, form.niveau.data, idT)
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

@app.route('/connexion', methods=['GET', 'POST'])
def connexion():
    form = LoginForm()
    if not form.is_submitted():
        form.next.data = request.args.get("next")
    elif form.validate_on_submit():
        email = form.email.data
        motdepasse = form.motdepasse.data
        user = get_all_user_info(email)
        if user and check_password_hash(user.mot_de_passe, motdepasse):
            print("Connexion réussie")
            login_user(user)
            print(current_user)
        else:
            return render_template('connexion.html', error="Nom d'utilisateur ou mot de passe incorrect", form=form)
        return redirect(url_for('home'))
    return render_template('connexion.html', form=form)

@app.route('/deconnexion')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

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

def cours_reserves(user_id):
    try:
        cursor = mysql.connection.cursor()
        query = """
            SELECT c.typeC, c.jour, c.heureD, c.heureF, c.prix
            FROM RESERVATION r
            JOIN COURS c ON r.coursPayee = c.coursID
            WHERE r.idM = %s
        """
        cursor.execute(query, (user_id,))
        cours_reserves = cursor.fetchall()
        cursor.close()
    except Exception as e:
        print(f"Erreur lors de la récupération des cours : {e}")
        cours_reserves = []
    return cours_reserves

@app.route('/mes_cours')
def mes_cours():
    """Affiche les cours réservés par l'utilisateur connecté."""
    user_id = 2
    cours = cours_reserves(user_id)
    return render_template('mesCours.html', cours=cours)