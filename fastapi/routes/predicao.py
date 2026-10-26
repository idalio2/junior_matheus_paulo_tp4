from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session

from models.database import Prediction, Usuario, get_session
from models.predicao import (
    EntradaPredicao,
    PredictionPublica,
    SaidaPredicao,
)
from security.autenticacao import validar_token


router = APIRouter()


@router.post(
    "/predict",
    response_model=SaidaPredicao,
    summary="Prevê a intenção de uma mensagem",
    description=(
        "Recebe o texto de uma mensagem de atendimento e registra a prediction "
        "para o usuário autenticado. Exige token Bearer. "
        "Enquanto o modelo não é treinado, a intenção retornada é fixa."
    ),
    responses={
        401: {"description": "Token ausente, inválido ou expirado"},
    },
)
def prever_intencao(
        entrada: EntradaPredicao,
        usuario: Annotated[
            Usuario,
            Depends(validar_token)
        ],
        session: Annotated[
            Session,
            Depends(get_session)
        ],
):
    intencao = "Refund request"

    prediction = Prediction(
        texto=entrada.texto,
        intencao=intencao,
        owner_id=usuario.id,
    )

    session.add(prediction)
    session.commit()
    session.refresh(prediction)

    return SaidaPredicao(
        id=prediction.id,
        intencao=prediction.intencao,
    )


@router.get(
    "/predictions/{prediction_id}",
    response_model=PredictionPublica,
    summary="Consulta uma prediction",
    description=(
        "Retorna uma prediction do usuário autenticado. Exige token Bearer. "
        "Predictions de outros usuários não são retornadas."
    ),
    responses={
        401: {"description": "Token ausente, inválido ou expirado"},
        404: {"description": "Prediction não encontrada"},
    },
)
def obter_prediction(
        prediction_id: int,
        usuario: Annotated[
            Usuario,
            Depends(validar_token)
        ],
        session: Annotated[
            Session,
            Depends(get_session)
        ],
):
    prediction = session.get(
        Prediction,
        prediction_id,
    )

    if prediction is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Prediction não encontrada",
        )

    if prediction.owner_id != usuario.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Prediction não encontrada",
        )

    return PredictionPublica(
        id=prediction.id,
        texto=prediction.texto,
        intencao=prediction.intencao,
    )
