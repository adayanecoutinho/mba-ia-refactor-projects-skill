# Playbook de Refatoração (Fase 3)

Cada padrão abaixo mapeia um anti-pattern do catálogo para uma transformação concreta, com
exemplo de código antes/depois. Os exemplos usam Python/Flask e JS/Express (as duas stacks dos
3 projetos-alvo) — adapte a mesma ideia para outras linguagens.

## 1. Extrair configuração/segredos para módulo de Config

**Resolve**: Hardcoded Credentials (CRITICAL)

Antes:
```python
app.config["SECRET_KEY"] = "minha-chave-super-secreta-123"
app.config["DEBUG"] = True
```

Depois:
```python
# config/settings.py
import os

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-only-change-me")
    DEBUG = os.environ.get("FLASK_DEBUG", "false").lower() == "true"
    DATABASE_PATH = os.environ.get("DATABASE_PATH", "loja.db")

# app.py
app.config.from_object(Config)
```

## 2. Separar acesso a dados em Models (quebrar God File)

**Resolve**: God Class/File (CRITICAL)

Antes: um `models.py` de 300+ linhas com queries de produtos, usuários e pedidos misturadas.

Depois: um arquivo de model por domínio, cada um só com funções/classe daquele domínio:
```python
# models/produto_model.py
def get_todos() -> list[dict]: ...
def get_por_id(produto_id: int) -> dict | None: ...
def criar(nome, descricao, preco, estoque, categoria) -> int: ...

# models/usuario_model.py
def get_todos() -> list[dict]: ...
def autenticar(email, senha) -> dict | None: ...
```

## 3. Parametrizar queries (eliminar SQL Injection)

**Resolve**: SQL Injection (CRITICAL)

Antes:
```python
cursor.execute("SELECT * FROM produtos WHERE id = " + str(id))
```

Depois:
```python
cursor.execute("SELECT * FROM produtos WHERE id = ?", (id,))
```

Em Node.js/sqlite3:
```js
// antes
db.run("DELETE FROM users WHERE id = " + id)
// depois
db.run("DELETE FROM users WHERE id = ?", [id])
```

## 4. Extrair rotas para camada de Views/Routes

**Resolve**: mistura de roteamento com regra de negócio no entry point

Antes: `app.add_url_rule(...)` e regra de negócio no mesmo `app.py`.

Depois:
```python
# routes/produto_routes.py
from flask import Blueprint
from controllers import produto_controller as c

produto_bp = Blueprint("produtos", __name__)
produto_bp.add_url_rule("/produtos", "listar", c.listar_produtos, methods=["GET"])
produto_bp.add_url_rule("/produtos/<int:id>", "buscar", c.buscar_produto, methods=["GET"])

# app.py (composition root)
app.register_blueprint(produto_bp)
```

## 5. Mover lógica de negócio do handler para o Controller/Service

**Resolve**: Fat Controller / lógica de negócio na rota (HIGH)

Antes: handler de checkout do LMS decide status de pagamento, monta e persiste em cascata,
tudo dentro do callback da rota.

Depois:
```python
# controllers/pedido_controller.py
def criar_pedido(request_json):
    usuario_id = request_json.get("usuario_id")
    itens = request_json.get("itens", [])
    if not usuario_id or not itens:
        return {"erro": "dados obrigatórios ausentes"}, 400
    resultado = pedido_model.criar(usuario_id, itens)
    return {"dados": resultado, "sucesso": True}, 201
```
O controller apenas valida/orquestra; `pedido_model.criar` concentra a regra (checar estoque,
calcular total, persistir) em uma função testável isoladamente.

## 6. Substituir Callback Hell por async/await (Node.js)

**Resolve**: Callback Hell (HIGH)

Antes:
```js
this.db.get(sqlA, [id], (err, a) => {
  this.db.get(sqlB, [a.id], (err, b) => {
    this.db.run(sqlC, [b.id], (err) => { res.json({ok:true}) });
  });
});
```

Depois (usando um wrapper `promisify` sobre o driver, ou trocando por um driver com Promises
nativas):
```js
async function checkout(req, res) {
  const course = await db.get(sqlA, [req.body.c_id]);
  const user = await db.get(sqlB, [req.body.eml]);
  await db.run(sqlC, [user.id]);
  res.json({ ok: true });
}
```

