from http import HTTPStatus
from fastapi import FastAPI, status
from fastapi.requests import Request
from fastapi.responses import Response, JSONResponse
import time
import logging




logger = logging.getLogger('uvicorn.access')
logger.disabled = True

# logger = logging.getLogger("bookly")
# logger.setLevel(logging.INFO)

def register_middleware(app: FastAPI):

    @app.middleware('http')
    async def custom_logging(req: Request, call_next):
        st = time.time()

        response: Response = await call_next(req)

        process_time = time.time() - st
        status_code = response.status_code
        status_phrase = HTTPStatus(status_code).phrase
        log_msg = f"{req.client.host}:{req.client.port} - {req.method} - {req.url.path} - {status_code} {status_phrase} - {(process_time*1000):.2f}ms"

        print(log_msg)
        return response


    # check header if it contains "Authorization" before reaching api endpoint
    # @app.middleware('http')
    # async def auth_header_check(req: Request, call_next):
    #     if not "Authorization" in req.headers:
    #         return JSONResponse(
    #             content={
    #                 "message": "not authenticated",
    #                 "resolution": "please provide right credentials to proceed"
    #             },
    #             status_code=status.HTTP_401_UNAUTHORIZED
    #         )
    #     response: Response = await call_next(req)
    #     return response