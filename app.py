"""
在线课程学习平台 - Flask Web Application
"""
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from functools import wraps
import sqlite3
import os
from datetime import datetime
import hashlib
import secrets

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)
DATABASE = os.path.join(os.path.dirname(__file__), 'learning_platform.db')

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    c = conn.cursor()
    c.executescript('''
        CREATE TABLE IF NOT EXISTS user (user_id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT NOT NULL UNIQUE, email TEXT NOT NULL UNIQUE, password_hash TEXT NOT NULL, phone TEXT, status TEXT DEFAULT 'active', created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, last_login DATETIME);
        CREATE TABLE IF NOT EXISTS user_profile (profile_id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER NOT NULL UNIQUE, avatar_url TEXT, bio TEXT, gender TEXT, location TEXT, occupation TEXT, FOREIGN KEY (user_id) REFERENCES user(user_id));
        CREATE TABLE IF NOT EXISTS role (role_id INTEGER PRIMARY KEY AUTOINCREMENT, role_name TEXT NOT NULL UNIQUE, description TEXT);
        CREATE TABLE IF NOT EXISTS user_role (user_id INTEGER NOT NULL, role_id INTEGER NOT NULL, PRIMARY KEY (user_id, role_id));
        CREATE TABLE IF NOT EXISTS category (category_id INTEGER PRIMARY KEY AUTOINCREMENT, category_name TEXT NOT NULL, parent_id INTEGER, description TEXT, sort_order INTEGER DEFAULT 0);
        CREATE TABLE IF NOT EXISTS course (course_id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT NOT NULL, subtitle TEXT, description TEXT, instructor_id INTEGER NOT NULL, category_id INTEGER, cover_image TEXT, price REAL DEFAULT 0.00, original_price REAL, level TEXT DEFAULT 'beginner', duration_hours REAL DEFAULT 0, status TEXT DEFAULT 'draft', is_featured INTEGER DEFAULT 0, enrollment_count INTEGER DEFAULT 0, rating_avg REAL DEFAULT 0.00, rating_count INTEGER DEFAULT 0, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, published_at DATETIME);
        CREATE TABLE IF NOT EXISTS chapter (chapter_id INTEGER PRIMARY KEY AUTOINCREMENT, course_id INTEGER NOT NULL, title TEXT NOT NULL, description TEXT, sort_order INTEGER DEFAULT 0, is_free INTEGER DEFAULT 0);
        CREATE TABLE IF NOT EXISTS lesson (lesson_id INTEGER PRIMARY KEY AUTOINCREMENT, chapter_id INTEGER NOT NULL, title TEXT NOT NULL, content_type TEXT DEFAULT 'video', video_url TEXT, video_duration INTEGER DEFAULT 0, sort_order INTEGER DEFAULT 0, is_free INTEGER DEFAULT 0);
        CREATE TABLE IF NOT EXISTS "order" (order_id INTEGER PRIMARY KEY AUTOINCREMENT, order_no TEXT NOT NULL UNIQUE, user_id INTEGER NOT NULL, total_amount REAL NOT NULL, discount_amount REAL DEFAULT 0.00, final_amount REAL NOT NULL, payment_method TEXT DEFAULT 'alipay', payment_status TEXT DEFAULT 'pending', paid_at DATETIME, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP);
        CREATE TABLE IF NOT EXISTS order_item (item_id INTEGER PRIMARY KEY AUTOINCREMENT, order_id INTEGER NOT NULL, course_id INTEGER NOT NULL, price REAL NOT NULL);
        CREATE TABLE IF NOT EXISTS enrollment (enrollment_id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER NOT NULL, course_id INTEGER NOT NULL, order_id INTEGER, progress_percent REAL DEFAULT 0.00, completed_lessons INTEGER DEFAULT 0, total_lessons INTEGER DEFAULT 0, status TEXT DEFAULT 'active', enrolled_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, last_accessed_at DATETIME, UNIQUE (user_id, course_id));
        CREATE TABLE IF NOT EXISTS learning_progress (progress_id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER NOT NULL, lesson_id INTEGER NOT NULL, watched_duration INTEGER DEFAULT 0, progress_percent REAL DEFAULT 0.00, is_completed INTEGER DEFAULT 0, UNIQUE (user_id, lesson_id));
        CREATE TABLE IF NOT EXISTS review (review_id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER NOT NULL, course_id INTEGER NOT NULL, rating INTEGER NOT NULL, content TEXT, helpful_count INTEGER DEFAULT 0, status TEXT DEFAULT 'approved', created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, UNIQUE (user_id, course_id));
        CREATE TABLE IF NOT EXISTS favorite (favorite_id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER NOT NULL, course_id INTEGER NOT NULL, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, UNIQUE (user_id, course_id));
        CREATE TABLE IF NOT EXISTS cart (cart_id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER NOT NULL, course_id INTEGER NOT NULL, added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, UNIQUE (user_id, course_id));
    ''')
    conn.commit()
    c.execute("SELECT COUNT(*) FROM user")
    if c.fetchone()[0] == 0:
        insert_sample_data(conn)
    conn.close()

