from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import sqlite3

app = FastAPI()

# Initialize SQLite Database
def init_db():
    conn = sqlite3.connect("daily_quote.db")
    cursor = conn.cursor()
    
    # Create quotes table
    cursor.execute('''CREATE TABLE IF NOT EXISTS quotes (
                      id INTEGER PRIMARY KEY AUTOINCREMENT,
                      text TEXT,
                      author TEXT,
                      category TEXT
                      )''')
    
    # Create favorites table
    cursor.execute('''CREATE TABLE IF NOT EXISTS favorites (
                      id INTEGER PRIMARY KEY AUTOINCREMENT,
                      quote_id INTEGER,
                      category TEXT,
                      FOREIGN KEY(quote_id) REFERENCES quotes(id)
                      )''')

    # Create diary table
    cursor.execute('''CREATE TABLE IF NOT EXISTS diary (
                      id INTEGER PRIMARY KEY AUTOINCREMENT,
                      entry_date TEXT,
                      content TEXT
                      )''')
    
    # Insert sample quotes
    quotes = [
        # Sample quotes for each category
        # Success
        ("The only way to do great work is to love what you do.", "Steve Jobs", "Success"),
        ("Success is not final, failure is not fatal: It is the courage to continue that counts.", "Winston Churchill", "Success"),
        ("The best revenge is massive success.", "Frank Sinatra", "Success"),
        ("Success usually comes to those who are too busy to be looking for it.", "Henry David Thoreau", "Success"),
        ("The secret of success is to do the common thing uncommonly well.", "John D. Rockefeller Jr.", "Success"),
        ("Opportunities don't happen. You create them.", "Chris Grosser", "Success"),
        ("Success is walking from failure to failure with no loss of enthusiasm.", "Winston Churchill", "Success"),
        
        # Life
        ("Life is what happens when you're busy making other plans.", "John Lennon", "Life"),
        ("Your time is limited, don't waste it living someone else's life.", "Steve Jobs", "Life"),
        ("Life is either a daring adventure or nothing at all.", "Helen Keller", "Life"),
        ("In three words I can sum up everything I've learned about life: it goes on.", "Robert Frost", "Life"),
        ("Life is short, and it's up to you to make it sweet.", "Sarah Louise Delany", "Life"),
        ("The purpose of life is not to be happy. It is to be useful, to be honorable, to be compassionate, to have it make some difference that you have lived and lived well.", "Ralph Waldo Emerson", "Life"),
        ("Life isn't about waiting for the storm to pass; it's about learning how to dance in the rain.", "Vivian Greene", "Life"),
        
        # Happiness
        ("The purpose of our lives is to be happy.", "Dalai Lama", "Happiness"),
        ("Happiness is not something ready made. It comes from your own actions.", "Dalai Lama", "Happiness"),
        ("Happiness depends upon ourselves.", "Aristotle", "Happiness"),
        ("The happiest people don’t have the best of everything, they make the best of everything.", "Unknown", "Happiness"),
        ("Happiness is when what you think, what you say, and what you do are in harmony.", "Mahatma Gandhi", "Happiness"),
        ("For every minute you are angry you lose sixty seconds of happiness.", "Ralph Waldo Emerson", "Happiness"),
        ("Happiness is a warm puppy.", "Charles M. Schulz", "Happiness"),
        
        # Inspiration
        ("The only limit to our realization of tomorrow is our doubts of today.", "Franklin D. Roosevelt", "Inspiration"),
        ("Act as if what you do makes a difference. It does.", "William James", "Inspiration"),
        ("The best way to predict the future is to invent it.", "Alan Kay", "Inspiration"),
        ("You miss 100% of the shots you don't take.", "Wayne Gretzky", "Inspiration"),
        ("Believe you can and you're halfway there.", "Theodore Roosevelt", "Inspiration"),
        ("The future belongs to those who believe in the beauty of their dreams.", "Eleanor Roosevelt", "Inspiration"),
        ("You have within you right now, everything you need to deal with whatever the world can throw at you.", "Brian Tracy", "Inspiration"),
        
        # Wisdom
        ("In the end, we will remember not the words of our enemies, but the silence of our friends.", "Martin Luther King Jr.", "Wisdom"),
        ("To be yourself in a world that is constantly trying to make you something else is the greatest accomplishment.", "Ralph Waldo Emerson", "Wisdom"),
        ("It does not matter how slowly you go as long as you do not stop.", "Confucius", "Wisdom"),
        ("We can't help everyone, but everyone can help someone.", "Ronald Reagan", "Wisdom"),
        ("The greatest glory in living lies not in never falling, but in rising every time we fall.", "Nelson Mandela", "Wisdom"),
        ("The only true wisdom is in knowing you know nothing.", "Socrates", "Wisdom"),
        ("The unexamined life is not worth living.", "Socrates", "Wisdom")
    ]
    
    cursor.executemany('''INSERT INTO quotes (text, author, category) VALUES (?, ?, ?)''', quotes)
    
    conn.commit()
    conn.close()

init_db()

# Models
class Quote(BaseModel):
    text: str
    author: str
    category: Optional[str] = None

class DiaryEntry(BaseModel):
    entry_date: date
    content: str

class DiaryUpdate(BaseModel):
    content: Optional[str]

# ------------------- Quote CRUD Functions -------------------

