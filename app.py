from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)

# Sample wellness tips
WELLNESS_TIPS = [
    "Take a deep breath and stretch for a few minutes.",
    "Drink a glass of water—you’ve earned it!",
    "Step outside for 5 minutes of fresh air.",
    "Write down one thing you’re grateful for today.",
    "Rest is productive too. Give yourself permission.",
    "Talk to a friend—you’re not alone.",
    "Try a 2-minute guided breathing exercise."
]

@app.route('/')
def home():
    # You can pass dynamic data here if needed (e.g., current date)
    from datetime import datetime
    current_month = datetime.now().strftime("%B %Y")  # e.g., "December 2025"
    week_range = "Dec 10 – Dec 16"  # You can calculate this dynamically if needed

    return render_template(
        'index.html',
        current_month=current_month,
        week_range=week_range,
        wellness_tip=random.choice(WELLNESS_TIPS)
    )

@app.route('/api/log-wellness', methods=['POST'])
def log_wellness():
    data = request.get_json()
    mood = data.get('mood')
    stress_level = data.get('stress_level')
    
    # Here you would usually save to a database
    print(f"Received: Mood = {mood}, Stress = {stress_level}")

    return jsonify({"status": "success", "message": "Wellness logged!"})

if __name__ == '__main__':
    app.run(debug=True)