from functools import wraps
from flask import render_template, request, redirect, url_for, flash
from flask_wtf import FlaskForm
from wtforms import FloatField, SelectField, StringField, PasswordField, HiddenField, SubmitField, DateField, TimeField
from wtforms.validators import DataRequired, Email, Regexp
from . import app  # ou import app si app est défini dans __init__.py

from .models import *
from flask_login import current_user, login_required, login_user, logout_user
from werkzeug.security import generate_password_hash, check_password_hash

from app.models import *
from datetime import timedelta, datetime, time



def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for('connexion', next=request))
        if not current_user.is_admin():
            # return redirect(url_for('not_admin', role='administrateur'))
            return render_template('not_admin.html', role='administrateur')
        return f(*args, **kwargs)
    return decorated_function

def monitor_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for('connexion', next=request))
        if not current_user.is_monitor():
            # return redirect(url_for('not_admin', role='moniteur'))
            return render_template('not_admin.html', role='moniteur')
        return f(*args, **kwargs)
    return decorated_function

def guest(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user.is_authenticated:
            return redirect(url_for('home'))
        return f(*args, **kwargs)
    return decorated_function

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
@guest
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
@guest
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
            # print(current_user)
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
    return render_template('calendrier.html', emploi_du_temps=emploi_du_temps)


@app.route('/club')
def club():
    print(getTarifs())
    return render_template('club.html', tarifs=getTarifs())

@app.route('/profil')
@login_required
def profil():
    user = current_user.id_membre
    utilisateur = profil_utilisateur(user)
    return render_template('profil.html', utilisateur=utilisateur)

@app.route("/not_admin")
def not_admin():
    return render_template("not_admin.html")

class AjoutCoursForm(FlaskForm):
    # typeC = SelectField('Type', choices=[('Collectif', 'Collectif'), ('Particulier', 'Particulier')], validators=[DataRequired()])
    typeC = SelectField('Type', choices=['Collectif', 'Particulier'], validators=[DataRequired()])
    # duree = SelectField('Durée', choices=[(1, 1), (2, 2)], validators=[DataRequired()])
    duree = SelectField('Durée', choices=[1, 2], validators=[DataRequired()])
    nbParticipantsMax = SelectField('Nombre de participants maximum', choices=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10], validators=[DataRequired()])
    jour = SelectField('Jour', choices=['Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi', 'Samedi', 'Dimanche'], validators=[DataRequired()])
    heureD = TimeField('Heure de début', validators=[DataRequired()])
    prix = FloatField('Prix', validators=[DataRequired()])
    idM = SelectField('Moniteur', choices=[], validators=[DataRequired()])
    submit = StringField('Ajouter')

@app.route('/gestion_cours', methods=['GET', 'POST'])
@admin_required
def gestion_cours():
    form = AjoutCoursForm()
    form.idM.choices = getMoniteursForCours()
    if form.validate_on_submit():
        try:
            if form.typeC.data == 'Particulier' and int(form.nbParticipantsMax.data) > 1:
                flash("Un cours particulier ne peut pas avoir plus d'un participant.", "danger")
                return render_template('gestion_cours.html', form=form, cours=getCoursSimple())
            ajouterCours(form.typeC.data, form.duree.data, form.nbParticipantsMax.data, form.jour.data, form.heureD.data, form.prix.data, form.idM.data)
            flash("Le cours a été ajouté avec succès.", "success")
            return redirect(url_for('gestion_cours'))
        except Exception as e:
            flash("Une erreur est survenue lors de l'ajout du cours.", "danger")
            print(e)
    return render_template('gestion_cours.html', form=form, cours=getCoursSimple())

@app.route('/supprimer_cours/<int:id_cours>', methods=['GET', 'POST'])
@admin_required
def supprimer_cours(id_cours):
    try:
        supprimerReservationDuCours(id_cours)
        supprimerCours(id_cours)
        flash("Le cours a été supprimé avec succès.", "success")
    except Exception as e:
        flash("Une erreur est survenue lors de la suppression du cours.", "danger")
    return redirect(url_for('gestion_cours'))

