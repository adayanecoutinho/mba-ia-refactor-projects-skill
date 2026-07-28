# Skill de Auditoria e Refatoração Arquitetural — `refactor-arch`

Este repositório é a entrega do desafio "Skill de Auditoria e Refatoração Arquitetural" da
Pós em IA. Contém a skill `refactor-arch` (Claude Code, `.claude/skills/`), copiada e
validada dentro dos 3 projetos-alvo fornecidos no repositório base, os 3 projetos já
refatorados para o padrão MVC, e os relatórios de auditoria gerados na Fase 2 de cada um.

- Skill: `code-smells-project/.claude/skills/refactor-arch/` (e cópia idêntica em
  `ecommerce-api-legacy/` e `task-manager-api/`)
- Relatórios de auditoria: `reports/audit-project-{1,2,3}.md`
- Código refatorado: dentro de cada pasta de projeto (estrutura `src/` em MVC)

---

## A) Análise Manual

Problemas identificados por leitura manual do código original, antes de qualquer criação da
skill. A classificação de severidade segue a escala do enunciado (CRITICAL / HIGH / MEDIUM /
LOW). Os relatórios completos e definitivos (gerados pela skill na Fase 2, com todos os
achados e linhas exatas) estão em `reports/audit-project-{1,2,3}.md` — abaixo, um resumo dos
achados manuais mais relevantes de cada projeto, com a justificativa de por que importam.

### Projeto 1 — code-smells-project (Python/Flask, E-commerce)

| Severidade | Problema | Por que importa |
|---|---|---|
| CRITICAL | SQL Injection generalizado (`models.py`, toda query concatenada por string) + endpoint `/admin/query` que executa SQL arbitrário vindo do cliente | Compromete o banco inteiro; o endpoint admin é, por definição, uma porta de execução remota de comandos SQL sem autenticação |
| CRITICAL | `SECRET_KEY` hardcoded e exposta de volta no `/health` | Chave de assinatura pública, comprometendo qualquer mecanismo de sessão/token |
| HIGH | `models.py` é um God File de ~314 linhas com 4 domínios misturados | Impossível testar isoladamente, alto acoplamento |
| MEDIUM | N+1 queries em `get_pedidos_usuario`/`get_todos_pedidos` | Degrada performance conforme a base cresce |
| MEDIUM | Validação de payload duplicada entre `criar_produto`/`atualizar_produto` | Alto risco das duas cópias divergirem |
| LOW | Magic numbers nas faixas de desconto do relatório de vendas | Regra de negócio importante fica escondida no meio do código |
| LOW | `print()` como único mecanismo de log em toda a aplicação | Sem níveis, formato ou destino configuráveis |

### Projeto 2 — ecommerce-api-legacy (Node.js/Express, LMS com checkout)

| Severidade | Problema | Por que importa |
|---|---|---|
| CRITICAL | `AppManager.js` é uma God Class (schema + rotas + regra de pagamento no mesmo arquivo) | Mistura total de responsabilidades, impossível testar checkout isoladamente |
| CRITICAL | Credenciais e chave de gateway de pagamento hardcoded em `utils.js` (`pk_live_...`) | Chave de produção real exposta no repositório |
| HIGH | Callback hell de 3-5 níveis no checkout e no relatório financeiro | Difícil de ler, tratar erro e testar; risco de bugs de concorrência |
| MEDIUM | N+1 queries no relatório financeiro (1 query por matrícula + 1 por pagamento) | Escala mal com o número de alunos matriculados |
| MEDIUM | `DELETE /users/:id` deixa matrículas e pagamentos órfãos (a própria mensagem de resposta admite isso) | Inconsistência de dados que pode quebrar relatórios futuros |
| LOW | Variáveis de uma letra (`u`, `e`, `p`, `cid`, `cc`) no handler mais crítico (pagamento) | Dificulta revisão de código sensível a segurança |
| LOW | Respostas HTTP inconsistentes (`res.send(string)` vs `res.json(...)`) | Cliente da API precisa tratar dois formatos de erro |

### Projeto 3 — task-manager-api (Python/Flask, Task Manager, parcialmente organizado)

