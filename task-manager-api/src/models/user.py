from datetime import datetime

from werkzeug.security import generate_password_hash, check_password_hash

from src.config.database import db


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(50), default="user")
    active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        # Nunca inclui o hash de senha na resposta (o código legado retornava
        # `password` em todo endpoint que serializava um usuário).
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "role": self.role,
            "active": self.active,
            "created_at": str(self.created_at),
        }

    def set_password(self, pwd: str) -> None:
        # Substitui o hashlib.md5 (deprecated/inseguro para senha) por um
        # hash com salt via werkzeug.security (padrão do próprio Flask).
        self.password = generate_password_hash(pwd)

    def check_password(self, pwd: str) -> bool:
        return check_password_hash(self.password, pwd)

    def is_admin(self) -> bool:
        return self.role == "admin"
