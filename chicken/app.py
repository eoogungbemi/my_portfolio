from flask import Flask, render_template, request, redirect, url_for, session
import random

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Use a secure random key in production

# Initialize a leaderboard list to store player names and their highest level achieved
leaderboard = []


def initialize_game():
    level = session.get('level', 1)
    max_number = 15 * level if level <= 50 else 25 * level  # Increase difficulty
    session['number'] = random.randint(1, max_number)
    session['attempts'] = 0
    session['max_attempts'] = 5 if level <= 50 else 10
    session['level'] = level
    session['max_number'] = max_number


@app.route('/')
def index():
    if 'number' not in session:
        session['level'] = 1
        initialize_game()
    return render_template('index.html', level=session['level'], max_number=session['max_number'])


@app.route('/guess', methods=['POST'])
def guess():
    guess = int(request.form['guess'])
    session['attempts'] += 1
    message = ""

    if guess < session['number']:
        message = "Too low! Try again."
    elif guess > session['number']:
        message = "Too high! Try again."
    else:
        session['level'] += 1
        initialize_game()
        message = f"Congratulations! You've moved to level {session['level']}."

    if session['attempts'] >= session['max_attempts'] and guess != session['number']:
        message = f"Game Over! The number was {session['number']}. Restarting at level 1."
        session.clear()
        initialize_game()

    return render_template('index.html', level=session['level'], max_number=session['max_number'], message=message)


@app.route('/restart')
def restart():
    session.clear()
    return redirect(url_for('index'))


@app.route('/leaderboard', methods=['GET', 'POST'])
def view_leaderboard():
    # Handle leaderboard submission
    if request.method == 'POST':
        username = request.form.get('username').strip()
        if username:  # Only add non-empty usernames
            # Add player to leaderboard with their level
            leaderboard.append({'username': username, 'level': session.get('level', 1)})
            # Sort leaderboard by level in descending order
            leaderboard.sort(key=lambda x: x['level'], reverse=True)

    # Render leaderboard page with current leaderboard
    return render_template('leaderboard.html', leaderboard=leaderboard)


if __name__ == '__main__':
    app.run(debug=True, port=8080)
