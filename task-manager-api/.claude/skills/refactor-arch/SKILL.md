---
name: refactor-arch
description: Audita uma codebase de API (qualquer linguagem/framework), detecta anti-patterns de arquitetura MVC/SOLID com severidade, gera relatório de auditoria e refatora o projeto para o padrão MVC, validando que a aplicação continua funcionando. Use quando o usuário disser "/refactor-arch", pedir para auditar arquitetura, encontrar code smells, ou migrar um projeto legado para MVC.
---

# Refactor Arch — Auditoria e Refatoração para MVC

Você é um agente de arquitetura de software. Seu trabalho é auditar um projeto de API
(agnóstico de linguagem/framework) e refatorá-lo para o padrão **MVC** (Model / View-Routes /
Controller), eliminando anti-patterns de arquitetura e SOLID. Você NUNCA modifica arquivos sem
antes mostrar o relatório de auditoria completo e receber confirmação explícita do usuário.

Este SKILL.md é o roteiro de execução. O conhecimento de domínio (como detectar stack, o
catálogo de anti-patterns, o template do relatório, as regras de MVC-alvo e o playbook de
transformação) está nos arquivos de referência desta pasta (`references/`). Leia cada um deles
no momento indicado abaixo — não tente reconstruir esse conhecimento de memória.

Execute sempre as 3 fases, nesta ordem, e nunca pule a pausa de confirmação entre a Fase 2 e a
Fase 3.

## Fase 1 — Análise do Projeto

1. Leia `references/project-analysis.md` para as heurísticas de detecção.
2. Percorra a raiz do projeto (arquivos de manifesto: `requirements.txt`, `package.json`,
   `Pipfile`, `go.mod`, `pom.xml`, etc.) e o código-fonte para identificar:
   - Linguagem e versão (se inferível)
   - Framework web e versão
   - Bibliotecas/dependências relevantes (ORM, driver de banco, CORS, etc.)
   - Banco de dados usado e tabelas/entidades (via `CREATE TABLE`, migrations, models ORM)
   - Domínio de negócio da aplicação (o que a API faz — infira pelas rotas/entidades)
   - Arquitetura atual (monolítica em poucos arquivos? já tem camadas? mistura tudo?)
   - Número de arquivos de código-fonte analisados (não conte `node_modules`, `venv`, `.git`)
3. Imprima um resumo no formato abaixo (adapte os campos ao que foi encontrado; não invente
   dados que não existem no código):

```
================================
PHASE 1: PROJECT ANALYSIS
================================
Language:      <linguagem>
Framework:     <framework + versão>
Dependencies:  <lista curta de deps relevantes>
Domain:        <domínio de negócio inferido>
Architecture:  <descrição curta da arquitetura atual>
Source files:  <N> files analyzed
DB tables:     <tabelas/entidades encontradas>
================================
```

## Fase 2 — Auditoria (Anti-patterns)

1. Leia `references/anti-patterns-catalog.md` (catálogo com sinais de detecção e severidade)
   e `references/audit-report-template.md` (formato do relatório).
2. Para cada arquivo de código-fonte relevante, procure os sinais de detecção do catálogo.
   Para cada achado, registre: nome do anti-pattern, severidade (CRITICAL/HIGH/MEDIUM/LOW),
   arquivo e **linha(s) exatas**, descrição do problema, impacto, e recomendação de correção
   (referenciando o padrão de transformação do playbook quando aplicável).
3. Inclua explicitamente uma checagem de **APIs/práticas deprecated** (ver seção própria no
   catálogo) — versões de framework antigas, funções descontinuadas, padrões de callback
   obsoletos, etc.
4. Ordene os achados por severidade: CRITICAL → HIGH → MEDIUM → LOW. Dentro da mesma
   severidade, ordene por arquivo.
5. Gere o relatório completo seguindo `references/audit-report-template.md` e salve-o em
   `reports/audit-<slug-do-projeto>.md` na raiz do repositório (crie a pasta `reports/` se
   necessário, um nível acima da pasta do projeto se for um subprojeto dentro de um monorepo).
6. Exiba o relatório no terminal.
7. **PARE aqui.** Pergunte explicitamente: "Proceed with refactoring (Phase 3)? [y/n]" e
   aguarde a resposta do usuário. Não avance para a Fase 3 sem confirmação explícita ("y",
   "sim", "yes", ou equivalente inequívoco). Se o usuário disser não, encerre e não modifique
   nenhum arquivo.

## Fase 3 — Refatoração para MVC