| Severidade | Problema | Por que importa |
|---|---|---|
| CRITICAL | Hashing de senha com MD5 + hash de senha retornado em `to_dict()` de `User` em toda resposta da API | Combinados, permitem quebrar a senha de qualquer usuário só chamando `GET /users` |
| CRITICAL | Token de login `'fake-jwt-token-' + str(user.id)` — forjável por qualquer cliente | Bypass completo de autenticação/personificação de usuário |
| HIGH | Lógica de "tarefa atrasada" duplicada em 3 rotas diferentes, apesar de já existir `Task.is_overdue()` não utilizado | Alto risco das cópias divergirem; código morto ao lado de duplicação |
| HIGH | `Model.query.get(id)` usado em 9 pontos — API deprecated desde SQLAlchemy 2.0 | Gera warnings hoje, pode quebrar em upgrade futuro do SQLAlchemy |
| MEDIUM | N+1 queries no relatório de produtividade por usuário | `/reports/summary` degrada linearmente com o nº de usuários |
| MEDIUM | `utils/helpers.process_task_data()` já existe pronta para validar, mas nunca é chamada — cada rota reimplementa a validação manualmente | Código morto ao lado de lógica duplicada divergente |
| LOW | Imports não utilizados (`os, sys, json, time`) e utilitários mortos (`sanitize_string`, `generate_id`, `log_action`) | Ruído de leitura, sinaliza uso que não existe |

Este projeto confirma o alerta do enunciado: ter pastas `models/`, `routes/`, `services/` não
significa arquitetura correta — os achados CRITICAL (MD5, token forjável) estavam dentro dessas
pastas "organizadas".

---

## B) Construção da Skill

### Estrutura

A skill (`refactor-arch`) segue a convenção do Claude Code: `SKILL.md` como roteiro de
execução (o "prompt") + uma pasta `references/` com 5 arquivos Markdown, cada um cobrindo uma
das áreas de conhecimento exigidas:

- `project-analysis.md` — heurísticas de detecção de linguagem/framework/banco/domínio/
  arquitetura, baseadas em arquivos de manifesto (`requirements.txt`, `package.json`, etc.) e
  padrões de código, sem assumir nenhuma stack específica.
- `anti-patterns-catalog.md` — 12 anti-patterns (acima do mínimo de 8 exigido), cobrindo as 4
  severidades e incluindo uma seção dedicada a detecção de APIs/práticas deprecated.
- `audit-report-template.md` — formato exato do relatório da Fase 2 (o mesmo usado nos 3
  relatórios em `reports/`).
- `mvc-architecture-guidelines.md` — as 5 camadas obrigatórias da arquitetura alvo (Config,
  Models, Views/Routes, Controllers, Middlewares) e as regras que definem cada uma.
- `refactoring-playbook.md` — 12 padrões de transformação (acima do mínimo de 8), cada um com
  exemplo de código antes/depois em Python/Flask e/ou JS/Express.

O `SKILL.md` mantém as 3 fases obrigatórias (Análise → Auditoria com pausa de confirmação →
Refatoração com validação) e instrui explicitamente o agente a ler cada arquivo de referência
no momento certo, em vez de "reconstruir esse conhecimento de memória" — a ideia é que o
SKILL.md seja curto e sirva de roteiro, e o conhecimento de domínio pesado fique nos arquivos
de referência (mais fácil de manter e de revisar isoladamente).

### Anti-patterns escolhidos e por quê

O catálogo prioriza anti-patterns que apareceram de fato nos 3 projetos durante a análise
manual (God Class, credenciais hardcoded, SQL Injection, callback hell, estado global,
N+1, validação duplicada, hashing fraco/deprecated, magic numbers, uso de `print`/`console.log`
como log) — a lógica foi: catalogar primeiro o que realmente existe no código real, depois
generalizar o sinal de detecção o suficiente para pegar a mesma classe de problema em outra
linguagem (ex.: "SQL concatenado por string" descreve tanto `models.py` em Python quanto
`AppManager.js` em Node, sem amarrar a um driver específico).

### Como a skill foi mantida agnóstica de tecnologia

- Nenhuma heurística do `project-analysis.md` assume Python ou Flask — a detecção de
  linguagem/framework é feita por tabela de "arquivo de manifesto → linguagem provável" e por
  padrões de import, cobrindo Python, Node/JS, Go, Java, Ruby, PHP e .NET.