# 1. Get Daily Quote
@app.get("/daily_quote/")
async def get_daily_quote(category: Optional[str] = None):
    conn = sqlite3.connect("daily_quote.db")
    cursor = conn.cursor()
    
    if category:
        cursor.execute("SELECT * FROM quotes WHERE category = ? ORDER BY RANDOM() LIMIT 1", (category,))
    else:
        cursor.execute("SELECT * FROM quotes ORDER BY RANDOM() LIMIT 1")
    
    quote = cursor.fetchone()
    conn.close()
    
    if quote:
        return {"quote": {"id": quote[0], "text": quote[1], "author": quote[2], "category": quote[3]}}
    raise HTTPException(status_code=404, detail="No quotes available")

# 2. Push Notification Simulation (Daily at Set Time)
@app.get("/quote_notification/")
async def send_daily_quote_notification(category: Optional[str] = None):
    conn = sqlite3.connect("daily_quote.db")
    cursor = conn.cursor()
    
    if category:
        cursor.execute("SELECT * FROM quotes WHERE category = ? ORDER BY RANDOM() LIMIT 1", (category,))
    else:
        cursor.execute("SELECT * FROM quotes ORDER BY RANDOM() LIMIT 1")
    
    quote = cursor.fetchone()
    conn.close()

    if quote:
        # Simulate sending a push notification to the user
        return {"message": f"Daily Quote: '{quote[1]}' - {quote[2]}"}
    raise HTTPException(status_code=404, detail="No quotes available")

# 3. Random Quote from a Specific Category
@app.get("/random_quote/{category}")
async def get_random_quote_by_category(category: str):
    conn = sqlite3.connect("daily_quote.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM quotes WHERE category = ? ORDER BY RANDOM() LIMIT 1", (category,))
    quote = cursor.fetchone()
    conn.close()
    
    if quote:
        return {"quote": {"id": quote[0], "text": quote[1], "author": quote[2], "category": quote[3]}}
    raise HTTPException(status_code=404, detail=f"No quotes available in the {category} category")

# ------------------- Quote Library -------------------

# 4. Browse All Quotes
@app.get("/quote_library/")
async def get_all_quotes():
    conn = sqlite3.connect("daily_quote.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM quotes ORDER BY id")
    quotes = cursor.fetchall()
    conn.close()
    return {"quotes": [{"id": q[0], "text": q[1], "author": q[2], "category": q[3]} for q in quotes]}

# ------------------- Favorites Functions -------------------

# 5. Add Quote to Favorites with Category
@app.post("/favorites/")
async def add_favorite(quote_id: int, category: str):
    conn = sqlite3.connect("daily_quote.db")
    cursor = conn.cursor()
    cursor.execute('''INSERT INTO favorites (quote_id, category)
                      VALUES (?, ?)''', (quote_id, category))
    conn.commit()
    conn.close()
    return {"message": "Quote added to favorites"}

# 6. Get All Favorite Quotes by Category
@app.get("/favorites/{category}")
async def get_favorites_by_category(category: str):
    conn = sqlite3.connect("daily_quote.db")
    cursor = conn.cursor()
    cursor.execute('''SELECT q.id, q.text, q.author FROM favorites f
                      JOIN quotes q ON f.quote_id = q.id
                      WHERE f.category = ?''', (category,))
    favorites = cursor.fetchall()
    conn.close()
    return {"favorites": [{"id": f[0], "text": f[1], "author": f[2]} for f in favorites]}

# ------------------- Diary Functions -------------------

# 7. Add Diary Entry
@app.post("/diary/")
async def add_diary_entry(entry: DiaryEntry):
    conn = sqlite3.connect("daily_quote.db")
    cursor = conn.cursor()
    cursor.execute('''INSERT INTO diary (entry_date, content)
                      VALUES (?, ?)''', (entry.entry_date.isoformat(), entry.content))
    conn.commit()
    conn.close()
    return {"message": "Diary entry added"}

# 8. Get Diary Entries for a Specific Date
@app.get("/diary/{entry_date}")
async def get_diary_entries(entry_date: date):
    conn = sqlite3.connect("daily_quote.db")
    cursor = conn.cursor()
    cursor.execute('''SELECT content FROM diary WHERE entry_date = ?''', (entry_date.isoformat(),))
    entries = cursor.fetchall()
    conn.close()
    
    return {"entries": [entry[0] for entry in entries]}

# 9. Update Diary Entry
@app.put("/diary/{entry_date}")
async def update_diary_entry(entry_date: date, entry_update: DiaryUpdate):
    conn = sqlite3.connect("daily_quote.db")
    cursor = conn.cursor()
    
    if entry_update.content:
        cursor.execute('''UPDATE diary SET content = ? WHERE entry_date = ?''', (entry_update.content, entry_date.isoformat()))
        conn.commit()
    
    conn.close()
    return {"message": "Diary entry updated"}

# 10. Delete Diary Entry
@app.delete("/diary/{entry_date}")
async def delete_diary_entry(entry_date: date):
    conn = sqlite3.connect("daily_quote.db")
    cursor = conn.cursor()
    cursor.execute('''DELETE FROM diary WHERE entry_date = ?''', (entry_date.isoformat(),))
    conn.commit()
    conn.close()
    return {"message": "Diary entry deleted"}
