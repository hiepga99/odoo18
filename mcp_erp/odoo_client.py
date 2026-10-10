# -*- coding: utf-8 -*-
import xmlrpc.client
from typing import Dict, Any, List, Optional

class OdooClient:
    """
    Client kết nối trực tiếp Odoo 18 ERP qua XML-RPC API.
    Quản lý xác thực, tự động kết nối lại và xử lý lỗi.
    """
    def __init__(
        self,
        url: str = "http://localhost:8069",
        db: str = "odoo18",
        username: str = "binhphung19112003@gmail.com",
        password: str = "admin"
    ):
        self.url = url
        self.db = db
        self.username = username
        self.password = password
        self.uid = None
        self.common = None
        self.models = None
        self._authenticate()

    def _authenticate(self) -> bool:
        try:
            self.common = xmlrpc.client.ServerProxy(f"{self.url}/xmlrpc/2/common")
            self.uid = self.common.authenticate(self.db, self.username, self.password, {})
            if self.uid:
                self.models = xmlrpc.client.ServerProxy(f"{self.url}/xmlrpc/2/object")
                return True
        except Exception:
            pass
        return False

    def is_connected(self) -> bool:
        return bool(self.uid and self.models)

    def execute_kw(self, model: str, method: str, args: List, kwargs: Optional[Dict] = None) -> Any:
        if not self.is_connected():
            if not self._authenticate():
                raise ConnectionError("Không thể kết nối đến Odoo 18 ERP.")
        kwargs = kwargs or {}
        return self.models.execute_kw(self.db, self.uid, self.password, model, method, args, kwargs)
