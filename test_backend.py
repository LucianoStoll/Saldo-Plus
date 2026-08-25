"""
test_backend.py
Testes automatizados da camada de backend (database.py + repository.py),
sem depender de interface gráfica.

Cada teste roda em um banco SQLite temporário isolado (nunca toca no
financas.db real), então é seguro rodar quantas vezes quiser.

Como rodar:
    python -m unittest test_backend.py -v

ou simplesmente:
    python test_backend.py
"""

import os
import sqlite3
import tempfile
import unittest

import database
import repository as repo


class BaseTestCaseFix(unittest.TestCase):
    """Cria um banco temporário novo (com schema + categorias padrão) antes
    de cada teste e apaga depois — garante testes independentes entre si."""

    def setUp(self):
        fd, self.caminho_temp = tempfile.mkstemp(suffix=".db")
        os.close(fd)
        self._db_path_original = database.DB_PATH
        database.DB_PATH = self.caminho_temp

        database.criar_tabelas()
        database.popular_categorias_padrao()

    def tearDown(self):
        database.DB_PATH = self._db_path_original
        try:
            os.remove(self.caminho_temp)
        except (FileNotFoundError, OSError):
            pass


# ---------------------------------------------------------------------------
# CONTAS
# ---------------------------------------------------------------------------

class TestContas(BaseTestCaseFix):

    def test_criar_e_listar_conta(self):
        conta_id = repo.criar_conta("Carteira", "corrente", 100.0)
        contas = repo.listar_contas()
        self.assertEqual(len(contas), 1)
        self.assertEqual(contas[0].id, conta_id)
        self.assertEqual(contas[0].nome, "Carteira")
        self.assertEqual(contas[0].saldo_inicial, 100.0)

    def test_excluir_conta(self):
        conta_id = repo.criar_conta("Poupança", "poupanca", 0.0)
        repo.excluir_conta(conta_id)
        self.assertEqual(len(repo.listar_contas()), 0)


# ---------------------------------------------------------------------------
# CATEGORIAS
# ---------------------------------------------------------------------------

class TestCategorias(BaseTestCaseFix):

    def test_categorias_padrao_populadas(self):
        categorias = repo.listar_categorias()
        nomes = [c.nome for c in categorias]
        self.assertIn("Alimentação", nomes)
        self.assertIn("Salário", nomes)

    def test_criar_categoria(self):
        cat_id = repo.criar_categoria("Pets", "despesa")
        categorias = repo.listar_categorias(tipo="despesa")
        self.assertIn(cat_id, [c.id for c in categorias])

    def test_listar_categorias_filtra_por_tipo(self):
        receitas = repo.listar_categorias(tipo="receita")
        despesas = repo.listar_categorias(tipo="despesa")
        self.assertTrue(all(c.tipo == "receita" for c in receitas))
        self.assertTrue(all(c.tipo == "despesa" for c in despesas))

    def test_atualizar_categoria_nome(self):
        cat_id = repo.criar_categoria("Pets", "despesa")
        repo.atualizar_categoria(cat_id, nome="Animais de estimação")
        atualizada = next(c for c in repo.listar_categorias() if c.id == cat_id)
        self.assertEqual(atualizada.nome, "Animais de estimação")
        self.assertEqual(atualizada.tipo, "despesa")  # tipo não mexido, deve manter

    def test_atualizar_categoria_tipo(self):
        cat_id = repo.criar_categoria("Reembolsos", "despesa")
        repo.atualizar_categoria(cat_id, tipo="receita")
        atualizada = next(c for c in repo.listar_categorias() if c.id == cat_id)
        self.assertEqual(atualizada.tipo, "receita")

    def test_atualizar_categoria_inexistente_lanca_erro(self):
        with self.assertRaises(ValueError):
            repo.atualizar_categoria(9999, nome="Não existe")

    def test_excluir_categoria_sem_uso(self):
        cat_id = repo.criar_categoria("Temporária", "despesa")
        repo.excluir_categoria(cat_id)
        self.assertNotIn(cat_id, [c.id for c in repo.listar_categorias()])

    def test_excluir_categoria_com_transacao_falha(self):
        conta_id = repo.criar_conta("Carteira", "corrente", 0.0)
        cat_id = repo.criar_categoria("Com transação", "despesa")
        repo.criar_transacao(conta_id, cat_id, 10.0, "2026-08-24", "teste", "despesa")

        with self.assertRaises(sqlite3.IntegrityError):
            repo.excluir_categoria(cat_id)

        # a conexão não deve ter ficado travada após a exceção
        outro_id = repo.criar_categoria("Outra categoria", "despesa")
        self.assertIsNotNone(outro_id)


