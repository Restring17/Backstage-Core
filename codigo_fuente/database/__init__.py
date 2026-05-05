"""Módulo de Base de Datos: Capa de persistencia (Nube/Local)"""

from .db_abstracta import BaseDatos
from .db_supabase import DBSupabase
from .db_sqlite import DBSQLite

__all__ = ["BaseDatos", "DBSupabase", "DBSQLite"]
