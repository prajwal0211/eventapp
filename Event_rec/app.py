from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
from utils import hash_password  # Import from utils.py
from datetime import datetime
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # Make sure to set a strong secret key

def init_db():
    conn = sqlite3.connect('database/events.db')
    c = conn.cursor()
    
    # Create tables
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                  username TEXT NOT NULL, 
                  password TEXT NOT NULL, 
                  interests TEXT,
                  is_admin INTEGER NOT NULL)''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS events
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                  title TEXT NOT NULL, 
                  description TEXT NOT NULL,
                  organizer TEXT NOT NULL, 
                  category TEXT,
                  date TEXT NOT NULL,
                  created_at TEXT DEFAULT (datetime('now')),
                  image_url TEXT)''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS participation
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                  user_id INTEGER NOT NULL, 
                  event_id INTEGER NOT NULL,
                  FOREIGN KEY (user_id) REFERENCES users (id),
                  FOREIGN KEY (event_id) REFERENCES events (id))''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS feedback (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,  
    event_id INTEGER, 
    rating INTEGER, 
    comments TEXT, 
    date TEXT,  
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (event_id) REFERENCES events(id)
);
''')
    
    conn.commit()
    conn.close()

@app.route('/')
def index():
    return render_template('index.html')

# Register the admin_signup blueprint
from admin_signup import admin_bp
app.register_blueprint(admin_bp)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = hash_password(request.form['password'])

        conn = sqlite3.connect('database/events.db')
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
        user = c.fetchone()
        conn.close()

        if user:
            session['username'] = username
            session['user_id'] = user[0]
            session['is_admin'] = user[3]  # Store admin status
            return redirect(url_for('home'))
        else:
            flash('Invalid login credentials')

    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = hash_password(request.form['password'])
        interests = request.form['interests']

        conn = sqlite3.connect('database/events.db')
        c = conn.cursor()
        
        # Check if the username already exists
        c.execute("SELECT * FROM users WHERE username=?", (username,))
        existing_user = c.fetchone()
        if existing_user:
            flash('Username already exists')
            return render_template('signup.html')

        # Insert the new user
        c.execute("INSERT INTO users (username, password, is_admin, interests) VALUES (?, ?, 0, ?)", (username, password, interests))
        conn.commit()
        conn.close()

        flash('Signup successful! You can now log in.')
        print('a')
        return redirect(url_for('login'))

    return render_template('signup.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    session.pop('user_id', None)
    session.pop('is_admin', None)
    flash('You have been logged out.')
    return redirect(url_for('index'))

# @app.route('/home')
# def home():
#     conn = sqlite3.connect('database/events.db')
#     c = conn.cursor()
#     c.execute("SELECT * FROM events")
#     events = c.fetchall()
#     conn.close()

#     # Convert events to a list of dictionaries for easier access in the template
#     events_list = [
#         {
#             "id": event[0],
#             "title": event[1],
#             "description": event[2],
#             "organizer": event[3],
#             "date": event[4],
#             "category": event[5],
#             "image_url": event[7]
#         }
#         for event in events
#     ]

#     return render_template('home.html', events=events_list)

@app.route('/home')
def home():
    conn = sqlite3.connect('database/events.db')
    conn.row_factory = sqlite3.Row  # This allows row access by column name
    c = conn.cursor()

    c.execute("SELECT DISTINCT category FROM events")
    categories = [row['category'] for row in c.fetchall()]

    selected_category = request.args.get('category')

    # Modify the query to filter by category if selected
    if selected_category:
        c.execute("SELECT * FROM events WHERE date >= DATE('now') AND category = ? ORDER BY date ASC", (selected_category,))
    else:
        c.execute("SELECT * FROM events WHERE date >= DATE('now') ORDER BY date ASC")
    upcoming_events = [dict(row) for row in c.fetchall()]

     # Fetch recently completed events
    if selected_category:
        c.execute("SELECT * FROM events WHERE date < DATE('now') AND category = ? ORDER BY date DESC", (selected_category,))
    else:
        c.execute("SELECT * FROM events WHERE date < DATE('now') ORDER BY date DESC")
    completed_events = [dict(row) for row in c.fetchall()]

    # Fetch participated events if applicable
    user_id = session.get('user_id')
    is_admin = False
    if user_id:
        c.execute("""
            SELECT events.* FROM events
            JOIN participation ON events.id = participation.event_id
            WHERE participation.user_id = ?
            ORDER BY events.date DESC
        """, (user_id,))
        participated_events = [dict(row) for row in c.fetchall()]

        c.execute("""SELECT * FROM users WHERE id = ?""", (user_id,))
        user = c.fetchone()
        
        if user and user['is_admin'] == 1:
            is_admin = True
    else:
        participated_events = []

    conn.close()
    return render_template('home.html', upcoming_events=upcoming_events, completed_events=completed_events, participated_events=participated_events,categories=categories,selected_category=selected_category,user_id=user_id,is_admin=is_admin)

@app.route('/add_event', methods=['GET', 'POST'])
def add_event():
    if request.method == 'POST':
        # Retrieve form data
        title = request.form['title']
        description = request.form['description']
        date = request.form['date']
        organizer = request.form['organizer']
        category = request.form['category']
        image_url = request.form.get('image_url')  # Optional

        # Connect to the database
        conn = sqlite3.connect('database/events.db')
        c = conn.cursor()

        # Insert new event into the database
        c.execute("""
            INSERT INTO events (title, description, date, organizer, category, image_url)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (title, description, date, organizer, category, image_url))
        conn.commit()
        conn.close()

        return redirect(url_for('home'))

    return render_template('add_event.html')

@app.route('/event/<int:event_id>')
def event_detail(event_id):
    conn = sqlite3.connect('database/events.db')
    conn.row_factory = sqlite3.Row  # Access rows as dictionaries
    is_admin = False

    c = conn.cursor()

    # Fetch event details
    c.execute("SELECT * FROM events WHERE id = ?", (event_id,))
    event = c.fetchone()

    current_date = datetime.now().strftime('%Y-%m-%d')
    is_completed = event['date'] < current_date

    # Get the logged-in user's details
    user_id = session.get('user_id')
    if user_id:
        c.execute("SELECT * FROM users WHERE id = ?", (user_id,))
        user = c.fetchone()
        
        if user and user['is_admin'] == 1:
            is_admin = True

    else:
        user = None

    is_participated = False
    if user_id:
        c.execute("SELECT * FROM participation WHERE user_id = ? AND event_id = ?", (user_id, event_id))
        is_participated = bool(c.fetchone())
    
    conn.close()

    registered = session.pop('registered', False)

    if event:
        return render_template('event.html', event=dict(event),is_participated=is_participated,is_completed=is_completed, user=dict(user) if user else None,  registered=registered,is_admin=is_admin)
    else:
        return "Event not found", 404
    
@app.route('/register_for_event/<int:event_id>', methods=['POST'])
def register_for_event(event_id):
    user_id = session.get('user_id')
    email = request.form.get('email')
    
    if not user_id:
        return redirect(url_for('login'))  # Redirect to login if user is not logged in

    # Connect to the database
    conn = sqlite3.connect('database/events.db')
    c = conn.cursor()

    # Check if the user is already registered for this event
    c.execute("SELECT * FROM participation WHERE user_id = ? AND event_id = ?", (user_id, event_id))
    if c.fetchone():
        conn.close()
        return "You are already registered for this event!", 400

    # Register the user for the event
    c.execute("INSERT INTO participation (user_id, event_id, email) VALUES (?, ?, ?)", (user_id, event_id, email))
    conn.commit()
    conn.close()

    session['registered'] = True

    return redirect(url_for('event_detail', event_id=event_id))

@app.route('/recommendations')
def recommendations():
    user_id = session.get('user_id')
    if not user_id:
        flash("You need to be logged in to see recommendations.")
        return redirect(url_for('login'))

    recommended_events = recommend_events(user_id)
    return render_template('recommendations.html', recommended_events=recommended_events)

def calculate_similarity(text1, text2):
    vectorizer = TfidfVectorizer().fit_transform([text1, text2])
    vectors = vectorizer.toarray()
    similarity = cosine_similarity([vectors[0]], [vectors[1]])
    return similarity[0][0]

def recommend_events(user_id):
    conn = sqlite3.connect('database/events.db')
    c = conn.cursor()

    # Fetch the user's interests
    c.execute("SELECT interests FROM users WHERE id=?", (user_id,))
    result = c.fetchone()

    if result is None:
        # Handle case where the user is not found or has no interests
        flash("No interests found for the user.")
        return []

    user_interests = result[0]

    # Fetch all events
    c.execute("SELECT id, title, description, image_url, organizer, date, category FROM events")
    all_events = c.fetchall()

    # Threshold for similarity
    similarity_threshold = 0.2
    recommended_events = {}

    c.execute("SELECT event_id FROM participation WHERE user_id=?", (user_id,))
    past_participation = [row[0] for row in c.fetchall()]

    for event in all_events:
        event_id, title, description, image_url, organizer, date, category = event
        event_text = f"{title} "

        # Calculate similarity between interests and event text
        similarity = calculate_similarity(user_interests, event_text)

        # If similarity is above threshold, add or update the event in the recommendations
        if similarity >= similarity_threshold:
            if event_id not in recommended_events:
                recommended_events[event_id] = {
                    'id': event_id,
                    'title': title,
                    'description': description,
                    'image_url': image_url,
                    'organizer': organizer,
                    'date': date,
                    'category': category
                }

        # If the event was attended before, prioritize it
        if event_id in past_participation:
            if event_id not in recommended_events:
                recommended_events[event_id] = {
                    'id': event_id,
                    'title': title,
                    'description': description,
                    'image_url': image_url,
                    'organizer': organizer,
                    'date': date,
                    'category': category
                }

    # Convert dictionary to list and sort by date
    recommended_events_list = list(recommended_events.values())
    recommended_events_list.sort(key=lambda x: x['date'])

    conn.close()

    return recommended_events_list

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