# ---------------------------------------------------------------------------
# SUBCATEGORIAS
# ---------------------------------------------------------------------------

class TestSubcategorias(BaseTestCaseFix):

    def setUp(self):
        super().setUp()
        self.cat_id = repo.criar_categoria("Pets", "despesa")

    def test_criar_e_listar_subcategoria(self):
        sub_id = repo.criar_subcategoria(self.cat_id, "Ração")
        subs = repo.listar_subcategorias(categoria_id=self.cat_id)
        self.assertEqual(len(subs), 1)
        self.assertEqual(subs[0].id, sub_id)
        self.assertEqual(subs[0].nome, "Ração")

    def test_listar_subcategorias_sem_filtro_retorna_todas(self):
        outro_cat_id = repo.criar_categoria("Transporte extra", "despesa")
        repo.criar_subcategoria(self.cat_id, "Ração")
        repo.criar_subcategoria(outro_cat_id, "Uber")
        self.assertEqual(len(repo.listar_subcategorias()), 2)

    def test_atualizar_subcategoria_nome(self):
        sub_id = repo.criar_subcategoria(self.cat_id, "Ração")
        repo.atualizar_subcategoria(sub_id, nome="Ração e petiscos")
        sub = next(s for s in repo.listar_subcategorias(categoria_id=self.cat_id) if s.id == sub_id)
        self.assertEqual(sub.nome, "Ração e petiscos")

    def test_atualizar_subcategoria_categoria_pai(self):
        sub_id = repo.criar_subcategoria(self.cat_id, "Ração")
        nova_cat_id = repo.criar_categoria("Outra categoria", "despesa")
        repo.atualizar_subcategoria(sub_id, categoria_id=nova_cat_id)
        subs_categoria_antiga = repo.listar_subcategorias(categoria_id=self.cat_id)
        subs_categoria_nova = repo.listar_subcategorias(categoria_id=nova_cat_id)
        self.assertEqual(len(subs_categoria_antiga), 0)
        self.assertEqual(len(subs_categoria_nova), 1)

    def test_atualizar_subcategoria_inexistente_lanca_erro(self):
        with self.assertRaises(ValueError):
            repo.atualizar_subcategoria(9999, nome="Não existe")

    def test_excluir_subcategoria(self):
        sub_id = repo.criar_subcategoria(self.cat_id, "Ração")
        repo.excluir_subcategoria(sub_id)
        self.assertEqual(len(repo.listar_subcategorias(categoria_id=self.cat_id)), 0)

    def test_excluir_categoria_cascateia_subcategorias(self):
        repo.criar_subcategoria(self.cat_id, "Ração")
        repo.criar_subcategoria(self.cat_id, "Veterinário")
        repo.excluir_categoria(self.cat_id)
        self.assertEqual(len(repo.listar_subcategorias(categoria_id=self.cat_id)), 0)

    def test_excluir_subcategoria_mantem_transacao_com_categoria(self):
        conta_id = repo.criar_conta("Carteira", "corrente", 0.0)
        sub_id = repo.criar_subcategoria(self.cat_id, "Ração")
        repo.criar_transacao(conta_id, self.cat_id, 80.0, "2026-08-24", "Ração do gato",
                              "despesa", subcategoria_id=sub_id)

        repo.excluir_subcategoria(sub_id)

        transacoes = repo.listar_transacoes()
        self.assertEqual(len(transacoes), 1)
        self.assertIsNone(transacoes[0]["subcategoria_nome"])
        self.assertEqual(transacoes[0]["categoria_nome"], "Pets")


# ---------------------------------------------------------------------------
# TRANSAÇÕES
# ---------------------------------------------------------------------------

