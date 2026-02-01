from flask import Flask, render_template
from database import criar_tabelas

app = Flask(__name__)

# cria banco ao iniciar
criar_tabelas()

@app.route("/")
def home():
    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)
