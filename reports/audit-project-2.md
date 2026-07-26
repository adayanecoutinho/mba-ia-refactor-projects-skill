================================
PHASE 1: PROJECT ANALYSIS
================================
Language:      JavaScript (Node.js)
Framework:     Express ^4.18.2
Dependencies:  sqlite3 ^5.1.6 (driver original, baseado em callback)
Domain:        LMS / plataforma de cursos com checkout de pagamento (matrículas, pagamentos,
               relatório financeiro para admin)
Architecture:  God Class — toda a aplicação (schema do banco, rotas, regra de pagamento,
               relatório financeiro) concentrada em uma única classe `AppManager`
               (src/AppManager.js), instanciada e conectada ao Express em src/app.js
Source files:  3 files analyzed (src/app.js, src/AppManager.js, src/utils.js)
DB tables:     users, courses, enrollments, payments, audit_logs
================================

================================
ARCHITECTURE AUDIT REPORT
================================
Project: ecommerce-api-legacy
Stack:   Node.js + Express
Files:   3 analyzed | ~165 lines of code

Summary
CRITICAL: 4 | HIGH: 3 | MEDIUM: 3 | LOW: 2

Findings

[CRITICAL] God Class
File: src/AppManager.js:1-141
Description: Uma única classe cria e mantém a conexão com o banco (constructor), define o
             schema (initDb) e implementa as 3 rotas da API com toda a regra de negócio de
             checkout e relatório financeiro (setupRoutes), tudo no mesmo arquivo.
Impact: Impossível testar a regra de checkout sem subir o Express inteiro; qualquer mudança de
        schema, rota ou regra de negócio mexe no mesmo arquivo monolítico.
Recommendation: Separar em models por entidade (User, Course, Enrollment, Payment, AuditLog),
                controllers por caso de uso e routes por recurso — ver playbook, padrões #2 e #4.

[CRITICAL] Hardcoded Credentials / Secrets
File: src/utils.js:2-6
Description: `dbUser`, `dbPass`, `paymentGatewayKey` (chave de gateway de pagamento) e
             `smtpUser` estão escritos diretamente no código-fonte, incluindo uma chave com
             prefixo `pk_live_` (indicativo de chave de produção real).
Impact: Qualquer pessoa com acesso ao repositório tem a chave de pagamento e credenciais de
        banco/SMTP de produção.
Recommendation: Mover para variáveis de ambiente via `dotenv` — ver playbook, padrão #1.

[CRITICAL] Hashing de Senha Falso ("badCrypto")
File: src/utils.js:17-23 (definição); src/AppManager.js:68 (uso)
Description: A função `badCrypto` não é um algoritmo de hashing criptográfico — apenas repete
             uma codificação Base64 truncada 10.000 vezes e corta o resultado em 10 caracteres.
             É trivialmente reversível/colidível, ao contrário de um hash real.
Impact: Senhas de usuário ficam, na prática, sem proteção nenhuma caso o banco vaze.
Recommendation: Substituir por `bcrypt`/`bcryptjs` — ver playbook, padrão #11.

[CRITICAL] Dado Sensível (número de cartão + chave de gateway) em Log Não Estruturado
File: src/AppManager.js:45
Description: `console.log(\`Processando cartão ${cc} na chave ${config.paymentGatewayKey}\`)`
             grava o número completo do cartão de crédito informado pelo cliente junto com a
             chave secreta do gateway de pagamento, em texto puro, no log padrão da aplicação.
Impact: Qualquer sistema de agregação de logs (ou acesso ao stdout do processo) passa a
        armazenar dados de cartão em claro — violação direta de práticas mínimas de segurança
        de dados de pagamento (PCI).
Recommendation: Nunca logar PAN de cartão nem segredos; logar no máximo um identificador
                mascarado (ex.: últimos 4 dígitos).

[HIGH] Callback Hell / Pyramid of Doom
File: src/AppManager.js:37-77 (checkout), 80-129 (financial-report)
Description: Os dois handlers principais encadeiam 3 a 5 níveis de callbacks aninhados do
             driver `sqlite3` (`db.get(..., (err, x) => { db.get(..., (err, y) => {...}) })`),
             incluindo contadores manuais (`pending--`) para simular espera de operações
             assíncronas paralelas no relatório financeiro.