class TestTransacoes(BaseTestCaseFix):

    def setUp(self):
        super().setUp()
        self.conta_id = repo.criar_conta("Carteira", "corrente", 100.0)
        self.cat_despesa = next(c for c in repo.listar_categorias(tipo="despesa"))
        self.cat_receita = next(c for c in repo.listar_categorias(tipo="receita"))

    def test_criar_transacao_sem_subcategoria(self):
        t_id = repo.criar_transacao(self.conta_id, self.cat_despesa.id, 50.0,
                                     "2026-08-20", "Mercado", "despesa")
        transacoes = repo.listar_transacoes()
        self.assertEqual(len(transacoes), 1)
        self.assertEqual(transacoes[0]["id"], t_id)
        self.assertIsNone(transacoes[0]["subcategoria_nome"])

    def test_criar_transacao_com_subcategoria(self):
        sub_id = repo.criar_subcategoria(self.cat_despesa.id, "Feira")
        repo.criar_transacao(self.conta_id, self.cat_despesa.id, 50.0,
                              "2026-08-20", "Feira da semana", "despesa",
                              subcategoria_id=sub_id)
        transacoes = repo.listar_transacoes()
        self.assertEqual(transacoes[0]["subcategoria_nome"], "Feira")

    def test_listar_transacoes_filtra_por_conta(self):
        outra_conta_id = repo.criar_conta("Poupança", "poupanca", 0.0)
        repo.criar_transacao(self.conta_id, self.cat_despesa.id, 10.0, "2026-08-20", "A", "despesa")
        repo.criar_transacao(outra_conta_id, self.cat_despesa.id, 20.0, "2026-08-20", "B", "despesa")

        transacoes_conta = repo.listar_transacoes(conta_id=self.conta_id)
        self.assertEqual(len(transacoes_conta), 1)
        self.assertEqual(transacoes_conta[0]["descricao"], "A")

    def test_listar_transacoes_ordenadas_por_data_desc(self):
        repo.criar_transacao(self.conta_id, self.cat_despesa.id, 10.0, "2026-08-01", "Mais antiga", "despesa")
        repo.criar_transacao(self.conta_id, self.cat_despesa.id, 10.0, "2026-08-20", "Mais recente", "despesa")
        transacoes = repo.listar_transacoes()
        self.assertEqual(transacoes[0]["descricao"], "Mais recente")
        self.assertEqual(transacoes[1]["descricao"], "Mais antiga")

    def test_excluir_transacao(self):
        t_id = repo.criar_transacao(self.conta_id, self.cat_despesa.id, 10.0,
                                     "2026-08-20", "teste", "despesa")
        repo.excluir_transacao(t_id)
        self.assertEqual(len(repo.listar_transacoes()), 0)


# ---------------------------------------------------------------------------
# SALDOS E RESUMOS
# ---------------------------------------------------------------------------

class TestSaldosEResumos(BaseTestCaseFix):

    def setUp(self):
        super().setUp()
        self.conta_id = repo.criar_conta("Carteira", "corrente", 100.0)
        self.cat_despesa = next(c for c in repo.listar_categorias(tipo="despesa"))
        self.cat_receita = next(c for c in repo.listar_categorias(tipo="receita"))

    def test_saldo_da_conta_soma_receitas_e_despesas(self):
        repo.criar_transacao(self.conta_id, self.cat_despesa.id, 30.0, "2026-08-20", "Mercado", "despesa")
        repo.criar_transacao(self.conta_id, self.cat_receita.id, 200.0, "2026-08-21", "Freela", "receita")
        # 100 (inicial) - 30 (despesa) + 200 (receita) = 270
        self.assertEqual(repo.saldo_da_conta(self.conta_id), 270.0)

    def test_saldo_total_soma_todas_as_contas(self):
        outra_conta_id = repo.criar_conta("Poupança", "poupanca", 50.0)
        repo.criar_transacao(self.conta_id, self.cat_despesa.id, 30.0, "2026-08-20", "Mercado", "despesa")
        # conta 1: 100 - 30 = 70 | conta 2: 50 | total = 120
        self.assertEqual(repo.saldo_total(), 120.0)

    def test_resumo_mes_filtra_por_ano_mes(self):
        repo.criar_transacao(self.conta_id, self.cat_despesa.id, 30.0, "2026-08-20", "Dentro do mês", "despesa")
        repo.criar_transacao(self.conta_id, self.cat_receita.id, 500.0, "2026-08-05", "Dentro do mês", "receita")
        repo.criar_transacao(self.conta_id, self.cat_despesa.id, 999.0, "2026-07-01", "Mês passado", "despesa")

        resumo = repo.resumo_mes("2026-08")
        self.assertEqual(resumo["despesas"], 30.0)
        self.assertEqual(resumo["receitas"], 500.0)

    def test_resumo_por_categoria_agrupa_totais(self):
        repo.criar_transacao(self.conta_id, self.cat_despesa.id, 10.0, "2026-08-20", "a", "despesa")
        repo.criar_transacao(self.conta_id, self.cat_despesa.id, 15.0, "2026-08-21", "b", "despesa")

        resumo = repo.resumo_por_categoria()
        item = next(r for r in resumo if r["categoria"] == self.cat_despesa.nome)
        self.assertEqual(item["total"], 25.0)


