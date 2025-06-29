from fastapi import APIRouter, Depends, HTTPException, status
from starlette.requests import Request

router = APIRouter(prefix="/users", tags=["users"])


def get_current_user(request: Request):
    if not request.state.user:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="Не авторизован")
    return request.state.user

current_user_dep = Depends(get_current_user)

@router.get("/me")
def read_profile(current_user=current_user_dep):
    return {
        "id": current_user.id,
        "email": current_user.email,
        "is_active": current_user.is_active
    }
