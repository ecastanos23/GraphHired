# COMENTARIO DE ARCHIVO - GRAPHHIRED
# Inicializa el paquete core con configuracion, base de datos y seguridad.

"""Core module initialization"""
from app.core.config import settings
from app.core.database import get_db, Base, engine
from app.core.security import sanitize_text, sanitize_email, sanitize_dict
