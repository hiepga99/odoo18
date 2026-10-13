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
    print(" Go 'exit' hoac 'quit' de thoat.")
    print("=" * 70)

    agent = HermesAgent()

    while True:
        try:
            user_input = input("\n Ban: ").strip()
            if not user_input:
                continue
            if user_input.lower() in ["exit", "quit"]:
                print("Tam biet ban!")
                break

            response = agent.chat(user_input)
            
            # Nếu Agent thực hiện Tool Call
            if response.get("type") == "tool_call":
                print(f"\n⚙️  [Hệ thống ERP] Đã định tuyến công cụ: '{response.get('tool_name')}' | Tham số: {response.get('arguments')}")
            
            print(f"\n🤖 [Chuyên viên Phân tích ERP]:\n{response.get('final_answer')}\n")
            print("-" * 70)

        except KeyboardInterrupt:
            print("\nĐã dừng chương trình.")
            break
        except Exception as e:
            print(f"Lỗi: {e}")

if __name__ == "__main__":
    main()