- O catálogo de anti-patterns descreve **sinais de detecção conceituais** ("query construída
  por concatenação de string com dado de entrada", não "`cursor.execute` do sqlite3 do
  Python"), e cada item lista exemplos em mais de uma sintaxe quando aplicável.
- O playbook traz exemplos antes/depois tanto em Python/Flask quanto em JS/Express — as duas
  stacks presentes nos 3 projetos — deixando explícito que o padrão de transformação (ex.:
  "extrair config para variável de ambiente") é o mesmo independente da linguagem.
- A prova real de agnosticismo foi a execução: a mesma pasta `refactor-arch/`, copiada sem
  nenhuma alteração, produziu relatórios e refatorações coerentes nos 3 projetos (2x
  Python/Flask com níveis de organização diferentes + 1x Node/Express).

### Desafios encontrados

- **Ambiente sandboxed sem `git rm`/`rm` no volume de entrega.** O diretório de trabalho
  montado (`D:\pos-ia`) bloqueia deleção/renomeação de arquivo a nível de sistema de arquivos.
  Isso quebra o fluxo normal de `git commit` (que depende de rename para escrever objetos/
  index) e impede remover fisicamente os arquivos legados (`controllers.py`, `models.py`,
  `database.py`, `AppManager.js`, etc.) direto nesse volume. Solução: todo o trabalho de
  refatoração e o histórico de commits foi produzido em um clone de trabalho local (com
  suporte total a delete/rename), e o resultado final foi copiado de volta para a pasta
  conectada ao usuário — ver seção "Como Executar" sobre como sincronizar/publicar a partir
  daqui.
- **Arquivo legado esquecido na primeira entrega.** Na primeira rodada, `ecommerce-api-legacy/
  src/AppManager.js` e `src/utils.js` foram corretamente recriados dentro de `src/` (God Class
  quebrada em models/controllers/services), mas os dois arquivos originais — com a chave
  `pk_live_...` hardcoded e o `console.log` do número do cartão — não foram removidos do
  repositório entregue, porque o ambiente sandboxed bloqueou a exclusão física (mesmo problema
  do item acima) e a lista de comandos `git rm` passada ao usuário não incluiu esses dois
  arquivos por engano. Correção: o passo 5 da Fase 3 do `SKILL.md` foi reforçado para tornar a
  remoção de arquivo legado uma etapa obrigatória e explicitamente reportada no resumo final
  (com fallback documentado para `git rm` quando delete físico não é possível), e os dois
  arquivos foram removidos na rodada seguinte antes deste commit.
- **`sqlite3` (driver Node.js) exige compilação nativa via `node-gyp`**, que falhou no sandbox
  por bloqueio de download dos headers do Node. Em vez de brigar com a toolchain nativa, a
  refatoração do projeto 2 trocou o driver por `node:sqlite` (módulo nativo do próprio Node
  ≥ 22.5, ainda experimental) — decisão documentada no próprio `src/config/database.js`, com
  nota de portabilidade para quem rodar em Node mais antigo (trocar por `better-sqlite3`
  mantendo a mesma assinatura `run/get/all`).
- **Achados que exigem quebra de contrato para serem corrigidos de verdade.** O endpoint
  `/admin/query` do projeto 1 (executa SQL arbitrário vindo do cliente) e o token
  `fake-jwt-token-<id>` do projeto 3 não têm uma versão "corrigida" que preserve o
  comportamento original — a funcionalidade em si era a vulnerabilidade. Nesses dois casos a
  skill (e esta execução) documentou explicitamente a mudança de contrato no relatório e no
  código, em vez de manter uma versão "meio corrigida" que desse falsa sensação de segurança.

---

## C) Resultados

### Resumo dos relatórios de auditoria

| Projeto | CRITICAL | HIGH | MEDIUM | LOW | Total |
|---|---|---|---|---|---|
| 1 — code-smells-project | 5 | 3 | 4 | 3 | 15 |
| 2 — ecommerce-api-legacy | 4 | 3 | 3 | 2 | 12 |
| 3 — task-manager-api | 5 | 3 | 3 | 2 | 13 |

Relatórios completos: `reports/audit-project-1.md`, `reports/audit-project-2.md`,
`reports/audit-project-3.md` — cada um segue exatamente o template de
`references/audit-report-template.md`, com achados ordenados por severidade e arquivo:linha
exatos.

### Antes / depois de cada projeto

**Projeto 1 (code-smells-project):** de 4 arquivos na raiz (`app.py`, `controllers.py`,
`models.py`, `database.py`, com SQL Injection generalizado e segredo hardcoded) para
`src/{config,models,routes,controllers,middlewares}/` com 5 models por domínio, queries
100% parametrizadas, config via variável de ambiente, error handler central e o endpoint de
execução de SQL arbitrário removido.

**Projeto 2 (ecommerce-api-legacy):** de uma God Class (`AppManager.js`, 141 linhas, callback
hell) para `src/{config,models,controllers,routes,middlewares,services}/`, com `async/await`
no lugar de callbacks aninhados, `bcryptjs` no lugar do "hash" falso, e credenciais/chave de
pagamento em variável de ambiente.

**Projeto 3 (task-manager-api):** de uma organização parcial (models/routes/services/utils
sem Controller nem Config, com MD5 e token forjável) para `src/{config,models,controllers,
routes,middlewares,services,utils}/`, com `werkzeug.security` no lugar de MD5, token assinado
com `itsdangerous` no lugar do token forjável, senha nunca mais retornada pela API, e a
função de validação que já existia (`process_task_data`) finalmente sendo usada.

### Checklist de validação (preenchido para os 3 projetos)

**Fase 1 — Análise**
- [x] Linguagem detectada corretamente (Python nos projetos 1 e 3, JavaScript/Node no projeto 2)
- [x] Framework detectado corretamente (Flask 3.1.1 / Express ^4.18.2 / Flask 3.0.0)
- [x] Domínio da aplicação descrito corretamente (E-commerce / LMS com checkout / Task Manager)
- [x] Número de arquivos analisados condiz com a realidade (4 / 3 / 15)

**Fase 2 — Auditoria**
- [x] Relatório segue o template definido nos arquivos de referência
- [x] Cada finding tem arquivo e linhas exatas
- [x] Findings ordenados por severidade (CRITICAL → LOW)
- [x] Mínimo de 5 findings identificados (15 / 12 / 13)
- [x] Detecção de APIs deprecated incluída (MD5 para senha, `Query.get()` do SQLAlchemy,
      `DEBUG=True` em produção, driver `sqlite3` baseado em callback)
- [x] Pausa de confirmação antes da Fase 3 (documentada no SKILL.md; nesta execução a
      confirmação foi dada explicitamente pelo usuário antes de qualquer refatoração)

**Fase 3 — Refatoração**
- [x] Estrutura de diretórios segue padrão MVC (`src/config|models|routes|controllers|
      middlewares` nos 3 projetos, + `services`/`utils` onde fazia sentido)
- [x] Configuração extraída para módulo de config (sem hardcoded) — `Config`/`config/index.js`
      lendo de variável de ambiente nos 3 projetos
- [x] Models criados/isolados para abstrair dados
- [x] Views/Routes separadas para roteamento
- [x] Controllers concentram o fluxo da aplicação
- [x] Error handling centralizado (`middlewares/error_handler.*` nos 3 projetos)
- [x] Entry point claro (`app.py` / `src/server.js` / `app.py`, todos como composition root)
- [x] Aplicação inicia sem erros (validado via boot real, ver logs abaixo)
- [x] Endpoints originais respondem corretamente (validado via `curl`, mesmo contrato)

### Logs de validação (aplicações rodando após a refatoração)

**Projeto 1 — boot + endpoints:**
```
==================================================
SERVIDOR INICIADO
Rodando em http://localhost:5000
==================================================
GET  /                          -> 200
GET  /health                    -> 200 {"status":"ok","database":"connected",...}
GET  /produtos                  -> 200
POST /produtos                  -> 201 {"dados":{"id":11},"sucesso":true,...}
GET  /produtos/busca?q=Notebook -> 200
POST /pedidos                   -> 201 {"dados":{"pedido_id":1,"total":5999.99},...}
GET  /relatorios/vendas         -> 200
POST /login                     -> 200 {"mensagem":"Login OK",...}
```

**Projeto 2 — boot + endpoints:**
```
API rodando na porta 3000...
POST /api/checkout (cartão aprovado)  -> 200 {"msg":"Sucesso","enrollment_id":2}
GET  /api/admin/financial-report      -> 200 [{"course":"Clean Architecture","revenue":1994,...}]
POST /api/checkout (cartão recusado)  -> 400 {"error":"Pagamento recusado"}
DELETE /api/users/1                   -> 200 {"message":"Usuário deletado"}
POST /api/checkout (payload inválido) -> 400
```

**Projeto 3 — seed + boot + endpoints:**
```
Seed concluído com sucesso!
  3 usuários
  4 categorias
  10 tasks

GET  /                    -> 200 {"message":"Task Manager API","version":"1.0"}
GET  /health               -> 200
POST /login                 -> 200 (token assinado, não mais "fake-jwt-token-1")
GET  /users                 -> 200 (sem campo "password" na resposta)
GET  /tasks                 -> 200
GET  /tasks/1                -> 200
POST /tasks                  -> 201
GET  /tasks/search?status=pending -> 200
GET  /tasks/stats                  -> 200
GET  /reports/summary              -> 200
GET  /reports/user/1               -> 200
GET  /categories                   -> 200
GET  /tasks/9999 (inexistente)     -> 404
```

### Observações sobre o comportamento em stacks diferentes

A mesma skill (sem nenhuma edição entre execuções) funcionou nos 2 projetos Python/Flask e no
projeto Node/Express. A principal diferença de comportamento entre eles foi na Fase 1: no
projeto 3 (já parcialmente organizado), a etapa de análise precisou reconhecer que a presença
de pastas `models/`/`routes/` não implicava ausência de problemas — os achados CRITICAL mais
graves (MD5, token forjável, exposição de senha) estavam justamente dentro dessas pastas
"organizadas". Isso confirma a orientação do catálogo de anti-patterns de nunca inferir
qualidade de arquitetura só pela presença de diretórios com nomes de camada.

---

## D) Como Executar

### Pré-requisitos

- [Claude Code](https://docs.claude.com/en/docs/claude-code) instalado e autenticado.
- Para reproduzir o boot de cada projeto localmente:
  - Projeto 1 e 3: Python 3.10+ e `pip`.
  - Projeto 2: Node.js ≥ 22.5 (usa o módulo nativo `node:sqlite`; se estiver em uma versão
    mais antiga, troque `src/config/database.js` para usar `better-sqlite3`, mantendo a mesma
    assinatura de funções).

### Executar a skill em cada projeto

```bash
# Projeto 1
cd code-smells-project
claude "/refactor-arch"

# Projeto 2 (a pasta .claude/skills/refactor-arch/ já está copiada aqui)
cd ../ecommerce-api-legacy
claude "/refactor-arch"

# Projeto 3 (a pasta .claude/skills/refactor-arch/ já está copiada aqui)
cd ../task-manager-api
claude "/refactor-arch"
```

A skill imprime o resumo da Fase 1, gera e imprime o relatório da Fase 2, salva-o em
`reports/audit-project-N.md`, e pausa pedindo confirmação (`Proceed with refactoring (Phase 3)?
[y/n]`) antes de tocar em qualquer arquivo.

### Como validar que a refatoração funcionou

**Projeto 1 (Flask):**
```bash
cd code-smells-project
python3 -m venv venv && ./venv/bin/pip install -r requirements.txt
./venv/bin/python app.py
# em outro terminal:
curl http://localhost:5000/health
curl http://localhost:5000/produtos
```

**Projeto 2 (Express):**
```bash
cd ecommerce-api-legacy
npm install
npm start
# em outro terminal:
curl -X POST http://localhost:3000/api/checkout \
  -H "Content-Type: application/json" \
  -d '{"usr":"Teste","eml":"teste@teste.com","pwd":"123456","c_id":1,"card":"4111111111111111"}'
```

**Projeto 3 (Flask):**
```bash
cd task-manager-api
python3 -m venv venv && ./venv/bin/pip install -r requirements.txt
./venv/bin/python seed.py     # popula o banco
./venv/bin/python app.py
# em outro terminal:
curl -X POST http://localhost:5000/login \
  -H "Content-Type: application/json" \
  -d '{"email":"joao@email.com","password":"1234"}'
curl http://localhost:5000/tasks
```

Em todos os casos, sucesso = a aplicação sobe sem exceção não tratada e os endpoints
originais (mesmas rotas/métodos do projeto legado) respondem com o mesmo contrato de
resposta observado antes da refatoração — exceto os 2 desvios de contrato deliberados e
documentados nos relatórios: remoção do endpoint `/admin/query` (projeto 1, SQL Injection por
design) e resposta de `/login` do projeto 3 passando a trazer um token assinado real em vez de
`fake-jwt-token-<id>`.

### Publicação no GitHub

Este workspace não tem credenciais do GitHub do autor configuradas para `git push`; o
histórico de commits (`chore: initial commit...` + 3 commits de refatoração, um por projeto)
foi produzido localmente. Para publicar: faça um fork de
`https://github.com/devfullcycle/mba-ia-refactor-projects-skill`, aponte o `origin` deste
diretório para o seu fork (`git remote set-url origin <seu-fork>.git`) e rode `git push`.
