# Catálogo de Anti-Patterns (Fase 2)

Escala de severidade adotada em todo o catálogo:

- **CRITICAL**: falha grave de arquitetura ou segurança — impede funcionamento correto, expõe
  dados sensíveis (credenciais hardcoded, SQL Injection) ou viola completamente a separação de
  responsabilidades (God Class com banco de dados + lógica + roteamento no mesmo arquivo).
- **HIGH**: forte violação do MVC/SOLID que dificulta muito manutenção e testes (lógica de
  negócio pesada dentro de Controllers, acoplamento forte sem DI, estado global mutável).
- **MEDIUM**: padronização, duplicação de código, gargalos de performance moderados (N+1,
  middlewares mal usados, validação ausente nas rotas).
- **LOW**: legibilidade, nomenclatura ruim, magic numbers.

Cada anti-pattern abaixo lista: definição, sinais de detecção (o que grep/ler no código) e
severidade padrão (pode subir/descer um nível dependendo do contexto — justifique no relatório
se desviar do padrão).

## 1. God Class / God File (CRITICAL)

**Definição**: um único arquivo ou classe concentra rotas, acesso a dados (SQL/ORM), validação
e regra de negócio de múltiplos domínios diferentes.

**Sinais de detecção**:
- Um arquivo com centenas de linhas contendo funções de mais de 2 domínios distintos (ex.:
  produtos + usuários + pedidos no mesmo `models.py`).
- Uma classe (`class XManager`, `class AppManager`, `class Service`) que instancia a conexão de
  banco, define rotas (`app.get(...)`, `app.post(...)`) e executa queries, tudo dentro de si.
- Ausência de qualquer separação de pastas (`models/`, `controllers/`, `routes/`).

## 2. Hardcoded Credentials / Secrets (CRITICAL)

**Definição**: chaves, senhas, tokens ou segredos de API escritos diretamente no código-fonte.

**Sinais de detecção**: literais de string atribuídos a variáveis como `SECRET_KEY`,
`password`, `pass`, `apiKey`, `dbPass`, `paymentGatewayKey`, `smtpUser`/`smtpPassword`, sem
uso de `os.environ`/`process.env`/`.env`. Também conta expor a secret key em uma resposta de
API (ex.: endpoint de health check retornando `secret_key`).

## 3. SQL Injection (CRITICAL)

**Definição**: construção de queries SQL por concatenação/interpolação de strings com dados de
entrada do usuário, sem parametrização.

**Sinais de detecção**: `"SELECT * FROM x WHERE id = " + str(id)`, f-strings com dados de
usuário dentro de `execute(...)`, template literals JS interpolando `req.body`/`req.params`
diretamente numa query. Também conta um endpoint que aceita SQL arbitrário do cliente e executa
(`cursor.execute(dados.get("sql"))`).

## 4. Fat Controller / Business Logic in Route Handler (HIGH)

**Definição**: a função de rota (controller) contém regras de negócio complexas — cálculos,
orquestração de múltiplas entidades, decisões de fluxo — em vez de apenas orquestrar
chamadas a camadas inferiores.

**Sinais de detecção**: handler de rota com múltiplos `if/else` de regra de negócio (ex.:
cálculo de desconto, verificação de estoque, callback aninhado de pagamento), sem chamar uma
camada de serviço/model dedicada para isso.

## 5. Callback Hell / Pyramid of Doom (HIGH)

**Definição**: encadeamento profundo de callbacks aninhados (típico de Node.js pré-`async/await`
ou uso incorreto de Promises), tornando o fluxo difícil de seguir, testar e tratar erros.

**Sinais de detecção**: 3+ níveis de callbacks aninhados dentro de um handler
(`db.get(..., (err, x) => { db.get(..., (err, y) => { db.run(..., (err,z) => {...}) }) })`),
contadores manuais de pendências (`pending--`) para simular espera assíncrona em vez de
`Promise.all`/`async-await`.

## 6. Estado Global Mutável / Ausência de Injeção de Dependência (HIGH)

**Definição**: módulos usam variáveis globais mutáveis compartilhadas entre requisições
(cache, contadores, conexão de banco como singleton implícito acessado por função global) em
vez de injetar dependências explicitamente.

**Sinais de detecção**: `let globalCache = {}` em nível de módulo sendo escrito por múltiplos
handlers; função `get_db()` com `global db_connection`; falta de um construtor/factory que
receba dependências (conexão, config) como parâmetro.

## 7. N+1 Queries (MEDIUM)

