import os
import mysql.connector
from dotenv import load_dotenv
from flask import Flask, jsonify

load_dotenv()

app = Flask(__name__)


def get_connection():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        port=int(os.getenv("DB_PORT")),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME"),
    )

@app.route("/imoveis", methods=["GET"])
def listar_imoveis():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM imoveis")
    imoveis = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(imoveis), 200

@app.route("/imoveis/<int:id>", methods=["GET"])
def listar_imovel(id):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM imoveis WHERE id = %s", (id,))
    imovel = cursor.fetchone()
    cursor.close()
    conn.close()

    if imovel is None:
        return jsonify({"erro": "Imóvel não encontrado"}), 404

    return jsonify(imovel), 200

if __name__ == "__main__":
    app.run(debug=True)