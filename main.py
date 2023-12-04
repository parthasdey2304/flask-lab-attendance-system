# app.py
from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import csv

app = Flask(__name__)

# Connect to SQLite database
conn = sqlite3.connect('attendance.db')
cursor = conn.cursor()

# Create a table if it doesn't exist
cursor.execute('''
    CREATE TABLE IF NOT EXISTS students (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        student_id INTEGER NOT NULL,
        department TEXT NOT NULL,
        section TEXT NOT NULL,
        computer_id INTEGER NOT NULL,
        date TEXT NOT NULL,
        time TEXT NOT NULL
    )
''')
conn.commit()

# Close the connection
conn.close()


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/submit', methods=['POST'])
def submit():
    name = request.form['name'].upper()
    student_id = request.form['student_id'].upper()
    department = request.form['department'].upper()
    section = request.form['section'].upper()
    computer_id = request.form['computer_id'].upper()
    date = request.form['date'].upper()
    time = request.form['time'].upper()

    conn = sqlite3.connect('attendance.db')
    cursor = conn.cursor()

    # Insert data into the database
    cursor.execute("INSERT INTO students (name, student_id, department, section, computer_id, date, time) VALUES (?, ?, ?, ?, ?, ?, ?)",
                   (name, student_id, department, section, computer_id, date, time))
    conn.commit()

    conn.close()
    return redirect(url_for('index'))


@app.route('/attendance', methods=['GET', 'POST'])
def attendance():
    conn = sqlite3.connect('attendance.db')
    cursor = conn.cursor()

    # Retrieve all entries from the database
    cursor.execute("SELECT * FROM students")
    rows = cursor.fetchall()

    # Get unique departments and sections for dynamic dropdowns
    unique_departments = set(row[3] for row in rows)
    unique_sections = set(row[4] for row in rows)

    if request.method == 'POST':
        department_filter = request.form.get('department_filter')
        section_filter = request.form.get('section_filter')
        date_filter = request.form.get('date_filter')

        # Build the SQL query based on the selected filters
        query = "SELECT * FROM students WHERE 1=1"
        parameters = []

        if department_filter and department_filter != 'null':
            query += " AND department = ?"
            parameters.append(department_filter)

        if section_filter and section_filter != 'null':
            query += " AND section = ?"
            parameters.append(section_filter)

        if date_filter:
            query += " AND date = ?"
            parameters.append(date_filter)

        cursor.execute(query, parameters)
        rows = cursor.fetchall()

    conn.close()

    return render_template('attendance.html', rows=rows, departments=unique_departments, sections=unique_sections)


@app.route('/export/<selected_date>', methods=['GET'])
def export(selected_date):
    conn = sqlite3.connect('attendance.db')
    cursor = conn.cursor()

    # Retrieve entries for the selected date
    cursor.execute("SELECT * FROM students WHERE date LIKE ?", (f"{selected_date}%",))
    rows = cursor.fetchall()

    # Generate CSV file
    filename = f"attendance_{selected_date}.csv"
    with open(filename, 'w', newline='') as csvfile:
        csv_writer = csv.writer(csvfile)
        csv_writer.writerow(['ID', 'Name', 'Student ID', 'Department', 'Section', 'Computer ID', 'Date', 'Time'])
        csv_writer.writerows(rows)

    conn.close()

    return f"CSV file exported as {filename}"


@app.route('/clear_database', methods=['POST'])
def clear_database():
    conn = sqlite3.connect('attendance.db')
    cursor = conn.cursor()

    # Drop the students table
    cursor.execute("DROP TABLE IF EXISTS students")

    # Recreate the table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            student_id INTEGER NOT NULL,
            department TEXT NOT NULL,
            section TEXT NOT NULL,
            computer_id INTEGER NOT NULL,
            date TEXT NOT NULL,
            time TEXT NOT NULL
        )
    ''')

    conn.commit()
    conn.close()

    return redirect(url_for('attendance'))


if __name__ == '__main__':
    app.run(debug=True)
