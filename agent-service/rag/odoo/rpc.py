from __future__ import annotations

import xmlrpc.client
from typing import Any

from ..config import settings


class OdooRpcClient:
    """Small Odoo XML-RPC adapter used behind the MCP tool boundary."""

    def __init__(
        self,
        *,
        url: str = settings.odoo_url,
        database: str = settings.odoo_database,
        login: str = settings.odoo_login,
        api_key: str = settings.odoo_api_key,
    ) -> None:
        if not api_key:
            raise RuntimeError(
                "Thiếu ODOO_API_KEY trong agent-service/.env. "
                "Hãy tạo API key cho tài khoản worker có quyền Settings."
            )
        self.url = url.rstrip("/")
        self.database = database
        self.login = login
        self.api_key = api_key
        self._common = xmlrpc.client.ServerProxy(
            f"{self.url}/xmlrpc/2/common", allow_none=True
        )
        self._models = xmlrpc.client.ServerProxy(
            f"{self.url}/xmlrpc/2/object", allow_none=True
        )
        self._uid: int | None = None

    @property
    def uid(self) -> int:
        if self._uid is None:
            uid = self._common.authenticate(
                self.database, self.login, self.api_key, {}
            )
            if not uid:
                raise RuntimeError(
                    "Odoo từ chối ODOO_LOGIN/ODOO_API_KEY hoặc sai database."
                )
            self._uid = int(uid)
        return self._uid

    def call(self, method: str, *args: Any) -> Any:
        return self._models.execute_kw(
            self.database,
            self.uid,
            self.api_key,
            "ai.rag.document",
            method,
            list(args),
            {},
        )
