from .info import router as info_router
from .login import router as login_router
from .logout import router as logout_router
from .responses import response_403

from curd import CURDSession

from fastapi import FastAPI, Request, Response
from fastapi.responses import ORJSONResponse

api_router = FastAPI()
api_router.include_router(login_router, prefix="/login", tags=["login"])

api_router.include_router(info_router, prefix="/info", tags=["info"])
api_router.include_router(logout_router, prefix="/logout", tags=["logout"])

NEED_AUTH = (
    "/api/info",
    "/api/logout",
)

curd_session = CURDSession()


@api_router.middleware("")
async def api_filter(request: Request, call_next):
    if request.url.path.startswith(NEED_AUTH):
        session = request.cookies.get("session")
        login_session = await curd_session.get_by_session(session)
        if login_session is None:
            status_code, c_response = response_403()
            return ORJSONResponse(
                c_response.dict(),
                status_code,
                headers={"cache-control": "max-age=0"}
            )
        await curd_session.update_time(login_session)

    response: Response = await call_next(request)
    if not response.headers.get("cache-control"):
        response.headers["cache-control"] = "max-age=0"

    return response