class ModifierCoursForm(FlaskForm):
    coursID = HiddenField('ID')
    typeC = SelectField('Type', choices=['Collectif', 'Particulier'], validators=[DataRequired()])
    duree = SelectField('Durée', choices=[1, 2], validators=[DataRequired()])
    nbParticipantsMax = SelectField('Nombre de participants maximum', choices=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10], validators=[DataRequired()])
    jour = SelectField('Jour', choices=['Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi', 'Samedi', 'Dimanche'], validators=[DataRequired()])
    heureD = TimeField('Heure de début', validators=[DataRequired()])
    heureF = TimeField('Heure de fin', validators=[DataRequired()])
    prix = FloatField('Prix', validators=[DataRequired()])
    idM = SelectField('Moniteur', choices=[], validators=[DataRequired()])
    submit = StringField('Modifier')

@app.route('/modifier_cours/<int:id_cours>', methods=['GET', 'POST'])
@admin_required
def modifier_cours(id_cours):
    form = ModifierCoursForm()
    cours = getCours(id_cours)

    form.idM.choices = getMoniteursForCours(cours.idM)
    if request.method == 'GET':
        if isinstance(cours.heureD, timedelta):
            form.heureD.data = (datetime.min + cours.heureD).time()
        else:
            form.heureD.data = cours.heureD

        if isinstance(cours.heureF, timedelta):
            form.heureF.data = (datetime.min + cours.heureF).time()
        else:
            form.heureF.data = cours.heureF 
        form.coursID.data = cours.coursID
        form.typeC.data = cours.typeC
        form.duree.data = cours.duree
        form.nbParticipantsMax.data = cours.nbParticipantsMax
        form.jour.data = cours.jour
        form.prix.data = cours.prix
        form.idM.data = next((moniteur[0] for moniteur in form.idM.choices if moniteur[0] == cours.idM), None)

    if form.validate_on_submit():
        try:
            if form.heureD.data > form.heureF.data:
                flash("L'heure de début doit être inférieure à l'heure de fin.", "danger")
                return render_template('modifier_cours.html', cours=cours, form=form)
            start_time = datetime.combine(datetime.today(), form.heureD.data)
            end_time = datetime.combine(datetime.today(), form.heureF.data)
            time_difference = end_time - start_time
            expected_duration = timedelta(hours=int(form.duree.data))
            if time_difference != expected_duration:
                flash("La durée du cours ne correspond pas à l'intervalle entre l'heure de début et l'heure de fin.", "danger")
                return render_template('modifier_cours.html', cours=cours, form=form)
            if moniteurACours(form.coursID.data, form.jour.data, form.heureD.data, form.heureF.data, form.idM.data):
                flash("Le moniteur sélectionné est déjà occupé à ce moment-là.", "danger")
                return render_template('modifier_cours.html', cours=cours, form=form)
            modifierCours(form.typeC.data, form.duree.data, form.nbParticipantsMax.data, form.jour.data, form.heureD.data, form.heureF.data, form.prix.data, form.idM.data, form.coursID.data)
            flash("Le cours a été modifié avec succès.", "success")
            return redirect(url_for('gestion_cours'))
        except Exception as e:
            flash("Une erreur est survenue lors de la modification du cours.", "danger")
            print(e)
    return render_template('modifier_cours.html', cours=cours, form=form)


@app.route('/modifier_profil', methods=['POST'])
@login_required
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
        flash("Une erreur est survenue lors de l'annulation du cours.", "danger")

    return redirect(url_for('mes_cours'))

class AjoutPoneyForm(FlaskForm):
    poneyID = HiddenField('ID')
    nomP = StringField('Nom', validators=[DataRequired()])
    age = FloatField('Age', validators=[DataRequired()])
    poidsSupportableMax = FloatField('Taille', validators=[DataRequired()])
    submit = StringField('Ajouter')


@app.route('/nosPoneys', methods=['GET', 'POST'])
def nosPoneys():
    form = AjoutPoneyForm()
    if form.validate_on_submit():
        try: 
            ajouterPoney(form.nomP.data, str(form.age.data), str(form.poidsSupportableMax.data))
            flash("Le poney a été ajouté avec succès.", "success")
            return redirect(url_for('nosPoneys'))
        except Exception as e:
            flash("Une erreur est survenue lors de l'ajout du poney.", "danger")
    return render_template('gerer_poneys.html', poneys=getPoneys(), form=form)

