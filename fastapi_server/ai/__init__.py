from fastapi import APIRouter
from .razvorot import router as razvorot

router = APIRouter()
router.include_router(razvorot)
