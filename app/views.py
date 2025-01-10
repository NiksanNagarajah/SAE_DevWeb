from functools import wraps
from flask import render_template, request, redirect, url_for, flash
from flask_wtf import FlaskForm
from wtforms import FloatField, SelectField, StringField, PasswordField, HiddenField, SubmitField, DateField
from wtforms.validators import DataRequired, Email, Regexp
from . import app  # ou import app si app est défini dans __init__.py

from .models import *
from flask_login import current_user, login_required, login_user, logout_user
from werkzeug.security import generate_password_hash, check_password_hash

from app.models import *



def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if  not current_user.is_authenticated:
            return redirect(url_for('connexion', next=request))
        if current_user.nom_role != 'Administrateur':
            return redirect(url_for('not_admin'))
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

# @app.route('/calendrier')
# def calendrier():
    # emploi_du_temps = get_cours()
    # return render_template('calendrier.html', emploi_du_temps=emploi_du_temps[0], horaires=emploi_du_temps[1])

@app.route('/calendrier')
def calendrier():
    emploi_du_temps = get_cours()
    print(emploi_du_temps)
    return render_template('calendrier.html', emploi_du_temps=emploi_du_temps)


@app.route('/club')
def club():
    return render_template('club.html')

@app.route('/profil')
@login_required
def profil():
    user = current_user.id_membre
    utilisateur = profil_utilisateur(user)
    return render_template('profil.html', utilisateur=utilisateur)

@app.route("/not_admin")
def not_admin():
    return render_template("not_admin.html")

@app.route('/gestion_cours')
@admin_required
def gestion_cours():
    return render_template('gestion_cours.html')



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
            flash("Une erreur est survenue lors de l'ajout du poney.", "error")
    return render_template('gerer_poneys.html', poneys=getPoneys(), form=form)

@app.route('/modifier_poney/<int:poney_id>', methods=['GET', 'POST'])
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
            flash("Une erreur est survenue lors de la modification du poney.", "error")
    return render_template('modifier_poney.html', poney=poney, form=form)


@app.route('/supprimer_poney/<int:poney_id>', methods=['GET', 'POST'])
def supprimer_poney(poney_id):
    try:
        print("i"*50)
        supprimerPoney(poney_id)
        flash("Le poney a été supprimé avec succès.", "success")
    except Exception as e:
        print(e)
        print("e"*50)
        flash("Une erreur est survenue lors de la suppression du poney.", "error")
    return redirect(url_for('nosPoneys')) 

# class AjoutCoursForm ?????

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
            flash(e.args[1], "error")
    return render_template('mesCours.html', cours=cours, form=form)

