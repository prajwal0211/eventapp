# admin_signup.py
from flask import Blueprint, render_template, request, redirect, url_for, flash
import sqlite3
from utils import hash_password  # Import from utils.py

admin_bp = Blueprint('admin_signup', __name__)

@admin_bp.route('/signup/admin', methods=['GET', 'POST'])
def admin_signup():
    if request.method == 'POST':
        username = request.form['username']
        password = hash_password(request.form['password'])
        
        conn = sqlite3.connect('database/events.db')
        c = conn.cursor()
        
        # Check if the username already exists
        c.execute("SELECT * FROM users WHERE username=?", (username,))
        existing_user = c.fetchone()
        if existing_user:
            flash('Username already exists')
            conn.close()
            return render_template('admin_signup.html')  # Use a dedicated template if needed

        # Set is_admin = 1 for the admin user
        c.execute("INSERT INTO users (username, password, is_admin,interests) VALUES (?, ?, 1,null)", (username, password))
        conn.commit()
        conn.close()
        
        flash('Admin signup successful! You can now log in.')
        return redirect(url_for('login'))
    
    return render_template('admin_signup.html')  # Use a dedicated template if needed
