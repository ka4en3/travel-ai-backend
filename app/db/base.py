from app.db.base_class import Base

# Import all models so that they are included in the metadata
from app.models.user import User
from app.models.route import Route
from app.models.route import RouteDay
from app.models.route import Activity
from app.models.route_access import RouteAccess
from app.models.ai_cache import AICache
from app.models.export import Export
