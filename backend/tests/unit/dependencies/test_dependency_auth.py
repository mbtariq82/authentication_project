from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from jose import JWTError

from database import async_session_factory

from dependencies.auth import (
    get_auth_service,
    get_current_user,
    require_admin,
    get_user_account,
)
from enums import Role
from exceptions import (
    AccountNotFoundError,
    InvalidAccessTokenError,
    PermissionDeniedError,
)
from schemas.user import UserResponse
from services.auth_service import AuthService
from domain.card import AuthenticatedUserContext


class TestGetAuthService:

    @patch("dependencies.auth.AuthService")
    @patch("dependencies.auth.SqlAlchemyAuthUnitOfWork")
    def test_returns_auth_service(
        self,
        mock_uow_class,
        mock_auth_service,
    ):
        image_storage = MagicMock()

        mock_uow = MagicMock()
        mock_uow_class.return_value = mock_uow

        expected_service = MagicMock(spec=AuthService)
        mock_auth_service.return_value = expected_service

        result = get_auth_service(
            image_storage=image_storage,
        )

        assert result is expected_service

        mock_uow_class.assert_called_once_with(
            async_session_factory
        )

        mock_auth_service.assert_called_once_with(
            mock_uow,
            image_storage,
        )


class TestGetCurrentUser:

    @pytest.mark.asyncio
    @patch("dependencies.auth.decode_token")
    async def test_returns_current_user(
        self,
        mock_decode_token,
    ):
        user_service = MagicMock()
        user_service.get_by_id = AsyncMock()

        user = MagicMock(spec=UserResponse)
        user.id = 123

        user_service.get_by_id.return_value = user

        mock_decode_token.return_value = {
            "sub": "123",
            "type": "access",
        }

        result = await get_current_user(
            access_token="valid-token",
            user_service=user_service,
        )

        assert result is user

        mock_decode_token.assert_called_once_with("valid-token")
        user_service.get_by_id.assert_awaited_once_with(123)

    @pytest.mark.asyncio
    @patch("dependencies.auth.decode_token")
    async def test_invalid_jwt_raises_invalid_access_token_error(
        self,
        mock_decode_token,
    ):
        user_service = MagicMock()

        mock_decode_token.side_effect = JWTError()

        with pytest.raises(InvalidAccessTokenError):
            await get_current_user(
                access_token="invalid-token",
                user_service=user_service,
            )

    @pytest.mark.asyncio
    @patch("dependencies.auth.decode_token")
    async def test_invalid_sub_raises_invalid_access_token_error(
        self,
        mock_decode_token,
    ):
        user_service = MagicMock()

        mock_decode_token.return_value = {
            "sub": "not-an-integer",
            "type": "access",
        }

        with pytest.raises(InvalidAccessTokenError):
            await get_current_user(
                access_token="invalid-token",
                user_service=user_service,
            )

        user_service.get_by_id.assert_not_called()

    @pytest.mark.asyncio
    @patch("dependencies.auth.decode_token")
    async def test_missing_sub_raises_invalid_access_token_error(
        self,
        mock_decode_token,
    ):
        user_service = MagicMock()

        mock_decode_token.return_value = {
            "type": "access",
        }

        with pytest.raises(InvalidAccessTokenError):
            await get_current_user(
                access_token="token",
                user_service=user_service,
            )

        user_service.get_by_id.assert_not_called()

    @pytest.mark.asyncio
    @patch("dependencies.auth.decode_token")
    async def test_refresh_token_is_rejected(
        self,
        mock_decode_token,
    ):
        user_service = MagicMock()

        mock_decode_token.return_value = {
            "sub": "123",
            "type": "refresh",
        }

        with pytest.raises(InvalidAccessTokenError):
            await get_current_user(
                access_token="refresh-token",
                user_service=user_service,
            )

        user_service.get_by_id.assert_not_called()

    @pytest.mark.asyncio
    @patch("dependencies.auth.decode_token")
    async def test_user_not_found_raises_invalid_access_token_error(
        self,
        mock_decode_token,
    ):
        user_service = MagicMock()
        user_service.get_by_id = AsyncMock(return_value=None)

        mock_decode_token.return_value = {
            "sub": "123",
            "type": "access",
        }

        with pytest.raises(InvalidAccessTokenError):
            await get_current_user(
                access_token="valid-token",
                user_service=user_service,
            )

        user_service.get_by_id.assert_awaited_once_with(123)


class TestRequireAdmin:

    @pytest.mark.asyncio
    async def test_admin_is_allowed(self):
        user = MagicMock(spec=UserResponse)
        user.role = Role.ADMIN

        result = await require_admin(user=user)

        assert result is user

    @pytest.mark.asyncio
    async def test_non_admin_is_rejected(self):
        user = MagicMock(spec=UserResponse)
        user.role = Role.USER

        with pytest.raises(PermissionDeniedError):
            await require_admin(user=user)


class TestGetUserAccount:

    @pytest.mark.asyncio
    async def test_returns_authenticated_user_context(self):
        user = MagicMock(spec=UserResponse)
        user.id = 123

        account = MagicMock()
        account.id = 456

        account_service = MagicMock()
        account_service.get_account = AsyncMock(
            return_value=account
        )

        result = await get_user_account(
            user=user,
            account_service=account_service,
        )

        assert isinstance(result, AuthenticatedUserContext)
        assert result.user is user
        assert result.account is account

        account_service.get_account.assert_awaited_once_with(123)

    @pytest.mark.asyncio
    async def test_missing_account_raises_account_not_found_error(self):
        user = MagicMock(spec=UserResponse)
        user.id = 123

        account_service = MagicMock()
        account_service.get_account = AsyncMock(
            return_value=None
        )

        with pytest.raises(AccountNotFoundError):
            await get_user_account(
                user=user,
                account_service=account_service,
            )

        account_service.get_account.assert_awaited_once_with(123)