def insert_sample_data(conn):
    c = conn.cursor()
    pw = hashlib.sha256('password123'.encode()).hexdigest()
    c.executemany("INSERT INTO role (role_name, description) VALUES (?, ?)", [('student', 'Student'), ('instructor', 'Instructor'), ('admin', 'Administrator')])
    c.executemany("INSERT INTO user (username, email, password_hash, phone, status) VALUES (?, ?, ?, ?, ?)", [
        ('John', 'john@example.com', pw, '1234567001', 'active'),
        ('Mike', 'mike@example.com', pw, '1234567002', 'active'),
        ('Prof. Wang', 'wang@example.com', pw, '1234567003', 'active'),
        ('Prof. Liu', 'liu@example.com', pw, '1234567004', 'active'),
        ('Prof. Chen', 'chen@example.com', pw, '1234567005', 'active'),
        ('admin', 'admin@example.com', pw, '1234567000', 'active'),
        ('Sarah', 'sarah@example.com', pw, '1234567006', 'active'),
        ('Tom', 'tom@example.com', pw, '1234567007', 'active')])
    c.executemany("INSERT INTO user_profile (user_id, avatar_url, bio, gender, location, occupation) VALUES (?, ?, ?, ?, ?, ?)", [
        (1, '/static/images/avatar1.png', 'Passionate programmer', 'male', 'New York', 'Software Engineer'),
        (2, '/static/images/avatar2.png', 'Frontend enthusiast', 'female', 'Los Angeles', 'Frontend Developer'),
        (3, '/static/images/avatar3.png', '10 years Python experience', 'male', 'San Francisco', 'Senior Engineer'),
        (4, '/static/images/avatar4.png', 'Full-stack expert', 'male', 'Seattle', 'Tech Lead'),
        (5, '/static/images/avatar5.png', 'Data scientist', 'female', 'Boston', 'Data Scientist')])
    c.executemany("INSERT INTO user_role (user_id, role_id) VALUES (?, ?)", [(1,1),(2,1),(3,2),(4,2),(5,2),(6,3),(7,1),(8,1)])
    c.executemany("INSERT INTO category (category_id, category_name, parent_id, description, sort_order) VALUES (?, ?, ?, ?, ?)", [
        (1, 'Programming', None, 'Programming languages and development', 1),
        (2, 'Frontend', 1, 'HTML/CSS/JavaScript', 1),
        (3, 'Backend', 1, 'Python/Java/Node.js', 2),
        (4, 'Mobile', 1, 'iOS/Android/Flutter', 3),
        (5, 'Data Science', None, 'Data analysis and machine learning', 2),
        (6, 'Machine Learning', 5, 'ML algorithms', 1),
        (7, 'Deep Learning', 5, 'Neural networks', 2)])
    c.executemany("INSERT INTO course (course_id, title, subtitle, description, instructor_id, category_id, price, original_price, level, duration_hours, status, is_featured, enrollment_count, rating_avg, rating_count, published_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", [
        (1, 'Python Masterclass', 'From Zero to Hero', 'Python is one of the most popular programming languages today', 3, 3, 199.00, 399.00, 'beginner', 42.5, 'published', 1, 1580, 4.85, 328, '2024-01-15'),
        (2, 'Web Frontend Development', 'HTML+CSS+JavaScript', 'Complete frontend learning path', 4, 2, 299.00, 599.00, 'intermediate', 68.0, 'published', 1, 1230, 4.72, 256, '2024-02-20'),
        (3, 'Machine Learning Fundamentals', 'Python for ML', 'Systematic learning of ML algorithms', 5, 6, 399.00, 799.00, 'intermediate', 55.5, 'published', 1, 890, 4.90, 178, '2024-03-10'),
        (4, 'MySQL Database Mastery', 'From Basics to Optimization', 'Deep dive into MySQL database', 3, 3, 149.00, 299.00, 'beginner', 35.0, 'published', 0, 760, 4.65, 152, '2024-04-05'),
        (5, 'Vue.js 3.0 in Action', 'Modern Vue3 Development', 'Learn Vue3 latest features', 4, 2, 259.00, 499.00, 'intermediate', 48.0, 'published', 1, 650, 4.78, 130, '2024-05-12'),
        (6, 'Deep Learning & Neural Networks', 'TensorFlow & PyTorch', 'Master deep learning core technologies', 5, 7, 499.00, 999.00, 'advanced', 72.0, 'published', 1, 420, 4.92, 84, '2024-06-20'),
        (7, 'Flask Web Development', 'Python Web Framework', 'Build web apps with Flask', 3, 3, 199.00, 399.00, 'intermediate', 38.0, 'published', 0, 380, 4.60, 76, '2024-07-15'),
        (8, 'Git Version Control', 'Team Collaboration Essential', 'Master Git workflow', 3, 1, 0.00, 0.00, 'beginner', 8.0, 'published', 0, 2100, 4.45, 420, '2024-01-01')])
    c.executemany("INSERT INTO chapter (chapter_id, course_id, title, description, sort_order, is_free) VALUES (?, ?, ?, ?, ?, ?)", [
        (1, 1, 'Chapter 1: Python Setup', 'Install Python and configure environment', 1, 1),
        (2, 1, 'Chapter 2: Python Basics', 'Variables, data types, operators', 2, 1),
        (3, 1, 'Chapter 3: Control Flow', 'Conditionals and loops', 3, 0),
        (4, 2, 'Chapter 1: HTML Basics', 'HTML tags and structure', 1, 1),
        (5, 2, 'Chapter 2: CSS Styling', 'Selectors and box model', 2, 0),
        (6, 3, 'Chapter 1: ML Overview', 'What is machine learning', 1, 1)])
    c.executemany("INSERT INTO lesson (lesson_id, chapter_id, title, content_type, video_url, video_duration, sort_order, is_free) VALUES (?, ?, ?, ?, ?, ?, ?, ?)", [
        (1, 1, '1.1 Introduction to Python', 'video', 'https://example.com/v1.mp4', 600, 1, 1),
        (2, 1, '1.2 Installing Python', 'video', 'https://example.com/v2.mp4', 480, 2, 1),
        (3, 2, '2.1 Variables and Naming', 'video', 'https://example.com/v3.mp4', 540, 1, 1),
        (4, 2, '2.2 Data Types', 'video', 'https://example.com/v4.mp4', 900, 2, 0),
        (5, 3, '3.1 If Statements', 'video', 'https://example.com/v5.mp4', 600, 1, 0),
        (6, 4, '1.1 HTML Structure', 'video', 'https://example.com/v6.mp4', 480, 1, 1)])
    c.executemany('INSERT INTO "order" (order_id, order_no, user_id, total_amount, discount_amount, final_amount, payment_method, payment_status, paid_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)', [
        (1, 'ORD202401150001', 1, 199.00, 0.00, 199.00, 'paypal', 'paid', '2024-01-15 14:30:00'),
        (2, 'ORD202401200002', 1, 299.00, 50.00, 249.00, 'credit_card', 'paid', '2024-01-20 10:15:00'),
        (3, 'ORD202402050003', 2, 399.00, 0.00, 399.00, 'paypal', 'paid', '2024-02-05 16:45:00')])
    c.executemany("INSERT INTO order_item (order_id, course_id, price) VALUES (?, ?, ?)", [(1, 1, 199.00), (2, 2, 299.00), (3, 3, 399.00)])
    c.executemany("INSERT INTO enrollment (user_id, course_id, order_id, progress_percent, completed_lessons, total_lessons, status, enrolled_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?)", [
        (1, 1, 1, 75.50, 3, 5, 'active', '2024-01-15'), (1, 2, 2, 30.00, 1, 4, 'active', '2024-01-20'), (2, 3, 3, 45.00, 1, 3, 'active', '2024-02-05')])
    c.executemany("INSERT INTO review (user_id, course_id, rating, content, helpful_count, status) VALUES (?, ?, ?, ?, ?, ?)", [
        (1, 1, 5, 'Excellent course! Very well explained.', 45, 'approved'),
        (2, 3, 5, 'Best introduction to machine learning!', 38, 'approved')])
    c.executemany("INSERT INTO favorite (user_id, course_id) VALUES (?, ?)", [(1, 3), (1, 5), (2, 1), (2, 5)])
    conn.commit()

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please login first', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def index():
    conn = get_db()
    c = conn.cursor()
    c.execute('''SELECT c.*, u.username as instructor_name, cat.category_name FROM course c
        LEFT JOIN user u ON c.instructor_id = u.user_id LEFT JOIN category cat ON c.category_id = cat.category_id
        WHERE c.status = 'published' AND c.is_featured = 1 ORDER BY c.enrollment_count DESC LIMIT 6''')
    featured_courses = c.fetchall()
    c.execute('''SELECT c.*, u.username as instructor_name, cat.category_name FROM course c
        LEFT JOIN user u ON c.instructor_id = u.user_id LEFT JOIN category cat ON c.category_id = cat.category_id
        WHERE c.status = 'published' ORDER BY c.created_at DESC LIMIT 12''')
    latest_courses = c.fetchall()
    c.execute('SELECT * FROM category WHERE parent_id IS NULL ORDER BY sort_order')
    categories = c.fetchall()
    conn.close()
    return render_template('index.html', featured_courses=featured_courses, latest_courses=latest_courses, categories=categories)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        if not all([username, email, password]):
            flash('Please fill in all required fields', 'error')
            return render_template('register.html')
        if password != confirm_password:
            flash('Passwords do not match', 'error')
            return render_template('register.html')
        if len(password) < 6:
            flash('Password must be at least 6 characters', 'error')
            return render_template('register.html')
        conn = get_db()
        c = conn.cursor()
        c.execute('SELECT user_id FROM user WHERE username = ? OR email = ?', (username, email))
        if c.fetchone():
            flash('Username or email already exists', 'error')
            conn.close()
            return render_template('register.html')
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        c.execute('INSERT INTO user (username, email, password_hash) VALUES (?, ?, ?)', (username, email, password_hash))
        user_id = c.lastrowid
        c.execute('INSERT INTO user_role (user_id, role_id) VALUES (?, 1)', (user_id,))
        c.execute('INSERT INTO user_profile (user_id) VALUES (?)', (user_id,))
        conn.commit()
        conn.close()
        flash('Registration successful, please login', 'success')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        if not all([email, password]):
            flash('Please enter email and password', 'error')
            return render_template('login.html')
        conn = get_db()
        c = conn.cursor()
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        c.execute('SELECT * FROM user WHERE email = ? AND password_hash = ?', (email, password_hash))
        user = c.fetchone()
        if user:
            if user['status'] != 'active':
                flash('Account has been disabled', 'error')
                conn.close()
                return render_template('login.html')
            c.execute('UPDATE user SET last_login = ? WHERE user_id = ?', (datetime.now(), user['user_id']))
            conn.commit()
            session['user_id'] = user['user_id']
            session['username'] = user['username']
            session['email'] = user['email']
            c.execute('SELECT r.role_name FROM role r JOIN user_role ur ON r.role_id = ur.role_id WHERE ur.user_id = ?', (user['user_id'],))
            session['roles'] = [row['role_name'] for row in c.fetchall()]
            conn.close()
            flash(f'Welcome back, {user["username"]}!', 'success')
            return redirect(url_for('index'))
        flash('Invalid email or password', 'error')
        conn.close()
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('Logged out successfully', 'success')
    return redirect(url_for('index'))

