#!/usr/bin/env python3
from flask import Flask, render_template, flash, request, redirect, url_for, session
import random

app = Flask(__name__)
app.secret_key = b'i\'m the maverick'

deck = list(range(1, 26))

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/go_to_sleep')
def sleep():
    return render_template('sleep.html')

@app.route('/menu', methods=["POST"])
def main_menu():
    if request.form.get('hand', False):
        return redirect(url_for('hand'))
    elif request.form.get('new_game', False):
        return redirect(url_for('game'));

@app.route('/hand')
def hand():
    if not session.get('cards', False):
        session['cards'] = {}
        session['next_card'] = 0

    return render_template('hand.html', cards=session['cards'])

@app.route('/hand', methods=["POST"])
def draw():
    if request.form.get('draw', False):
        new_card = {
            'id': "card" + str(session['next_card']),
            'text': random.choice(deck),
        }
        session['cards'][new_card['id']] = new_card
        session['next_card'] += 1
    elif request.form.get('clear', False):
        session['cards'] = {}
        session['next_card'] = 0

    return redirect(url_for('hand'))

@app.route('/remove_card', methods=["POST"])
def remove_card():
    new_cards = {}
    for name in session['cards']:
        if not request.form.get(name, False):
            new_cards[name] = session['cards'][name]
    session['cards'] = new_cards

    return redirect(url_for('hand'))

if __name__ == "__main__":
    app.run()
