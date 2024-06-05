from fastapi import HTTPException
from fastapi.exceptions import RequestValidationError

EXCEPTION_HANDLERS = {
    400: {
        "status_code": 400,
        "detail": "잘못된 값이 입력되었습니다."
    },
    500: {
        "status_code": 500,
        "detail": "서버 내부 오류입니다."
    },
    Exception: {
        "status_code": 501,
        "detail": "일반적인 예외가 발생했습니다."
    },
    HTTPException: {
        "status_code": lambda exc: exc.status_code,
        "detail": lambda exc: exc.detail
    },
    422: {
        "status_code": 422,
        "detail": "잘못된 입력값입니다."
    },
    404: {
        "status_code": 404,
        "detail": "데이터를 불러오지 못했습니다."
    },
    424: {
        "status_code": 424,
        "detail": "의존성 실패로 요청이 처리되지 않았습니다."
    },
    429: {
        "status_code": 429,
        "detail": "요청이 너무 많습니다."
    },
    502: {
        "status_code": 502,
        "detail": "게이트웨이 오류가 발생했습니다."
    }
}