@app.route('/courses')
def courses():
    conn = get_db()
    c = conn.cursor()
    category_id = request.args.get('category', type=int)
    level = request.args.get('level', '')
    sort = request.args.get('sort', 'newest')
    keyword = request.args.get('keyword', '').strip()
    query = '''SELECT c.*, u.username as instructor_name, cat.category_name FROM course c
        LEFT JOIN user u ON c.instructor_id = u.user_id LEFT JOIN category cat ON c.category_id = cat.category_id WHERE c.status = 'published' '''
    params = []
    if category_id:
        query += ' AND (c.category_id = ? OR cat.parent_id = ?)'
        params.extend([category_id, category_id])
    if level:
        query += ' AND c.level = ?'
        params.append(level)
    if keyword:
        query += ' AND (c.title LIKE ? OR c.description LIKE ?)'
        params.extend([f'%{keyword}%', f'%{keyword}%'])
    order_map = {'popular': 'c.enrollment_count DESC', 'rating': 'c.rating_avg DESC', 'price_low': 'c.price ASC', 'price_high': 'c.price DESC'}
    query += f" ORDER BY {order_map.get(sort, 'c.published_at DESC')}"
    c.execute(query, params)
    courses_list = c.fetchall()
    c.execute('SELECT * FROM category ORDER BY parent_id, sort_order')
    categories = c.fetchall()
    conn.close()
    return render_template('courses.html', courses=courses_list, categories=categories, current_category=category_id, current_level=level, current_sort=sort, keyword=keyword)