## 7. Eliminar estado global mutável / introduzir injeção de dependência

**Resolve**: Global State sem DI (HIGH)

Antes:
```python
db_connection = None
def get_db():
    global db_connection
    if db_connection is None:
        db_connection = sqlite3.connect(...)
    return db_connection
```

Depois:
```python
# config/database.py
def create_connection(database_path: str):
    conn = sqlite3.connect(database_path, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

# composition root injeta a conexão nos models via app.config ou app context,
# em vez dos models acessarem uma variável global do módulo database.
```

## 8. Resolver N+1 queries com JOIN/lote

**Resolve**: N+1 Queries (MEDIUM)

Antes:
```python
for row in pedidos:
    cursor2.execute("SELECT * FROM itens_pedido WHERE pedido_id = " + str(row["id"]))
    for item in cursor2.fetchall():
        cursor3.execute("SELECT nome FROM produtos WHERE id = " + str(item["produto_id"]))
```

Depois:
```python
cursor.execute("""
    SELECT p.id AS pedido_id, ip.produto_id, ip.quantidade, ip.preco_unitario, pr.nome
    FROM pedidos p
    JOIN itens_pedido ip ON ip.pedido_id = p.id
    JOIN produtos pr ON pr.id = ip.produto_id
    WHERE p.usuario_id = ?
""", (usuario_id,))
# agrupa o resultset único em memória por pedido_id, em vez de 1 query por item
```

## 9. Centralizar validação em vez de duplicar por rota

**Resolve**: Validação duplicada/ausente (MEDIUM)

Antes: cada handler reescreve `if "nome" not in dados: return erro`.

Depois:
```python
# controllers/validators.py
REQUIRED_PRODUTO_FIELDS = ("nome", "preco", "estoque")

def validate_produto_payload(dados: dict) -> str | None:
    for field in REQUIRED_PRODUTO_FIELDS:
        if field not in dados:
            return f"{field} é obrigatório"
    if dados["preco"] < 0:
        return "Preço não pode ser negativo"
    return None
```
Controllers chamam `validate_produto_payload` uma única vez; a regra vive em um só lugar.

## 10. Centralizar tratamento de erros em um middleware/error handler

**Resolve**: try/except repetido, mensagens de erro inconsistentes (MEDIUM)

Antes: todo handler tem seu próprio `try/except Exception as e: return jsonify({"erro": str(e)}), 500`.

Depois:
```python
# middlewares/error_handler.py
from flask import jsonify

def register_error_handlers(app):
    @app.errorhandler(404)
    def not_found(e):
        return jsonify({"erro": "Recurso não encontrado", "sucesso": False}), 404

    @app.errorhandler(Exception)
    def handle_exception(e):
        app.logger.exception(e)
        return jsonify({"erro": "Erro interno do servidor", "sucesso": False}), 500
```
Controllers deixam de precisar de `try/except` genérico — apenas levantam exceções específicas
quando fizer sentido (ex.: `NotFoundError`).

## 11. Trocar hashing de senha inseguro por padrão seguro

**Resolve**: Hashing fraco/deprecated (CRITICAL)

Antes:
```python
self.password = hashlib.md5(pwd.encode()).hexdigest()
```

Depois:
```python
from werkzeug.security import generate_password_hash, check_password_hash

self.password = generate_password_hash(pwd)
# verificação: check_password_hash(self.password, pwd)
```

## 12. Nomear magic numbers e melhorar nomenclatura

**Resolve**: Magic numbers / nomes ruins (LOW)

Antes:
```python
if faturamento > 10000:
    desconto = faturamento * 0.1
elif faturamento > 5000:
    desconto = faturamento * 0.05
```

Depois:
```python
# config/business_rules.py
DESCONTO_FAIXA_ALTA = (10_000, 0.10)
DESCONTO_FAIXA_MEDIA = (5_000, 0.05)
DESCONTO_FAIXA_BAIXA = (1_000, 0.02)

def calcular_desconto(faturamento: float) -> float:
    for limite, taxa in (DESCONTO_FAIXA_ALTA, DESCONTO_FAIXA_MEDIA, DESCONTO_FAIXA_BAIXA):
        if faturamento > limite:
            return faturamento * taxa
    return 0
```
