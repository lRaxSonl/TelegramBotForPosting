from .new_post import router as new_post_router
from .start import router as start_router
from .admin_panel import router as admin_panel_router
from .manage_voice_actor import router as manage_voice_actor_router
from .manage_editor import router as manage_editor_router
from .manage_tag import router as manage_tag_router
from .manage_moderator import router as manage_moderator_router
from .manage_admin import router as manage_admin_router

from .error import router as error_router
from aiogram import Router

router = Router()

router.include_router(start_router)
router.include_router(admin_panel_router)
router.include_router(manage_voice_actor_router)
router.include_router(manage_editor_router)
router.include_router(manage_tag_router)
router.include_router(manage_moderator_router)
router.include_router(manage_admin_router)
router.include_router(new_post_router)


router.include_router(error_router)

__all__ = ['router']