@app.route('/course/<int:course_id>')
def course_detail(course_id):
    conn = get_db()
    c = conn.cursor()
    c.execute('''SELECT c.*, u.username as instructor_name, up.bio as instructor_bio, cat.category_name FROM course c
        LEFT JOIN user u ON c.instructor_id = u.user_id LEFT JOIN user_profile up ON u.user_id = up.user_id
        LEFT JOIN category cat ON c.category_id = cat.category_id WHERE c.course_id = ?''', (course_id,))
    course = c.fetchone()
    if not course:
        flash('Course not found', 'error')
        return redirect(url_for('courses'))
    c.execute('SELECT * FROM chapter WHERE course_id = ? ORDER BY sort_order', (course_id,))
    chapters = c.fetchall()
    chapters_with_lessons = []
    for chapter in chapters:
        c.execute('SELECT * FROM lesson WHERE chapter_id = ? ORDER BY sort_order', (chapter['chapter_id'],))
        chapters_with_lessons.append({'chapter': chapter, 'lessons': c.fetchall()})
    c.execute('SELECT r.*, u.username FROM review r LEFT JOIN user u ON r.user_id = u.user_id WHERE r.course_id = ? AND r.status = "approved" ORDER BY r.created_at DESC LIMIT 10', (course_id,))
    reviews = c.fetchall()
    is_enrolled = is_favorited = False
    if 'user_id' in session:
        c.execute('SELECT * FROM enrollment WHERE user_id = ? AND course_id = ?', (session['user_id'], course_id))
        is_enrolled = c.fetchone() is not None
        c.execute('SELECT * FROM favorite WHERE user_id = ? AND course_id = ?', (session['user_id'], course_id))
        is_favorited = c.fetchone() is not None
    conn.close()
    return render_template('course_detail.html', course=course, chapters=chapters_with_lessons, reviews=reviews, is_enrolled=is_enrolled, is_favorited=is_favorited)

