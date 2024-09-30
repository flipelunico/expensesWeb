from flask import Flask, render_template, request, jsonify, redirect, url_for, session
import duckdb

app = Flask(__name__)
app.secret_key = 'tu_clave_secreta_aqui'  # Necesario para usar sesiones


def createDatabase():
    # Conexión a DuckDB
    conn = duckdb.connect('file_sorter.db')

    # Crear tablas si no existen
    conn.execute("""
        CREATE TABLE IF NOT EXISTS rules (
            id INTEGER PRIMARY KEY,
            name VARCHAR,
            file_type VARCHAR,
            destination VARCHAR,
            action VARCHAR
        );
        CREATE SEQUENCE IF NOT EXISTS id START 1;
        CREATE TABLE IF NOT EXISTS config (
            key VARCHAR PRIMARY KEY,
            value BOOLEAN
        );
        INSERT OR IGNORE INTO config (key, value) VALUES ('dark_mode', true);
    """)


@app.route('/')
def index():
    return redirect(url_for('rules_page'))

@app.route('/rules')
def rules_page():
    conn = duckdb.connect('file_sorter.db')
    rules = conn.execute("SELECT * FROM rules").fetchall()
    dark_mode = conn.execute("SELECT value FROM config WHERE key = 'dark_mode'").fetchone()[0]
    return render_template('index.html', active_page='rules', rules=rules, dark_mode=dark_mode)

@app.route('/logs')
def logs_page():
    conn = duckdb.connect('file_sorter.db')
    dark_mode = conn.execute("SELECT value FROM config WHERE key = 'dark_mode'").fetchone()[0]
    return render_template('index.html', active_page='logs', dark_mode=dark_mode)

@app.route('/settings')
def settings_page():
    conn = duckdb.connect('file_sorter.db')
    dark_mode = conn.execute("SELECT value FROM config WHERE key = 'dark_mode'").fetchone()[0]
    return render_template('index.html', active_page='settings', dark_mode=dark_mode)

@app.route('/toggle_dark_mode', methods=['POST'])
def toggle_dark_mode():
    conn = duckdb.connect('file_sorter.db')
    current_mode = conn.execute("SELECT value FROM config WHERE key = 'dark_mode'").fetchone()[0]
    new_mode = not current_mode
    conn.execute("UPDATE config SET value = ? WHERE key = 'dark_mode'", [new_mode])
    return redirect(url_for('settings_page'))

@app.route('/add_rule', methods=['POST'])
def add_rule():
    data = request.form
    conn = duckdb.connect('file_sorter.db')
    conn.execute("""
        INSERT INTO rules (id, name, file_type, destination, action)
        VALUES (nextval('id'),?, ?, ?, ?)
    """, [data['name'], data['file_type'], data['destination'], data['action']])
    return redirect(url_for('rules_page'))

@app.route('/delete_rule/<int:rule_id>', methods=['POST'])
def delete_rule(rule_id):
    conn = duckdb.connect('file_sorter.db')
    conn.execute("DELETE FROM rules WHERE id = ?", [rule_id])
    return redirect(url_for('rules_page'))

if __name__ == '__main__':
    app.run(debug=True)