**Definição**: uma query é executada dentro de um loop para buscar dados relacionados, quando
poderia ser feito com uma única query (join) ou uma query em lote.

**Sinais de detecção**: `for item in itens: cursor.execute("SELECT ... WHERE id = " + ...)`;
`tasks.forEach(t => db.get(...))`; qualquer `SELECT` dentro de `for`/`forEach`/`map` que roda
uma vez por item de uma coleção já carregada.

## 8. Validação Ausente ou Duplicada nas Rotas (MEDIUM)

**Definição**: cada handler reimplementa manualmente a mesma validação (campos obrigatórios,
formato de e-mail, ranges numéricos) em vez de usar um validador/schema centralizado, ou algumas
rotas simplesmente não validam entrada nenhuma.

**Sinais de detecção**: blocos repetidos de `if "campo" not in dados: return erro` copiados
entre múltiplos handlers; regex de e-mail reimplementada em mais de um arquivo; endpoints POST/PUT
que fazem `request.get_json()` e usam os campos sem checar tipo/presença.

## 9. Uso Inadequado de Middlewares / CORS Aberto (MEDIUM)

**Definição**: middlewares aplicados de forma genérica demais (CORS liberado para qualquer
origem em produção, `DEBUG=True` implícito em produção) ou ausência de middleware de erro
centralizado, fazendo cada handler tratar exceções manualmente e de forma inconsistente.

**Sinais de detecção**: `CORS(app)` sem configuração de origem; `app.config["DEBUG"] = True`
sem depender de ambiente; blocos `try/except` repetidos em toda rota fazendo a mesma coisa
(logar e retornar 500) em vez de um error handler central.

## 10. Hashing de Senha Fraco / Deprecated (CRITICAL — também é achado de API deprecated)

**Definição**: uso de algoritmo de hash inadequado para senhas (MD5, SHA1 sem salt, ou "hash"
customizado sem função criptográfica real).

**Sinais de detecção**: `hashlib.md5(pwd.encode())`; função caseira tipo `badCrypto` que
manipula `base64` como se fosse hashing seguro. MD5/SHA1 para senha são considerados
**deprecated/inseguros** pelas próprias bibliotecas padrão (recomendação atual: `bcrypt`,
`argon2`, `werkzeug.security.generate_password_hash`).

## 11. Magic Numbers e Nomenclatura Ruim (LOW)

**Definição**: literais numéricos ou de string sem nome semântico espalhados pelo código, ou
identificadores que não comunicam intenção (`u`, `e`, `p`, `cc`, `x`, `d`).

**Sinais de detecção**: comparações como `if faturamento > 10000:` sem constante nomeada;
parâmetros de função de 1 letra em handlers de rota; variáveis `data`, `d`, `obj` genéricas
reutilizadas para coisas diferentes no mesmo arquivo.

## 12. Prints/Logs Não Estruturados como Observabilidade (LOW)

**Definição**: uso de `print()`/`console.log()` como único mecanismo de log, incluindo em
código que simula envio de notificação (e-mail/SMS/push) apenas imprimindo no console.

**Sinais de detecção**: `print("ENVIANDO EMAIL: ...")`, `console.log("[LOG] ...")` sem nenhum
logger configurável (níveis, formato, destino).

## Detecção de APIs / práticas deprecated (obrigatório verificar)

Ao auditar, verifique explicitamente:

- **Versões de framework desatualizadas** com CVEs conhecidas ou EOL declarado pelo mantenedor
  (reporte a versão encontrada no manifesto e sinalize como MEDIUM/HIGH se muito antiga —
  justifique a severidade pelo tipo de exposição, ex.: API pública vs. uso interno).
- **`hashlib.md5`/`hashlib.sha1` para senhas** (Python) — deprecated para esse uso.
- **Callbacks de `sqlite3`/driver assíncrono baseados em callback** em vez de Promise/async-await
  (Node.js) — padrão antigo, não é erro de sintaxe mas é considerado legado/deprecated na prática
  atual de Node.
- **`request.get_json()` sem `silent=True`/tratamento**, `app.run(debug=True)` em produção —
  não é "deprecated" tecnicamente, mas é uma prática desaconselhada pela documentação oficial do
  framework para produção; reporte como MEDIUM.
- Qualquer chamada marcada como deprecated na documentação oficial da versão do framework
  detectada na Fase 1 (se souber; caso não tenha certeza, diga explicitamente que não pôde
  confirmar contra a documentação oficial e recomende validação manual).
