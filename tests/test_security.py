from fastapi.testclient import TestClient

from main import app


client = TestClient(app)


def obter_token(username: str, password: str) -> str:
    resposta = client.post(
        "/auth/token",
        data={
            "username": username,
            "password": password,
        },
    )

    assert resposta.status_code == 200
    return resposta.json()["access_token"]


def test_autenticacao_com_credenciais_validas_e_invalidas():
    resposta_valida = client.post(
        "/auth/token",
        data={
            "username": "admin",
            "password": "infnet",
        },
    )

    assert resposta_valida.status_code == 200
    assert resposta_valida.json()["token_type"] == "bearer"
    assert resposta_valida.json()["access_token"]

    resposta_invalida = client.post(
        "/auth/token",
        data={
            "username": "admin",
            "password": "senha-errada",
        },
    )

    assert resposta_invalida.status_code == 401
    assert resposta_invalida.json()["detail"] == "Usuário ou senha inválidos"


def test_acesso_sem_token():
    resposta = client.post(
        "/predict",
        json={"texto": "Quero um reembolso"},
    )

    assert resposta.status_code == 401
    assert resposta.json()["detail"] == "Not authenticated"


def test_usuario_nao_acessa_recurso_de_outro_usuario():
    token = obter_token("usuario2", "teste123")

    resposta = client.get(
        "/predictions/1",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert resposta.status_code == 404
    assert resposta.json()["detail"] == "Prediction não encontrada"


def test_campo_extra_e_rejeitado():
    token = obter_token("admin", "infnet")

    resposta = client.post(
        "/predict",
        json={
            "texto": "Quero um reembolso",
            "campo_extra": "valor não permitido",
        },
        headers={"Authorization": f"Bearer {token}"},
    )

    assert resposta.status_code == 422
    assert resposta.json()["detail"][0]["type"] == "extra_forbidden"


def test_rate_limit_bloqueia_apos_10_requisicoes():
    for _ in range(10):
        resposta = client.post(
            "/auth/token",
            data={
                "username": "admin",
                "password": "senha-errada",
            },
        )

        assert resposta.status_code == 401

    resposta = client.post(
        "/auth/token",
        data={
            "username": "admin",
            "password": "senha-errada",
        },
    )

    assert resposta.status_code == 429
    assert "Rate limit exceeded" in resposta.json()["error"]
