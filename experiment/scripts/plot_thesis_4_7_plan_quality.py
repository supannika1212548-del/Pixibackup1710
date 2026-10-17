"""
plot_thesis_4_7_plan_quality.py
--------------------------------------------------------------------------------
สคริปต์สำหรับสร้างกราฟหัวข้อ 4.7 Plan Quality Benchmark
วิทยานิพนธ์ Pixinerary
- Graph 1: Comparison of Travel Itinerary Quality across Models (Heatmap Likert 1-5)
- Graph 2: Average Evaluation Scores by Model and Dimension (Grouped Bar Chart)
- Graph 3: Processing Time by Model (Bar Chart, sorted ascending)
- Data Export: table_4_7_plan_quality_summary.csv (สำหรับตรวจสอบย้อนกลับ)
--------------------------------------------------------------------------------
"""

import os
import sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# จัดการ Encoding สำหรับ Windows Terminal
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
        os.path.join(base_dir, "exp6_plan_evaluation.csv"),
        os.path.join(base_dir, "..", "exp6_plan_evaluation.csv"),
        os.path.join(base_dir, "..", "..", "exp6_plan_evaluation.csv"),
        os.path.join("D:\\", "1210backup", "experiment", "exp6_plan_evaluation.csv"),
        os.path.join("experiment", "exp6_plan_evaluation.csv"),
    ]
    
    csv_path = None
    for p in possible_csv_paths:
        if os.path.exists(p):
            csv_path = os.path.abspath(p)
            break
            
    if not csv_path:
        print("[Error] CSV not found: exp6_plan_evaluation.csv. Please verify file location.")
        sys.exit(1)
        
    print(f"[1/5] Found CSV Data File: {csv_path}")

    # โฟลเดอร์ปลายทางสำหรับบันทึกภาพและไฟล์สรุปผล
    output_dir = os.path.join(os.path.dirname(csv_path), "figures", "chapter_4")
    os.makedirs(output_dir, exist_ok=True)
    root_dir = os.path.abspath(os.path.join(os.path.dirname(csv_path), ".."))

    # --------------------------------------------------------------------------
    # 2. โหลดและตรวจสอบข้อมูล (Data Inspection & Verification)
    # --------------------------------------------------------------------------
    df = pd.read_csv(csv_path)
    print(f"      - Total Records: {len(df)} rows, Total Columns: {len(df.columns)}")

    dim_cols = [
        ("Dim1_ConstraintSatisfaction", "Constraint Compliance"),
        ("Dim2_ActivityRelevance", "Activity Relevance"),
        ("Dim3_Spatiality", "Spatial Feasibility"),
        ("Dim4_AccuracyValidity", "Accuracy & Validity"),
        ("Dim5_OverallQuality", "Overall Quality"),
    ]
    
    raw_dim_keys = [c[0] for c in dim_cols]
    dim_labels = [c[1] for c in dim_cols]

    required_cols = ["Model", "Model Label", "Gen Latency MS", "Total Score"] + raw_dim_keys
    for col in required_cols:
        if col not in df.columns:
            raise KeyError(f"Missing required column '{col}' in CSV file.")

    # ตรวจสอบ Missing Values
    null_counts = df[required_cols].isnull().sum().to_dict()
    print(f"      - Missing values check: {null_counts}")

    # ตรวจสอบขอบเขตคะแนน (Score Range Check)
    for k in raw_dim_keys + ["Total Score"]:
        c_min, c_max = df[k].min(), df[k].max()
        if c_min < 1.0 or c_max > 5.0:
            print(f"      [Warning] Column {k} has values outside Likert 1-5: min={c_min}, max={c_max}")

    # ตรวจสอบจำนวนแผนต่อโมเดล
    model_counts = df.groupby(["Model", "Model Label"]).size().reset_index(name="Plan_Count")
    print(f"      - Plan counts per model:\n{model_counts.to_string(index=False)}")

    # ผู้ประเมิน
    evaluators = df["Evaluator Name"].unique().tolist()
    print(f"      - Evaluators recorded: {evaluators} (Total {len(evaluators)} entity)")

    # --------------------------------------------------------------------------
    # 3. คำนวณค่าเฉลี่ยและสรุปผลสถิติ (Mean Aggregation & Traceability Export)
    # --------------------------------------------------------------------------
    # รวบรวมค่าเฉลี่ยรายโมเดล
    agg_dict = {k: "mean" for k in raw_dim_keys}
    agg_dict["Total Score"] = "mean"
    agg_dict["Gen Latency MS"] = ["mean", "std", "count"]

    grouped = df.groupby(["Model", "Model Label"]).agg(
        **{label: (col, "mean") for col, label in dim_cols},
        Total_Score=("Total Score", "mean"),
        Latency_Mean_MS=("Gen Latency MS", "mean"),
        Latency_Std_MS=("Gen Latency MS", "std"),
        Latency_Mean_Sec=("Gen Latency MS", lambda x: np.mean(x) / 1000.0),
        Plan_Count=("Request ID", "count")
    ).reset_index()

    # เรียงลำดับโมเดลตาม Total Score จากมากไปน้อย
    grouped = grouped.sort_values(by="Total_Score", ascending=False).reset_index(drop=True)

    # ส่งออกตารางสรุปเป็น CSV เพื่อให้ตรวจสอบย้อนกลับได้ (Auditability)
    summary_csv_path1 = os.path.join(output_dir, "table_4_7_plan_quality_summary.csv")
    summary_csv_path2 = os.path.join(root_dir, "table_4_7_plan_quality_summary.csv")
    grouped.round(3).to_csv(summary_csv_path1, index=False, encoding="utf-8-sig")
    grouped.round(3).to_csv(summary_csv_path2, index=False, encoding="utf-8-sig")

    print("\n[2/5] Summary Table (Exported to CSV):")
    print("-" * 105)
    print(f"{'Model':<18} | {'N':<4} | {'Constraint':<11} | {'Relevance':<10} | {'Spatial':<8} | {'Accuracy':<9} | {'Quality':<8} | {'Total':<6} | {'Time (s)':<8}")
    print("-" * 105)
    for _, r in grouped.iterrows():
        print(f"{r['Model Label']:<18} | {int(r['Plan_Count']):<4} | {r['Constraint Compliance']:>10.2f}  | {r['Activity Relevance']:>9.2f}  | {r['Spatial Feasibility']:>7.2f}  | {r['Accuracy & Validity']:>8.2f}  | {r['Overall Quality']:>7.2f}  | {r['Total_Score']:>5.2f}  | {r['Latency_Mean_Sec']:>7.1f}s")
    print("-" * 105)

    # --------------------------------------------------------------------------
    # ตั้งค่าสไตล์กราฟเชิงวิชาการ (Academic Clean Publication Style)
    # --------------------------------------------------------------------------
    plt.rcParams["font.sans-serif"] = ["DejaVu Sans", "Arial", "Helvetica"]
    plt.rcParams["font.family"] = "sans-serif"
    plt.rcParams["axes.edgecolor"] = "#333333"
    plt.rcParams["axes.linewidth"] = 0.8

    # --------------------------------------------------------------------------
    # 4. สร้างกราฟที่ 1: Heatmap of Model Evaluation Scores
    # --------------------------------------------------------------------------
    print("\n[3/5] Generating Graph 1: Comparison of Travel Itinerary Quality across Models (Heatmap)...")
    fig1, ax1 = plt.subplots(figsize=(8.8, 5.0), dpi=300)
    fig1.patch.set_facecolor("white")
    ax1.set_facecolor("white")

    heatmap_cols = dim_labels + ["Total Score"]
    heatmap_data = grouped.set_index("Model Label")[dim_labels + ["Total_Score"]].copy()
    heatmap_data.columns = heatmap_cols

    # ใช้ Colormap YlGnBu หรือ Blues/Blues_r สำหรับสเกล Likert 1-5
    sns.heatmap(
        heatmap_data,
        annot=True,
        fmt=".2f",
        cmap="YlGnBu",
        vmin=1.0,
        vmax=5.0,
        cbar_kws={"label": "Evaluation Score (Likert Scale 1–5)", "ticks": [1.0, 2.0, 3.0, 4.0, 5.0]},
        linewidths=1.0,
        linecolor="#ffffff",
        annot_kws={"fontweight": "bold", "fontsize": 10},
        ax=ax1
    )

    ax1.set_title("Comparison of Travel Itinerary Quality across Models", fontsize=13, fontweight="bold", pad=14)
    ax1.set_xlabel("Evaluation Dimension", fontsize=11, fontweight="bold", labelpad=8)
    ax1.set_ylabel("Evaluated AI Model", fontsize=11, fontweight="bold", labelpad=8)
    plt.xticks(rotation=25, ha="right", fontsize=10, fontweight="semibold")
    plt.yticks(rotation=0, fontsize=10, fontweight="semibold")

    out_file1_sub = os.path.join(output_dir, "fig_4_7_1_quality_heatmap.png")
    out_file1_root = os.path.join(root_dir, "fig_4_7_1_quality_heatmap.png")
    fig1.savefig(out_file1_sub, dpi=300, bbox_inches="tight")
    fig1.savefig(out_file1_root, dpi=300, bbox_inches="tight")
    plt.close(fig1)
    print(f"      -> Successfully saved: {out_file1_sub}")
    print(f"      -> Successfully saved: {out_file1_root}")

    # --------------------------------------------------------------------------
    # 5. สร้างกราฟที่ 2: Grouped Bar Chart by Evaluation Dimension
    # --------------------------------------------------------------------------
    print("\n[4/5] Generating Graph 2: Average Evaluation Scores by Model and Dimension...")
    fig2, ax2 = plt.subplots(figsize=(11.0, 5.6), dpi=300)
    fig2.patch.set_facecolor("white")
    ax2.set_facecolor("white")

    n_dims = len(dim_labels)
    x_dim = np.arange(n_dims)
    n_models = len(grouped)
    bar_width = 0.13

    # กำหนด Palette ชัดเจนสำหรับ 6 โมเดล
    model_colors = ["#2563eb", "#059669", "#d97706", "#dc2626", "#0891b2", "#7c3aed"]

    for i, (_, row) in enumerate(grouped.iterrows()):
        scores = [row[d] for d in dim_labels]
        offset = (i - n_models / 2 + 0.5) * bar_width
        bars = ax2.bar(
            x_dim + offset,
            scores,
            width=bar_width,
            label=row["Model Label"],
            color=model_colors[i % len(model_colors)],
            edgecolor="#1f2937",
            linewidth=0.7,
            zorder=3
        )
        
        # แสดงค่าตัวเลขเหนือแท่งกราฟ (ขนาดกะทัดรัด)
        for bar in bars:
            h = bar.get_height()
            ax2.annotate(
                f"{h:.1f}",
                xy=(bar.get_x() + bar.get_width() / 2, h),
                xytext=(0, 3),
                textcoords="offset points",
                ha="center",
                va="bottom",
                fontsize=7.5,
                fontweight="bold",
                color="#111827"
            )

    ax2.set_title("Average Evaluation Scores by Model and Dimension", fontsize=13, fontweight="bold", pad=14)
    ax2.set_ylabel("Average Score (Likert Scale 1–5)", fontsize=11, fontweight="bold", labelpad=8)
    ax2.set_xlabel("Evaluation Dimension", fontsize=11, fontweight="bold", labelpad=8)
    ax2.set_xticks(x_dim)
    ax2.set_xticklabels(dim_labels, fontsize=10, fontweight="semibold")
    ax2.set_ylim(1.0, 5.2)
    ax2.set_yticks(np.arange(1.0, 5.1, 0.5))

    ax2.grid(axis="y", linestyle="--", alpha=0.4, color="#9ca3af", zorder=0)
    ax2.set_axisbelow(True)

    ax2.legend(loc="upper right", frameon=True, framealpha=0.95, edgecolor="#d1d5db", fontsize=9.5, ncol=2)
    ax2.spines["top"].set_visible(False)
    ax2.spines["right"].set_visible(False)

    out_file2_sub = os.path.join(output_dir, "fig_4_7_2_quality_grouped_bar.png")
    out_file2_root = os.path.join(root_dir, "fig_4_7_2_quality_grouped_bar.png")
    fig2.savefig(out_file2_sub, dpi=300, bbox_inches="tight")
    fig2.savefig(out_file2_root, dpi=300, bbox_inches="tight")
    plt.close(fig2)
    print(f"      -> Successfully saved: {out_file2_sub}")
    print(f"      -> Successfully saved: {out_file2_root}")

    # --------------------------------------------------------------------------
    # 6. สร้างกราฟที่ 3: Model Processing Time (Gen Latency MS -> Seconds)
    # --------------------------------------------------------------------------
    print("\n[5/5] Generating Graph 3: Processing Time by Model...")
    # เรียงลำดับโมเดลตามเวลาประมวลผลจากน้อยไปมาก (Fastest to Slowest)
    time_sorted = grouped.sort_values(by="Latency_Mean_Sec", ascending=True).reset_index(drop=True)

    fig3, ax3 = plt.subplots(figsize=(8.5, 4.8), dpi=300)
    fig3.patch.set_facecolor("white")
    ax3.set_facecolor("white")

    y_pos = np.arange(len(time_sorted))
    # สีไล่เฉด: เร็วสุด (เขียว) ไปจนถึง ช้าสุด (แดง/ส้ม)
    time_colors = ["#16a34a", "#059669", "#0284c7", "#2563eb", "#d97706", "#dc2626"]

    bars_time = ax3.barh(
        y_pos,
        time_sorted["Latency_Mean_Sec"],
        height=0.55,
        color=time_colors,
        edgecolor="#1f2937",
        linewidth=0.8,
        zorder=3
    )

    ax3.set_title("Processing Time by Model", fontsize=13, fontweight="bold", pad=14)
    ax3.set_xlabel("Mean Generation Latency (Seconds)", fontsize=11, fontweight="bold", labelpad=8)
    ax3.set_ylabel("Evaluated AI Model", fontsize=11, fontweight="bold", labelpad=8)
    ax3.set_yticks(y_pos)
    ax3.set_yticklabels(time_sorted["Model Label"], fontsize=10, fontweight="semibold")
    ax3.set_xlim(0, max(time_sorted["Latency_Mean_Sec"]) * 1.18)

    ax3.grid(axis="x", linestyle="--", alpha=0.4, color="#9ca3af", zorder=0)
    ax3.set_axisbelow(True)

    # แสดงตัวเลขวินาที (และ ms ในวงเล็บ) หลังแท่งกราฟ
    for bar, (_, r) in zip(bars_time, time_sorted.iterrows()):
        w = bar.get_width()
        ms_val = int(r["Latency_Mean_MS"])
        ax3.annotate(
            f"{w:.1f} s ({ms_val:,} ms)",
            xy=(w, bar.get_y() + bar.get_height() / 2),
            xytext=(6, 0),
            textcoords="offset points",
            ha="left",
            va="center",
            fontsize=9.5,
            fontweight="bold",
            color="#111827"
        )

    ax3.spines["top"].set_visible(False)
    ax3.spines["right"].set_visible(False)

    out_file3_sub = os.path.join(output_dir, "fig_4_7_3_processing_time.png")
    out_file3_root = os.path.join(root_dir, "fig_4_7_3_processing_time.png")
    fig3.savefig(out_file3_sub, dpi=300, bbox_inches="tight")
    fig3.savefig(out_file3_root, dpi=300, bbox_inches="tight")
    plt.close(fig3)
    print(f"      -> Successfully saved: {out_file3_sub}")
    print(f"      -> Successfully saved: {out_file3_root}")

    print("\n" + "=" * 75)
    print(f"[Done] All 3 figures and summary CSV table exported successfully at:")
    print(f"  - {output_dir}")
    print(f"  - {root_dir}")
    print("=" * 75)

if __name__ == "__main__":
    main()
