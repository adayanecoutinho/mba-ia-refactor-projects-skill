# Template do Relatório de Auditoria (Fase 2)

Use exatamente esta estrutura ao gerar `reports/audit-<slug>.md`. Preencha apenas com dados
reais observados — nunca com placeholders.

```markdown
================================
ARCHITECTURE AUDIT REPORT
================================
Project: <nome do projeto/pasta>
Stack:   <linguagem + framework>
Files:   <N> analyzed | ~<M> lines of code

Summary
CRITICAL: <n> | HIGH: <n> | MEDIUM: <n> | LOW: <n>

Findings

[CRITICAL] <Nome do anti-pattern>
File: <arquivo>:<linha ou intervalo de linhas>
Description: <o que foi encontrado, em 1-3 linhas>
Impact: <consequência prática para manutenção/segurança/teste>
Recommendation: <o que fazer, referenciando o padrão de transformação do playbook>

[CRITICAL] <próximo achado CRITICAL...>

[HIGH] <achados HIGH...>

[MEDIUM] <achados MEDIUM...>

[LOW] <achados LOW...>

================================
Total: <N> findings
================================
```

Regras de preenchimento:

- **Ordenação**: primeiro todos os CRITICAL, depois HIGH, depois MEDIUM, depois LOW. Dentro da
  mesma severidade, ordene por nome de arquivo e depois por linha.
- **File**: sempre caminho relativo à raiz do projeto + linha exata (`arquivo.py:42`) ou
  intervalo (`arquivo.py:1-350`) quando o problema abrange várias linhas (ex.: God Class).
- **Summary**: a contagem de cada severidade deve bater exatamente com o número de blocos
  `[SEVERIDADE]` listados abaixo.
- **Total**: soma de todos os findings, deve bater com `Summary`.
- Inclua pelo menos um achado relacionado a **API/prática deprecated** quando aplicável
  (ver catálogo), citando a versão/API específica.
- Não é necessário incluir uma seção separada de "phase 2 pause" no arquivo salvo — a pausa de
  confirmação acontece na conversa com o usuário, não no arquivo de relatório.
