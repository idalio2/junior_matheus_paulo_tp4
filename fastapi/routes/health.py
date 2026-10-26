from fastapi import APIRouter


router = APIRouter()


@router.get(
    "/health",
    summary="Verifica se a API está ativa",
    description="Rota pública, não exige autenticação.",
)
def verificar_saude():
    return {"status": "ok"}
