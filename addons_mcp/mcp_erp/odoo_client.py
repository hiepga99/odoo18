# -*- coding: utf-8 -*-
import xmlrpc.client
import http.client
from typing import Dict, Any, List, Optional

class TimeoutTransport(xmlrpc.client.Transport):
    """Transport XML-RPC với cơ chế timeout kết nối nhanh (tránh treo socket)"""
    def __init__(self, timeout: float = 1.0, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.timeout = timeout

    def make_connection(self, host):
        return http.client.HTTPConnection(host, timeout=self.timeout)

class OdooClient:
    """
    Client kết nối trực tiếp Odoo 18 ERP qua XML-RPC API.
    Hỗ trợ timeout nhanh, tự động ngắt (circuit breaker) khi Odoo offline để tránh làm chậm Agent.
    """
    def __init__(
        self,
        url: str = "http://localhost:8069",
        db: str = "odoo18",
        username: str = "binhphung19112003@gmail.com",
        password: str = "admin",
        timeout: float = 1.0
    ):
        self.url = url
        self.db = db
        self.username = username
        self.password = password
        self.timeout = timeout
        self.uid = None
        self.common = None
        self.models = None
        self.is_offline = False
        self._authenticate()

    def _authenticate(self) -> bool:
        # No early return on is_offline: a server started before Odoo must recover on the next call.
        try:
            transport = TimeoutTransport(timeout=self.timeout)
            self.common = xmlrpc.client.ServerProxy(f"{self.url}/xmlrpc/2/common", transport=transport)
            self.uid = self.common.authenticate(self.db, self.username, self.password, {})
            if self.uid:
                self.models = xmlrpc.client.ServerProxy(f"{self.url}/xmlrpc/2/object", transport=transport)
                self.is_offline = False
                return True
        except Exception:
            self.is_offline = True
        return False

    def is_connected(self) -> bool:
        return bool(self.uid and self.models)

    def execute_kw(self, model: str, method: str, args: List, kwargs: Optional[Dict] = None) -> Any:
        if not self.is_connected():
            if not self._authenticate():
                raise ConnectionError("Không thể kết nối đến Odoo 18 ERP.")
        kwargs = kwargs or {}
        return self.models.execute_kw(self.db, self.uid, self.password, model, method, args, kwargs)

