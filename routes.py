from functools import wraps
from datetime import datetime, timedelta
from flask import Blueprint, jsonify, request
from services.email_service import listar_remetentes, limpar_emails

bp = Blueprint("mail_bp", __name__)
tokens = {}

def require_token(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return jsonify({"status": "erro", "mensagem": "Token ausente ou inválido"}), 401
        token = auth_header.split("Bearer ")[1]
        if token not in tokens:
            return jsonify({"status": "erro", "mensagem": "Token inválido"}), 401
        if datetime.now() > tokens[token]:
            del tokens[token]
            return jsonify({"status": "erro", "mensagem": "Token expirado"}), 401
        return func(*args, **kwargs)
    return wrapper

@bp.route("/token", methods=["POST"])
def generate_token():
    import secrets
    token = secrets.token_hex(16)
    tokens[token] = datetime.now() + timedelta(hours=24)
    return jsonify({"status": "ok", "token": token})

@bp.route("/listar", methods=["GET"])
@require_token
def rota_listar():
    resultado = listar_remetentes()
    return jsonify(resultado)

@bp.route("/limpar", methods=["POST"])
@require_token
def rota_limpar():
    data = request.get_json() or {}
    remetentes = data.get("remetentes", None)
    resultado = limpar_emails(remetentes)
    return jsonify(resultado)
