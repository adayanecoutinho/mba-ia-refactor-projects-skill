================================
PHASE 1: PROJECT ANALYSIS
================================
Language:      Python
Framework:     Flask 3.1.1
Dependencies:  flask-cors 5.0.1
Domain:        E-commerce API (produtos, usuários, pedidos, relatório de vendas)
Architecture:  Monolítica — toda a aplicação em 4 arquivos (app.py, controllers.py, models.py,
               database.py), sem separação de camadas Model/View/Controller
Source files:  4 files analyzed
DB tables:     produtos, usuarios, pedidos, itens_pedido
================================

================================
ARCHITECTURE AUDIT REPORT
================================
Project: code-smells-project
Stack:   Python + Flask
Files:   4 analyzed | ~688 lines of code

Summary
CRITICAL: 5 | HIGH: 3 | MEDIUM: 4 | LOW: 3

Findings

[CRITICAL] God Class / God File
File: models.py:1-314
Description: Um único arquivo concentra todo o acesso a dados (queries SQL), regra de negócio
             (cálculo de total, verificação de estoque, desconto por faixa de faturamento) e
             formatação de resposta para 4 domínios diferentes (produtos, usuários, pedidos,
             relatórios).
Impact: Impossível testar qualquer domínio isoladamente; qualquer alteração em um domínio tem
        risco de efeito colateral nos outros; onboarding de novos devs é lento.
Recommendation: Dividir em um model por domínio (produto_model.py, usuario_model.py,
                pedido_model.py) — ver playbook, padrão #2.

[CRITICAL] Hardcoded Credentials / Secrets
File: app.py:7-8; controllers.py:289
Description: `SECRET_KEY` e `DEBUG` fixos no código-fonte (app.py:7-8). Além disso, o endpoint
             `/health` retorna a própria `secret_key` em texto puro na resposta JSON
             (controllers.py:289), expondo o segredo publicamente a qualquer chamador.
Impact: Comprometimento total de sessões/tokens assinados com essa chave; qualquer cliente da
        API pode ler a secret key chamando `/health`.
Recommendation: Extrair para variável de ambiente com default seguro apenas para dev — ver
                playbook, padrão #1. Nunca retornar segredos em respostas de API.

[CRITICAL] SQL Injection
File: models.py:28, 48-50, 58-61, 68, 92, 109-111, 127-129, 140, 148-151, 155-166, 174, 188,
      192, 203-233, 279-280, 289-297
Description: Praticamente todas as queries do arquivo são construídas por concatenação de
             string com dados de entrada do usuário (`"WHERE id = " + str(id)`,
             `"WHERE email = '" + email + "' AND senha = '" + senha + "'"`), sem uso de
             parâmetros. O caso do login (models.py:109-111) é particularmente grave: permite
             bypass de autenticação via injeção clássica (`' OR '1'='1`).
Impact: Vazamento, adulteração ou destruição total do banco de dados; bypass de autenticação.
Recommendation: Trocar toda concatenação por placeholders parametrizados (`?`) — ver playbook,
                padrão #3.

[CRITICAL] SQL Injection / Execução de Query Arbitrária
File: app.py:59-78
Description: O endpoint `/admin/query` recebe uma string SQL diretamente do corpo da
             requisição (`dados.get("sql", "")`) e a executa sem nenhuma validação, sanitização
             ou allowlist.
Impact: É, por definição, uma porta aberta para execução de qualquer comando SQL (leitura,
        escrita ou destruição de dados) por qualquer cliente não autenticado.
Recommendation: Remover o endpoint. Não existe forma de "corrigir" esse contrato mantendo a
                funcionalidade original — a funcionalidade em si é a vulnerabilidade.

[CRITICAL] Armazenamento de Senha em Texto Puro
File: models.py:105-120 (login_usuario), 122-131 (criar_usuario), database.py:75-83 (seed)
Description: Senhas de usuário são gravadas e comparadas em texto puro (nenhum hashing é
             aplicado em nenhum momento do fluxo de cadastro/login).
Impact: Qualquer acesso de leitura ao banco (inclusive via o próprio SQL Injection acima)
        expõe as senhas de todos os usuários em claro.
Recommendation: Aplicar hashing seguro (`werkzeug.security.generate_password_hash` /
                `check_password_hash`) — ver playbook, padrão #11.

[HIGH] Estado Global Mutável sem Injeção de Dependência
File: database.py:4, 7-11
Description: A conexão com o banco é um singleton implícito guardado em uma variável de módulo
             (`db_connection`) manipulada via `global`, em vez de ser criada no composition
             root e injetada explicitamente.
Impact: Dificulta testes (impossível trocar a conexão por um mock/banco de teste sem
        monkeypatch), e esconde uma dependência importante da aplicação.
Recommendation: Criar a conexão no composition root e injetá-la via `app.config` — ver
                playbook, padrão #7.

