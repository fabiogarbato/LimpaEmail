from flask import Blueprint, jsonify, request
from services.email_service import listar_remetentes, limpar_emails

bp = Blueprint("mail_bp", __name__)

@bp.route("/listar", methods=["GET"])
def rota_listar():
    resultado = listar_remetentes()
    return jsonify(resultado)

@bp.route("/limpar", methods=["POST"])
def rota_limpar():
    data = request.get_json() or {}
    remetentes = data.get("remetentes", None)
    resultado = limpar_emails(remetentes)
    return jsonify(resultado)
