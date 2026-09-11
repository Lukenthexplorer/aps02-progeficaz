import pytest
from servidor import app, get_connection

ATRIBUTOS = ["id", "logradouro", "tipo_logradouro", "bairro", "cidade",
             "cep", "tipo", "valor", "data_aquisicao"]

NOVO_IMOVEL = {
    "logradouro": "Rua dos Testes",
    "tipo_logradouro": "Rua",
    "bairro": "Vila Pytest",
    "cidade": "Cidade Teste",
    "cep": "12345",
    "tipo": "casa",
    "valor": 500000.0,
    "data_aquisicao": "2024-01-15",
}

def apagar_do_banco(id_imovel):
    """Remove um imóvel direto no banco (usado para limpar o que os testes criam)."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM imoveis WHERE id = %s", (id_imovel,))
    conn.commit()
    cursor.close()
    conn.close()


@pytest.fixture
def cliente():
    return app.test_client()


@pytest.fixture
def imovel_teste():
    """Cria um imóvel direto no banco antes do teste e apaga depois, mesmo se o teste falhar."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO imoveis (logradouro, tipo_logradouro, bairro, cidade, cep, tipo, valor, data_aquisicao) "
        "VALUES (%(logradouro)s, %(tipo_logradouro)s, %(bairro)s, %(cidade)s, "
        "%(cep)s, %(tipo)s, %(valor)s, %(data_aquisicao)s)",
        NOVO_IMOVEL,
    )
    conn.commit()
    id_criado = cursor.lastrowid
    cursor.close()
    conn.close()

    yield id_criado

    apagar_do_banco(id_criado)


def test_listar_imoveis(cliente):
    resposta = cliente.get("/imoveis")

    assert resposta.status_code == 200
    imoveis = resposta.get_json()
    assert isinstance(imoveis, list)
    assert len(imoveis) > 0
    for atributo in ATRIBUTOS:
        assert atributo in imoveis[0]

def test_buscar_imovel_por_id(cliente):
    resposta = cliente.get("/imoveis/1")

    assert resposta.status_code == 200
    imovel = resposta.get_json()
    assert imovel["id"] == 1
    for atributo in ATRIBUTOS:
        assert atributo in imovel


def test_buscar_imovel_inexistente(cliente):
    resposta = cliente.get("/imoveis/999999")

    assert resposta.status_code == 404

def test_adicionar_imovel(cliente):
    resposta = cliente.post("/imoveis", json=NOVO_IMOVEL)

    assert resposta.status_code == 201
    imovel = resposta.get_json()
    assert "id" in imovel

    apagar_do_banco(imovel["id"])  # limpa antes de conferir os campos

    for campo, valor in NOVO_IMOVEL.items():
        assert imovel[campo] == valor


def test_adicionar_imovel_sem_campos_obrigatorios(cliente):
    resposta = cliente.post("/imoveis", json={"tipo": "casa"})

    assert resposta.status_code == 400

def test_atualizar_imovel(cliente, imovel_teste):
    dados = {**NOVO_IMOVEL, "valor": 750000.0, "bairro": "Bairro Atualizado"}
    resposta = cliente.put(f"/imoveis/{imovel_teste}", json=dados)

    assert resposta.status_code == 200
    imovel = resposta.get_json()
    assert imovel["id"] == imovel_teste
    assert imovel["valor"] == 750000.0
    assert imovel["bairro"] == "Bairro Atualizado"

    # confere se a mudança foi salva de verdade
    resposta_get = cliente.get(f"/imoveis/{imovel_teste}")
    assert resposta_get.get_json()["valor"] == 750000.0


def test_atualizar_imovel_inexistente(cliente):
    resposta = cliente.put("/imoveis/999999", json=NOVO_IMOVEL)

    assert resposta.status_code == 404

def test_remover_imovel(cliente, imovel_teste):
    resposta = cliente.delete(f"/imoveis/{imovel_teste}")

    assert resposta.status_code == 204

    # depois de remover, buscar tem que dar 404
    resposta_get = cliente.get(f"/imoveis/{imovel_teste}")
    assert resposta_get.status_code == 404


def test_remover_imovel_inexistente(cliente):
    resposta = cliente.delete("/imoveis/999999")

    assert resposta.status_code == 404


def test_buscar_imoveis_por_tipo(cliente):
    resposta = cliente.get("/imoveis", query_string={"tipo": "terreno"})

    assert resposta.status_code == 200
    imoveis = resposta.get_json()
    assert len(imoveis) > 0
    for imovel in imoveis:
        assert imovel["tipo"] == "terreno"
        for atributo in ATRIBUTOS:
            assert atributo in imovel


def test_buscar_imoveis_por_tipo_sem_resultados(cliente):
    resposta = cliente.get("/imoveis", query_string={"tipo": "castelo"})

    assert resposta.status_code == 200
    assert resposta.get_json() == []


def test_buscar_imoveis_por_cidade(cliente):
    resposta = cliente.get("/imoveis", query_string={"cidade": "Lake Michael"})

    assert resposta.status_code == 200
    imoveis = resposta.get_json()
    assert len(imoveis) > 0
    for imovel in imoveis:
        assert imovel["cidade"] == "Lake Michael"
        for atributo in ATRIBUTOS:
            assert atributo in imovel


def test_buscar_imoveis_por_cidade_sem_resultados(cliente):
    resposta = cliente.get("/imoveis", query_string={"cidade": "Cidade Que Nao Existe"})

    assert resposta.status_code == 200
    assert resposta.get_json() == []