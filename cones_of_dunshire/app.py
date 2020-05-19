#!/usr/bin/env python3
from flask import Flask, render_template, flash, request, redirect, url_for, session
try:
    from player import Player, Role
except:
    from .player import Player, Role
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
        session['player_ct'] = 0
        return redirect(url_for('player_setup'))

@app.route('/hand')
def hand():
    if not session.get('cards', False):
        session['cards'] = []
        session['next_card'] = 0

    return render_template('hand.html', cards=session['cards'])

@app.route('/hand', methods=["POST"])
def draw():
    if request.form.get('draw', False):
        new_card = {
            'id': "card" + str(session['next_card']),
            'text': random.choice(deck),
        }
        session['cards'].append(new_card)
        session['next_card'] += 1
    elif request.form.get('clear', False):
        session['cards'] = []
        session['next_card'] = 0

    return redirect(url_for('hand'))

@app.route('/remove_card', methods=["POST"])
def remove_card():
    new_cards = []
    for card in session['cards']:
        name = card['id']
        if not request.form.get(name, False):
            new_cards.append(card)
    session['cards'] = new_cards

    return redirect(url_for('hand'))

@app.route('/player_setup', methods=["GET"])
def player_setup():
    return render_template(
        "player_setup.html",
        roles=list(Role),
        players=range(session['player_ct']),
    )

@app.route('/player_setup', methods=["POST"])
def player_form():
    if request.form.get('add_player', False):
        session['player_ct'] += 1
        return redirect(url_for('player_setup'))
    elif request.form.get('submit', False):
        session['players'] = []
        for i in range(session['player_ct']):
            session['players'].append(
                Player(
                    request.form[f'player_{i}'],
                    Role(int(request.form[f'player_{i}_role'])),
                ).to_json()
            )
        return redirect(url_for('game'))
    elif request.form.get('delete_players', False):
        session['player_ct'] = 0
        return redirect(url_for('player_setup'))

@app.route('/game')
def game():
    return render_template(
        'game.html',
        players=(Player.from_json(x) for x in session['players'])
    )

if __name__ == "__main__":
    app.run()
