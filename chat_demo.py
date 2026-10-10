# -*- coding: utf-8 -*-
import sys
import os

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

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
            
            # Neu Agent thuc hien Tool Call
            if response.get("type") == "tool_call":
                print(f"[*] [Agent Core] -> Quyet dinh goi Tool: {response.get('tool_name')}")
                print(f"[+] [Tham so]: {response.get('arguments')}")
                print(f"[+] [Du lieu ERP]: {response.get('tool_result')}")
            else:
                print(f"[>] [Agent Core] -> Tra loi truc tiep: {response.get('final_answer')}")

        except KeyboardInterrupt:
            print("\nĐã dừng chương trình.")
            break
        except Exception as e:
            print(f"Lỗi: {e}")

if __name__ == "__main__":
    main()