1. Leia `references/mvc-architecture-guidelines.md` (regras da arquitetura alvo) e
   `references/refactoring-playbook.md` (padrões de transformação com exemplos antes/depois).
2. Crie a nova estrutura de diretórios MVC dentro do projeto (tipicamente `src/` com
   `config/`, `models/`, `views/` ou `routes/`, `controllers/`, `middlewares/`, e um
   composition root/entry point). Adapte os nomes às convenções idiomáticas da linguagem
   (ex.: `snake_case` em Python, `camelCase`/PascalCase em JS), mas mantenha as 5 camadas
   exigidas.
3. Para cada finding do relatório da Fase 2, aplique o padrão de transformação correspondente
   do playbook:
   - Extraia configuração/segredos para um módulo de config, lendo de variáveis de ambiente
     (nunca hardcoded).
   - Separe queries e regras de acesso a dados em Models.
   - Separe roteamento em Views/Routes.
   - Separe orquestração e regra de negócio em Controllers (ou Controllers + Services quando
     a lógica de negócio for complexa o suficiente para merecer sua própria camada, mantendo
     o Controller fino).
   - Centralize tratamento de erros em um middleware/handler único.
   - Elimine SQL string-concatenado, substituindo por queries parametrizadas.
   - Elimine prints soltos como "logging", credenciais hardcoded, magic numbers e nomes ruins.
4. Preserve o **comportamento e os contratos de API existentes** (mesmas rotas, métodos,
   payloads de entrada/saída) — isso é refatoração, não reescrita de produto. Novas camadas
   internas podem mudar; a superfície pública da API não deve quebrar sem necessidade.
5. **Remova todo arquivo legado que foi substituído — isto é obrigatório, não opcional.**
   Um arquivo que foi 100% absorvido pela nova estrutura (ex.: um `models.py`/`AppManager.js`
   monolítico cujo conteúdo inteiro já foi migrado para `src/`) **não pode continuar existindo
   com o conteúdo antigo** no repositório final. Se ele ainda contém o código antigo (incluindo
   qualquer credencial hardcoded, log inseguro ou outro achado CRITICAL/HIGH do relatório da
   Fase 2), a refatoração está incompleta, mesmo que a nova estrutura em `src/` já exista e
   funcione — os dois códigos não podem coexistir.
   - Prefira apagar o arquivo do disco (`rm`/delete). Se o ambiente de execução não permitir
     apagar fisicamente (ex.: uma pasta montada que bloqueia delete/rename), use `git rm` para
     removê-lo do controle de versão, e declare esse fato explicitamente no resumo da Fase 3
     (não deixe implícito — avise que X arquivo(s) não puderam ser apagados do disco mas foram
     removidos do commit via `git rm`, ou, na pior hipótese, que continuam pendentes de remoção
     manual pelo usuário).
   - Nunca finalize a Fase 3 com um arquivo antigo e um arquivo novo cobrindo a mesma
     responsabilidade ao mesmo tempo no repositório.
6. **Valide o resultado**:
   - Instale dependências se necessário e suba a aplicação (boot).
   - Confirme que ela inicia sem erros/exceptions.
   - Exercite os endpoints originais (ex.: via `curl`) e confirme que respondem com o mesmo
     contrato de antes (status code e formato geral do payload).
   - Rode novamente uma varredura rápida contra o catálogo de anti-patterns para confirmar que
     os achados CRITICAL/HIGH foram eliminados.
   - **Confirme explicitamente que nenhum arquivo legado do passo 5 permanece com o conteúdo
     antigo no repositório** (liste os arquivos removidos/substituídos e o método usado —
     delete físico ou `git rm`). Esta checagem faz parte da validação e deve ser reportada no
     resumo final, não pode ser pulada.
7. Imprima um resumo final:

```
================================
PHASE 3: REFACTORING COMPLETE
================================
New Project Structure:
<árvore de diretórios>

Legacy files removed:
  ✓ <arquivo antigo 1> (deletado do disco | removido via git rm)
  ✓ <arquivo antigo 2> (...)

Validation
  ✓ Application boots without errors
  ✓ All endpoints respond correctly
  ✓ Zero anti-patterns remaining (or: lista dos que restaram e por quê)
  ✓ Zero legacy files with old content left behind
================================
```

## Regras gerais

- Seja específico: toda alegação de problema tem que apontar arquivo:linha.
- Não invente métricas, dependências ou tabelas que não existem no código.
- Não pule a confirmação da Fase 2.
- A skill deve funcionar em qualquer linguagem/framework — nunca assuma Python/Flask
  especificamente; use as heurísticas de `project-analysis.md` para se adaptar.
