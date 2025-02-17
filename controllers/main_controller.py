from fastapi import APIRouter
import controllers.auth_controller as auth_controller
import controllers.lp_generate_controller as lp_generate_controller
import controllers.course_controller as course_controller


router = APIRouter()


router.include_router(auth_controller.router, tags=["auth"])
router.include_router(course_controller.router, tags=["auth"])
router.include_router(lp_generate_controller.router, tags=["auth"])
