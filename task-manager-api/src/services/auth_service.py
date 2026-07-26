"""Emissão/validação de token de sessão. Substitui o token falso e
previsível do código legado (`'fake-jwt-token-' + str(user.id)`, que
qualquer cliente conseguia forjar para se passar por outro usuário) por um
token assinado com itsdangerous usando a SECRET_KEY da aplicação."""
from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired

TOKEN_MAX_AGE_SECONDS = 60 * 60 * 24  # 24h


def issue_token(secret_key: str, user_id: int) -> str:
    serializer = URLSafeTimedSerializer(secret_key)
    return serializer.dumps({"user_id": user_id})


def decode_token(secret_key: str, token: str):
    serializer = URLSafeTimedSerializer(secret_key)
    try:
        data = serializer.loads(token, max_age=TOKEN_MAX_AGE_SECONDS)
        return data.get("user_id")
    except (BadSignature, SignatureExpired):
        return None
