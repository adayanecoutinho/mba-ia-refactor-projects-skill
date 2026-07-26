# Guidelines de Arquitetura MVC Alvo (Fase 3)

Estas regras definem o padrão MVC que a skill deve produzir, independentemente da linguagem.

## Camadas obrigatórias

1. **Config** (`config/`): centraliza toda configuração e segredos. Lê de variáveis de
   ambiente (`.env` via `python-dotenv`/`dotenv`/`os.environ`/`process.env`), nunca hardcoded.
   Expõe um único ponto de acesso (ex.: `settings.py` com um objeto/dict `Config`, ou
   `config/index.js`).

2. **Models** (`models/`): representam entidades de domínio e encapsulam **todo** o acesso a
   dados (queries, ORM). Um model por entidade/domínio (ex.: `produto_model.py`,
   `usuario_model.py`, ou classes ORM `Course`, `User`). Nenhuma query SQL deve existir fora
   desta camada. Toda query com parâmetros de entrada do usuário deve ser parametrizada
   (nunca concatenação de string).

3. **Views/Routes** (`views/` ou `routes/`): apenas definição de rotas/endpoints e o mapeamento
   HTTP → Controller. Não contém lógica de negócio nem acesso a dados. Um arquivo de rotas pode
   agrupar por domínio (ex.: `routes/produtos.py`, `routes/pedidos.py`) ou ficar em um único
   `routes.py` se o projeto for pequeno — desde que só faça roteamento.

4. **Controllers** (`controllers/`): orquestram o fluxo de uma requisição — chamam Models,
   aplicam regra de negócio (ou delegam a uma camada de Service quando a regra for complexa
   o bastante para merecer isolamento e teste próprio), formatam a resposta HTTP (status code +
   payload). Um controller por domínio.

5. **Middlewares** (`middlewares/`): tratamento de erro centralizado (um único lugar que
   converte exceções em respostas HTTP padronizadas), e outros cross-cutting concerns (CORS,
   auth, logging de requisição).

6. **Entry point / Composition root** (`app.py`, `src/app.js`, etc.): monta a aplicação —
   cria a instância do framework, registra config, registra middlewares, registra rotas, e
   sobe o servidor. Não deve conter lógica de negócio nem definição de rotas inline.

## Regras adicionais

- **Uma responsabilidade por arquivo/classe** (Single Responsibility). Se um arquivo mistura 2+
  domínios de negócio (produtos + pedidos + usuários), ele deve ser dividido por domínio.
- **Sem estado global mutável compartilhado** entre requisições fora de uma camada de
  infraestrutura explícita (ex.: pool de conexão passado por injeção/factory, não uma variável
  solta no módulo sendo escrita por handlers).
- **Contratos de API preservados**: mesmas rotas, métodos HTTP, formatos de request/response
  do projeto original, a menos que o achado da auditoria exija uma mudança de contrato para
  corrigir uma falha de segurança (nesse caso, documente a mudança no relatório e no README).
- **Configuração nunca hardcoded**: toda credencial/segredo/porta deve vir de variável de
  ambiente com um valor default seguro apenas para desenvolvimento local (nunca um segredo
  real como default).
- **Erro centralizado**: um único handler/middleware converte exceções em respostas HTTP
  consistentes (mesmo formato de erro em toda a API), em vez de cada rota reimplementar
  `try/except`/`try/catch` com uma resposta diferente.
- **Idiomatismo da linguagem**: siga a convenção de nomes e organização de módulos idiomática
  da stack (ex.: Flask usa Blueprints para rotas; Express usa Router; snake_case em Python,
  camelCase em JS/Node), mas as 5 camadas conceituais acima devem sempre existir.