Impact: Fluxo de controle difícil de seguir, tratar erro e testar; risco real de bug (o
        relatório teria um "race" sutil se duas requisições concorrentes reaproveitassem a
        variável `report` do escopo externo).
Recommendation: Reescrever com `async/await` sobre uma versão Promise-friendly do driver —
                ver playbook, padrão #6.

[HIGH] Lógica de Negócio de Pagamento Dentro do Route Handler
File: src/AppManager.js:43-64
Description: A decisão de aprovação/recusa do pagamento (`cc.startsWith("4")`), a criação da
             matrícula e o registro do pagamento estão todos inline dentro do callback da rota
             `/api/checkout`, sem nenhuma camada de Controller/Model separada.
Impact: Regra de negócio de pagamento não pode ser reaproveitada nem testada fora do contexto
        HTTP.
Recommendation: Extrair para Controller (orquestração) + Models (persistência) — ver playbook,
                padrão #5.

[HIGH] Estado Global Mutável Compartilhado
File: src/utils.js:9-10, 12-15
Description: `globalCache` e `totalRevenue` são variáveis mutáveis em nível de módulo,
             escritas por `logAndCache` a partir de qualquer requisição concorrente, sem
             nenhum mecanismo de isolamento por request.
Impact: Estado compartilhado entre requisições concorrentes sem controle, e impossível de
        mockar em teste sem reiniciar o processo Node inteiro.
Recommendation: Encapsular em um serviço instanciado no composition root e injetado por
                requisição — ver playbook, padrão #7.

[MEDIUM] N+1 Queries no Relatório Financeiro
File: src/AppManager.js:83-127
Description: Para cada curso, busca as matrículas; para cada matrícula, busca o usuário e o
             pagamento em queries separadas — resultando em `1 + N + (2 × M)` queries para
             N cursos e M matrículas totais.
Impact: Tempo de resposta do relatório cresce linearmente com o número de matrículas; sob
        carga, é um dos primeiros endpoints a degradar.
Recommendation: Uma única query com `JOIN` por curso — ver playbook, padrão #8.

[MEDIUM] Integridade Referencial Quebrada Deliberadamente ao Deletar Usuário
File: src/AppManager.js:131-137
Description: O endpoint `DELETE /api/users/:id` remove o usuário mas deixa matrículas e
             pagamentos órfãos — o próprio texto de resposta da API admite isso
             ("...ficaram sujos no banco").
Impact: Relatórios futuros (ex.: financial-report) podem quebrar ou mostrar dados
        inconsistentes ao encontrar `user_id` sem usuário correspondente.
Recommendation: Documentar explicitamente a limitação (mantida nesta refatoração para
                preservar o contrato de API) e recomendar exclusão em cascata ou soft-delete
                como próximo passo, fora do escopo desta rodada de MVC.

[MEDIUM] Respostas HTTP Inconsistentes (texto puro vs. JSON)
File: src/AppManager.js:35, 38, 41, 48, 51, 55, 60, 70, 84, 133-136
Description: Alguns erros são retornados com `res.status(...).send("texto")` (string pura) e
             outros com `res.json({...})`, sem um formato de erro padronizado nem um handler
             central.
Impact: Clientes da API precisam tratar dois formatos de erro diferentes dependendo do
        endpoint/situação.
Recommendation: Centralizar em um middleware de erro único — ver playbook, padrão #10.

[LOW] Magic Strings para Status de Pagamento e Regra de Aprovação
File: src/AppManager.js:46, 54
Description: `"PAID"`/`"DENIED"` e o prefixo `"4"` usado para "aprovar" um cartão de teste
             estão soltos como literais, sem constante nomeada.
Impact: Reduz legibilidade e facilita erro de digitação ao comparar strings de status em
        outros pontos do código.
Recommendation: Nomear como constantes em `config/index.js` — ver playbook, padrão #12.

[LOW] Nomenclatura de Parâmetros de Uma Letra
File: src/AppManager.js:29-33
Description: `u`, `e`, `p`, `cid`, `cc` para nome, e-mail, senha, id do curso e cartão,
             respectivamente — nomes não comunicam o dado que carregam.
Impact: Aumenta o tempo de leitura/revisão do handler mais crítico da aplicação (pagamento).
Recommendation: Usar destructuring com nomes completos (`{ usr: name, eml: email, ... }`).

================================
Total: 12 findings
================================
