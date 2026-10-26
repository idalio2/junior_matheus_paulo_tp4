import sqlite3

from security.senhas import gerar_hash_senha


def popular_banco(conexao: sqlite3.Connection):
    cursor = conexao.cursor()

    usuarios = [
        (1, "admin", gerar_hash_senha("infnet")),
        (2, "usuario2", gerar_hash_senha("teste123")),
    ]

    cursor.executemany(
        """
        INSERT INTO users (id, username, password_hash)
        VALUES (?, ?, ?)
        ON CONFLICT(username) DO UPDATE SET password_hash=excluded.password_hash
        """,
        usuarios,
    )

    predictions = [
        (1, "Quero meu dinheiro de volta", "Refund request", 1),
        (2, "Meu produto ainda não chegou", "Product inquiry", 2),
    ]

    cursor.executemany(
        """
        INSERT OR IGNORE INTO predictions (id, texto, intencao, owner_id)
        VALUES (?, ?, ?, ?)
        """,
        predictions,
    )


if __name__ == "__main__":
    from sqlite_database import DATABASE_PATH

    conexao = sqlite3.connect(DATABASE_PATH)
    conexao.execute("PRAGMA foreign_keys=ON")
    popular_banco(conexao)
    conexao.commit()
    conexao.close()

    print(f"Banco populado em: {DATABASE_PATH}")
