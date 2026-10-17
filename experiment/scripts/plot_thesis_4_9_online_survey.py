"""
plot_thesis_4_9_online_survey.py
--------------------------------------------------------------------------------
สคริปต์สำหรับสร้างกราฟหัวข้อ 4.9 Online Survey Evaluation
วิทยานิพนธ์ Pixinerary
- Graph 1: Mean Scores by Evaluation Dimension (Bar Chart, Likert 1-5)
- Graph 2: Likert Response Distribution (100% Stacked Bar Chart, Scores 1-5)
- Graph 3: Item-Level Mean Scores (Horizontal Bar Chart, 25 items: DKA, PFC, DVC, INV, CMP)
- Graph 4: System Readiness Assessment (Scale 1-10)
- Tables Export: table_4_9_1_dimension_summary.csv & table_4_9_2_item_summary.csv
--------------------------------------------------------------------------------
"""

import os
import sys
import re
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
    print("=" * 80)
    print("PIXINERARY THESIS: CHAPTER 4.9 ONLINE SURVEY EVALUATION (EXPERT ASSESSMENT)")
    print("=" * 80)

    base_dir = os.path.dirname(os.path.abspath(__file__))
    root_dir = os.path.abspath(os.path.join(base_dir, "..", ".."))
    output_dir = os.path.join(root_dir, "experiment", "figures", "chapter_4")
    os.makedirs(output_dir, exist_ok=True)

    # --------------------------------------------------------------------------
    # 1. ค้นหาและโหลดไฟล์แบบสอบถามจริง
    # --------------------------------------------------------------------------
    survey_filename = "แบบประเมินคุณภาพระบบโดยผู้เชี่ยวชาญด้านการท่องเที่ยว (Expert Quality Assessment).csv"
    possible_paths = [
        os.path.join(base_dir, survey_filename),
        os.path.join(base_dir, "..", survey_filename),
        os.path.join(root_dir, "experiment", survey_filename),
        os.path.join(root_dir, survey_filename),
        survey_filename,
    ]

    csv_path = None
    for p in possible_paths:
        if os.path.exists(p):
            csv_path = os.path.abspath(p)
            break

    if not csv_path:
        print(f"[Error] Survey CSV file '{survey_filename}' not found.")
        sys.exit(1)

    print(f"\n[1/5] Loaded Survey File: {csv_path}")

    # โหลดไฟล์ CSV (รองรับ UTF-8 / UTF-8-sig)
    try:
        df = pd.read_csv(csv_path, encoding="utf-8")
    except UnicodeDecodeError:
        df = pd.read_csv(csv_path, encoding="utf-8-sig")

    n_respondents = len(df)
    print(f"      - Number of Respondents (N): {n_respondents}")
    print(f"      - Total Columns: {len(df.columns)}")

    # --------------------------------------------------------------------------
    # 2. จำแนกและจับคู่ข้อคำถามกับ 5 มิติการประเมิน (DKA, PFC, DVC, INV, CMP)
    # --------------------------------------------------------------------------
    dim_metadata = {
        "DKA": {
            "name": "Accuracy of Tourism Content",
            "thai_name": "ความถูกต้องของเนื้อหาการท่องเที่ยว",
            "color": "#1e40af"
        },
        "PFC": {
            "name": "Practical Feasibility",
            "thai_name": "ความเป็นไปได้ในทางปฏิบัติ",
            "color": "#0284c7"
        },
        "DVC": {
            "name": "Diversity & Coverage",
            "thai_name": "ความหลากหลายและความครอบคลุม",
            "color": "#059669"
        },
        "INV": {
            "name": "Innovation & Tourism Utility",
            "thai_name": "นวัตกรรมและประโยชน์ต่อวงการ",
            "color": "#d97706"
        },
        "CMP": {
            "name": "Comparison with Existing Tools",
            "thai_name": "การเปรียบเทียบกับเครื่องมือเดิม",
            "color": "#7c3aed"
        }
    }

    # ค้นหาคอลัมน์ Likert 25 ข้อจาก Header จริง
    item_cols = [c for c in df.columns if any(k in c for k in ["DKA", "PFC", "DVC", "INV", "CMP"])]
    print(f"      - Identified Likert Scale Items: {len(item_cols)} items")

    items_list = []
    dim_scores = {k: [] for k in dim_metadata}

    for col in item_cols:
        match = re.search(r"\[([A-Z0-9]+):\s*(.*?)\]", col)
        if match:
            item_code = match.group(1).strip()
            item_desc = match.group(2).strip()
        else:
            item_code = col[:4].strip()
            item_desc = col

        dim_code = item_code[:3]
        scores = df[col].astype(float).tolist()
        mean_score = np.mean(scores)
        sd_score = np.std(scores, ddof=1) if len(scores) > 1 else 0.0

        items_list.append({
            "Item_Code": item_code,
            "Dimension": dim_code,
            "Description": item_desc,
            "Score_Resp1": scores[0] if len(scores) > 0 else np.nan,
            "Score_Resp2": scores[1] if len(scores) > 1 else np.nan,
            "Item_Mean": mean_score,
            "Item_SD": sd_score
        })
        dim_scores[dim_code].extend(scores)

    items_df = pd.DataFrame(items_list)

    # คำนวณค่าเฉลี่ยและ SD ระดับมิติ
    dim_summary_list = []
    for dim_code, meta in dim_metadata.items():
        vals = dim_scores[dim_code]
        mean_val = np.mean(vals)
        sd_val = np.std(vals, ddof=1)
        dim_summary_list.append({
            "Dimension_Code": dim_code,
            "Dimension_Name": meta["name"],
            "Thai_Name": meta["thai_name"],
            "Item_Count": len(vals) // n_respondents,
            "Total_Responses": len(vals),
            "Mean_Score": mean_val,
            "SD": sd_val,
            "Color": meta["color"]
        })

    dim_df = pd.DataFrame(dim_summary_list)

    # ส่งออกตารางสรุปผลเพื่อการตรวจสอบย้อนกลับ (Traceability)
    dim_csv1 = os.path.join(output_dir, "table_4_9_1_dimension_summary.csv")
    dim_csv2 = os.path.join(root_dir, "table_4_9_1_dimension_summary.csv")
    dim_df.drop(columns=["Color"]).round(3).to_csv(dim_csv1, index=False, encoding="utf-8-sig")
    dim_df.drop(columns=["Color"]).round(3).to_csv(dim_csv2, index=False, encoding="utf-8-sig")

    item_csv1 = os.path.join(output_dir, "table_4_9_2_item_summary.csv")
    item_csv2 = os.path.join(root_dir, "table_4_9_2_item_summary.csv")
    items_df.round(3).to_csv(item_csv1, index=False, encoding="utf-8-sig")
    items_df.round(3).to_csv(item_csv2, index=False, encoding="utf-8-sig")

    print("\n[2/5] Summary by Dimension Table:")
    print("-" * 88)
    print(f"{'Dimension':<32} | {'Items':<6} | {'Responses (N)':<14} | {'Mean (1-5)':<12} | {'SD':<6}")
    print("-" * 88)
    for _, r in dim_df.iterrows():
        print(f"{r['Dimension_Code']} - {r['Dimension_Name']:<26} | {r['Item_Count']:<6} | {r['Total_Responses']:<14} | {r['Mean_Score']:>10.2f}  | {r['SD']:>5.2f}")
    print("-" * 88)

    # --------------------------------------------------------------------------
    # สไตล์กราฟทางวิชาการ (Academic Publication Style)
    # --------------------------------------------------------------------------
    plt.rcParams["font.sans-serif"] = ["DejaVu Sans", "Arial", "Helvetica"]
    plt.rcParams["font.family"] = "sans-serif"
    plt.rcParams["axes.edgecolor"] = "#333333"
    plt.rcParams["axes.linewidth"] = 0.8

    # --------------------------------------------------------------------------
    # 3. สร้างกราฟที่ 1: Mean Scores by Evaluation Dimension
    # --------------------------------------------------------------------------
    print("\n[3/5] Generating Graph 1: Mean Scores by Evaluation Dimension...")
    fig1, ax1 = plt.subplots(figsize=(8.5, 5.0), dpi=300)
    fig1.patch.set_facecolor("white")
    ax1.set_facecolor("white")

    bars1 = ax1.bar(
        dim_df["Dimension_Code"],
        dim_df["Mean_Score"],
        color=dim_df["Color"],
        width=0.52,
        edgecolor="#1f2937",
        linewidth=0.8,
        zorder=3
    )

    # เกณฑ์การแปลผล Likert 5 ระดับ (เกณฑ์มาตรฐาน: 3.51 - 4.50 = ระดับมาก/ดี, 4.51 - 5.00 = ระดับมากที่สุด)
    ax1.axhline(3.50, color="#6b7280", linestyle=":", linewidth=1.1, alpha=0.8, label="Benchmark: Good / High Quality (3.50)")
    ax1.axhline(4.50, color="#10b981", linestyle="--", linewidth=1.1, alpha=0.8, label="Benchmark: Excellent (4.50)")

    ax1.set_title("Expert Evaluation Scores by Dimension", fontsize=13, fontweight="bold", pad=14)
    ax1.set_ylabel("Mean Evaluation Score (Likert 1–5)", fontsize=11, fontweight="bold", labelpad=8)
    ax1.set_xlabel("Evaluation Dimension", fontsize=11, fontweight="bold", labelpad=8)
    ax1.set_ylim(1.0, 5.2)
    ax1.set_yticks(np.arange(1.0, 5.1, 0.5))
    ax1.set_xticks(np.arange(len(dim_df)))
    ax1.set_xticklabels([f"{r['Dimension_Code']}\n({r['Dimension_Name'][:18]}..)" for _, r in dim_df.iterrows()], fontsize=9.5, fontweight="semibold")

    ax1.grid(axis="y", linestyle="--", alpha=0.4, color="#9ca3af", zorder=0)
    ax1.set_axisbelow(True)
    ax1.legend(loc="lower right", frameon=True, framealpha=0.92, fontsize=8.5)

    for bar in bars1:
        h = bar.get_height()
        ax1.annotate(f"{h:.2f}", xy=(bar.get_x() + bar.get_width() / 2, h),
                     xytext=(0, 4), textcoords="offset points", ha="center", va="bottom",
                     fontsize=9.5, fontweight="bold", color="#111827")

    ax1.spines["top"].set_visible(False)
    ax1.spines["right"].set_visible(False)

    fig1_sub = os.path.join(output_dir, "fig_4_9_1_dimension_means.png")
    fig1_root = os.path.join(root_dir, "fig_4_9_1_dimension_means.png")
    fig1.savefig(fig1_sub, dpi=300, bbox_inches="tight")
    fig1.savefig(fig1_root, dpi=300, bbox_inches="tight")
    plt.close(fig1)
    print(f"      -> Successfully saved: {fig1_sub}")
    print(f"      -> Successfully saved: {fig1_root}")

    # --------------------------------------------------------------------------
    # 4. สร้างกราฟที่ 2: Likert Response Distribution (100% Stacked Bar Chart)
    # --------------------------------------------------------------------------
    print("\n[4/5] Generating Graph 2: Distribution of Expert Ratings across Evaluation Dimensions...")
    fig2, ax2 = plt.subplots(figsize=(9.2, 5.0), dpi=300)
    fig2.patch.set_facecolor("white")
    ax2.set_facecolor("white")

    # คำนวณสัดส่วนคะแนน 1, 2, 3, 4, 5 ในแต่ละมิติ
    dist_records = []
    for dim_code in dim_metadata:
        scores = dim_scores[dim_code]
        counts = {s: scores.count(s) for s in [1, 2, 3, 4, 5]}
        total_s = len(scores)
        pcts = {s: (counts[s] / total_s * 100.0) for s in [1, 2, 3, 4, 5]}
        pcts["Dimension"] = dim_code
        dist_records.append(pcts)

    dist_df = pd.DataFrame(dist_records).set_index("Dimension")

    # สี Likert 1-5 เชิงวิชาการ (1 = แดงเข้ม, 2 = ส้ม, 3 = เทา/ฟ้าอ่อน, 4 = น้ำเงิน, 5 = เขียวเข้ม)
    likert_colors = {
        1: "#ef4444",  # Score 1: Strongly Disagree
        2: "#f97316",  # Score 2: Disagree
        3: "#94a3b8",  # Score 3: Neutral
        4: "#3b82f6",  # Score 4: Agree
        5: "#10b981",  # Score 5: Strongly Agree
    }

    bottom = np.zeros(len(dist_df))
    for score in [1, 2, 3, 4, 5]:
        values = dist_df[score].values
        bars = ax2.bar(
            dist_df.index,
            values,
            bottom=bottom,
            label=f"Rating {score}" + (" (Neutral)" if score == 3 else " (Agree)" if score == 4 else " (Strongly Agree)" if score == 5 else ""),
            color=likert_colors[score],
            width=0.55,
            edgecolor="#ffffff",
            linewidth=0.8,
            zorder=3
        )
        
        # เขียนตัวเลขเปอร์เซ็นต์ในช่องที่มีค่า > 0
        for i, val in enumerate(values):
            if val >= 8.0:
                ax2.annotate(f"{val:.0f}%",
                             xy=(i, bottom[i] + val / 2),
                             ha="center", va="center",
                             fontsize=8.5, fontweight="bold",
                             color="#ffffff" if score in [1, 4, 5] else "#1e293b")
        bottom += values

    ax2.set_title("Distribution of Expert Ratings across Evaluation Dimensions", fontsize=13, fontweight="bold", pad=14)
    ax2.set_ylabel("Proportion of Responses (%)", fontsize=11, fontweight="bold", labelpad=8)
    ax2.set_xlabel("Evaluation Dimension", fontsize=11, fontweight="bold", labelpad=8)
    ax2.set_ylim(0, 105)
    ax2.set_yticks(np.arange(0, 101, 20))
    ax2.set_xticks(np.arange(len(dist_df)))
    ax2.set_xticklabels([f"{d}\n({dim_metadata[d]['name'][:18]}..)" for d in dist_df.index], fontsize=9.5, fontweight="semibold")

    ax2.grid(axis="y", linestyle="--", alpha=0.3, color="#9ca3af", zorder=0)
    ax2.set_axisbelow(True)
    ax2.legend(loc="upper right", bbox_to_anchor=(1.26, 1.0), frameon=True, fontsize=8.5)
    ax2.spines["top"].set_visible(False)
    ax2.spines["right"].set_visible(False)

    fig2_sub = os.path.join(output_dir, "fig_4_9_2_likert_distribution.png")
    fig2_root = os.path.join(root_dir, "fig_4_9_2_likert_distribution.png")
    fig2.savefig(fig2_sub, dpi=300, bbox_inches="tight")
    fig2.savefig(fig2_root, dpi=300, bbox_inches="tight")
    plt.close(fig2)
    print(f"      -> Successfully saved: {fig2_sub}")
    print(f"      -> Successfully saved: {fig2_root}")

    # --------------------------------------------------------------------------
    # 5. สร้างกราฟที่ 3: Item-Level Mean Scores (Horizontal Bar Chart)
    # --------------------------------------------------------------------------
    print("\n[5/5] Generating Graph 3: Mean Score by Questionnaire Item...")
    # เรียงลำดับข้อคำถามจากข้อแรกไปข้อสุดท้ายตามแบบสอบถาม
    items_sorted = items_df.sort_values(by="Item_Code", ascending=False).reset_index(drop=True)

    fig3, ax3 = plt.subplots(figsize=(9.5, 9.5), dpi=300)
    fig3.patch.set_facecolor("white")
    ax3.set_facecolor("white")

    y_pos = np.arange(len(items_sorted))
    bar_colors = [dim_metadata[r["Dimension"]]["color"] for _, r in items_sorted.iterrows()]

    bars3 = ax3.barh(
        y_pos,
        items_sorted["Item_Mean"],
        height=0.62,
        color=bar_colors,
        edgecolor="#1f2937",
        linewidth=0.7,
        zorder=3
    )

    ax3.set_title("Mean Score by Questionnaire Item (25 Items across 5 Dimensions)", fontsize=13, fontweight="bold", pad=14)
    ax3.set_xlabel("Mean Likert Score (1–5)", fontsize=11, fontweight="bold", labelpad=8)
    ax3.set_ylabel("Questionnaire Item Code", fontsize=11, fontweight="bold", labelpad=8)
    ax3.set_yticks(y_pos)
    ax3.set_yticklabels(items_sorted["Item_Code"], fontsize=9.5, fontweight="semibold")
    ax3.set_xlim(1.0, 5.3)
    ax3.set_xticks(np.arange(1.0, 5.1, 0.5))

    ax3.grid(axis="x", linestyle="--", alpha=0.4, color="#9ca3af", zorder=0)
    ax3.set_axisbelow(True)

    for bar in bars3:
        w = bar.get_width()
        ax3.annotate(f"{w:.2f}",
                     xy=(w, bar.get_y() + bar.get_height() / 2),
                     xytext=(4, 0), textcoords="offset points",
                     ha="left", va="center",
                     fontsize=8.5, fontweight="bold", color="#111827")

    # Legend สำหรับ 5 มิติ
    handles = [plt.Rectangle((0, 0), 1, 1, color=dim_metadata[d]["color"]) for d in dim_metadata]
    labels = [f"{d}: {dim_metadata[d]['name']}" for d in dim_metadata]
    ax3.legend(handles, labels, loc="lower left", frameon=True, fontsize=8.5)

    ax3.spines["top"].set_visible(False)
    ax3.spines["right"].set_visible(False)

    fig3_sub = os.path.join(output_dir, "fig_4_9_3_item_means.png")
    fig3_root = os.path.join(root_dir, "fig_4_9_3_item_means.png")
    fig3.savefig(fig3_sub, dpi=300, bbox_inches="tight")
    fig3.savefig(fig3_root, dpi=300, bbox_inches="tight")
    plt.close(fig3)
    print(f"      -> Successfully saved: {fig3_sub}")
    print(f"      -> Successfully saved: {fig3_root}")

    # --------------------------------------------------------------------------
    # 6. สร้างกราฟที่ 4: System Readiness Assessment (Scale 1-10)
    # --------------------------------------------------------------------------
    readiness_col = [c for c in df.columns if "ความพร้อมในระดับใดสำหรับการนำไปใช้งานจริง" in c]
    if readiness_col:
        print("\nGenerating Graph 4: System Readiness Assessment...")
        col_name = readiness_col[0]
        readiness_scores = df[col_name].astype(float).tolist()
        mean_readiness = np.mean(readiness_scores)

        fig4, ax4 = plt.subplots(figsize=(7.5, 4.8), dpi=300)
        fig4.patch.set_facecolor("white")
        ax4.set_facecolor("white")

        x_labels = ["Expert 1", "Expert 2", "Mean Overall"]
        y_vals = [readiness_scores[0], readiness_scores[1], mean_readiness]
        bar_colors4 = ["#0284c7", "#0284c7", "#1e40af"]

        bars4 = ax4.bar(x_labels, y_vals, color=bar_colors4, width=0.48, edgecolor="#1f2937", linewidth=0.8, zorder=3)
        ax4.axhline(mean_readiness, color="#1e40af", linestyle="--", linewidth=1.2, alpha=0.8, label=f"Mean Readiness ({mean_readiness:.1f} / 10)")

        ax4.set_title("System Readiness Assessment (Scale 1–10)", fontsize=13, fontweight="bold", pad=14)
        ax4.set_ylabel("Readiness Score (1–10)", fontsize=11, fontweight="bold", labelpad=8)
        ax4.set_xlabel("Evaluator Panel", fontsize=11, fontweight="bold", labelpad=8)
        ax4.set_ylim(0, 11)
        ax4.set_yticks(np.arange(0, 11, 2))

        ax4.grid(axis="y", linestyle="--", alpha=0.4, color="#9ca3af", zorder=0)
        ax4.set_axisbelow(True)
        ax4.legend(loc="lower right", frameon=True, fontsize=9.0)

        for bar in bars4:
            h = bar.get_height()
            ax4.annotate(f"{h:.1f}", xy=(bar.get_x() + bar.get_width() / 2, h),
                         xytext=(0, 4), textcoords="offset points", ha="center", va="bottom",
                         fontsize=10, fontweight="bold", color="#111827")

        ax4.spines["top"].set_visible(False)
        ax4.spines["right"].set_visible(False)

        fig4_sub = os.path.join(output_dir, "fig_4_9_4_system_readiness.png")
        fig4_root = os.path.join(root_dir, "fig_4_9_4_system_readiness.png")
        fig4.savefig(fig4_sub, dpi=300, bbox_inches="tight")
        fig4.savefig(fig4_root, dpi=300, bbox_inches="tight")
        plt.close(fig4)
        print(f"      -> Successfully saved: {fig4_sub}")
        print(f"      -> Successfully saved: {fig4_root}")
    else:
        print("\n[Warning] Column for system readiness not found, skipping Graph 4.")

    print("\n" + "=" * 80)
    print("ALL 4 FIGURES & 2 SUMMARY CSV TABLES GENERATED SUCCESSFULLY!")
    print(f"Outputs located in:\n  - {output_dir}\n  - {root_dir}")
    print("=" * 80)

if __name__ == "__main__":
    main()
