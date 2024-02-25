from flask import Flask, render_template, request, Response, url_for, session, redirect
import pandas as pd
import json 
import io
import xlsxwriter


app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # Change this to a secure secret key

users = {
    'user1': 'password1',
    'user2': 'password2'
}

def is_logged_in():
    return 'username' in session

@app.route('/')
def index():
    if is_logged_in():
        return render_template('index.html', username=session['username'])
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username in users and users[username] == password:
            session['username'] = username
            return redirect(url_for('index'))
        else:
            return render_template('login.html', message='Invalid username or password')
    return render_template('login.html')



@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('index'))



@app.route('/upload', methods=['POST'])
def upload():
    if 'files[]' not in request.files:
        return render_template('index.html', message='No file part')

    files = request.files.getlist('files[]')
    tables = []

    for file in files:
        if file.filename == '':
            return render_template('index.html', message='No file selected')

        if file:
            try:
                df = pd.read_csv(file)
                if not df.empty:
                    tables.append(df)
                else:
                    return render_template('index.html', message='Uploaded file is empty')
            except pd.errors.EmptyDataError:
                return render_template('index.html', message='Uploaded file is empty')

    return render_template('table.html', tables=tables)


@app.route('/export', methods=['POST'])
def export():
    export_data = request.form.get('exportData')
    if export_data:
        export_data = json.loads(export_data)
        df = pd.DataFrame(export_data)
        output = io.BytesIO()
        writer = pd.ExcelWriter(output, engine='xlsxwriter')
        df.to_excel(writer, index=False, header=False)
        writer.close()
        output.seek(0)
        return Response(output, mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        headers={"Content-Disposition": "attachment;filename=exported_data.xlsx"})
    return "No data to export"

if __name__ == '__main__':
    app.run(debug=True)
