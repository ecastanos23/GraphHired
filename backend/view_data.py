import sqlite3

conn = sqlite3.connect('graphhired.db')
cursor = conn.cursor()

# List tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = [t[0] for t in cursor.fetchall()]
print("=== TABLAS EN LA BASE DE DATOS ===")
print(tables)

# Show candidates
print("\n=== CANDIDATOS ===")
cursor.execute("SELECT id, email, full_name, expected_salary, work_modality, location FROM candidates")
for row in cursor.fetchall():
    print(f"ID: {row[0]}, Email: {row[1]}, Nombre: {row[2]}, Salario: {row[3]}, Modalidad: {row[4]}, Ubicación: {row[5]}")

# Show logs
print("\n=== LOGS (PoC) ===")
cursor.execute("SELECT id, input_text, output_text FROM logs LIMIT 5")
for row in cursor.fetchall():
    print(f"ID: {row[0]}, Input: {row[1]}, Output: {row[2]}")

conn.close()
