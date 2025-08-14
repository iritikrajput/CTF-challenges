# app.py
from flask import Flask, request, jsonify, render_template, session, redirect, url_for
import sqlite3
import os
import hashlib
import time
from datetime import datetime
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

# CTF Flags
FLAGS = {
    'level1': 'CTF{b4s1c_4uth_byp4ss_w1th_0r}',
    'level2': 'CTF{un10n_s3l3ct_d4t4_3xtr4ct10n}',
    'level3': 'CTF{bl1nd_1nj3ct10n_t1m3_b4s3d}',
    'level4': 'CTF{4dv4nc3d_sch3m4_d1sc0v3ry}'
}

DATABASE = 'ctf_lab.db'

def get_db_connection():
    """Create SQLite database connection with logging"""
    try:
        connection = sqlite3.connect(DATABASE)
        connection.row_factory = sqlite3.Row
        return connection
    except sqlite3.Error as e:
        app.logger.error(f"Database connection error: {e}")
        return None

def log_attempt(level, payload, success, ip_address):
    """Log CTF attempts for monitoring"""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    log_entry = f"[{timestamp}] Level-{level} | IP: {ip_address} | Success: {success} | Payload: {payload[:100]}\n"
    
    with open('ctf_attempts.log', 'a') as f:
        f.write(log_entry)

@app.route('/')
def index():
    """Main CTF lab page"""
    return render_template('index.html')

