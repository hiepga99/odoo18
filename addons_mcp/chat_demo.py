# -*- coding: utf-8 -*-
import sys
import os

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

addons_mcp_dir = os.path.abspath(os.path.dirname(__file__))
root_dir = os.path.abspath(os.path.join(addons_mcp_dir, '..'))
sys.path.insert(0, addons_mcp_dir)
sys.path.insert(0, root_dir)

from agent_core.agent import HermesAgent

def main():
    print("=" * 70)
    print(" CHUONG TRINH DEMO TUONG TAC AI AGENT ERP (HERMES AGENT CORE)")
    print(" Nguoi phat trien: Phung Thanh Binh (Engineer: BE/FE)")
    print(" Tinh nang: Phan quyen RBAC, Fast-Path 1-Pass, 12 MCP Tools Odoo")
    print(" Lenh ho tro: '/role manager' (Giam doc), '/role sales' (Sale), 'exit'")
    print("=" * 70)

    agent = HermesAgent()
    current_role = os.getenv("USER_ROLE", "sales_user")
    role_name_vn = "Ban Giám đốc / Quản lý (manager)" if current_role in ["manager", "admin"] else "Nhân viên Kinh doanh (sales_user)"

    print(f"🤖 Đang sử dụng Model LLM: {agent.llm_client.provider.upper()} ({agent.llm_client.model_name})")
    print(f"🔐 [Bảo mật RBAC] Đang đăng nhập với vai trò: {role_name_vn}")

    while True:
        try:
            user_input = input(f"\n Bạn [{current_role}]: ").strip()
            if not user_input:
                continue
            if user_input.lower() in ["exit", "quit"]:
                print("Tạm biệt bạn!")
                break
            
            # Lệnh chuyển đổi vai trò người dùng (RBAC test) - Hỗ trợ cả lệnh /role và câu nói tiếng Việt tự nhiên
            lower_input = user_input.lower().strip()
            if lower_input.startswith("/role") or any(kw in lower_input for kw in ["tôi là sếp", "tôi là giám đốc", "quyền giám đốc", "đổi sang sếp", "đổi sang giám đốc", "tài khoản quản lý"]):
                if any(w in lower_input for w in ["sales", "nhân viên", "sale"]):
                    current_role = "sales_user"
                    role_name_vn = "Nhân viên Kinh doanh (sales_user)"
                    print(f"🔄 Đã chuyển vai trò sang: {role_name_vn}")
                else:
                    current_role = "manager"
                    role_name_vn = "Ban Giám đốc / Quản lý (manager)"
                    print(f"🔄 Đã chuyển vai trò sang: {role_name_vn} (Được phép xem doanh thu, tài chính)")
                continue
            elif any(kw in lower_input for kw in ["tôi là nhân viên", "quyền nhân viên", "đổi sang nhân viên", "đổi sang sale", "tài khoản sale"]):
                current_role = "sales_user"
                role_name_vn = "Nhân viên Kinh doanh (sales_user)"
                print(f"🔄 Đã chuyển vai trò sang: {role_name_vn} (Giới hạn: không xem được doanh thu)")
                continue

            response = agent.chat(user_input, user_role=current_role)
            
            # Nếu Agent thực hiện Tool Call
            if response.get("type") == "tool_call":
                print(f"\n⚙️  [Hệ thống ERP] Đã định tuyến công cụ: '{response.get('tool_name')}' | Tham số: {response.get('arguments')}")
            
            engine_name = response.get("engine", "Chuyên viên Phân tích ERP")
            print(f"\n🤖 [{engine_name}]:\n{response.get('final_answer')}\n")
            print("-" * 70)

        except KeyboardInterrupt:
            print("\nĐã dừng chương trình.")
            break
        except Exception as e:
            print(f"Lỗi: {e}")

if __name__ == "__main__":
    main()
