import pathlib
from odoo.tests import TransactionCase, tagged

# ngoại lệ có chủ đích; tool_provider/ir_actions_server: đọc định nghĩa
# action như core run() làm — code action vẫn chạy với env user (test_call_runs_as_user)
ALLOWED_SUDO_FILES = {'audit.py', 'ir_http.py', 'tool_provider.py', 'ir_actions_server.py'}


@tagged('post_install', '-at_install', 'ai_mcp')
class TestNoSudo(TransactionCase):

    def test_no_sudo_in_tool_flow(self):
        root = pathlib.Path(__file__).resolve().parent.parent
        offenders = []
        for py in root.rglob('*.py'):
            if 'tests' in py.parts or py.name in ALLOWED_SUDO_FILES:
                continue
            if '.sudo(' in py.read_text():
                offenders.append(str(py))
        self.assertFalse(offenders, f'sudo() ngoài vùng cho phép: {offenders}')