# ---------------------------------------------------------------------------
# MIGRAÇÃO DE SCHEMA (banco antigo sem a coluna subcategoria_id)
# ---------------------------------------------------------------------------

class TestMigracaoSchema(unittest.TestCase):

    def setUp(self):
        fd, self.caminho_temp = tempfile.mkstemp(suffix=".db")
        os.close(fd)
        self._db_path_original = database.DB_PATH
        database.DB_PATH = self.caminho_temp

        # Simula um banco "antigo", criado antes de subcategorias existir.
        conn = sqlite3.connect(self.caminho_temp)
        conn.execute("""
            CREATE TABLE contas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                tipo TEXT NOT NULL DEFAULT 'corrente',
                saldo_inicial REAL NOT NULL DEFAULT 0
            )
        """)
        conn.execute("""
            CREATE TABLE categorias (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL UNIQUE,
                tipo TEXT NOT NULL CHECK (tipo IN ('receita', 'despesa'))
            )
        """)
        conn.execute("""
            CREATE TABLE transacoes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                conta_id INTEGER NOT NULL,
                categoria_id INTEGER NOT NULL,
                valor REAL NOT NULL,
                data TEXT NOT NULL,
                descricao TEXT,
                tipo TEXT NOT NULL CHECK (tipo IN ('receita', 'despesa'))
            )
        """)
        conn.execute("INSERT INTO categorias (nome, tipo) VALUES ('Alimentação', 'despesa')")
        conn.execute("INSERT INTO contas (nome, tipo, saldo_inicial) VALUES ('Carteira', 'corrente', 100)")
        conn.execute(
            "INSERT INTO transacoes (conta_id, categoria_id, valor, data, descricao, tipo) "
            "VALUES (1, 1, 50, '2026-08-20', 'Mercado', 'despesa')"
        )
        conn.commit()
        conn.close()

    def tearDown(self):
        database.DB_PATH = self._db_path_original
        try:
            os.remove(self.caminho_temp)
        except (FileNotFoundError, OSError):
            pass

    def test_migracao_preserva_dados_e_adiciona_coluna(self):
        database.criar_tabelas()
        database.popular_categorias_padrao()

        transacoes = repo.listar_transacoes()
        self.assertEqual(len(transacoes), 1)
        self.assertEqual(transacoes[0]["descricao"], "Mercado")
        self.assertIsNone(transacoes[0]["subcategoria_nome"])

        # popular_categorias_padrao não deve duplicar a categoria já existente
        categorias = repo.listar_categorias()
        nomes = [c.nome for c in categorias]
        self.assertEqual(nomes.count("Alimentação"), 1)

    def test_migracao_e_idempotente(self):
        # Rodar criar_tabelas() duas vezes não pode quebrar (coluna já existe)
        database.criar_tabelas()
        database.criar_tabelas()
        transacoes = repo.listar_transacoes()
        self.assertEqual(len(transacoes), 1)


if __name__ == "__main__":
    unittest.main(verbosity=2)