@app.route('/profile')
@login_required
def profile():
    conn = get_db()
    c = conn.cursor()
    c.execute('SELECT u.*, up.* FROM user u LEFT JOIN user_profile up ON u.user_id = up.user_id WHERE u.user_id = ?', (session['user_id'],))
    user = c.fetchone()
    c.execute('''SELECT e.*, c.title, c.cover_image, u.username as instructor_name FROM enrollment e
        JOIN course c ON e.course_id = c.course_id LEFT JOIN user u ON c.instructor_id = u.user_id
        WHERE e.user_id = ? AND e.status = 'active' ORDER BY e.last_accessed_at DESC''', (session['user_id'],))
    learning_courses = c.fetchall()
    c.execute('''SELECT f.*, c.title, c.cover_image, c.price, u.username as instructor_name FROM favorite f
        JOIN course c ON f.course_id = c.course_id LEFT JOIN user u ON c.instructor_id = u.user_id
        WHERE f.user_id = ? ORDER BY f.created_at DESC''', (session['user_id'],))
    favorites = c.fetchall()
    conn.close()
    return render_template('profile.html', user=user, learning_courses=learning_courses, favorites=favorites)

@app.route('/profile/edit', methods=['GET', 'POST'])
@login_required
def edit_profile():
    conn = get_db()
    c = conn.cursor()
    if request.method == 'POST':
        bio = request.form.get('bio', '')
        location = request.form.get('location', '')
        occupation = request.form.get('occupation', '')
        gender = request.form.get('gender', '')
        c.execute('UPDATE user_profile SET bio = ?, location = ?, occupation = ?, gender = ? WHERE user_id = ?', (bio, location, occupation, gender, session['user_id']))
        conn.commit()
        flash('Profile updated', 'success')
        return redirect(url_for('profile'))
    c.execute('SELECT u.*, up.* FROM user u LEFT JOIN user_profile up ON u.user_id = up.user_id WHERE u.user_id = ?', (session['user_id'],))
    user = c.fetchone()
    conn.close()
    return render_template('edit_profile.html', user=user)

@app.route('/favorite/<int:course_id>', methods=['POST'])
@login_required
def toggle_favorite(course_id):
    conn = get_db()
    c = conn.cursor()
    c.execute('SELECT * FROM favorite WHERE user_id = ? AND course_id = ?', (session['user_id'], course_id))
    if c.fetchone():
        c.execute('DELETE FROM favorite WHERE user_id = ? AND course_id = ?', (session['user_id'], course_id))
        message, is_favorited = 'Removed from favorites', False
    else:
        c.execute('INSERT INTO favorite (user_id, course_id) VALUES (?, ?)', (session['user_id'], course_id))
        message, is_favorited = 'Added to favorites', True
    conn.commit()
    conn.close()
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({'success': True, 'message': message, 'is_favorited': is_favorited})
    flash(message, 'success')
    return redirect(url_for('course_detail', course_id=course_id))

