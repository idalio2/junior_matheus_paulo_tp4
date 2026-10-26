import argparse
import os
import sqlite3
from pathlib import Path

from sqlite_populate import popular_banco


BASE_DIR = Path(__file__).resolve().parent
DATABASE_PATH = Path(
    os.environ.get("DATABASE_PATH", BASE_DIR / "database.db")
).resolve()


def criar_banco(recriar: bool = False):
    if recriar:
        DATABASE_PATH.unlink(missing_ok=True)

    conexao = sqlite3.connect(DATABASE_PATH)
    conexao.execute("PRAGMA foreign_keys=ON")
    cursor = conexao.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL
        )
        """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS predictions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            texto TEXT NOT NULL,
            intencao TEXT NOT NULL,
            owner_id INTEGER NOT NULL,
            FOREIGN KEY (owner_id) REFERENCES users (id)
        )
        """
    )

    popular_banco(conexao)

    conexao.commit()
    conexao.close()

    print(f"Banco criado e populado em: {DATABASE_PATH}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--recriar",
        action="store_true",
        help="Remove o banco existente antes de criar os dados de exemplo.",
    )
    argumentos = parser.parse_args()
    criar_banco(recriar=argumentos.recriar)
