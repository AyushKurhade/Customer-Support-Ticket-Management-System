"""
One-Click College Lab Database & System Setup Script
====================================================
Run this script on any college lab computer to automatically:
 1. Verify MySQL connection (XAMPP / WAMP / Standalone MySQL)
 2. Create the database 'support_ticket_db'
 3. Execute all tables, master seed data, views, functions, stored procedures, and triggers
 4. Verify AI classification model artifact
"""

import os
import sys
from pathlib import Path
import pymysql
from dotenv import load_dotenv

# Load environment variables
base_dir = Path(__file__).resolve().parent
load_dotenv(base_dir / ".env")

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = int(os.getenv("DB_PORT", 3306))
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_NAME = os.getenv("DB_NAME", "support_ticket_db")

print("=" * 70)
print("CUSTOMER SUPPORT TICKET SYSTEM - ONE-CLICK LAB SETUP")
print("=" * 70)
print(f"Target Database Server: {DB_USER}@{DB_HOST}:{DB_PORT}")
print(f"Database Name:          {DB_NAME}")
print("=" * 70)

# Step 1: Connect to MySQL Server (without selecting database initially)
print("\n[1/5] Connecting to MySQL Server...")
try:
    conn = pymysql.connect(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PASSWORD,
        autocommit=True,
        client_flag=pymysql.constants.CLIENT.MULTI_STATEMENTS
    )
    cursor = conn.cursor()
    print("      Connected successfully to MySQL engine.")
except Exception as e:
    print(f"\n[ERROR] Could not connect to MySQL server at {DB_HOST}:{DB_PORT}.")
    print(f"Details: {e}")
    print("\nTroubleshooting Tips:")
    print(" 1. Make sure XAMPP or MySQL service is started (Port 3306).")
    print(" 2. If MySQL root has a password in your lab, update DB_PASSWORD in the .env file.")
    sys.exit(1)

# Step 2: Create Database
print(f"\n[2/5] Creating database '{DB_NAME}'...")
cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{DB_NAME}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;")
cursor.execute(f"USE `{DB_NAME}`;")
print(f"      Database '{DB_NAME}' is ready.")

# Helper to execute multi-statement SQL script cleanly
def execute_sql_file(file_path, step_name):
    print(f"      Applying: {file_path.name} ({step_name})...")
    if not file_path.exists():
        print(f"      [WARNING] File not found: {file_path}")
        return
    
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Split by custom delimiter if procedures/triggers use DELIMITER //
    if "DELIMITER //" in content:
        # Split on DELIMITER statements
        parts = content.split("DELIMITER //")
        # Run initial part before first DELIMITER
        initial_sql = parts[0].strip()
        if initial_sql:
            for stmt in initial_sql.split(";"):
                stmt = stmt.strip()
                if stmt:
                    cursor.execute(stmt)
        # Run middle parts
        for part in parts[1:]:
            if "DELIMITER ;" in part:
                routine_code, rest = part.split("DELIMITER ;", 1)
                for r in routine_code.split("//"):
                    r = r.strip()
                    if r:
                        cursor.execute(r)
                if rest.strip():
                    for stmt in rest.split(";"):
                        stmt = stmt.strip()
                        if stmt:
                            cursor.execute(stmt)
            else:
                for r in part.split("//"):
                    r = r.strip()
                    if r:
                        cursor.execute(r)
    else:
        # Standard multi-statement execution
        for stmt in content.split(";"):
            stmt = stmt.strip()
            if stmt:
                cursor.execute(stmt)

# Step 3: Run Database Scripts in Strict Dependency Order
print("\n[3/5] Applying Schema, Master Seeds, Views, Functions, Procedures & Triggers...")
sql_steps = [
    (base_dir / "database" / "schema" / "schema.sql", "Core 3NF Relational Tables"),
    (base_dir / "database" / "seed" / "01_seed_master_data.sql", "Master Seed Users & Categories"),
    (base_dir / "database" / "views" / "01_create_views.sql", "Operational Database Views"),
    (base_dir / "database" / "functions" / "01_create_functions.sql", "Scalar Deterministic Functions"),
    (base_dir / "database" / "procedures" / "01_create_procedures.sql", "Transactional Stored Procedures"),
    (base_dir / "database" / "triggers" / "01_create_triggers.sql", "Automated History & Timestamp Triggers")
]

for script_path, label in sql_steps:
    execute_sql_file(script_path, label)

# Step 4: Verify Tables & Seed Counts
print("\n[4/5] Verifying Database Objects...")
cursor.execute("SHOW TABLES;")
tables = [r[0] for r in cursor.fetchall()]
print(f"      Total tables created: {len(tables)} ({', '.join(tables)})")

cursor.execute("SELECT COUNT(*) FROM Users;")
user_count = cursor.fetchone()[0]
cursor.execute("SELECT COUNT(*) FROM Categories;")
cat_count = cursor.fetchone()[0]
cursor.execute("SELECT COUNT(*) FROM Priorities;")
prio_count = cursor.fetchone()[0]
cursor.execute("SELECT COUNT(*) FROM Tickets;")
ticket_count = cursor.fetchone()[0]

print(f"      Database Record Counts:")
print(f"       - Users:      {user_count} accounts")
print(f"       - Categories: {cat_count} categories")
print(f"       - Priorities: {prio_count} SLA priority tiers")
print(f"       - Tickets:    {ticket_count} active & historical tickets")

# Step 5: Check AI Model Artifact
print("\n[5/5] Checking AI / NLP Model Artifact...")
model_file = base_dir / "ai" / "models" / "ticket_classifier.joblib"
if model_file.exists():
    print(f"      AI model artifact found ({model_file.stat().st_size / 1024:.1f} KB). Ready for live triage.")
else:
    print("      AI model artifact not found. Training model now...")
    from ai.training.train_model import train_and_save_model
    train_and_save_model()

conn.close()

print("\n" + "=" * 70)
print("SUCCESS! COLLEGE LAB SETUP COMPLETED IN SECONDS!")
print("=" * 70)
print("You can now launch the application:")
print("  python -m backend.app")
print("\nThen open your browser at:")
print("  http://localhost:5000/")
print("=" * 70)