@app.route('/modifier_poney/<int:poney_id>', methods=['GET', 'POST'])
@admin_required
def modifier_poney(poney_id):
    form = AjoutPoneyForm()
    poney = getPoney(poney_id)
    if request.method == 'GET':
        form.poneyID.data = poney.poneyID
        form.nomP.data = poney.nomP
        form.age.data = poney.age
        form.poidsSupportableMax.data = poney.poidsSupportableMax
    if form.validate_on_submit():
        try:
            modifierPoney(form.nomP.data, form.age.data, form.poidsSupportableMax.data, form.poneyID.data)
            flash("Le poney a été modifié avec succès.", "success")
            return redirect(url_for('nosPoneys'))
        except Exception as e:
            flash("Une erreur est survenue lors de la modification du poney.", "danger")
    return render_template('modifier_poney.html', poney=poney, form=form)


@app.route('/supprimer_poney/<int:poney_id>', methods=['GET', 'POST'])
@admin_required
def supprimer_poney(poney_id):
    try:
        supprimerPoney(poney_id)
        flash("Le poney a été supprimé avec succès.", "success")
    except Exception as e:
        print(e)
        flash("Une erreur est survenue lors de la suppression du poney.", "danger")
    return redirect(url_for('nosPoneys')) 

class AjoutReservationForm(FlaskForm):
    # poneyID = SelectField('Poney', choices=getPoneyForRerservation(current_user.poids), validators=[DataRequired()])
    poneyID = SelectField('Poney', choices=[], validators=[DataRequired()])
    coursID = SelectField('Cours', choices=[], validators=[DataRequired()])
    submit = StringField('Ajouter')

@app.route('/mes_cours', methods=['GET', 'POST'])
@login_required
def mes_cours():
    form = AjoutReservationForm()
    user_id = current_user.id_membre
    form.poneyID.choices = getPoneyForRerservation(current_user.poids)
    form.coursID.choices = getCoursForReservation(user_id)
    cours = cours_reserves(user_id)
    if form.validate_on_submit():
        try:
            ajouterReservation(current_user.id_membre, form.poneyID.data, form.coursID.data)
            flash("La réservation a été ajoutée avec succès.", "success")
            return redirect(url_for('mes_cours'))
        except Exception as e:
            flash(e.args[1], "danger")
    return render_template('mesCours.html', cours=cours, form=form)

@app.route('/gestion_membres')
@admin_required
def gestion_membres():
    return render_template('gestion_membres.html', adherents=get_membres('Adhérent', current_user.id_membre), moniteurs=get_membres('Moniteur', current_user.id_membre), admins=get_membres('Administrateur', current_user.id_membre))

@app.route('/changer_role_moniteur/<int:id_membre>', methods=['POST'])
@admin_required
def passerMoniteur(id_membre):
    try:
        changerRole(id_membre, 'Moniteur')
        supprimerReservationDuMembre(id_membre)
        flash("Le rôle de l'utilisateur a été modifié avec succès.", "success")
    except Exception as e:
        flash("Une erreur est survenue lors de la modification du rôle de l'utilisateur.", "danger")
    return redirect(url_for('gestion_membres'))

@app.route('/changer_role_admin/<int:id_membre>', methods=['POST'])
@admin_required
def passerAdmin(id_membre):
    try:
        changerRole(id_membre, 'Administrateur')
        supprimerReservationDuMembre(id_membre)
        supprimerCoursDuMembre(id_membre)
        flash("Le rôle de l'utilisateur a été modifié avec succès.", "success")
    except Exception as e:
        flash("Une erreur est survenue lors de la modification du rôle de l'utilisateur.", "danger")
    return redirect(url_for('gestion_membres'))

@app.route('/changer_role_adherent/<int:id_membre>', methods=['POST'])
@admin_required
def passerAdherent(id_membre):
    try:
        changerRole(id_membre, 'Adhérent')
        supprimerCoursDuMembre(id_membre)
        flash("Le rôle de l'utilisateur a été modifié avec succès.", "success")
    except Exception as e:
        flash("Une erreur est survenue lors de la modification du rôle de l'utilisateur.", "danger")
    return redirect(url_for('gestion_membres'))

@app.route('/cours_moniteur/<int:id_membre>')
@monitor_required
def cours_moniteur(id_membre):
    return render_template('cours_moniteur.html', emploi_du_temps=get_cours(current_user.id_membre))

