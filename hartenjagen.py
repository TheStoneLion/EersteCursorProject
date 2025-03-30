from flask import Flask, render_template, request, redirect, url_for, session
from typing import Dict, List

app = Flask(__name__)
app.secret_key = 'jouw_geheime_sleutel_hier'  # Nodig voor session management

class Hartenjagen:
    def __init__(self):
        self.spelers = []
        self.scores: Dict[str, int] = {}
        self.ronde = 1
        self.MAX_SCORE_PER_RONDE = 15
        self.AANTAL_SPELERS = 4
        self.START_PHASE_PUNTEN = 60
        self.game_phase = "minimizeren"  # "minimizeren" of "maximizeren"
        self.game_over = False
        self.winner = None

    def voeg_speler_toe(self, naam: str) -> bool:
        """Voeg een nieuwe speler toe aan het spel."""
        if len(self.spelers) >= self.AANTAL_SPELERS:
            return False
        if naam not in self.spelers and naam.strip():
            self.spelers.append(naam)
            self.scores[naam] = 0
            return True
        return False

    def controleer_game_phase(self):
        """Controleer of de game phase moet veranderen."""
        for score in self.scores.values():
            if score >= self.START_PHASE_PUNTEN and self.game_phase == "minimizeren":
                self.game_phase = "maximizeren"
                return
            if score <= 0 and self.game_phase == "maximizeren":
                self.game_over = True
                self.winner = [speler for speler, score in self.scores.items() if score <= 0][0]
                return

    def voer_score_in(self, scores: Dict[str, int]) -> bool:
        """Voer de scores in voor de huidige ronde."""
        if len(scores) != len(self.spelers):
            return False
        
        # Controleer of de som van alle scores 15 is
        if sum(scores.values()) != self.MAX_SCORE_PER_RONDE:
            return False

        # Update scores
        for speler, score in scores.items():
            if speler in self.scores:
                self.scores[speler] += score

        self.ronde += 1
        self.controleer_game_phase()
        return True

    def is_spel_vol(self) -> bool:
        """Controleer of het spel vol is met spelers."""
        return len(self.spelers) >= self.AANTAL_SPELERS

    def get_game_status(self) -> dict:
        """Krijg de huidige status van het spel."""
        return {
            "spelers": self.spelers,
            "scores": self.scores,
            "ronde": self.ronde,
            "game_phase": self.game_phase,
            "game_over": self.game_over,
            "winner": self.winner,
            "is_spel_vol": self.is_spel_vol()
        }

# Global game instance
game = Hartenjagen()

@app.route('/')
def index():
    return render_template('index.html', game=game.get_game_status())

@app.route('/voeg_speler_toe', methods=['POST'])
def voeg_speler_toe():
    naam = request.form.get('naam', '').strip()
    if naam and game.voeg_speler_toe(naam):
        return redirect(url_for('index'))
    return render_template('index.html', game=game.get_game_status(), error="Ongeldige speler naam of spel is vol")

@app.route('/voer_score_in', methods=['POST'])
def voer_score_in():
    scores = {}
    for speler in game.spelers:
        try:
            score = int(request.form.get(f'score_{speler}', ''))
            scores[speler] = score
        except ValueError:
            return render_template('index.html', game=game.get_game_status(), error="Voer geldige scores in")
    
    if game.voer_score_in(scores):
        return redirect(url_for('index'))
    return render_template('index.html', game=game.get_game_status(), error="De som van alle scores moet 15 zijn")

@app.route('/reset')
def reset():
    global game
    game = Hartenjagen()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True) 