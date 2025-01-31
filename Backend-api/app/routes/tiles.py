from fastapi import APIRouter

router = APIRouter()

@router.get("/tiles/test")
def test_tiles():
    return {"message": "Tiles endpoint is working"}
