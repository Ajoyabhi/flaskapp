from flask import Flask, render_template, request, flash, redirect, url_for, send_file
from werkzeug.utils import secure_filename
import os
import pandas as pd
import zipfile

app = Flask(__name__)
app.secret_key = 'secret_key'
app.config['UPLOAD_FOLDER'] = ''
ALLOWED_EXTENSIONS = {'zip'}


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/')
def home():
    return render_template('index.html')


df1 = pd.DataFrame()
df1['row_num'] = [str(i) for i in range(1000000)]
df1['col_1'] = [i*2 for i in range(1000000)]
df1.to_csv('file1.csv', index=False)

df2 = pd.DataFrame()
df2['row_num'] = [str(i) for i in range(1000000)]
df2['col_2'] = [i+3 for i in range(1000000)]
df2.to_csv('file2.csv', index=False)


@app.route('/upload', methods=['POST'])
def upload():
    if 'file' not in request.files:
        flash('No file uploaded', 'error')
        return redirect(url_for('home'))
    file = request.files['file']
    if file.filename == '':
        flash('No selected file', 'error')
        return redirect(url_for('home'))
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        flash('File uploaded successfully', 'success')
        return redirect(url_for('analyze', filename=filename))
    else:
        flash('Invalid file format', 'error')
        return redirect(url_for('home'))


@app.route('/analyze/<filename>')
def analyze(filename):
    # Unzip the file
    zip_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(app.config['UPLOAD_FOLDER'])

    # Load and merge the data frames
    df1_path = os.path.join(app.config['UPLOAD_FOLDER'], 'file1.csv')
    df2_path = os.path.join(app.config['UPLOAD_FOLDER'], 'file2.csv')
    df1 = pd.read_csv(df1_path)
    df2 = pd.read_csv(df2_path)

    # Merge the data frames
    final_df = pd.merge(df1, df2, on='row_num')

    # Calculate col_3 = col_1 + col_2
    final_df['col_3'] = final_df['col_1'] + final_df['col_2']

    # Save the final_df as CSV
    output_path = os.path.join(app.config['UPLOAD_FOLDER'], 'final_df.csv')
    final_df.to_csv(output_path, index=False)

    return render_template('analyze.html', filename=filename)


@app.route('/download/<filename>')
def download(filename):
    csv_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    return send_file(csv_path, as_attachment=True, mimetype='text/csv')


if __name__ == '__main__':
    app.run(debug=True, port=8000)