@app.route('/enroll/<int:course_id>', methods=['POST'])
@login_required
def enroll_course(course_id):
    conn = get_db()
    c = conn.cursor()
    c.execute('SELECT * FROM course WHERE course_id = ?', (course_id,))
    course = c.fetchone()
    if not course:
        flash('Course not found', 'error')
        return redirect(url_for('courses'))
    c.execute('SELECT * FROM enrollment WHERE user_id = ? AND course_id = ?', (session['user_id'], course_id))
    if c.fetchone():
        flash('You have already enrolled in this course', 'warning')
        return redirect(url_for('course_detail', course_id=course_id))
    order_no = f"ORD{datetime.now().strftime('%Y%m%d%H%M%S')}{session['user_id']:04d}"
    price = course['price']
    payment_method = 'free' if price == 0 else 'alipay'
    c.execute('INSERT INTO "order" (order_no, user_id, total_amount, final_amount, payment_method, payment_status, paid_at) VALUES (?, ?, ?, ?, ?, ?, ?)',
              (order_no, session['user_id'], price, price, payment_method, 'paid', datetime.now()))
    order_id = c.lastrowid
    c.execute('INSERT INTO order_item (order_id, course_id, price) VALUES (?, ?, ?)', (order_id, course_id, price))
    c.execute('SELECT COUNT(*) as total FROM lesson l JOIN chapter ch ON l.chapter_id = ch.chapter_id WHERE ch.course_id = ?', (course_id,))
    total_lessons = c.fetchone()['total']
    c.execute('INSERT INTO enrollment (user_id, course_id, order_id, total_lessons) VALUES (?, ?, ?, ?)', (session['user_id'], course_id, order_id, total_lessons))
    c.execute('UPDATE course SET enrollment_count = enrollment_count + 1 WHERE course_id = ?', (course_id,))
    conn.commit()
    conn.close()
    flash('Enrollment successful! Start learning!', 'success')
    return redirect(url_for('learn', course_id=course_id))

@app.route('/learn/<int:course_id>')
@login_required
def learn(course_id):
    conn = get_db()
    c = conn.cursor()
    c.execute('SELECT * FROM enrollment WHERE user_id = ? AND course_id = ?', (session['user_id'], course_id))
    enrollment = c.fetchone()
    if not enrollment:
        flash('Please enroll first', 'warning')
        return redirect(url_for('course_detail', course_id=course_id))
    c.execute('SELECT * FROM course WHERE course_id = ?', (course_id,))
    course = c.fetchone()
    c.execute('''SELECT ch.chapter_id, ch.title as chapter_title, ch.sort_order as chapter_order,
        l.lesson_id, l.title as lesson_title, l.content_type, l.video_url, l.video_duration, l.sort_order as lesson_order
        FROM chapter ch LEFT JOIN lesson l ON ch.chapter_id = l.chapter_id WHERE ch.course_id = ? ORDER BY ch.sort_order, l.sort_order''', (course_id,))
    rows = c.fetchall()
    chapters = {}
    for row in rows:
        ch_id = row['chapter_id']
        if ch_id not in chapters:
            chapters[ch_id] = {'chapter_id': ch_id, 'title': row['chapter_title'], 'lessons': []}
        if row['lesson_id']:
            chapters[ch_id]['lessons'].append({'lesson_id': row['lesson_id'], 'title': row['lesson_title'], 'content_type': row['content_type'], 'video_url': row['video_url'], 'video_duration': row['video_duration']})
    c.execute('SELECT lesson_id, is_completed, progress_percent FROM learning_progress WHERE user_id = ?', (session['user_id'],))
    progress_data = {row['lesson_id']: row for row in c.fetchall()}
    lesson_id = request.args.get('lesson', type=int)
    current_lesson = None
    if lesson_id:
        c.execute('SELECT * FROM lesson WHERE lesson_id = ?', (lesson_id,))
        current_lesson = c.fetchone()
    c.execute('UPDATE enrollment SET last_accessed_at = ? WHERE user_id = ? AND course_id = ?', (datetime.now(), session['user_id'], course_id))
    conn.commit()
    conn.close()
    return render_template('learn.html', course=course, chapters=list(chapters.values()), current_lesson=current_lesson, progress_data=progress_data, enrollment=enrollment)

# 课程管理 CRUD
@app.route('/admin/courses')
@login_required
def admin_courses():
    if 'instructor' not in session.get('roles', []) and 'admin' not in session.get('roles', []):
        flash('Access denied', 'error')
        return redirect(url_for('index'))
    conn = get_db()
    c = conn.cursor()
    if 'admin' in session.get('roles', []):
        c.execute('SELECT c.*, u.username as instructor_name, cat.category_name FROM course c LEFT JOIN user u ON c.instructor_id = u.user_id LEFT JOIN category cat ON c.category_id = cat.category_id ORDER BY c.created_at DESC')
    else:
        c.execute('SELECT c.*, u.username as instructor_name, cat.category_name FROM course c LEFT JOIN user u ON c.instructor_id = u.user_id LEFT JOIN category cat ON c.category_id = cat.category_id WHERE c.instructor_id = ? ORDER BY c.created_at DESC', (session['user_id'],))
    courses_list = c.fetchall()
    conn.close()
    return render_template('admin/courses.html', courses=courses_list)

