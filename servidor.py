import os
import mysql.connector
from dotenv import load_dotenv
from flask import Flask, jsonify, request

load_dotenv()

app = Flask(__name__)

def adicionar_links(imovel):
    imovel["links"] = {
        "self": f"/imoveis/{imovel['id']}",
        "update": f"/imoveis/{imovel['id']}",
        "delete": f"/imoveis/{imovel['id']}",
        "todos": "/imoveis",
    }
    return imovel

# Gera a conexao com o bd
def get_connection():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        port=int(os.getenv("DB_PORT")),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME"),
    )

# Lista imovel por id
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

    return jsonify(adicionar_links(imovel)), 200

# Cria imovel
@app.route("/imoveis", methods=['POST'])
def adicionar_imoveis():

    dados = request.get_json()

    if not dados or not dados.get("logradouro") or not dados.get("cidade"):
        return jsonify({"erro": "logradouro e cidade são obrigatórios"}), 400

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO imoveis "
        "(logradouro, tipo_logradouro, bairro, cidade, cep, tipo, valor, data_aquisicao) "
        "VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
        (
            dados.get("logradouro"),
            dados.get("tipo_logradouro"),
            dados.get("bairro"),
            dados.get("cidade"),
            dados.get("cep"),
            dados.get("tipo"),
            dados.get("valor"),
            dados.get("data_aquisicao"),
        ),
    )
    conn.commit()
    id_criado = cursor.lastrowid
    cursor.close()
    conn.close()

    imovel = {**dados, "id": id_criado}
    return jsonify(adicionar_links(imovel)), 201

# Update um imovel
@app.route("/imoveis/<int:id>", methods=["PUT"])
def atualizar_imovel(id):
    dados = request.get_json()
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE imoveis SET " \
        "logradouro = %s, " \
        "tipo_logradouro = %s, " \
        "bairro = %s, " \
        "cidade = %s, " \
        "cep = %s, " \
        "tipo = %s, " \
        "valor = %s, " \
        "data_aquisicao = %s " \
        "WHERE id = %s",
        (
            dados.get("logradouro"),
            dados.get("tipo_logradouro"),
            dados.get("bairro"),
            dados.get("cidade"),
            dados.get("cep"),
            dados.get("tipo"),
            dados.get("valor"),
            dados.get("data_aquisicao"),
            id
        ),
    )

    if cursor.rowcount == 0:
        cursor.close()
        conn.close()
        return jsonify({"error": "Imóvel não encontrado"}), 404

    conn.commit()
    cursor.close()
    conn.close()

    imovel = {**dados, "id": id}
    return jsonify(adicionar_links(imovel)), 200

# Remover um imovel
@app.route("/imoveis/<int:id>", methods=["DELETE"])
def remover_imovel(id):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    DELETE FROM imoveis WHERE id = %s
    """,
    (id,) )
    if cursor.rowcount == 0:
        cursor.close()
        conn.close()
        return jsonify({"error": "Imóvel não encontrado"}), 404

    conn.commit()
    cursor.close()
    conn.close()
    return "", 204

# Lista todos os imoveis, com filtros opcionais por tipo e cidade
@app.route("/imoveis", methods=["GET"])
def listar_imoveis():
    tipo = request.args.get("tipo")
    cidade = request.args.get("cidade")

    query = "SELECT * FROM imoveis"
    condicoes = []
    parametros = []

    if tipo:
        condicoes.append("tipo = %s")
        parametros.append(tipo)

    if cidade:
        condicoes.append("cidade = %s")
        parametros.append(cidade)

    if condicoes:
        query += " WHERE " + " AND ".join(condicoes)

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(query, parametros)
    imoveis = cursor.fetchall()
    imoveis = [adicionar_links(imovel) for imovel in imoveis]
    cursor.close()
    conn.close()

    return jsonify(imoveis), 200

if __name__ == "__main__":
    app.run(debug=True)