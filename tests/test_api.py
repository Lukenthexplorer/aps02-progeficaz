from servidor import app

ATRIBUTOS = ["id", "logradouro", "tipo_logradouro", "bairro", "cidade",
             "cep", "tipo", "valor", "data_aquisicao"]


def test_listar_imoveis():
    cliente = app.test_client()
    resposta = cliente.get("/imoveis")
    assert resposta.status_code == 200

def test_buscar_imovel_por_id():
    cliente = app.test_client()
    resposta = cliente.get("/imoveis/1")

    assert resposta.status_code == 200

    imovel = resposta.get_json()
    assert imovel["id"] == 1
    for atributo in ATRIBUTOS:
        assert atributo in imovel

def test_buscar_imovel_inexistente():
    cliente = app.test_client()
    resposta = cliente.get("/imoveis/999999")

    assert resposta.status_code == 404