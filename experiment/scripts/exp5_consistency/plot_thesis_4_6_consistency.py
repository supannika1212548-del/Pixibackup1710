"""
plot_thesis_4_6_consistency.py
--------------------------------------------------------------------------------
สคริปต์สำหรับสร้างกราฟหัวข้อ 4.6 Model Consistency and Stability
วิทยานิพนธ์ Pixinerary
- Graph 1: Model Performance under Different Temperature Settings (Grouped Bar Chart)
- Graph 2: Performance Change from Temperature 0.1 to 0.7 (Percentage Points: pp)
--------------------------------------------------------------------------------
"""

import os
import sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# ป้องกันปัญหา UnicodeEncodeError บน Windows PowerShell / Command Prompt
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

def main():
    # --------------------------------------------------------------------------
    # 1. จัดการ Path ให้เหมาะกับ Windows และ Cross-Platform
    # --------------------------------------------------------------------------
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    possible_csv_paths = [
        os.path.join(base_dir, "exp5_consistency.csv"),
        os.path.join(base_dir, "..", "exp5_consistency.csv"),
        os.path.join(base_dir, "..", "..", "exp5_consistency.csv"),
        os.path.join("D:\\", "1210backup", "experiment", "exp5_consistency.csv"),
        os.path.join("experiment", "exp5_consistency.csv"),
    ]
    
    csv_path = None
    for p in possible_csv_paths:
        if os.path.exists(p):
            csv_path = os.path.abspath(p)
            break
            
    if not csv_path:
        print("[Error] CSV not found: exp5_consistency.csv. Please check file path.")
        sys.exit(1)
        
    print(f"[1/4] Found CSV Data File: {csv_path}")

    # โฟลเดอร์ปลายทางสำหรับบันทึกภาพ
    output_dir = os.path.join(os.path.dirname(csv_path), "figures", "chapter_4")
    os.makedirs(output_dir, exist_ok=True)
    root_dir = os.path.abspath(os.path.join(os.path.dirname(csv_path), ".."))

    # --------------------------------------------------------------------------
    # 2. โหลดและตรวจสอบข้อมูล (Data Inspection & Verification)
    # --------------------------------------------------------------------------
    df = pd.read_csv(csv_path)
    print(f"      - Total Records: {len(df)} rows, Total Columns: {len(df.columns)}")

    required_cols = ["Model", "Temperature", "Is Correct"]
    for col in required_cols:
        if col not in df.columns:
            raise KeyError(f"Missing required column '{col}' in CSV file.")

    # ตรวจสอบค่า Temperature และ Model ที่มีอยู่จริงในไฟล์
    unique_temps = sorted(df["Temperature"].unique().tolist())
    unique_models = df["Model"].unique().tolist()
    print(f"      - Temperatures present in data: {unique_temps}")
    print(f"      - Models present in data: {unique_models}")

    # ตรวจสอบค่า Missing Values
    null_counts = df[required_cols].isnull().sum().to_dict()
    print(f"      - Missing values check: {null_counts}")

    # แปลงสถานะ Is Correct เป็น Boolean อย่างแม่นยำ
    df["is_correct_bool"] = df["Is Correct"].astype(str).str.strip().str.lower().isin(["true", "1"])

    # Mapping ชื่อโมเดลสำหรับแสดงผลทางวิชาการ (อ้างอิงตาม convention ของวิทยานิพนธ์)
    model_labels_map = {
        "anthropic-claude-sonnet5": "Claude Sonnet 5",
        "google-gemini-38-flash": "Gemini 3.8 Flash",
        "openai-gpt-54": "GPT-5.4",
        "openai-gpt-54-mini": "GPT-5.4 Mini",
        "qwen-25-vl-72b": "Qwen 2.5 VL 72B",
        "meta-llama4": "Llama 4 Maverick"
    }

    # --------------------------------------------------------------------------
    # 3. คำนวณ Accuracy และ Performance Change ตามโมเดลและ Temperature
    # --------------------------------------------------------------------------
    # สรุปค่าสถิติ: นับจำนวนรายการ, จำนวนที่ถูก, และคำนวณ Top-1 Accuracy (%)
    perf_summary = []
    for model_id in unique_models:
        row_dict = {
            "Model_ID": model_id,
            "Model_Label": model_labels_map.get(model_id, model_id)
        }
        for temp in unique_temps:
            sub = df[(df["Model"] == model_id) & (df["Temperature"] == temp)]
            n_total = len(sub)
            n_correct = sub["is_correct_bool"].sum()
            acc = (n_correct / n_total * 100.0) if n_total > 0 else 0.0
            row_dict[f"N_T{temp}"] = n_total
            row_dict[f"Correct_T{temp}"] = n_correct
            row_dict[f"Acc_T{temp}"] = acc
        
        # คำนวณผลต่าง (Performance Change = T0.7 - T0.1) ในหน่วย Percentage Points (pp)
        row_dict["Change_pp"] = row_dict["Acc_T0.7"] - row_dict["Acc_T0.1"]
        perf_summary.append(row_dict)

    summary_df = pd.DataFrame(perf_summary)
    
    # เรียงลำดับโมเดลตามผลการทดสอบที่ Temperature = 0.1 (Baseline Setting) จากมากไปน้อย
    summary_df = summary_df.sort_values(by="Acc_T0.1", ascending=False).reset_index(drop=True)

    print("\n[2/4] Summary Statistics Table (Top-1 Accuracy across Temperature):")
    print("-" * 88)
    print(f"{'Model':<20} | {'T=0.1 (N)':<10} | {'T=0.1 Acc':<12} | {'T=0.7 (N)':<10} | {'T=0.7 Acc':<12} | {'Change (pp)':<12}")
    print("-" * 88)
    for _, row in summary_df.iterrows():
        print(f"{row['Model_Label']:<20} | {int(row['N_T0.1']):<10} | {row['Acc_T0.1']:>10.2f}% | {int(row['N_T0.7']):<10} | {row['Acc_T0.7']:>10.2f}% | {row['Change_pp']:>+10.2f} pp")
    print("-" * 88)

    # --------------------------------------------------------------------------
    # ตั้งค่าสไตล์กราฟเชิงวิชาการ (Academic Clean Publication Style)
    # --------------------------------------------------------------------------
    plt.rcParams["font.sans-serif"] = ["DejaVu Sans", "Arial", "Helvetica"]
    plt.rcParams["font.family"] = "sans-serif"
    plt.rcParams["axes.edgecolor"] = "#333333"
    plt.rcParams["axes.linewidth"] = 0.8

    # --------------------------------------------------------------------------
    # 4. สร้างกราฟที่ 1: Model Performance under Different Temperature Settings
    # --------------------------------------------------------------------------
    print("\n[3/4] Generating Graph 1: Model Performance under Different Temperature Settings...")
    fig1, ax1 = plt.subplots(figsize=(9.2, 5.2), dpi=300)
    fig1.patch.set_facecolor("white")
    ax1.set_facecolor("white")

    x = np.arange(len(summary_df))
    bar_width = 0.36

    # สีวิชาการแยกตาม Temperature: T=0.1 (น้ำเงินสุขุม), T=0.7 (ส้มแอมเบอร์)
    color_t01 = "#1e40af"  # Deep Blue (Low entropy / Deterministic)
    color_t07 = "#d97706"  # Amber Orange (Higher sampling entropy)

    bars_t01 = ax1.bar(
        x - bar_width / 2,
        summary_df["Acc_T0.1"],
        width=bar_width,
        label="Temperature = 0.1 (Deterministic)",
        color=color_t01,
        edgecolor="#1f2937",
        linewidth=0.8,
        zorder=3
    )

    bars_t07 = ax1.bar(
        x + bar_width / 2,
        summary_df["Acc_T0.7"],
        width=bar_width,
        label="Temperature = 0.7 (Stochastic)",
        color=color_t07,
        edgecolor="#1f2937",
        linewidth=0.8,
        zorder=3
    )

    ax1.set_title("Model Performance under Different Temperature Settings", fontsize=13, fontweight="bold", pad=14)
    ax1.set_ylabel("Top-1 Accuracy (%)", fontsize=11, fontweight="bold", labelpad=8)
    ax1.set_xlabel("Evaluated AI Model", fontsize=11, fontweight="bold", labelpad=8)
    ax1.set_xticks(x)
    ax1.set_xticklabels(summary_df["Model_Label"], fontsize=10, fontweight="semibold", rotation=15, ha="right")
    ax1.set_ylim(0, 110)
    ax1.set_yticks(np.arange(0, 101, 20))

    # Grid แนวนอนแบบบาง
    ax1.grid(axis="y", linestyle="--", alpha=0.4, color="#9ca3af", zorder=0)
    ax1.set_axisbelow(True)

    # Legend ชัดเจน
    ax1.legend(loc="upper right", frameon=True, framealpha=0.95, edgecolor="#d1d5db", fontsize=9.5)

    # แสดงตัวเลขบนแท่งกราฟ
    for bar in bars_t01:
        h = bar.get_height()
        ax1.annotate(
            f"{h:.1f}%",
            xy=(bar.get_x() + bar.get_width() / 2, h),
            xytext=(0, 4),
            textcoords="offset points",
            ha="center",
            va="bottom",
            fontsize=8.5,
            fontweight="bold",
            color="#1e3a8a"
        )

    for bar in bars_t07:
        h = bar.get_height()
        ax1.annotate(
            f"{h:.1f}%",
            xy=(bar.get_x() + bar.get_width() / 2, h),
            xytext=(0, 4),
            textcoords="offset points",
            ha="center",
            va="bottom",
            fontsize=8.5,
            fontweight="bold",
            color="#92400e"
        )

    ax1.spines["top"].set_visible(False)
    ax1.spines["right"].set_visible(False)

    out_file1_sub = os.path.join(output_dir, "fig_4_6_1_model_temperature_comparison.png")
    out_file1_root = os.path.join(root_dir, "fig_4_6_1_model_temperature_comparison.png")
    fig1.savefig(out_file1_sub, dpi=300, bbox_inches="tight")
    fig1.savefig(out_file1_root, dpi=300, bbox_inches="tight")
    plt.close(fig1)
    print(f"      -> Successfully saved: {out_file1_sub}")
    print(f"      -> Successfully saved: {out_file1_root}")

    # --------------------------------------------------------------------------
    # 5. สร้างกราฟที่ 2: Performance Change from Temperature 0.1 to 0.7
    # --------------------------------------------------------------------------
    print("\n[4/4] Generating Graph 2: Performance Change from Temperature 0.1 to 0.7...")
    fig2, ax2 = plt.subplots(figsize=(8.8, 5.0), dpi=300)
    fig2.patch.set_facecolor("white")
    ax2.set_facecolor("white")

    # กำหนดสีตามทิศทางผลต่าง: ค่าบวก (เขียววิชาการ), ค่าลบ (แดงวิชาการ), ศูนย์ (เทา)
    change_colors = []
    for val in summary_df["Change_pp"]:
        if val > 0:
            change_colors.append("#16a34a")  # Green for gain
        elif val < 0:
            change_colors.append("#dc2626")  # Red for drop
        else:
            change_colors.append("#6b7280")  # Slate gray for neutral (0.0 pp)

    bars_diff = ax2.bar(
        x,
        summary_df["Change_pp"],
        width=0.48,
        color=change_colors,
        edgecolor="#1f2937",
        linewidth=0.8,
        zorder=3
    )

    # เส้นอ้างอิงชัดเจนที่ y = 0
    ax2.axhline(0, color="#111827", linewidth=1.2, zorder=4)

    ax2.set_title("Performance Change from Temperature 0.1 to 0.7", fontsize=13, fontweight="bold", pad=14)
    ax2.set_ylabel("Accuracy Change (Percentage Points, pp)", fontsize=11, fontweight="bold", labelpad=8)
    ax2.set_xlabel("Evaluated AI Model", fontsize=11, fontweight="bold", labelpad=8)
    ax2.set_xticks(x)
    ax2.set_xticklabels(summary_df["Model_Label"], fontsize=10, fontweight="semibold", rotation=15, ha="right")

    # กำหนดขอบเขตแกน Y ให้สมมาตรและอ่านง่าย
    y_min = min(summary_df["Change_pp"].min(), -6) - 2.5
    y_max = max(summary_df["Change_pp"].max(), 6) + 3.0
    ax2.set_ylim(y_min, y_max)

    # Grid แนวนอน
    ax2.grid(axis="y", linestyle="--", alpha=0.4, color="#9ca3af", zorder=0)
    ax2.set_axisbelow(True)

    # แสดงตัวเลขบน/ล่างแท่งกราฟ
    for bar, val in zip(bars_diff, summary_df["Change_pp"]):
        if val == 0:
            label_text = "0.0 pp"
            va = "bottom"
            y_annot = 0.3
        elif val > 0:
            label_text = f"+{val:.1f} pp"
            va = "bottom"
            y_annot = val + 0.3
        else:
            label_text = f"{val:.1f} pp"
            va = "top"
            y_annot = val - 0.4

        ax2.annotate(
            label_text,
            xy=(bar.get_x() + bar.get_width() / 2, val),
            xytext=(0, 4 if val >= 0 else -6),
            textcoords="offset points",
            ha="center",
            va=va,
            fontsize=9.5,
            fontweight="bold",
            color="#111827"
        )

    ax2.spines["top"].set_visible(False)
    ax2.spines["right"].set_visible(False)

    out_file2_sub = os.path.join(output_dir, "fig_4_6_1_temperature_performance_change.png")
    out_file2_target = os.path.join(output_dir, "fig_4_6_2_temperature_performance_change.png")
    out_file2_root = os.path.join(root_dir, "fig_4_6_2_temperature_performance_change.png")
    
    fig2.savefig(out_file2_target, dpi=300, bbox_inches="tight")
    fig2.savefig(out_file2_root, dpi=300, bbox_inches="tight")
    plt.close(fig2)
    print(f"      -> Successfully saved: {out_file2_target}")
    print(f"      -> Successfully saved: {out_file2_root}")

    print("\n" + "=" * 75)
    print(f"[Done] Both Chapter 4.6 figures saved successfully at:")
    print(f"  - {output_dir}")
    print(f"  - {root_dir}")
    print("=" * 75)

if __name__ == "__main__":
    main()
