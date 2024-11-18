from flask import render_template
from . import app  # ou import app si app est défini dans __init__.py
from .models import *

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/inscription')
def inscription():
    return render_template('inscription.html')

@app.route('/connexion')
def connexion():
    return render_template('connexion.html')

@app.route('/calendrier')
def calendrier():
    emploi_du_temps = get_cours()
    return render_template('calendrier.html', emploi_du_temps=emploi_du_temps[0], horaires=emploi_du_temps[1])
