from datetime import datetime

import pytest
from pydantic import ValidationError

from schemas.card import *

class TestCardResponse:

    def test_valid_response(self):
        created_at = datetime(2026, 8, 20, 10, 30, 0)
        expiry_date = datetime(2029, 12, 1)

        response = CardResponse(
            id=1,
            account_id=100,
            card_number="1234567890123456",
            cvc="123",
            expiry_date=expiry_date,
            status="ACTIVE",
            created_at=created_at,
        )

        assert response.id == 1
        assert response.account_id == 100
        assert response.card_number == "1234567890123456"
        assert response.cvc == "123"
        assert response.expiry_date == expiry_date
        assert response.status == "ACTIVE"
        assert response.created_at == created_at

    def test_missing_required_field(self):
        with pytest.raises(ValidationError):
            CardResponse(
                id=1,
                account_id=100,
                card_number="1234567890123456",
                cvc="123",
                expiry_date=datetime(2029, 12, 1),
                status="ACTIVE",
                # created_at missing
            )


class TestCardDetailsRequest:

    def test_valid_request(self):
        request = CardDetailsRequest(password="password123")

        assert request.password == "password123"

    def test_missing_password(self):
        with pytest.raises(ValidationError):
            CardDetailsRequest()


class TestCardDetailsResponse:

    def test_valid_response(self):
        expiry_date = datetime(2029, 12, 1)

        response = CardDetailsResponse(
            card_number="1234567890123456",
            expiry_date=expiry_date,
            cvc="123",
        )

        assert response.card_number == "1234567890123456"
        assert response.expiry_date == expiry_date
        assert response.cvc == "123"

    def test_expiry_date_serializer(self):
        response = CardDetailsResponse(
            card_number="1234567890123456",
            expiry_date=datetime(2029, 12, 1),
            cvc="123",
        )

        data = response.model_dump()

        assert data["expiry_date"] == "12/29"

    @pytest.mark.parametrize(
        "expiry_date, expected",
        [
            (datetime(2026, 1, 1), "01/26"),
            (datetime(2027, 6, 15), "06/27"),
            (datetime(2030, 11, 30), "11/30"),
        ],
    )
    def test_expiry_date_serializer_formats_correctly(
        self,
        expiry_date,
        expected,
    ):
        response = CardDetailsResponse(
            card_number="1234567890123456",
            expiry_date=expiry_date,
            cvc="123",
        )

        assert response.model_dump()["expiry_date"] == expected


class TestCardStatusResponse:

    def test_valid_response(self):
        response = CardStatusResponse(status="ACTIVE")

        assert response.status == "ACTIVE"

    def test_missing_status(self):
        with pytest.raises(ValidationError):
            CardStatusResponse()


class TestAdminCardResponse:

    def test_valid_response(self):
        created_at = datetime(2026, 8, 20, 10, 30, 0)
        expiry_date = datetime(2029, 12, 1)

        response = AdminCardResponse(
            id=1,
            account_id=100,
            card_number="1234567890123456",
            cvc="123",
            expiry_date=expiry_date,
            status="ACTIVE",
            created_at=created_at,
            user_id=50,
            first_name="John",
            last_name="Smith",
            email="john@example.com",
        )

        assert response.id == 1
        assert response.account_id == 100
        assert response.card_number == "1234567890123456"
        assert response.cvc == "123"
        assert response.expiry_date == expiry_date
        assert response.status == "ACTIVE"
        assert response.created_at == created_at

        assert response.user_id == 50
        assert response.first_name == "John"
        assert response.last_name == "Smith"
        assert response.email == "john@example.com"

    def test_missing_customer_information(self):
        with pytest.raises(ValidationError):
            AdminCardResponse(
                id=1,
                account_id=100,
                card_number="1234567890123456",
                cvc="123",
                expiry_date=datetime(2029, 12, 1),
                status="ACTIVE",
                created_at=datetime(2026, 8, 20),
                user_id=50,
                first_name="John",
                last_name="Smith",
                # email missing
            )