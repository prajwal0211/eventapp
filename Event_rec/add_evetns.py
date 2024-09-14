import sqlite3

def connect_db():
    """Establish a connection to the SQLite database."""
    return sqlite3.connect('database/events.db')

def insert_sample_events():
    """Insert sample events into the 'events' table."""
    conn = connect_db()
    c = conn.cursor()

    # Sample events to insert
    events = [
        ("Tech Conference 2024", 
         "A conference for tech enthusiasts to learn about the latest trends in technology.", 
         "Tech Corp", 
         "2024-09-15",
         "Technology",
         "https://www.shutterstock.com/shutterstock/photos/2475382741/display_1500/stock-photo-person-hands-and-typing-on-laptop-in-office-for-email-spreadsheet-and-proposal-or-application-for-2475382741.jpg"),
        ("Music Festival", 
         "Join us for a weekend of music, food, and fun at the annual music festival.", 
         "Music World", 
         "2024-10-05",
         "Music",
         "https://www.shutterstock.com/shutterstock/photos/2476927275/display_1500/stock-vector-music-icons-concept-player-and-melody-songs-and-playlist-treble-clef-and-notes-musical-notes-2476927275.jpg"),
        ("Startup Pitch Night", 
         "An event where startups pitch their ideas to potential investors.", 
         "Startup Hub", 
         "2024-09-25",
         "Business",
         "https://www.shutterstock.com/shutterstock/photos/2479039211/display_1500/stock-photo-create-a-picture-for-startup-consultancy-image-should-have-startup-written-on-the-image-2479039211.jpg"),
        ("Art Exhibition", 
         "Showcasing modern art from up-and-coming artists around the world.", 
         "Art Gallery", 
         "2024-11-01",
         "Art",
         "https://www.shutterstock.com/shutterstock/photos/2461401163/display_1500/stock-photo-fine-art-gallery-exhibit-in-a-large-city-in-france-futuristic-colorful-digital-display-art-gallery-2461401163.jpg"),
        ("Business Workshop", 
         "Learn effective business strategies from industry leaders.", 
         "Biz Leaders", 
         "2024-09-20",
         "Business",
         "https://www.shutterstock.com/shutterstock/photos/2463472593/display_1500/stock-photo-presentation-whiteboard-and-meeting-with-team-chart-and-sales-projection-for-planning-manager-2463472593.jpg"),
        ("Fitness Bootcamp", 
         "A week-long fitness program for all fitness levels.", 
         "FitLife", 
         "2024-10-12",
         "Fitness",
         "https://www.shutterstock.com/shutterstock/photos/630936851/display_1500/stock-photo-people-receiving-tire-obstacle-course-training-in-boot-camp-630936851.jpg"),
        ("Film Screening", 
         "A special screening of an indie film followed by a Q&A with the director.", 
         "Film Studio", 
         "2024-09-18",
         "Film",
         "https://www.shutterstock.com/shutterstock/photos/2373960657/display_1500/stock-photo-movies-and-popcorn-man-holding-pop-corn-box-at-cinema-action-thriller-or-scifi-entertainment-on-2373960657.jpg"),
        ("Community Charity Event", 
         "A charity event to raise funds for local causes.", 
         "Local Heroes", 
         "2024-11-05",
         "Charity",
         "https://www.shutterstock.com/shutterstock/photos/2503810317/display_1500/stock-photo-a-hand-offers-a-small-beautifully-wrapped-gift-to-another-hand-symbolizing-generosity-kindness-2503810317.jpg")
    ]

    # Insert events into the 'events' table
    c.executemany("""
        INSERT INTO events (title, description, organizer, date, category, image_url)
        VALUES (?, ?, ?, ?, ?, ?)""", events)

    # Commit and close the connection
    conn.commit()
    conn.close()

    print("8 events added successfully.")

if __name__ == '__main__':
    insert_sample_events()
