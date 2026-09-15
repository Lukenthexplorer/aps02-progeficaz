# aps02-progeficaz - API DE IMÓVEIS

API REST para uma imobiliária, construída com Flask e MySQL, desenvolvida com TDD.

## API no ar

**http://34.229.152.167:5000/imoveis**

Hospedada em uma instância EC2 da AWS (Gunicorn + Nginx), com banco de dados MySQL na Aiven.

## Integrantes

- Lucas Kenji Watanabe

## Rotas

| Método | Rota | Descrição | Sucesso | Erro |
|---|---|---|---|---|
| GET | `/imoveis` | Lista todos os imóveis | 200 | — |
| GET | `/imoveis/<id>` | Retorna um imóvel específico | 200 | 404 |
| POST | `/imoveis` | Adiciona um novo imóvel | 201 | 400 |
| PUT | `/imoveis/<id>` | Atualiza um imóvel existente | 200 | 404 |
| DELETE | `/imoveis/<id>` | Remove um imóvel | 204 | 404 |
| GET | `/imoveis?tipo=<tipo>` | Filtra imóveis por tipo | 200 | — |
| GET | `/imoveis?cidade=<cidade>` | Filtra imóveis por cidade | 200 | — |

Os filtros usam query string na própria coleção e podem ser combinados:
`/imoveis?tipo=casa&cidade=Lake%20Michael`

Buscas sem resultado retornam 200 com uma lista vazia, já que não encontrar nada
não é um erro.

### Exemplos

Listar todos:

```bash
curl http://34.229.152.167:5000/imoveis
```

Buscar por id:

```bash
curl http://34.229.152.167:5000/imoveis/1
```

Filtrar por tipo:

```bash
curl "http://34.229.152.167:5000/imoveis?tipo=terreno"
```

Criar um imóvel (`logradouro` e `cidade` são obrigatórios):

```bash
curl -X POST http://34.229.152.167:5000/imoveis \
  -H "Content-Type: application/json" \
  -d '{
    "logradouro": "Rua das Flores",
    "tipo_logradouro": "Rua",
    "bairro": "Centro",
    "cidade": "São Paulo",
    "cep": "01001",
    "tipo": "apartamento",
    "valor": 450000.0,
    "data_aquisicao": "2024-03-10"
  }'
```

Atualizar:

```bash
curl -X PUT http://34.229.152.167:5000/imoveis/1 \
  -H "Content-Type: application/json" \
  -d '{"logradouro": "Rua Nova", "cidade": "Campinas", "valor": 600000.0}'
```

Remover:

```bash
curl -X DELETE http://34.229.152.167:5000/imoveis/1
```

## Estrutura

```
.
├── servidor.py         # aplicação Flask com as rotas
├── requirements.txt    # dependências
├── tests/
│   └── test_api.py     # testes automatizados das rotas
└── README.md
```

## Rodando localmente

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Crie um arquivo `.env` na raiz com as credenciais do banco:

```
DB_HOST=seu-host.aivencloud.com
DB_PORT=sua-porta
DB_USER=avnadmin
DB_PASSWORD=sua-senha
DB_NAME=seu-banco
```

O `.env` está no `.gitignore` e nunca é versionado.

Para subir o servidor:

```bash
python servidor.py
```

## Testes

```bash
python -m pytest -v
```

Os testes cobrem os casos de sucesso e de erro de todas as rotas, verificando
códigos HTTP e a presença de todos os atributos dos imóveis. Os testes que
alteram dados usam uma fixture que cria um imóvel antes e o remove depois,
de modo que os dados originais do banco não são afetados.

## Banco de dados

Tabela `imoveis`:

| Coluna | Tipo |
|---|---|
| id | INTEGER, chave primária, auto incremento |
| logradouro | TEXT, obrigatório |
| tipo_logradouro | TEXT |
| bairro | TEXT |
| cidade | TEXT, obrigatório |
| cep | TEXT |
| tipo | TEXT |
| valor | REAL |
| data_aquisicao | TEXT (formato YYYY-MM-DD) |