from pathlib import Path
from typing import Annotated

import joblib

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

from models.database import Usuario
from security.autenticacao import validar_token

router = APIRouter()

caminho_modelo = (
        Path(__file__).resolve().parents[1]
        / "ml"
        / "classificador.joblib"
)

modelo = joblib.load(caminho_modelo)


class EntradaClassificacao(BaseModel):
    texto: str = Field(min_length=1, max_length=5000)


class SaidaClassificacao(BaseModel):
    intencao: str
    probabilidade: float


@router.post(
    "/classify",
    response_model=SaidaClassificacao,
    tags=["Classificação"],
    summary="Classifica a intenção do cliente"
)
def classificar_intencao(
        entrada: EntradaClassificacao,
        usuario: Annotated[Usuario, Depends(validar_token)]
):
    probabilidades = modelo.predict_proba(
        [entrada.texto]
    )[0]

    indice = probabilidades.argmax()

    return SaidaClassificacao(
        intencao=str(modelo.classes_[indice]),
        probabilidade=float(probabilidades[indice])
    )