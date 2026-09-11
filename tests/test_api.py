from servidor import app

def test_listar_imoveis():
    cliente = app.test_client()
    resposta = cliente.get("/imoveis")
    assert resposta.status_code == 200