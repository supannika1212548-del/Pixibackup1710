"""
plot_thesis_4_5_robustness.py
--------------------------------------------------------------------------------
สคริปต์สำหรับสร้างกราฟหัวข้อ 4.5 Robustness Test สำหรับวิทยานิพนธ์ Pixinerary
- Graph 1: Model Robustness under Image Disturbances (0-100% Y-axis)
- Graph 2: Accuracy Change Relative to Baseline (Percentage Points: pp)
--------------------------------------------------------------------------------
"""

import os
import sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# ป้องกันปัญหา UnicodeEncodeError บน Windows terminal
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
    # กำหนดตำแหน่ง base_dir โดยอ้างอิงจากตำแหน่งของไฟล์สคริปต์
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    # ลำดับการค้นหาไฟล์ CSV (รองรับทั้งการรันจาก root, experiment หรือโฟลเดอร์ scripts)
    possible_csv_paths = [
        os.path.join(base_dir, "exp4_robustness.csv"),
        os.path.join(base_dir, "..", "exp4_robustness.csv"),
        os.path.join(base_dir, "..", "..", "exp4_robustness.csv"),
        os.path.join("D:\\", "1210backup", "experiment", "exp4_robustness.csv"),
        os.path.join("experiment", "exp4_robustness.csv"),
    ]
    
    csv_path = None
    for p in possible_csv_paths:
        if os.path.exists(p):
            csv_path = os.path.abspath(p)
            break
            
    if not csv_path:
        print("[Error] CSV not found: exp4_robustness.csv. Please check file path.")
        sys.exit(1)
        
    print(f"[1/4] Found CSV Data File: {csv_path}")

    # โฟลเดอร์ปลายทางสำหรับบันทึกรูปภาพ
    output_dir = os.path.join(os.path.dirname(csv_path), "figures", "chapter_4")
    os.makedirs(output_dir, exist_ok=True)

    # --------------------------------------------------------------------------
    # 2. โหลดและตรวจสอบข้อมูล (Data Inspection & Validation)
    # --------------------------------------------------------------------------
    df = pd.read_csv(csv_path)
    print(f"      - Total Records: {len(df)} rows, Total Columns: {len(df.columns)}")

    required_cols = ["Condition Category", "Is Correct"]
    for col in required_cols:
        if col not in df.columns:
            raise KeyError(f"Missing required column '{col}' in CSV file.")

    # ตรวจสอบค่า Missing Values
    null_counts = df[required_cols].isnull().sum().to_dict()
    print(f"      - Missing values check: {null_counts}")

    # แปลงสถานะ Is Correct เป็น Boolean
    df["is_correct_bool"] = df["Is Correct"].astype(str).str.strip().str.lower().isin(["true", "1"])

    # ลำดับสภาวะการทดลองตามที่ระบุในระเบียบวิธีวิจัย (ห้ามเรียงตามคะแนน)
    condition_order = ["Baseline", "Illumination", "Atmospheric", "Geometric", "Occlusion"]

    # --------------------------------------------------------------------------
    # 3. คำนวณ Accuracy (%) และ Accuracy Change (pp)
    # --------------------------------------------------------------------------
    summary = []
    for cond in condition_order:
        sub = df[df["Condition Category"] == cond]
        total_count = len(sub)
        correct_count = sub["is_correct_bool"].sum()
        acc = (correct_count / total_count * 100.0) if total_count > 0 else 0.0
        summary.append({
            "Condition": cond,
            "Total": total_count,
            "Correct": correct_count,
            "Accuracy": acc
        })

    summary_df = pd.DataFrame(summary).set_index("Condition")
    
    # คำนวณความต่างเทียบกับ Baseline (Percentage Points)
    baseline_acc = summary_df.loc["Baseline", "Accuracy"]
    summary_df["Accuracy_Change_pp"] = summary_df["Accuracy"] - baseline_acc

    print("\n[2/4] Summary Statistics Table:")
    print("-" * 75)
    print(f"{'Condition':<15} | {'Total':<6} | {'Correct':<7} | {'Accuracy (%)':<14} | {'Change (pp)':<12}")
    print("-" * 75)
    for cond in condition_order:
        row = summary_df.loc[cond]
        print(f"{cond:<15} | {int(row['Total']):<6} | {int(row['Correct']):<7} | {row['Accuracy']:>13.2f}% | {row['Accuracy_Change_pp']:>+11.2f} pp")
    print("-" * 75)

    # --------------------------------------------------------------------------
    # ตั้งค่ารูปแบบกราฟทางวิชาการ (Academic Publication Style)
    # --------------------------------------------------------------------------
    plt.rcParams["font.sans-serif"] = ["DejaVu Sans", "Arial", "Helvetica"]
    plt.rcParams["font.family"] = "sans-serif"
    plt.rcParams["axes.edgecolor"] = "#333333"
    plt.rcParams["axes.linewidth"] = 0.8

    # ชุดสีเชิงวิชาการที่สบายตาและเหมาะกับการพิมพ์
    colors_acc = ["#1e40af", "#d97706", "#0284c7", "#dc2626", "#7c3aed"]

    # --------------------------------------------------------------------------
    # 4. สร้างกราฟที่ 1: Model Robustness under Image Disturbances
    # --------------------------------------------------------------------------
    print("\n[3/4] Generating Graph 1: Model Robustness under Image Disturbances...")
    fig1, ax1 = plt.subplots(figsize=(7.5, 4.8), dpi=300)
    fig1.patch.set_facecolor("white")
    ax1.set_facecolor("white")

    bars1 = ax1.bar(
        condition_order,
        summary_df["Accuracy"],
        color=colors_acc,
        width=0.52,
        edgecolor="#1f2937",
        linewidth=0.9,
        zorder=3
    )

    # กำหนดแกน Y ตั้งแต่ 0 ถึง 100% ตามหลักการนำเสนอทางวิชาการ
    ax1.set_ylim(0, 105)
    ax1.set_yticks(np.arange(0, 101, 20))
    ax1.set_ylabel("Top-1 Accuracy (%)", fontsize=11, fontweight="bold", labelpad=8)
    ax1.set_xlabel("Image Disturbance Condition", fontsize=11, fontweight="bold", labelpad=8)
    ax1.set_title("Model Robustness under Image Disturbances", fontsize=13, fontweight="bold", pad=14)

    # เส้น Grid แนวนอนแบบบาง
    ax1.grid(axis="y", linestyle="--", alpha=0.4, color="#9ca3af", zorder=0)
    ax1.set_axisbelow(True)

    # เส้นประอ้างอิงระดับ Baseline (98.9%)
    ax1.axhline(baseline_acc, color="#1e40af", linestyle=":", linewidth=1.2, alpha=0.7, zorder=2)

    # แสดงตัวเลข Accuracy เหนือแท่งกราฟ
    for bar in bars1:
        height = bar.get_height()
        ax1.annotate(
            f"{height:.1f}%",
            xy=(bar.get_x() + bar.get_width() / 2, height),
            xytext=(0, 4),
            textcoords="offset points",
            ha="center",
            va="bottom",
            fontsize=10,
            fontweight="bold",
            color="#111827"
        )

    # ปรับแต่ง Spines
    ax1.spines["top"].set_visible(False)
    ax1.spines["right"].set_visible(False)
    ax1.tick_params(axis="x", labelsize=10.5)
    ax1.tick_params(axis="y", labelsize=10)

    out_file1 = os.path.join(output_dir, "fig_4_5_1_robustness_accuracy.png")
    fig1.savefig(out_file1, dpi=300, bbox_inches="tight")
    plt.close(fig1)
    print(f"      -> Successfully saved: {out_file1}")

    # --------------------------------------------------------------------------
    # 5. สร้างกราฟที่ 2: Accuracy Change Relative to Baseline
    # --------------------------------------------------------------------------
    print("\n[4/4] Generating Graph 2: Accuracy Change Relative to Baseline...")
    fig2, ax2 = plt.subplots(figsize=(7.5, 4.8), dpi=300)
    fig2.patch.set_facecolor("white")
    ax2.set_facecolor("white")

    # กำหนดสี: Baseline = Slate/Neutral, ค่าติดลบ = แดงวิชาการ
    colors_change = []
    for cond in condition_order:
        val = summary_df.loc[cond, "Accuracy_Change_pp"]
        if cond == "Baseline":
            colors_change.append("#4b5563")  # Slate gray for baseline
        elif val < 0:
            colors_change.append("#dc2626")  # Red for degradation
        else:
            colors_change.append("#16a34a")  # Green for improvement

    bars2 = ax2.bar(
        condition_order,
        summary_df["Accuracy_Change_pp"],
        color=colors_change,
        width=0.52,
        edgecolor="#1f2937",
        linewidth=0.9,
        zorder=3
    )

    # เส้นอ้างอิงชัดเจนที่ y = 0
    ax2.axhline(0, color="#111827", linewidth=1.2, zorder=4)

    # ปรับสเกลแกน Y ให้ครอบคลุมค่าติดลบและเหลือพื้นที่หัวแท่ง
    min_val = summary_df["Accuracy_Change_pp"].min()
    y_lower = np.floor(min_val - 2.5)
    ax2.set_ylim(y_lower, 2.5)
    ax2.set_ylabel("Accuracy Change (Percentage Points, pp)", fontsize=11, fontweight="bold", labelpad=8)
    ax2.set_xlabel("Image Disturbance Condition", fontsize=11, fontweight="bold", labelpad=8)
    ax2.set_title("Accuracy Change Relative to Baseline", fontsize=13, fontweight="bold", pad=14)

    # เส้น Grid แนวนอน
    ax2.grid(axis="y", linestyle="--", alpha=0.4, color="#9ca3af", zorder=0)
    ax2.set_axisbelow(True)

    # แสดงตัวเลข pp บน/ล่างแท่งกราฟ
    for bar, cond in zip(bars2, condition_order):
        val = summary_df.loc[cond, "Accuracy_Change_pp"]
        if cond == "Baseline":
            label_text = "0.0 pp (Ref)"
            va = "bottom"
        else:
            label_text = f"{val:+.1f} pp"
            va = "top" if val < 0 else "bottom"

        ax2.annotate(
            label_text,
            xy=(bar.get_x() + bar.get_width() / 2, val if cond != "Baseline" else 0),
            xytext=(0, -8 if val < 0 else 5),
            textcoords="offset points",
            ha="center",
            va=va,
            fontsize=10,
            fontweight="bold",
            color="#111827"
        )

    ax2.spines["top"].set_visible(False)
    ax2.spines["right"].set_visible(False)
    ax2.tick_params(axis="x", labelsize=10.5)
    ax2.tick_params(axis="y", labelsize=10)

    out_file2 = os.path.join(output_dir, "fig_4_5_2_accuracy_change.png")
    fig2.savefig(out_file2, dpi=300, bbox_inches="tight")
    plt.close(fig2)
    print(f"      -> Successfully saved: {out_file2}")

    print("\n" + "=" * 75)
    print(f"[Done] Both publication-grade figures saved at:\n  {output_dir}")
    print("=" * 75)

if __name__ == "__main__":
    main()
