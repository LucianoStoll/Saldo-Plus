# Controle de Finanças

Projeto simples de controle de finanças pessoais usando **Python + SQLite + Flet**.

## Estrutura

```
controle_financas/
├── database.py      # conexão e criação das tabelas no SQLite
├── models.py         # dataclasses (Conta, Categoria, Transacao)
├── repository.py     # funções de CRUD e cálculo de saldos
├── main.py           # interface gráfica (Flet)
└── financas.db        # criado automaticamente na primeira execução
```

## Como rodar

1. Instale o Flet:
   ```
   pip install flet
   ```

2. Execute:
   ```
   python main.py
   ```
   (ou `flet run main.py`, se preferir usar o CLI do Flet)

O banco `financas.db` é criado automaticamente na primeira execução, já com
algumas categorias padrão (Salário, Alimentação, Transporte, etc).

## Funcionalidades

- Criar contas (carteira, conta corrente, poupança...)
- Registrar transações (receitas e despesas), vinculadas a uma conta e categoria
- Ver saldo total em tempo real
- Listar e excluir transações
- Camada `repository.py` já traz `resumo_por_categoria()`, pronta para
  alimentar gráficos futuramente (ex: com `fl_chart`/matplotlib)

## Próximos passos sugeridos

- Filtro de transações por período/categoria na interface
- Edição de transações existentes (hoje só é possível excluir e recriar)
- Gráfico de gastos por categoria (a query já existe em `resumo_por_categoria()`)
- Exportar relatório (CSV/PDF)
