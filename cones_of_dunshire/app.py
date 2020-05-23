#!/usr/bin/env python3
from flask import Flask, render_template, flash, request, redirect, url_for, session
try:
    from player import Player, Role, Resource, Biome, Tile
except:
    from .player import Player, Role, Resource, Biome, Tile
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
        rows = int(request.form['board_size_r'])
        cols = int(request.form['board_size_c'])
        biomes = list(Biome)
        session['board'] = [
            [
                Tile(
                    r * cols + c,
                    Biome.OCEAN if (r == 0 or c == 0
                        or r == (rows - 1) or c == (cols - 1)
                    ) else random.choice(biomes[1:]),
                    random.choice(list(Resource)),
                    random.randint(1, 6),
                ).to_json() for c in range(cols)
            ] for r in range(rows)
        ]
        session['players'] = []
        err = False
        for i in range(session['player_ct']):
            if not request.form.get(f'player_{i}', False):
                flash(f'You must enter a player name for Player {i+1}.')
                err = True
            if not request.form.get(f'player_{i}_role', False):
                flash(f'You must enter a role for Player {i+1}.')
                err = True
            if not err:
                session['players'].append(
                    Player(
                        i,
                        request.form[f'player_{i}'],
                        Role(int(request.form[f'player_{i}_role'])),
                    ).to_json()
                )
        session['dice_3'] = []
        session['dice'] = []
        session['turn'] = 0
        if not err:
            return redirect(url_for('game'))
        else:
            return redirect(url_for('player_setup'))
    elif request.form.get('delete_players', False):
        session['player_ct'] = 0
        return redirect(url_for('player_setup'))

@app.route('/game')
def game():
    board = [
        [Tile.from_json(t) for t in x]
        for x in session['board']
    ]
    rows = len(board)
    cols = len(board[0])
    return render_template(
        'game.html',
        players=[Player.from_json(x) for x in session['players']],
        turn=session['turn'],
        dice_3=session['dice_3'],
        dice=session['dice'],
        dice_total=sum(session['dice_3']),
        resources=list(Resource),
        biomes=list(Biome),
        board=board,
        rows=rows,
        cols=cols
    )

@app.route('/roll', methods=['POST'])
def dice_roll():
    session['dice_3'] = [
        random.randint(1, 6) for _ in range(3)
    ]
    dice_ct = sum(session['dice_3'])
    session['dice'] = [
        random.randint(1, 6) for _ in range(dice_ct)
    ]
    return redirect(url_for('game'))

@app.route('/resource_update/<int:player>/<int:resource>', methods=['POST'])
def resource_update(player, resource):
    p = Player.from_json(session['players'][player])
    if request.form.get('plus', False):
        p.resources[resource] += 1
    elif request.form.get('minus', False):
        p.resources[resource] -= 1
    elif request.form.get('reset', False):
        p.resources[resource] = 0
    session['players'][player] = p.to_json()
    session.modified = True # Since we modify a mutable object
    return redirect(url_for('game'))

@app.route('/board_action', methods=['POST'])
def board_action():
    if not request.form.get('idx', False):
        flash('You must select a board tile to act on.')
        return redirect(url_for('game'))

    idx = int(request.form['idx'])
    board = [
        [Tile.from_json(t) for t in x]
        for x in session['board']
    ]
    rows = len(board)
    cols = len(board[0])
    r = idx // cols
    c = idx % cols
    tile = board[r][c]

    if request.form.get('move', False):
        if not request.form.get('player', False):
            flash('You must select a player to perform that action.')
            err = True
        else:
            player = int(request.form['player'])
            for row in board:
                for t in row:
                    try:
                        t.players.remove(player)
                    except ValueError:
                        pass
            tile.players.append(player)
    elif request.form.get('settle', False):
        if not request.form.get('player', False):
            flash('You must select a player to perform that action.')
            err = True
        else:
            player = int(request.form['player'])
            tile.settlement = player
    elif request.form.get('civ', False):
        if not request.form.get('player', False):
            flash('You must select a player to perform that action.')
            err = True
        else:
            player = int(request.form['player'])
            tile.civilization = player
    elif request.form.get('remove_settle', False):
        tile.settlement = None
    elif request.form.get('remove_civ', False):
        tile.civilization = None
    board[r][c] = tile
    session['board'] = [
        [t.to_json() for t in r]
        for r in board
    ]
    return redirect(url_for('game'))

@app.route('/end_turn', methods=['POST'])
def end_turn():
    session['turn'] += 1
    if session['turn'] == len(session['players']):
        session['turn'] = 0
    session['dice_3'] = []
    session['dice'] = []
    return redirect(url_for('game'))

@app.route('/collect', methods=['POST'])
def collect():
    if not session['dice']:
        flash('You must roll the dice first.')
        return redirect(url_for('game'))

    board = [
        [Tile.from_json(t) for t in x]
        for x in session['board']
    ]
    players = [Player.from_json(x) for x in session['players']]

    for d in session['dice']:
        for r in board:
            for tile in r:
                if tile.number == d:
                    resource_idx = tile.resource.value
                    if tile.settlement is not None:
                        players[tile.settlement].resources[resource_idx] += 1
                    if tile.civilization is not None:
                        players[tile.civilization].resources[resource_idx] += 2

    session['board'] = [
        [t.to_json() for t in r]
        for r in board
    ]
    session['players'] = [p.to_json() for p in players]
    return redirect(url_for('game'))

if __name__ == "__main__":
    app.run()
