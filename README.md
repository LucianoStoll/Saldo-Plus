# Saldo+

Projeto de controle de finanças pessoais usando **Python + SQLite + Flet**,
com layout mobile (dark, verde neon).

## Estrutura

```
controle_financas/
├── app.py               # ponto de entrada (inicializa o banco e sobe o app)
├── database.py           # conexão e criação das tabelas no SQLite
├── models.py             # dataclasses (Conta, Categoria, Transacao)
├── repository.py         # funções de CRUD e cálculo de saldos
├── ui/
│   ├── theme.py           # cores, fontes, ícones e formatadores (identidade visual)
│   ├── components.py      # componentes visuais reutilizáveis (cards, pílulas, itens de lista)
│   └── home_view.py       # tela principal: estado, eventos e layout
└── financas.db            # criado automaticamente na primeira execução
```

**Por que separado assim?**
- `theme.py` — muda a cor/fonte do app inteiro num só lugar.
- `components.py` — só funções "puras" (recebem dados e callbacks, devolvem
  um Control do Flet). Fáceis de reaproveitar em outra tela ou testar isoladas.
- `home_view.py` — é a única parte que conhece `repository.py` e mantém estado;
  é aqui que a lógica de negócio encontra a interface.
- `app.py` — só liga tudo. Se um dia você tiver mais de uma tela, é aqui que
  entraria o roteamento entre elas.

## Como rodar

1. Instale o Flet:
   ```
   pip install flet
   ```

2. Execute:
   ```
   python app.py
   ```

O banco `financas.db` é criado automaticamente na primeira execução, já com
algumas categorias padrão (Salário, Alimentação, Transporte, etc).

## Funcionalidades

- Criar contas (carteira, conta corrente, poupança...)
- Registrar transações (receitas e despesas), vinculadas a uma conta e categoria,
  via bottom sheet aberto pelo botão flutuante (+)
- Ver saldo total e resumo do mês em tempo real (card em destaque)
- Listar transações e excluir com confirmação
- Barra de navegação inferior (só "Início" funcional por enquanto — os demais
  ícones já estão no lugar para novas telas)
- Camada `repository.py` já traz `resumo_por_categoria()`, pronta para
  alimentar gráficos futuramente (ex: com `fl_chart`/matplotlib)

## Próximos passos sugeridos

- Criar novas telas (ex: `ui/resumo_view.py`, `ui/contas_view.py`) e ligar
  a navegação inferior a elas
- Filtro de transações por período/categoria na interface
- Edição de transações existentes (hoje só é possível excluir e recriar)
- Gráfico de gastos por categoria (a query já existe em `resumo_por_categoria()`)
- Exportar relatório (CSV/PDF)
