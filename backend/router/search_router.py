
from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    status,
)
from elasticsearch import AsyncElasticsearch

es = AsyncElasticsearch(
    "http://localhost:9200"
)

from sqlalchemy.ext.asyncio import AsyncSession
from dependencies.database import get_db
from services.search_service import SearchService


router = APIRouter(
    prefix="/admin",
    tags=["Admin Search"],
)


# ============================================
# SEARCH CUSTOMERS
# ============================================

@router.get("/search")
async def admin_search(
    q: str = Query(
        ...,
        min_length=1,
    ),

    size: int = Query(
        20,
        ge=1,
        le=100,
    ),

    db: AsyncSession = Depends(get_db),
):
    service = SearchService(db)

    return await service.search_customers(
        query=q,
        size=size,
    )


# ============================================
# SYNC ALL CUSTOMERS
# ============================================

@router.post("/search/sync")
async def sync_search_data(
    skip: int = Query(
        0,
        ge=0,
    ),

    limit: int = Query(
        100,
        ge=1,
        le=100,
    ),

    db: AsyncSession = Depends(get_db),
):
    service = SearchService(db)

    return await service.sync_customers(
        skip=skip,
        limit=limit,
    )


# ============================================
# SYNC ONE CUSTOMER
# ============================================

@router.post("/search/sync/{user_id}")
async def sync_single_customer(
    user_id: int,

    db: AsyncSession = Depends(get_db),
):
    service = SearchService(db)

    result = await service.sync_customer_by_id(
        user_id,
    )

    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    return result


# ============================================
# DELETE CUSTOMER FROM SEARCH INDEX
# ============================================

@router.delete("/search/{user_id}")
async def delete_customer_from_search(
    user_id: int,

    db: AsyncSession = Depends(get_db),
):
    service = SearchService(db)

    return await service.delete_customer(
        user_id,
    )

@router.get("/elastic-test")
async def elastic_test():
    return await es.info()

@router.get("/elastic-index-test")
async def elastic_index_test():
    exists = await es.indices.exists(
        index="customers"
    )

    return {
        "exists": exists
    }