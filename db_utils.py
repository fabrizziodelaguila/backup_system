# backend/db_utils.py
from cryptography.fernet import Fernet
import os
import json
import pyodbc

SERVER = 'serverxd.database.windows.net' # Cambia esto por tu servidor real
DATABASE = 'SQLXD' 
USERNAME = 'xadmin' # Cambia esto por tu nombre de usuario real
PASSWORD = 'Mortadela1' # Cambia esto por tu contraseña real

def generate_key():
    return Fernet.generate_key()

def load_key():
    return open("secret.key", "rb").read()

def make_backup(year, month, path):
    filename = f'backup_{year}_{month}.json'
    full_path = os.path.join(path, filename)

    conn_str = (
        f"DRIVER={{ODBC Driver 17 for SQL Server}};"
        f"SERVER={SERVER};"
        f"DATABASE={DATABASE};"
    )
    conn_str += f"UID={USERNAME};PWD={PASSWORD};" if USERNAME and PASSWORD else "Trusted_Connection=yes;"
    conn = pyodbc.connect(conn_str)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT * FROM comprobante
        WHERE YEAR(fec_comp) = ? AND MONTH(fec_comp) = ?
    """, (year, month))

    columns = [desc[0] for desc in cursor.description]
    rows = cursor.fetchall()

    if not rows:
        conn.close()
        raise ValueError("No hay datos en esa fecha para realizar el backup.")
        
    data = [dict(zip(columns, row)) for row in rows]
    key = load_key()
    f = Fernet(key)

    json_data = json.dumps(data, indent=4, default=str)
    encrypted_data = f.encrypt(json_data.encode())

    with open(full_path, 'wb') as f_encrypted:
        f_encrypted.write(encrypted_data)

    conn.close()
    return filename

def get_backup_list(path):
    if not os.path.exists(path):
        return []
    return [f for f in os.listdir(path) if f.endswith('.json')]

def delete_backup(filename, path):
    filepath = os.path.join(path, filename)
    if os.path.exists(filepath):
        os.remove(filepath)
        return True
    return False

def create_est_comp_trigger():
    conn_str = (
        f"DRIVER={{ODBC Driver 17 for SQL Server}};"
        f"SERVER={SERVER};"
        f"DATABASE={DATABASE};"
    )
    conn_str += f"UID={USERNAME};PWD={PASSWORD};" if USERNAME and PASSWORD else "Trusted_Connection=yes;"
    conn = pyodbc.connect(conn_str)
    cursor = conn.cursor()

    cursor.execute("""
    IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='log_est_comp_changes' AND xtype='U')
    CREATE TABLE log_est_comp_changes (
        id INT IDENTITY PRIMARY KEY,
        id_comp INT,
        old_est_comp VARCHAR(50),
        new_est_comp VARCHAR(50),
        changed_by SYSNAME,
        changed_at DATETIME DEFAULT GETDATE()
    )
    """)
    conn.commit()

    cursor.execute("""
    IF NOT EXISTS (
        SELECT * FROM sys.triggers WHERE name = 'trg_est_comp_change'
    )
    EXEC('
    CREATE TRIGGER trg_est_comp_change
    ON comprobante
    AFTER UPDATE
    AS
    BEGIN
        SET NOCOUNT ON;
        IF UPDATE(est_comp)
        BEGIN
            INSERT INTO log_est_comp_changes (id_comp, old_est_comp, new_est_comp, changed_by)
            SELECT 
                i.id_comp,
                d.est_comp,
                i.est_comp,
                SYSTEM_USER
            FROM inserted i
            INNER JOIN deleted d ON i.id_comp = d.id_comp
            WHERE i.est_comp <> d.est_comp;
        END
    END
    ')
    """)
    conn.commit()
    conn.close()
    print("✅ Trigger creado o ya existente.")

def update_est_comp_to_I():
    conn_str = (
        f"DRIVER={{ODBC Driver 17 for SQL Server}};"
        f"SERVER={SERVER};"
        f"DATABASE={DATABASE};"
    )
    conn_str += f"UID={USERNAME};PWD={PASSWORD};" if USERNAME and PASSWORD else "Trusted_Connection=yes;"
    conn = pyodbc.connect(conn_str)
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE comprobante
        SET est_comp = 'I'
        WHERE est_comp = 'A'
    """)
    conn.commit()
    rows = cursor.rowcount
    conn.close()
    return rows

def get_est_comp_logs():
    conn_str = (
        f"DRIVER={{ODBC Driver 17 for SQL Server}};"
        f"SERVER={SERVER};"
        f"DATABASE={DATABASE};"
    )
    conn_str += f"UID={USERNAME};PWD={PASSWORD};" if USERNAME and PASSWORD else "Trusted_Connection=yes;"
    conn = pyodbc.connect(conn_str)
    cursor = conn.cursor()

    cursor.execute("SELECT id_comp, old_est_comp, new_est_comp, changed_by, changed_at FROM log_est_comp_changes ORDER BY changed_at DESC")
    logs = cursor.fetchall()

    result = []
    for row in logs:
        result.append({
            'id_comp': row[0],
            'old_est_comp': row[1],
            'new_est_comp': row[2],
            'changed_by': row[3],
            'changed_at': str(row[4])
        })
    conn.close()
    return result

def activate_est_comp_to_A():
    conn_str = (
        f"DRIVER={{ODBC Driver 17 for SQL Server}};"
        f"SERVER={SERVER};"
        f"DATABASE={DATABASE};"
    )
    conn_str += f"UID={USERNAME};PWD={PASSWORD};" if USERNAME and PASSWORD else "Trusted_Connection=yes;"
    conn = pyodbc.connect(conn_str)
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE comprobante
        SET est_comp = 'A'
        WHERE est_comp = 'I'
    """)
    conn.commit()
    rows = cursor.rowcount
    conn.close()
    return rows

