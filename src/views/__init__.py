from .atri_controller import atri_bp
from .test_controller import test_bp
from .auth_controller import auth_bp
from .static_blueprint import static_bp

__all__ = [atri_bp, auth_bp, static_bp, test_bp]