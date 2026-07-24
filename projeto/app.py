from flask import Flask, render_template, request

app = Flask(__name__)

# Rota principal que serve a página web (index.html dentro da pasta templates)
@app.route('/')
def index():
    return render_template('index.html')

# Rota para receber os comandos dos botões e pedais
@app.route('/comando/<acao>')
def comando(acao):
    print(f"Comando recebido: {acao}")
    # Ponto de entrada onde vais ligar a lógica dos motores do robô
    return "OK", 200

if __name__ == '__main__':
    # O '0.0.0.0' permite que o telemóvel aceda ao servidor pela rede Wi-Fi local
    app.run(host='0.0.0.0', port=5001, debug=True)