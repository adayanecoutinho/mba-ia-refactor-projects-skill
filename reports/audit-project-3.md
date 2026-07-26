================================
PHASE 1: PROJECT ANALYSIS
================================
Language:      Python
Framework:     Flask 3.0.0
Dependencies:  flask-sqlalchemy 3.1.1, flask-cors 4.0.0, marshmallow 3.20.1 (importada no
               requirements.txt mas nunca usada no código), requests 2.31.0 (idem),
               python-dotenv 1.0.0
Domain:        Task Manager (tarefas, usuários, categorias, relatórios de produtividade)
Architecture:  Parcialmente organizada — já existem pastas models/, routes/, services/,
               utils/, mas os handlers dentro de routes/ ainda fazem serialização manual,
               reimplementam a mesma lógica de negócio (cálculo de "atrasada") em 3 lugares
               diferentes, e não existe camada de Controller nem de Config centralizada;
               segredos e credenciais de SMTP ficam hardcoded dentro de classes de serviço.
Source files:  15 files analyzed (app.py, database.py, seed.py, models/*.py [4], routes/*.py
               [4], services/*.py [2], utils/*.py [2])
DB tables:     users, categories, tasks (SQLAlchemy declarative models)
================================

================================
ARCHITECTURE AUDIT REPORT
================================
Project: task-manager-api
Stack:   Python + Flask + Flask-SQLAlchemy
Files:   15 analyzed | ~520 lines of code

Summary
CRITICAL: 5 | HIGH: 3 | MEDIUM: 3 | LOW: 2

Findings

[CRITICAL] Hardcoded Secret Key
File: app.py:13
Description: `app.config['SECRET_KEY'] = 'super-secret-key-123'` fixo no código-fonte.
Impact: Compromete qualquer mecanismo de assinatura (sessão, token) baseado nessa chave.
Recommendation: Extrair para variável de ambiente — ver playbook, padrão #1.

[CRITICAL] Hashing de Senha Deprecated/Inseguro (MD5)
File: models/user.py:3, 27-29, 31-32
Description: `hashlib.md5(pwd.encode()).hexdigest()` é usado tanto para gravar quanto para
             comparar a senha. MD5 é criptograficamente quebrado e explicitamente desaconselhado
             pela própria documentação do Python para uso em senhas (API "deprecated" para este
             propósito).
Impact: Senhas podem ser revertidas via rainbow tables/força bruta em segundos.
Recommendation: Trocar por `werkzeug.security.generate_password_hash`/`check_password_hash`
                (já é dependência transitiva do Flask) — ver playbook, padrão #11.

[CRITICAL] Credenciais SMTP Hardcoded
File: services/notification_service.py:9-10
Description: `self.email_user = 'taskmanager@gmail.com'` e
             `self.email_password = 'senha123'` fixos no construtor da classe.
Impact: Qualquer pessoa com acesso ao repositório pode autenticar como essa conta de e-mail.
Recommendation: Ler de variáveis de ambiente — ver playbook, padrão #1.

[CRITICAL] Token de Autenticação Falso e Previsível
File: routes/user_routes.py:210
Description: `'token': 'fake-jwt-token-' + str(user.id)` — o "token" retornado no login é
             apenas o prefixo fixo concatenado com o ID do usuário, sem nenhuma assinatura
             criptográfica. Qualquer cliente pode forjar um token válido para qualquer usuário
             apenas conhecendo (ou adivinhando) o ID.
Impact: Bypass completo de autenticação/personificação de qualquer usuário do sistema.
Recommendation: Emitir um token assinado (HMAC/JWT real) com a SECRET_KEY da aplicação — ver
                playbook, padrão equivalente ao #11 aplicado a tokens de sessão.

[CRITICAL] Exposição do Hash de Senha nas Respostas da API
File: models/user.py:16-25 (to_dict inclui `password`); usado em routes/user_routes.py:15-25,
      33, 85-86, 129
Description: `User.to_dict()` inclui o campo `password` (o hash), retornado em `GET /users`,
             `GET /users/<id>` e na resposta de criação/atualização de usuário — expondo o hash
             de todos os usuários a qualquer chamador da API.
Impact: Combinado com o hashing fraco (achado anterior), permite quebra de senha de qualquer
        usuário só chamando `GET /users`.
Recommendation: Nunca serializar o campo de senha (nem o hash) em resposta HTTP.

[HIGH] Lógica de "Atrasada" (overdue) Duplicada em 3 Route Handlers
File: routes/task_routes.py:30-39, 71-80; routes/user_routes.py:171-180
Description: O mesmo bloco de decisão aninhada (`if due_date: if due_date < now: if status not
             in (done, cancelled): overdue = True`) é copiado e colado em 3 handlers
             diferentes — apesar de `models/task.py` já ter um método `is_overdue()` pronto
             para isso, que nunca é chamado em lugar nenhum do projeto.
Impact: Alto risco de as 3 cópias divergirem (já haviam pequenas diferenças de formatação
        entre elas); lógica de negócio importante espalhada em vez de centralizada.
Recommendation: Reusar `Task.is_overdue()` a partir de um único lugar (o `to_dict()` do model,
                chamado pelos controllers) — ver playbook, padrão #2 (Model concentra a regra).

[HIGH] Serialização Manual e Regra de Negócio Dentro das Rotas (Fat Route Handler)
File: routes/task_routes.py:11-63
Description: `get_tasks()` monta o dicionário de resposta campo a campo manualmente, decide
             overdue, e faz uma query adicional de `User`/`Category` por task dentro do
             próprio handler de rota — sem nenhuma camada de Controller intermediária, mesmo o
             projeto já tendo pastas de camada.
Impact: Rota mistura formatação HTTP com regra de domínio; impossível reusar a lógica de
        serialização fora de um request Flask.
Recommendation: Mover para Controller + `Task.to_dict()` — ver playbook, padrão #5.

[HIGH] Uso de API Deprecated do SQLAlchemy (`Query.get()`)
File: routes/task_routes.py:67, 158, 227; routes/user_routes.py:29, 94, 136;
      routes/report_routes.py:105, 192, 213
Description: `Model.query.get(id)` está marcado como legado desde SQLAlchemy 2.0 /
             Flask-SQLAlchemy 3.x (gera `LegacyAPIWarning`); a forma recomendada atual é
             `db.session.get(Model, id)`.
Impact: Código roda hoje, mas depende de uma API que pode ser removida em versões futuras do
        SQLAlchemy; gera warnings em cada chamada.
Recommendation: Substituir todas as ocorrências por `db.session.get(Model, id)`.

[MEDIUM] N+1 Queries no Relatório de Produtividade
File: routes/report_routes.py:53-68
Description: Para cada usuário retornado por `User.query.all()`, o código executa
             `Task.query.filter_by(user_id=u.id).all()` dentro do loop — uma query de tasks
             por usuário, em vez de uma única leitura agrupada.
Impact: Tempo do endpoint `/reports/summary` cresce linearmente com o número de usuários.
Recommendation: Buscar todas as tasks uma vez e agrupar em memória por `user_id` — ver
                playbook, padrão #8 (mesmo princípio de eliminar N+1).

[MEDIUM] Validação Duplicada Apesar de Helper Já Existir
File: routes/task_routes.py:92-144, 166-223; utils/helpers.py:57-108 (`process_task_data`)
Description: `utils/helpers.py` já define `process_task_data()`, uma função de validação
             completa para o payload de task — mas ela nunca é importada ou chamada em nenhum
             lugar do projeto. Os handlers de `create_task`/`update_task` reimplementam a
             mesma validação manualmente e de forma ligeiramente diferente entre si.
Impact: Código morto (a função correta já existe, mas ninguém usa) e duas versões da mesma
        regra de validação que podem divergir.
Recommendation: Reusar `process_task_data()` a partir do Controller — ver playbook, padrão #9.

[MEDIUM] CORS Aberto Sem Restrição de Origem
File: app.py:15
Description: `CORS(app)` sem configuração de `origins`, liberando a API para qualquer domínio.
Impact: Facilita ataques de exfiltração de dados via terceiros quando combinado com o
        token fraco descrito acima.
Recommendation: Restringir `origins` por variável de ambiente/config.

[LOW] Imports Não Utilizados / Código Morto
File: app.py:7 (`os, sys, json` nunca usados); routes/task_routes.py:7 (`json, os, sys, time`
      nunca usados); utils/helpers.py (`sanitize_string`, `generate_id`, `log_action` nunca
      chamadas em lugar nenhum do projeto)
Description: Vários imports e funções utilitárias existem mas nunca são referenciados.
Impact: Ruído de leitura, sinaliza para quem mantém o código que aquelas funções "devem"
        estar em uso em algum lugar (elas não estão).
Recommendation: Remover imports não usados; manter apenas utilitários efetivamente chamados.

[LOW] Mapeamento de Prioridade Hardcoded Sem Constante Compartilhada
File: routes/report_routes.py:24-28, 83-89
Description: O mapeamento de prioridade numérica (1-5) para rótulo (`critical`, `high`,
             `medium`, `low`, `minimal`) é escrito inline como 5 variáveis `p1`..`p5`, sem uma
             constante nomeada e compartilhável com o resto da aplicação.
Impact: Se o rótulo de uma prioridade mudar, é preciso lembrar de atualizar em todos os lugares
        que o replicam.
Recommendation: Centralizar em `Config.PRIORITY_LABELS` — ver playbook, padrão #12.

================================
Total: 13 findings
================================