[HIGH] Regra de Negócio Crítica Misturada com Acesso a Dados sem Abstração de Service
File: models.py:133-169 (criar_pedido)
Description: O cálculo de total do pedido e a verificação de estoque (regra de negócio de
             checkout) estão emaranhados nas mesmas linhas que executam INSERT/UPDATE SQL,
             sem nenhuma função isolável e testável sem um banco real.
Impact: Não é possível escrever um teste unitário da regra "não permitir pedido sem estoque"
        sem subir um banco SQLite de verdade.
Recommendation: Manter a regra no Model (camada de dados já é o lugar certo em MVC simples),
                mas isolar o cálculo em uma função pura auxiliar testável separadamente.

[HIGH] Efeito Colateral de Notificação Simulado Dentro do Controller
File: controllers.py:208-210
Description: O controller de criação de pedido imprime diretamente "ENVIANDO EMAIL",
             "ENVIANDO SMS", "ENVIANDO PUSH" — simulando disparo de notificações — misturando
             uma responsabilidade de integração externa com o handler HTTP.
Impact: Impossível reaproveitar/testar a lógica de notificação fora do contexto de uma
        requisição HTTP; quando a notificação virar uma integração real, o controller crescerá
        ainda mais.
Recommendation: Extrair para uma camada de serviço de notificação dedicada (fora do escopo
                estrito de MVC desta refatoração, mas documentado como próximo passo).

[MEDIUM] N+1 Queries
File: models.py:187-199 (get_pedidos_usuario), 219-231 (get_todos_pedidos)
Description: Para cada pedido, o código abre um cursor e executa uma query para buscar seus
             itens, e para cada item abre outro cursor para buscar o nome do produto —
             1 + N + M queries em vez de uma consulta com JOIN.
Impact: Degradação de performance proporcional ao número de pedidos e itens; múltiplos objetos
        `cursor` concorrentes na mesma conexão.
Recommendation: Substituir por uma única query com JOIN — ver playbook, padrão #8.

[MEDIUM] Validação Duplicada Entre Rotas
File: controllers.py:28-54 (criar_produto), 72-90 (atualizar_produto)
Description: As mesmas 7 validações de campo (nome, preço, estoque, categoria) são copiadas e
             coladas entre os dois handlers, em vez de centralizadas em uma função de
             validação reutilizável.
Impact: Alto risco de as duas cópias divergirem ao longo do tempo (uma delas ser corrigida e a
        outra não).
Recommendation: Extrair para uma função `validar_payload_produto()` única — ver playbook,
                padrão #9.

[MEDIUM] CORS Aberto Sem Restrição de Origem
File: app.py:9
Description: `CORS(app)` é chamado sem nenhuma configuração de origem permitida, liberando a
             API para qualquer domínio.
Impact: Facilita ataques de CSRF/exfiltração de dados a partir de sites de terceiros quando
        combinado com autenticação baseada em cookie.
Recommendation: Configurar `origins` explicitamente por ambiente (variável de config).

[MEDIUM] Debug Habilitado por Padrão (prática desaconselhada / API deprecated de uso)
File: app.py:8, 88
Description: `app.config["DEBUG"] = True` fixo no código e `app.run(..., debug=True)` sem
             depender de variável de ambiente. A documentação oficial do Flask desaconselha
             explicitamente rodar com o debugger ativo fora de desenvolvimento local, pois ele
             expõe um console interativo de execução de código arbitrário via navegador.
Impact: Se implantado assim em produção por engano, qualquer erro não tratado abre um console
        de execução remota de código para quem acessar a página de erro.
Recommendation: `DEBUG` deve vir de variável de ambiente, com default `False`.

[LOW] Magic Numbers nas Faixas de Desconto
File: models.py:256-262
Description: Os limiares de faturamento (`10000`, `5000`, `1000`) e taxas de desconto (`0.1`,
             `0.05`, `0.02`) estão soltos no meio da função, sem nome semântico.
Impact: Regra de negócio importante fica difícil de encontrar, revisar e ajustar.
Recommendation: Nomear como constantes de configuração — ver playbook, padrão #12.

[LOW] Uso de print() Como Mecanismo de Log
File: controllers.py:8, 11, 57, 61, 106, 161, 179, 182, 208-210, 219, 248, 250
Description: Dezenas de `print()` espalhados pelos handlers fazem o papel de logging, sem
             níveis, formato ou destino configuráveis.
Impact: Impossível filtrar por severidade ou desligar logs verbosos em produção; nenhuma
        estrutura para agregação de logs.
Recommendation: Usar `app.logger` (logging padrão do Flask) com níveis apropriados.

[LOW] Nomenclatura Genérica em Handler Administrativo
File: app.py:60-62
Description: Variáveis `dados` e `query` no handler de `/admin/query` não comunicam o risco
             da operação que representam (execução de SQL arbitrário).
Impact: Reduz a chance de um revisor notar o problema de segurança ao ler o código
        rapidamente.
Recommendation: Resolvido de forma definitiva pela remoção do endpoint (ver achado CRITICAL
                correspondente).

================================
Total: 15 findings
================================
