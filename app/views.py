from flask import render_template
from . import app  # ou import app si app est défini dans __init__.py

@app.route('/inscription')
def inscription():
    return render_template('inscription.html')

@app.route('/connexion')
def connexion():
    return render_template('connexion.html')