@app.route('/setup')
def setup_database():
    """Initialize CTF database with challenges"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Users table for basic challenges
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                email TEXT NOT NULL,
                password TEXT NOT NULL,
                role TEXT DEFAULT 'user',
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Admin table for advanced challenges
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS admin_users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                admin_name TEXT UNIQUE NOT NULL,
                admin_pass TEXT NOT NULL,
                secret_data TEXT NOT NULL,
                clearance_level INTEGER DEFAULT 1
            )
        ''')
        
        # Secrets table for flag storage
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS secrets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                secret_name TEXT NOT NULL,
                secret_value TEXT NOT NULL,
                access_level INTEGER NOT NULL
            )
        ''')
        
        # Insert test users
        users_data = [
            ('admin', 'admin@ctf.lab', 'admin123', 'admin'),
            ('user', 'user@ctf.lab', 'password', 'user'),
            ('john', 'john@ctf.lab', 'john123', 'user'),
            ('alice', 'alice@ctf.lab', 'secret456', 'user'),
            ('bob', 'bob@ctf.lab', 'bob789', 'user')
        ]
        
        cursor.executemany(
            'INSERT OR IGNORE INTO users (username, email, password, role) VALUES (?, ?, ?, ?)',
            users_data
        )
        
        # Insert admin users
        admin_data = [
            ('superadmin', 'sup3r_s3cr3t_p4ss', FLAGS['level4'], 5),
            ('ctf_admin', 'ctf_p4ssw0rd!', 'Hidden admin data', 3)
        ]
        
        cursor.executemany(
            'INSERT OR IGNORE INTO admin_users (admin_name, admin_pass, secret_data, clearance_level) VALUES (?, ?, ?, ?)',
            admin_data
        )
        
        # Insert flags as secrets
        secrets_data = [
            ('level1_flag', FLAGS['level1'], 1),
            ('level2_flag', FLAGS['level2'], 2),
            ('level3_flag', FLAGS['level3'], 3),
            ('level4_flag', FLAGS['level4'], 4),
            ('bonus_flag', 'CTF{y0u_f0und_th3_b0nus!}', 5)
        ]
        
        cursor.executemany(
            'INSERT OR IGNORE INTO secrets (secret_name, secret_value, access_level) VALUES (?, ?, ?)',
            secrets_data
        )
        
        conn.commit()
        return jsonify({
            'message': 'CTF Lab database initialized successfully!',
            'challenges': 4,
            'flags_hidden': len(FLAGS)
        })
        
    except Exception as e:
        return jsonify({'error': f'Setup failed: {str(e)}'}), 500
    finally:
        if conn:
            conn.close()

@app.route('/level1', methods=['GET', 'POST'])
def level1_basic_bypass():
    """Level 1: Basic Authentication Bypass"""
    if request.method == 'GET':
        return render_template('index.html', level=1, 
                             challenge="Basic Authentication Bypass",
                             hint="Try using SQL comments to bypass the password check")
    
    data = request.get_json()
    username = data.get('username', '')
    password = data.get('password', '')
    client_ip = request.remote_addr
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # VULNERABLE QUERY - Level 1
    query = f"SELECT * FROM users WHERE username = '{username}' AND password = '{password}'"
    
    try:
        cursor.execute(query)
        results = cursor.fetchall()
        
        # Check for successful bypass
        success = len(results) > 0
        log_attempt(1, username, success, client_ip)
        
        if success:
            if "OR" in username.upper() and "--" in username:
                return jsonify({
                    'success': True,
                    'message': 'Level 1 Completed! 🎉',
                    'flag': FLAGS['level1'],
                    'query_executed': query,
                    'technique': 'Authentication Bypass using OR condition'
                })
            else:
                return jsonify({
                    'success': True,
                    'message': 'Login successful, but this is not the intended solution.',
                    'hint': 'Try bypassing authentication without knowing the password'
                })
        else:
            return jsonify({
                'success': False,
                'message': 'Invalid credentials',
                'hint': 'Use SQL injection to bypass authentication'
            })
            
    except Exception as e:
        log_attempt(1, username, False, client_ip)
        return jsonify({'error': str(e), 'query': query}), 500
    finally:
        conn.close()

@app.route('/level2', methods=['GET', 'POST'])
def level2_union_select():
    """Level 2: UNION SELECT Data Extraction"""
    if request.method == 'GET':
        return render_template('index.html', level=2,
                             challenge="UNION SELECT Data Extraction",
                             hint="Extract data from the secrets table using UNION")
    
    data = request.get_json()
    username = data.get('username', '')
    password = data.get('password', '')
    client_ip = request.remote_addr
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # VULNERABLE QUERY - Level 2
    query = f"SELECT id, username, email FROM users WHERE username = '{username}' AND password = '{password}'"
    
    try:
        cursor.execute(query)
        results = cursor.fetchall()
        
        # Check for UNION SELECT in query
        if "UNION" in username.upper() and "secrets" in username.lower():
            log_attempt(2, username, True, client_ip)
            return jsonify({
                'success': True,
                'message': 'Level 2 Completed! 🎉',
                'flag': FLAGS['level2'],
                'query_executed': query,
                'technique': 'UNION SELECT data extraction',
                'data': [dict(row) for row in results]
            })
        elif len(results) > 0:
            return jsonify({
                'success': True,
                'message': 'Login successful, but try extracting data from other tables',
                'hint': 'Use UNION SELECT to access the secrets table'
            })
        else:
            return jsonify({
                'success': False,
                'message': 'No data found',
                'hint': 'Try using UNION SELECT to extract data from secrets table'
            })
            
    except Exception as e:
        # Check if error reveals successful injection
        if "secrets" in str(e).lower():
            log_attempt(2, username, True, client_ip)
        return jsonify({'error': str(e), 'query': query}), 500
    finally:
        conn.close()

@app.route('/level3', methods=['GET', 'POST'])
def level3_blind_injection():
    """Level 3: Time-based Blind SQL Injection"""
    if request.method == 'GET':
        return render_template('index.html', level=3,
                             challenge="Time-based Blind SQL Injection",
                             hint="Use time delays to extract data blindly")
    
    data = request.get_json()
    username = data.get('username', '')
    client_ip = request.remote_addr
    
    start_time = time.time()
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # VULNERABLE QUERY - Level 3 (only username field)
    query = f"SELECT COUNT(*) FROM users WHERE username = '{username}'"
    
    try:
        cursor.execute(query)
        result = cursor.fetchone()
        
        execution_time = time.time() - start_time
        
        # Check for time-based injection
        if execution_time > 2 and ("CASE" in username.upper() or "SLEEP" in username.upper()):
            log_attempt(3, username, True, client_ip)
            return jsonify({
                'success': True,
                'message': 'Level 3 Completed! 🎉',
                'flag': FLAGS['level3'],
                'query_executed': query,
                'execution_time': f"{execution_time:.2f} seconds",
                'technique': 'Time-based blind SQL injection'
            })
        else:
            return jsonify({
                'success': False,
                'message': f'Query executed in {execution_time:.2f} seconds',
                'hint': 'Try using time delays to extract information blindly',
                'count': result[0] if result else 0
            })
            
    except Exception as e:
        execution_time = time.time() - start_time
        if execution_time > 2:
            log_attempt(3, username, True, client_ip)
        return jsonify({'error': str(e), 'execution_time': f"{execution_time:.2f}s"}), 500
    finally:
        conn.close()

@app.route('/level4', methods=['GET', 'POST'])
def level4_advanced_schema():
    """Level 4: Advanced Schema Discovery"""
    if request.method == 'GET':
        return render_template('index.html', level=4,
                             challenge="Advanced Schema Discovery",
                             hint="Discover and access the admin_users table")
    
    data = request.get_json()
    search_term = data.get('search', '')
    client_ip = request.remote_addr
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # VULNERABLE QUERY - Level 4
    query = f"SELECT username, email FROM users WHERE username LIKE '%{search_term}%'"
    
    try:
        cursor.execute(query)
        results = cursor.fetchall()
        
        # Check for advanced schema discovery
        if ("sqlite_master" in search_term.lower() or 
            "admin_users" in search_term.lower() or
            ("UNION" in search_term.upper() and "admin" in search_term.lower())):
            
            log_attempt(4, search_term, True, client_ip)
            return jsonify({
                'success': True,
                'message': 'Level 4 Completed! 🎉',
                'flag': FLAGS['level4'],
                'query_executed': query,
                'technique': 'Advanced schema discovery and data extraction',
                'data': [dict(row) for row in results]
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Search completed',
                'results': [dict(row) for row in results],
                'hint': 'Try discovering hidden tables in the database'
            })
            
    except Exception as e:
        if any(word in str(e).lower() for word in ['admin_users', 'sqlite_master']):
            log_attempt(4, search_term, True, client_ip)
        return jsonify({'error': str(e), 'query': query}), 500
    finally:
        conn.close()

@app.route('/dashboard')
def dashboard():
    """CTF Dashboard showing progress"""
    return render_template('dashboard.html')

@app.route('/guide')
def ctf_guide():
    """CTF guidance and hints"""
    return render_template('ctf_guide.html')

@app.route('/leaderboard')
def leaderboard():
    """Show CTF completion statistics"""
    try:
        with open('ctf_attempts.log', 'r') as f:
            attempts = f.readlines()
        
        stats = {
            'total_attempts': len(attempts),
            'successful_attempts': len([a for a in attempts if 'Success: True' in a]),
            'level_stats': {
                'level1': len([a for a in attempts if 'Level-1' in a and 'Success: True' in a]),
                'level2': len([a for a in attempts if 'Level-2' in a and 'Success: True' in a]),
                'level3': len([a for a in attempts if 'Level-3' in a and 'Success: True' in a]),
                'level4': len([a for a in attempts if 'Level-4' in a and 'Success: True' in a])
            }
        }
        
        return jsonify(stats)
    except FileNotFoundError:
        return jsonify({'message': 'No attempts logged yet'})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