@app.route('/admin/course/create', methods=['GET', 'POST'])
@login_required
def create_course():
    if 'instructor' not in session.get('roles', []) and 'admin' not in session.get('roles', []):
        flash('Access denied', 'error')
        return redirect(url_for('index'))
    conn = get_db()
    c = conn.cursor()
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        subtitle = request.form.get('subtitle', '').strip()
        description = request.form.get('description', '').strip()
        category_id = request.form.get('category_id', type=int)
        price = request.form.get('price', type=float) or 0
        original_price = request.form.get('original_price', type=float) or price
        level = request.form.get('level', 'beginner')
        if not title:
            flash('Please enter course title', 'error')
        else:
            c.execute('INSERT INTO course (title, subtitle, description, instructor_id, category_id, price, original_price, level, status) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)',
                      (title, subtitle, description, session['user_id'], category_id, price, original_price, level, 'draft'))
            conn.commit()
            flash('Course created successfully', 'success')
            return redirect(url_for('admin_courses'))
    c.execute('SELECT * FROM category ORDER BY parent_id, sort_order')
    categories = c.fetchall()
    conn.close()
    return render_template('admin/course_form.html', course=None, categories=categories)

@app.route('/admin/course/<int:course_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_course(course_id):
    conn = get_db()
    c = conn.cursor()
    c.execute('SELECT * FROM course WHERE course_id = ?', (course_id,))
    course = c.fetchone()
    if not course:
        flash('Course not found', 'error')
        return redirect(url_for('admin_courses'))
    if 'admin' not in session.get('roles', []) and course['instructor_id'] != session['user_id']:
        flash('No permission to edit this course', 'error')
        return redirect(url_for('admin_courses'))
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        subtitle = request.form.get('subtitle', '').strip()
        description = request.form.get('description', '').strip()
        category_id = request.form.get('category_id', type=int)
        price = request.form.get('price', type=float) or 0
        original_price = request.form.get('original_price', type=float) or price
        level = request.form.get('level', 'beginner')
        status = request.form.get('status', 'draft')
        c.execute('UPDATE course SET title = ?, subtitle = ?, description = ?, category_id = ?, price = ?, original_price = ?, level = ?, status = ? WHERE course_id = ?',
                  (title, subtitle, description, category_id, price, original_price, level, status, course_id))
        if status == 'published' and not course['published_at']:
            c.execute('UPDATE course SET published_at = ? WHERE course_id = ?', (datetime.now(), course_id))
        conn.commit()
        flash('Course updated', 'success')
        return redirect(url_for('admin_courses'))
    c.execute('SELECT * FROM category ORDER BY parent_id, sort_order')
    categories = c.fetchall()
    conn.close()
    return render_template('admin/course_form.html', course=course, categories=categories)

@app.route('/admin/course/<int:course_id>/delete', methods=['POST'])
@login_required
def delete_course(course_id):
    conn = get_db()
    c = conn.cursor()
    c.execute('SELECT * FROM course WHERE course_id = ?', (course_id,))
    course = c.fetchone()
    if not course:
        flash('Course not found', 'error')
        return redirect(url_for('admin_courses'))
    if 'admin' not in session.get('roles', []) and course['instructor_id'] != session['user_id']:
        flash('No permission to delete this course', 'error')
        return redirect(url_for('admin_courses'))
    c.execute('SELECT COUNT(*) as count FROM enrollment WHERE course_id = ?', (course_id,))
    if c.fetchone()['count'] > 0:
        flash('Cannot delete course with enrolled students', 'error')
        return redirect(url_for('admin_courses'))
    c.execute('DELETE FROM course WHERE course_id = ?', (course_id,))
    conn.commit()
    conn.close()
    flash('Course deleted', 'success')
    return redirect(url_for('admin_courses'))

# SQL查询演示
@app.route('/demo/queries')
def demo_queries():
    conn = get_db()
    c = conn.cursor()
    queries = {}
    c.execute('SELECT course_id, title, price, level, rating_avg, enrollment_count FROM course WHERE price > 100 AND status = "published" ORDER BY rating_avg DESC')
    queries['single_table'] = {'title': '单表查询 - 价格>100的已发布课程', 'sql': "SELECT ... FROM course WHERE price > 100 AND status = 'published'", 'result': c.fetchall()}
    c.execute('SELECT c.title, c.price, u.username as instructor, cat.category_name FROM course c INNER JOIN user u ON c.instructor_id = u.user_id INNER JOIN category cat ON c.category_id = cat.category_id WHERE c.status = "published"')
    queries['inner_join'] = {'title': '内连接 - 课程与讲师、分类', 'sql': "SELECT ... FROM course c INNER JOIN user u ... INNER JOIN category cat ...", 'result': c.fetchall()}
    c.execute('SELECT c.title, c.price, COUNT(r.review_id) as review_count FROM course c LEFT JOIN review r ON c.course_id = r.course_id WHERE c.status = "published" GROUP BY c.course_id')
    queries['left_join'] = {'title': '左外连接 - 课程及评价数量', 'sql': "SELECT ... FROM course c LEFT JOIN review r ... GROUP BY ...", 'result': c.fetchall()}
    c.execute('SELECT c.category_name as category, COALESCE(p.category_name, "顶级分类") as parent FROM category c LEFT JOIN category p ON c.parent_id = p.category_id')
    queries['self_join'] = {'title': '自连接 - 分类层级关系', 'sql': "SELECT c.category_name, p.category_name FROM category c LEFT JOIN category p ON c.parent_id = p.category_id", 'result': c.fetchall()}
    c.execute('SELECT u.username, COUNT(c.course_id) as course_count, SUM(c.enrollment_count) as total_students, ROUND(AVG(c.rating_avg), 2) as avg_rating FROM user u JOIN course c ON u.user_id = c.instructor_id WHERE c.status = "published" GROUP BY u.user_id ORDER BY total_students DESC')
    queries['aggregate'] = {'title': '聚合函数 - 讲师统计', 'sql': "SELECT ... COUNT(), SUM(), AVG() ... GROUP BY ... ORDER BY ...", 'result': c.fetchall()}
    c.execute('SELECT DATE(created_at) as order_date, COUNT(*) as order_count, SUM(final_amount) as daily_revenue FROM "order" WHERE payment_status = "paid" GROUP BY DATE(created_at) ORDER BY order_date DESC')
    queries['date_functions'] = {'title': '日期函数 - 按日订单统计', 'sql': "SELECT DATE(created_at), COUNT(*), SUM() ... GROUP BY DATE(created_at)", 'result': c.fetchall()}
    c.execute('SELECT title, price, enrollment_count FROM course WHERE enrollment_count > (SELECT AVG(enrollment_count) FROM course WHERE status = "published") AND status = "published"')
    queries['subquery'] = {'title': '子查询 - 报名数超过平均值的课程', 'sql': "SELECT ... WHERE enrollment_count > (SELECT AVG(...) ...)", 'result': c.fetchall()}
    c.execute('SELECT c.title, c.rating_avg, cat.category_name FROM course c JOIN category cat ON c.category_id = cat.category_id WHERE c.rating_avg = (SELECT MAX(c2.rating_avg) FROM course c2 WHERE c2.category_id = c.category_id AND c2.status = "published") AND c.status = "published"')
    queries['correlated_subquery'] = {'title': '相关子查询 - 每个分类评分最高的课程', 'sql': "SELECT ... WHERE rating_avg = (SELECT MAX(...) WHERE c2.category_id = c.category_id ...)", 'result': c.fetchall()}
    c.execute('SELECT c.title, "已购买" as source FROM course c JOIN enrollment e ON c.course_id = e.course_id WHERE e.user_id = 1 UNION SELECT c.title, "已收藏" as source FROM course c JOIN favorite f ON c.course_id = f.course_id WHERE f.user_id = 1')
    queries['union'] = {'title': 'UNION - 用户1的收藏和已购课程', 'sql': "SELECT ... UNION SELECT ...", 'result': c.fetchall()}
    c.execute('SELECT u.username, c.title, e.progress_percent, cat.category_name, inst.username as instructor FROM user u JOIN enrollment e ON u.user_id = e.user_id JOIN course c ON e.course_id = c.course_id LEFT JOIN category cat ON c.category_id = cat.category_id JOIN user inst ON c.instructor_id = inst.user_id WHERE u.user_id = 1')
    queries['multi_join'] = {'title': '多表连接 - 用户学习报告', 'sql': "SELECT ... FROM user u JOIN enrollment e JOIN course c LEFT JOIN category cat JOIN user inst ...", 'result': c.fetchall()}
    c.execute('SELECT u.user_id, u.username, COUNT(DISTINCT e.course_id) as completed_courses FROM user u JOIN enrollment e ON u.user_id = e.user_id JOIN course c ON e.course_id = c.course_id WHERE c.instructor_id = 3 AND c.status = "published" AND e.status = "completed" GROUP BY u.user_id HAVING completed_courses = (SELECT COUNT(*) FROM course WHERE instructor_id = 3 AND status = "published")')
    queries['division'] = {'title': '除法查询 - 学完讲师3所有课程的学员', 'sql': "SELECT ... HAVING completed_courses = (SELECT COUNT(*) ...)", 'result': c.fetchall()}
    conn.close()
    return render_template('demo_queries.html', queries=queries)

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

if __name__ == '__main__':
    init_db()
    app.run(debug=True, host='0.0.0.0', port=5000)