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
    user = current_user.id_membre
    utilisateur = profil_utilisateur(user)
    return render_template('profil.html', utilisateur=utilisateur)


@app.route('/mes_cours')
def mes_cours():
    user_id = current_user.id_membre
    cours = cours_reserves(user_id)
    return render_template('mesCours.html', cours=cours)



@app.route('/modifier_profil', methods=['POST'])
def modifier_profil():
    try:
        
        id_membre = request.form.get('id_membre')
        nom = request.form.get('nom')
        prenom = request.form.get('prenom')
        date_naissance = request.form.get('date_naissance')
        email = request.form.get('email')
        telephone = request.form.get('telephone')
        poids = request.form.get('poids')
        niveau = request.form.get('niveau')
        

        cursor = mysql.connection.cursor()
        query = """
            UPDATE MEMBRE
            SET nomM = %s, prenomM = %s, dateNaissance = %s, email = %s,
            telephone = %s, poidsA  = %s,  niveau = %s
            WHERE idM = %s
        """
        cursor.execute(query, (nom, prenom, date_naissance, email, 
                               telephone, poids, niveau, id_membre))
        mysql.connection.commit()
        cursor.close()
    except Exception as e:
        mysql.connection.rollback()
        print(e)

    return redirect(url_for('profil'))

@app.route('/annuler_cours/<int:id_cours>', methods=['POST'])
@login_required
def annuler_cours(id_cours):
    try:
        # Suppression du cours de la base de données en fonction de son id
        cursor = mysql.connection.cursor()
        query = "DELETE FROM RESERVATION WHERE coursID = %s AND idM = %s"
        cursor.execute(query, (id_cours, current_user.id_membre))
        mysql.connection.commit()
        cursor.close()
        flash("Le cours a été annulé avec succès.", "success")
    except Exception as e:
        mysql.connection.rollback()
        print(e)
        flash("Une erreur est survenue lors de l'annulation du cours.", "error")

    return redirect(url_for('mes_cours'))