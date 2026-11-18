import re
from django.core.exceptions import ValidationError

CARACTERES_PELIGROSOS_REGEX = re.compile(r'[<>"\'%()&+\\\x00]')

def validar_texto_seguro(valor, campo="Campo", max_len=200, permitir_puntuacion_basica=False):
    """
    OWASP Proceso 1: Validación estricta de entrada.
    Rechaza caracteres nulos, etiquetas html y caracteres potencialmente peligrosos.
    """
    if valor is None:
        return ""
    
    # Comprobar caracteres nulos
    if "\x00" in valor or "%00" in valor:
        raise ValidationError(f"{campo}: Se detectaron caracteres nulos inválidos.")
    
    texto = str(valor).strip()
    if len(texto) > max_len:
        raise ValidationError(f"{campo}: Excede el largo máximo permitido ({max_len} caracteres).")
    
    # Detección de patrones de inyección script o etiquetas
    if re.search(r'<\s*script|javascript:|data:\s*text/html|<.*?>', texto, re.IGNORECASE):
        raise ValidationError(f"{campo}: Contiene etiquetas o secuencias no permitidas.")
    
    return texto


def validar_rango_entero(valor, nombre_campo, min_val, max_val):
    """Valida tipo entero y rango esperado."""
    try:
        val = int(valor)
    except (ValueError, TypeError):
        raise ValidationError(f"{nombre_campo} debe ser un número entero válido.")
    
    if val < min_val or val > max_val:
        raise ValidationError(f"{nombre_campo} debe estar dentro del rango [{min_val}, {max_val}].")
    
    return val
