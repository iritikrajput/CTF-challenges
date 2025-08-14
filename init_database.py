# init_database.py
import sqlite3
import os

def initialize_database():
    """Initialize the CTF database with all required tables and data"""
    
    DATABASE = 'ctf_lab.db'
    
    # Remove existing database
    if os.path.exists(DATABASE):
        os.remove(DATABASE)
    
    # Create new database
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    try:
        # Create users table
        cursor.execute('''
            CREATE TABLE users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                email TEXT NOT NULL,
                password TEXT NOT NULL,
                role TEXT DEFAULT 'user',
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create admin_users table
        cursor.execute('''
            CREATE TABLE admin_users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                admin_name TEXT UNIQUE NOT NULL,
                admin_pass TEXT NOT NULL,
                secret_data TEXT NOT NULL,
                clearance_level INTEGER DEFAULT 1
            )
        ''')
        
        # Create secrets table
        cursor.execute('''
            CREATE TABLE secrets (
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
            ('bob', 'bob@ctf.lab', 'bob789', 'user'),
            ('charlie', 'charlie@ctf.lab', 'charlie321', 'user'),
            ('diana', 'diana@ctf.lab', 'diana654', 'user'),
        ]
        
        cursor.executemany(
            'INSERT INTO users (username, email, password, role) VALUES (?, ?, ?, ?)',
            users_data
        )
        
        # Insert admin users
        admin_data = [
            ('superadmin', 'sup3r_s3cr3t_p4ss', 'CTF{4dv4nc3d_sch3m4_d1sc0v3ry}', 5),
            ('ctf_admin', 'ctf_p4ssw0rd!', 'Hidden admin data for level 4', 3),
            ('database_admin', 'db_4dm1n_p4ss', 'Database configuration secrets', 4),
        ]
        
        cursor.executemany(
            'INSERT INTO admin_users (admin_name, admin_pass, secret_data, clearance_level) VALUES (?, ?, ?, ?)',
            admin_data
        )
        
        # Insert secrets/flags
        secrets_data = [
            ('level1_flag', 'CTF{b4s1c_4uth_byp4ss_w1th_0r}', 1),
            ('level2_flag', 'CTF{un10n_s3l3ct_d4t4_3xtr4ct10n}', 2),
            ('level3_flag', 'CTF{bl1nd_1nj3ct10n_t1m3_b4s3d}', 3),
            ('level4_flag', 'CTF{4dv4nc3d_sch3m4_d1sc0v3ry}', 4),
            ('bonus_flag', 'CTF{y0u_f0und_th3_b0nus!}', 5),
            ('secret_key', 'S3cr3t_K3y_F0r_CTF_L4b', 3),
            ('api_token', 'CTF_API_T0K3N_2024', 2),
            ('master_password', 'M4st3r_P4ssw0rd_H1dd3n', 4),
        ]
        
        cursor.executemany(
            'INSERT INTO secrets (secret_name, secret_value, access_level) VALUES (?, ?, ?)',
            secrets_data
        )
        
        # Create additional tables for advanced challenges
        cursor.execute('''
            CREATE TABLE system_config (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                config_name TEXT NOT NULL,
                config_value TEXT NOT NULL,
                is_sensitive INTEGER DEFAULT 0
            )
        ''')
        
        config_data = [
            ('database_version', 'SQLite 3.39.0', 0),
            ('encryption_key', 'CTF{h1dd3n_c0nf1g_d4t4}', 1),
            ('debug_mode', 'enabled', 0),
            ('admin_email', 'admin@vulnerable-ctf.local', 0),
        ]
        
        cursor.executemany(
            'INSERT INTO system_config (config_name, config_value, is_sensitive) VALUES (?, ?, ?)',
            config_data
        )
        
        conn.commit()
        print("✅ CTF Database initialized successfully!")
        print(f"📊 Created {len(users_data)} users")
        print(f"👑 Created {len(admin_data)} admin users")
        print(f"🚩 Created {len(secrets_data)} secrets/flags")
        print(f"⚙️ Created {len(config_data)} config entries")
        
    except Exception as e:
        print(f"❌ Error initializing database: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    initialize_database()
