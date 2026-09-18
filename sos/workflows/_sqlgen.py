"""Helpers para generar SQL desde nodos Python del sandbox.

Se embeben (como texto) en el código de los nodos, así que deben ser autocontenidos:
solo stdlib. Se testean en local importándolos normalmente.
"""

SQL_HELPERS = r'''
import json as _json

def q(v):
    """Literal SQL: None→NULL, bool, números, dict/list→jsonb, str→'...'."""
    if v is None or v == "":
        return "NULL"
    if isinstance(v, bool):
        return "true" if v else "false"
    if isinstance(v, (int, float)):
        return repr(v)
    if isinstance(v, (dict, list)):
        return "'" + _json.dumps(v, ensure_ascii=False).replace("'", "''") + "'::jsonb"
    return "'" + str(v).replace("'", "''") + "'"

def num(v, default=None):
    try:
        return float(v)
    except (TypeError, ValueError):
        return default

def jbody(sql):
    """SQL → valor de cadena JSON ya escapado, listo para incrustar en body.raw."""
    return _json.dumps(sql, ensure_ascii=False)[1:-1]

def cfg_num(key):
    """Subconsulta SQL que lee un número de la tabla config."""
    return "(SELECT (value::text)::float8 FROM config WHERE key = '%s')" % key

def haversine_sql(lat_col, lon_col, lat, lon):
    return ("2 * 6371 * asin(sqrt(power(sin(radians((%s) - (%s)) / 2), 2) + cos(radians(%s)) * cos(radians(%s)) * "
            "power(sin(radians((%s) - (%s)) / 2), 2)))" % (lat_col, lat, lat, lat_col, lon_col, lon))
'''
