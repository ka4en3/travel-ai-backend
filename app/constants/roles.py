# app/constants/roles.py

from enum import Enum


class RouteRole(str, Enum):
    CREATOR = "creator"
    EDITOR = "editor"
    VIEWER = "viewer"
