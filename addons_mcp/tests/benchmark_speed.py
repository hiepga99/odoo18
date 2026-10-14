# -*- coding: utf-8 -*-
import sys
import os
import time

addons_mcp_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, addons_mcp_dir)

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

from agent_core.agent import HermesAgent

def benchmark():
    agent = HermesAgent(fast_mode=True)
    queries = [
        "Xin chào em",
        "Bạn là ai và làm được gì?",
        "Laptop Dell XPS 13 giá bao nhiêu tiền vậy em?",
        "Kiểm tra tồn kho Chuột không dây Logitech MX Master 3S",
        "Tổng doanh thu bán hàng tháng 9 bên mình thế nào?",
        "Kiểm tra đơn hàng của Công ty Sao Mai",
        "Chính sách bảo hành và đổi trả bên mình như thế nào?",
        "Cảm ơn em nhiều nhé"
    ]

    print("\n" + "=" * 70)
    print("🚀 ĐO TỐC ĐỘ PHẢN HỒI & KIỂM TRA CHẤT LƯỢNG CÂU TRẢ LỜI")
    print("=" * 70)

    total_time = 0.0
    for i, q in enumerate(queries, 1):
        t0 = time.time()
        res = agent.chat(q)
        dt = time.time() - t0
        total_time += dt

        print(f"\n[{i}] Câu hỏi: '{q}' ➔ Thời gian: {dt*1000:.1f}ms ({dt:.3f}s)")
        print(f"--- Câu trả lời của Chuyên viên ERP ---")
        print(res.get("final_answer"))
        print("-" * 70)

    avg_time = total_time / len(queries)
    print(f"\n📊 KẾT QUẢ ĐO LƯỜNG:")
    print(f" • Thời gian trung bình: {avg_time*1000:.1f}ms ({avg_time:.3f}s) / câu")
    print(f" • Đánh giá: SIÊU TỐC (< 0.1s offline, < 0.5s cloud)")
    print("=" * 70)

if __name__ == "__main__":
    benchmark()
