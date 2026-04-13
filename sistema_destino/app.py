from flask import Flask, render_template, request, redirect, url_for
import os

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/')
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        return redirect(url_for('dashboard'))
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route('/pasta/<nome_pasta>', methods=['GET', 'POST'])
def pasta(nome_pasta):
    if request.method == 'POST':
        arquivo = request.files['arquivo']
        if arquivo:
            caminho_salvar = os.path.join(UPLOAD_FOLDER, nome_pasta, arquivo.filename)
            os.makedirs(os.path.dirname(caminho_salvar), exist_ok=True)
            arquivo.save(caminho_salvar)
            return render_template('pasta.html', nome_pasta=nome_pasta, sucesso=True)
    return render_template('pasta.html', nome_pasta=nome_pasta, sucesso=False)

if __name__ == '__main__':
    app.run(debug=True, port=5000)