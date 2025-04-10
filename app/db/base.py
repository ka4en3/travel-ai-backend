# app/db/base_class.py

from db.base_class import Base

# Import all models so that they are included in the metadata
from models.user import User
from models.route import Route
from models.route import RouteDay
from models.route import Activity
from models.route_access import RouteAccess
from models.ai_cache import AICache
from models.export import Export
