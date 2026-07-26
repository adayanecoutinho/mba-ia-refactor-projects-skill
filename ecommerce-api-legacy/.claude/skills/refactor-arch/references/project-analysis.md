# Heurísticas de Análise de Projeto (Fase 1)

Objetivo: detectar linguagem, framework, dependências, banco de dados, domínio e arquitetura
atual de qualquer codebase, sem assumir uma stack específica.

## 1. Detecção de linguagem

Olhe para os arquivos de manifesto/build presentes na raiz (ou no subprojeto, se for monorepo):

| Arquivo encontrado                        | Linguagem provável       |
|--------------------------------------------|---------------------------|
| `requirements.txt`, `Pipfile`, `pyproject.toml`, `setup.py` | Python |
| `package.json`, `package-lock.json`, `yarn.lock` | JavaScript / TypeScript (checar `tsconfig.json` para TS) |
| `go.mod`                                   | Go |
| `pom.xml`, `build.gradle`                  | Java / Kotlin |
| `Gemfile`                                  | Ruby |
| `composer.json`                            | PHP |
| `*.csproj`, `*.sln`                        | C# / .NET |

Se houver mais de um manifesto (ex.: monorepo), analise por subpasta — cada subprojeto do
desafio (`code-smells-project`, `ecommerce-api-legacy`, `task-manager-api`) é independente e
deve ser tratado como seu próprio projeto.

## 2. Detecção de framework web

Procure os imports/dependências típicos:

- Python: `flask`/`Flask(__name__)` → Flask; `django` → Django; `fastapi` → FastAPI.
- Node: `express` no `package.json` e `require('express')`/`import express` → Express;
  `fastify`, `koa`, `@nestjs/core` → respectivos frameworks.
- Java: `spring-boot-starter-web` → Spring Boot.

A **versão** do framework normalmente está no manifesto (`requirements.txt`, `package.json`
`dependencies`). Reporte a versão exata quando presente (ex.: `flask==3.1.1`).

## 3. Dependências relevantes

Liste bibliotecas que indicam papéis arquiteturais: CORS (`flask-cors`, `cors`), ORM
(`flask-sqlalchemy`, `sequelize`, `sqlalchemy`, `typeorm`), driver de banco (`sqlite3`,
`psycopg2`, `pg`, `mysql2`), validação (`marshmallow`, `pydantic`, `joi`, `zod`), HTTP
(`requests`, `axios`).

## 4. Banco de dados e tabelas/entidades

- SQL cru: procure `CREATE TABLE` (em `.py`/`.js` embutido em strings, ou em arquivos `.sql`).
- ORM declarativo (SQLAlchemy, Sequelize, TypeORM, Django Models): procure classes que herdam
  de `db.Model`, `Model`, `@Entity`, etc. — cada classe é uma tabela/entidade.
- Reporte o nome do banco (SQLite/Postgres/MySQL) inferido pela connection string ou driver, e
  a lista de tabelas/entidades encontradas.

## 5. Domínio de negócio

Infira pelo **nome das rotas, dos models/tabelas e das mensagens de erro/log** — não pelo nome
da pasta do repositório. Exemplos:
- Rotas `/produtos`, `/pedidos`, `/usuarios` + tabelas `produtos`, `pedidos` → E-commerce.
- Rotas `/api/checkout`, tabelas `courses`, `enrollments`, `payments` → LMS / plataforma de
  cursos com checkout de pagamento.
- Rotas `/tasks`, `/users`, `/categories`, `/reports` → Task Manager / gestão de tarefas.

## 6. Arquitetura atual

Classifique em uma frase curta, com base na contagem de arquivos e na mistura de
responsabilidades observada nas fases de leitura:
- **Monolítica em poucos arquivos**: toda a lógica (rotas, SQL, regra de negócio, validação)
  concentrada em 1–4 arquivos, sem pastas de camadas.
- **Parcialmente organizada**: já existem pastas por camada (ex.: `models/`, `routes/`,
  `services/`), mas os arquivos dentro delas ainda violam responsabilidades (ex.: rota faz
  query direta, "service" que não orquestra nada, model com lógica de apresentação).
  Esse é o caso mais comum em projetos legados "que já tentaram organizar, mas não
  terminaram" — não subestime esses projetos só porque têm pastas: ainda pode haver
  violações graves dentro delas.
- **God Class/God File**: um único arquivo/classe concentra rotas + acesso a dados + regra de
  negócio para múltiplos domínios (ex.: um `AppManager`/`Manager` genérico).

## 7. Contagem de arquivos

Conte apenas arquivos de código-fonte do projeto (extensões da linguagem detectada), excluindo
diretórios de dependências instaladas (`node_modules/`, `venv/`, `.venv/`, `__pycache__/`),
controle de versão (`.git/`) e a própria pasta da skill (`.claude/`).

## 8. Formato de saída da Fase 1

Sempre preencha os 6 campos do template (Language, Framework, Dependencies, Domain,
Architecture, Source files, DB tables) com dados reais observados no código — nunca com
valores genéricos ou de exemplo.
