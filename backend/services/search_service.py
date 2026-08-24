from elasticsearch import NotFoundError
from numpy import size
from numpy import size
from httpx2 import query
from sqlalchemy.ext.asyncio import AsyncSession

from elasticsearch_client import es
from repositories.search_repository import SearchRepository
from elasticsearch import BadRequestError

CUSTOMER_INDEX = "customers"


class SearchService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = SearchRepository(db)

    # ============================================
    # CREATE ELASTICSEARCH INDEX
    # ============================================

    async def create_customer_index(self):
        print("Checking index")

        exists = await es.indices.exists(
            index=CUSTOMER_INDEX,
        )

        print("Index exists:", exists)

        if exists:
            return

        print("Creating index")

        await es.indices.create(
            index=CUSTOMER_INDEX,
            mappings={
                "properties": {
                    "user_id": {"type": "integer"},
                    "first_name": {"type": "text"},
                    "last_name": {"type": "text"},
                    "email": {"type": "keyword"},
                    "country": {"type": "text"},
                    "role": {"type": "keyword"},
                    "user_status": {"type": "keyword"},
                    "account_id": {"type": "integer"},
                    "account_number": {"type": "keyword"},
                    "account_type": {"type": "keyword"},
                    "account_status": {"type": "keyword"},
                }
            },
    )

    # ============================================
    # INDEX ONE CUSTOMER
    # ============================================

    async def index_customer(
        self,
        user,
        account=None,
    ):
        document = {
            "user_id": user.id,

            "first_name": user.first_name,

            "last_name": user.last_name,

            "email": user.email,

            "country": user.country,

            "role": (
                user.role.value
                if hasattr(user.role, "value")
                else user.role
            ),

            "user_status": (
                user.user_status.value
                if hasattr(user.user_status, "value")
                else user.user_status
            ),

            "account_id": (
                account.id
                if account
                else None
            ),

            "account_number": (
                account.account_number
                if account
                else None
            ),

            "account_type": (
                account.account_type
                if account
                else None
            ),

            "account_status": (
                account.account_status.value
                if account
                and hasattr(
                    account.account_status,
                    "value",
                )
                else (
                    account.account_status
                    if account
                    else None
                )
            ),
        }

        await es.index(
            index=CUSTOMER_INDEX,
            id=user.id,
            document=document,

            # Helpful while testing
            refresh=True,
        )

        return document

    # ============================================
    # SYNC POSTGRESQL -> ELASTICSEARCH
    # ============================================

    async def sync_customers(
        self,
        skip: int = 0,
        limit: int = 100,
    ):
        await self.create_customer_index()

        rows = await self.repo.get_all_customers(
            skip=skip,
            limit=limit,
        )

        indexed_count = 0

        for user, account in rows:
            await self.index_customer(
                user=user,
                account=account,
            )

            indexed_count += 1

        return {
            "message": "Customers indexed successfully",
            "indexed": indexed_count,
        }

    # ============================================
    # SYNC ONE CUSTOMER
    # ============================================

    async def sync_customer_by_id(
        self,
        user_id: int,
    ):
        await self.create_customer_index()

        row = await self.repo.get_customer_by_id(
            user_id,
        )

        if not row:
            return None

        user, account = row

        return await self.index_customer(
            user=user,
            account=account,
        )

    # ============================================
    # SEARCH
    # ============================================




    async def search_customers(
        self,

        query: str,
        size: int = 20,
    ):
        try:
            response = await es.search(
                index=CUSTOMER_INDEX,
                query={
                    "multi_match": {
                        "query": query,
                        "fields": [
                            "first_name",
                            "last_name",
                            "country",
                        ],
                        "fuzziness": "AUTO",
                    }
                },
                size=size,
            )

            return [
                hit["_source"]
                for hit in response["hits"]["hits"]
            ]

        except BadRequestError as exc:
            print("ELASTICSEARCH STATUS:", exc.status_code)
            print("ELASTICSEARCH BODY:", exc.body)
            print("ELASTICSEARCH MESSAGE:", exc)

            raise

    # ============================================
    # DELETE CUSTOMER FROM ELASTICSEARCH
    # ============================================

    async def delete_customer(
        self,
        user_id: int,
    ):
        try:
            await es.delete(
                index=CUSTOMER_INDEX,
                id=user_id,
                refresh=True,
            )

        except NotFoundError:
            return {
                "message": "Customer was not found in Elasticsearch",
            }

        return {
            "message": "Customer removed from Elasticsearch",
        }