"""
plot_thesis_4_8_blind_eval.py
--------------------------------------------------------------------------------
สคริปต์สำหรับตรวจสอบและแสดงผล Blind Evaluation หัวข้อ 4.8 ของวิทยานิพนธ์ Pixinerary
- ดำเนินการตรวจสอบความสมบูรณ์ของข้อมูล (Data Integrity Audit) ทุกแหล่งในโปรเจกต์
- สร้างตารางตรวจสอบย้อนกลับ: table_4_8_blind_data_audit.csv
- รายงานผลและข้อจำกัดเชิงวิชาการ: report_4_8_blind_evaluation_audit.txt
- สร้างกราฟตามข้อมูลที่มีอยู่จริง (ห้ามสร้างข้อมูลเท็จ):
  * fig_4_8_1_blind_evaluation_scores.png (เฉพาะคะแนนที่มีอยู่จริง พร้อมระบุ N)
  * ข้าม fig_4_8_2_plan_preference.png พร้อมให้เหตุผลทางวิชาการ
--------------------------------------------------------------------------------
"""

import os
import sys
import json
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# ป้องกันปัญหา UnicodeEncodeError บน Windows Terminal
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

def main():
    print("=" * 80)
    print("PIXINERARY THESIS: CHAPTER 4.8 BLIND EVALUATION DATA AUDIT & VISUALIZATION")
    print("=" * 80)

    base_dir = os.path.dirname(os.path.abspath(__file__))
    root_dir = os.path.abspath(os.path.join(base_dir, "..", ".."))
    output_dir = os.path.join(root_dir, "experiment", "figures", "chapter_4")
    os.makedirs(output_dir, exist_ok=True)

    # --------------------------------------------------------------------------
    # 1. สำรวจแหล่งข้อมูล Blind Evaluation ทั้งหมดในโปรเจกต์
    # --------------------------------------------------------------------------
    print("\n[1/4] Scanning all Blind Evaluation data sources in project...")
    sources = [
        ("Root /experiment/blind_evaluations.json", os.path.join(root_dir, "experiment", "blind_evaluations.json")),
        ("Root /experiment/blind_comparisons.json", os.path.join(root_dir, "experiment", "blind_comparisons.json")),
        ("Root /experiment/blind_trips.json", os.path.join(root_dir, "experiment", "blind_trips.json")),
        ("Backend /backend/experiment/blind_evaluations.json", os.path.join(root_dir, "backend", "experiment", "blind_evaluations.json")),
        ("Backend /backend/experiment/blind_comparisons.json", os.path.join(root_dir, "backend", "experiment", "blind_comparisons.json")),
        ("Backend /backend/experiment/blind_trips.json", os.path.join(root_dir, "backend", "experiment", "blind_trips.json")),
    ]

    source_inventory = []
    active_eval_path = None

    for label, path in sources:
        exists = os.path.exists(path)
        size = os.path.getsize(path) if exists else 0
        count = 0
        if exists and size > 2:
            try:
                with open(path, "r", encoding="utf-8") as f:
                    content = json.load(f)
                    count = len(content) if isinstance(content, list) else 1
            except Exception:
                count = -1

        source_inventory.append({
            "Source Label": label,
            "File Path": path,
            "Exists": exists,
            "Size (Bytes)": size,
            "Record Count": count
        })
        print(f"  - {label:<50} | Exists: {str(exists):<5} | Size: {size:>8} B | Records: {count}")

        if "blind_evaluations.json" in path and count > 0:
            active_eval_path = path

    # --------------------------------------------------------------------------
    # 2. ตรวจสอบความสมบูรณ์ของข้อมูลรายแถว (Data Completeness Audit)
    # --------------------------------------------------------------------------
    print("\n[2/4] Auditing Evaluation Records Integrity...")
    if not active_eval_path:
        print("[Critical Error] No non-empty blind evaluation data file found.")
        sys.exit(1)

    with open(active_eval_path, "r", encoding="utf-8") as f:
        eval_data = json.load(f)

    print(f"  -> Selected primary data source: {active_eval_path} (N = {len(eval_data)} records)")

    audit_rows = []
    for item in eval_data:
        scores = item.get("scores", {})
        audit_rows.append({
            "Eval_ID": item.get("id"),
            "Scenario_ID": item.get("scenario_id"),
            "Trip_ID": item.get("trip_id"),
            "Blind_Label": item.get("blind_label"),
            "Actual_Model": item.get("actual_model"),
            "Expert_Name": item.get("expert_name"),
            "Expert_ID": item.get("expert_id"),
            "Overall_Pick": item.get("overall_pick"),
            "Submitted_At": item.get("submitted_at"),
            "Spatial_Feasibility": scores.get("spatial_feasibility"),
            "Temporal_Pacing": scores.get("temporal_pacing"),
            "Persona_Alignment": scores.get("persona_alignment"),
            "Attraction_Quality": scores.get("attraction_quality"),
            "Info_Accuracy": scores.get("information_accuracy"),
            "Mean_Score": np.mean(list(scores.values())) if scores else np.nan
        })

    audit_df = pd.DataFrame(audit_rows)

    # บันทึกตาราง Audit ย้อนกลับได้
    audit_csv_path1 = os.path.join(output_dir, "table_4_8_blind_data_audit.csv")
    audit_csv_path2 = os.path.join(root_dir, "table_4_8_blind_data_audit.csv")
    audit_df.to_csv(audit_csv_path1, index=False, encoding="utf-8-sig")
    audit_df.to_csv(audit_csv_path2, index=False, encoding="utf-8-sig")
    print(f"  -> Audit table saved to: {audit_csv_path1}")

    # ตรวจสอบคู่ Plan A และ Plan B
    labels_present = audit_df["Blind_Label"].unique().tolist()
    scenarios_present = audit_df["Scenario_ID"].unique().tolist()
    experts_present = audit_df["Expert_Name"].unique().tolist()

    print(f"\n  [Audit Summary]")
    print(f"    - Total Evaluation Records: {len(audit_df)}")
    print(f"    - Evaluated Scenarios: {scenarios_present}")
    print(f"    - Blind Labels Present: {labels_present}")
    print(f"    - Evaluators Present: {experts_present} (Total {len(experts_present)})")

    has_plan_a = any("A" in str(l) for l in labels_present)
    has_plan_b = any("B" in str(l) for l in labels_present)
    is_paired_ab = has_plan_a and has_plan_b

    print(f"    - Has Plan A: {has_plan_a}")
    print(f"    - Has Plan B: {has_plan_b}")
    print(f"    - Is Paired A/B complete: {is_paired_ab}")

    # --------------------------------------------------------------------------
    # 3. สร้างรายงานการวิเคราะห์และระบุข้อจำกัดทางวิชาการ (Academic Audit Report)
    # --------------------------------------------------------------------------
    report_text = f"""================================================================================
PIXINERARY THESIS: SECTION 4.8 BLIND EVALUATION DATA INTEGRITY REPORT
================================================================================
Generated Date: 2026-10-17
Primary File Audited: {active_eval_path}
Total Records Available: {len(audit_df)}

1. DATA INVENTORY & VERIFICATION
--------------------------------------------------------------------------------
- Test Scenarios Evaluated: {', '.join(scenarios_present)}
- Evaluators Recorded: {', '.join(experts_present)} (Count = {len(experts_present)})
- Plan Labels Recorded: {', '.join(labels_present)}
- Paired Plan B Records: {'PRESENT' if is_paired_ab else 'MISSING (0 records for Plan B)'}

2. RECORD DETAILS
--------------------------------------------------------------------------------
"""
    for _, r in audit_df.iterrows():
        report_text += f"Record {r['Eval_ID']}: Scenario={r['Scenario_ID']} | Blind Label={r['Blind_Label']} | Actual Model={r['Actual_Model']} | Evaluator={r['Expert_Name']} | Pick={r['Overall_Pick']} | Mean Score={r['Mean_Score']:.2f}\n"

    report_text += f"""
3. METHODOLOGICAL CONSTRAINTS & LIMITATIONS
--------------------------------------------------------------------------------
[CRITICAL FINDING 1: Absence of Paired Plan B Evaluation]
The current repository contains only {len(audit_df)} evaluation records, both assigned to 'แผน A' 
(Plan A) under Scenario {scenarios_present}. No corresponding Plan B evaluations exist in the local 
dataset. Consequently, a head-to-head A/B comparison or relative win-rate calculation cannot be 
performed without fabricating unobserved data.

[CRITICAL FINDING 2: Inapplicability of Inter-Rater Agreement & Preference Distribution]
Because both records evaluate the same scenario from distinct actual models without a mutual 
paired choice between Plan A and Plan B, statistical metrics such as Cohen's Kappa, Fleiss' Kappa, 
or Win/Loss/Tie percentage distributions are mathematically and methodologically invalid.

[DECISION ON GRAPH CREATION]:
1. Graph 1 (fig_4_8_1_blind_evaluation_scores.png): CREATED
   - Renders ONLY the observed Likert scores across the 5 evaluation criteria for the 2 pilot evaluators.
   - Distinctly annotates that both records represent Plan A in a pilot evaluation (N = 2).
   - Explicitly does NOT display fictitious Plan B scores.

2. Graph 2 (fig_4_8_2_plan_preference.png): INTENTIONALLY SKIPPED
   - Rationale: A preference distribution requires paired pairwise choices (A vs B or Win/Loss/Tie).
   - Creating this chart with unpaired single-sided data would constitute research malpractice.

4. REQUIRED DATA COLLECTION PROTOCOL TO COMPLETE SECTION 4.8
--------------------------------------------------------------------------------
To achieve rigorous publication standards for Section 4.8 in the final thesis, the following 
empirical protocol must be completed:
  1. Multi-Scenario Coverage: Deploy at least 5–10 representative travel scenarios (e.g., SC-01 to SC-10).
  2. Balanced A/B Pairings: For each scenario, generate paired plans from competing LLM architectures 
     (e.g., Claude Sonnet 5 vs GPT-5.4 vs Gemini 3.8 Flash) with randomized, double-blind assignments.
  3. Multi-Expert Panel: Recruit at least 3–5 independent certified tourism domain experts.
  4. Decision Capture: Record both Likert dimensional ratings and explicit pairwise forced-choice 
     preferences (Plan A wins, Plan B wins, or Tie) to enable Fleiss' Kappa inter-rater reliability.
================================================================================
"""

    report_path1 = os.path.join(output_dir, "report_4_8_blind_evaluation_audit.txt")
    report_path2 = os.path.join(root_dir, "report_4_8_blind_evaluation_audit.txt")
    with open(report_path1, "w", encoding="utf-8") as f:
        f.write(report_text)
    with open(report_path2, "w", encoding="utf-8") as f:
        f.write(report_text)
    print(f"\n[3/4] Academic audit report written to: {report_path1}")

    # --------------------------------------------------------------------------
    # 4. สร้างกราฟที่ 1: Evaluation Scores by Plan and Evaluator (ข้อมูลจริงเท่านั้น)
    # --------------------------------------------------------------------------
    print("\n[4/4] Generating Visualizations based on Authenticated Data...")
    criteria_keys = [
        ("Spatial_Feasibility", "Spatial\nFeasibility"),
        ("Temporal_Pacing", "Temporal\nPacing"),
        ("Persona_Alignment", "Persona\nAlignment"),
        ("Attraction_Quality", "Attraction\nQuality"),
        ("Info_Accuracy", "Information\nAccuracy"),
    ]

    fig1, ax1 = plt.subplots(figsize=(8.8, 5.2), dpi=300)
    fig1.patch.set_facecolor("white")
    ax1.set_facecolor("white")

    x = np.arange(len(criteria_keys))
    bar_width = 0.32

    # แสดงคะแนนจริงของ Expert 1 และ Expert 2
    r1 = audit_df.iloc[0]
    r2 = audit_df.iloc[1]

    scores_exp1 = [r1[k[0]] for k in criteria_keys]
    scores_exp2 = [r2[k[0]] for k in criteria_keys]

    label_exp1 = f"{r1['Expert_Name']} (Plan A - {r1['Actual_Model']})"
    label_exp2 = f"{r2['Expert_Name']} (Plan A - {r2['Actual_Model']})"

    bars1 = ax1.bar(x - bar_width / 2, scores_exp1, bar_width, label=label_exp1,
                    color="#1e40af", edgecolor="#1f2937", linewidth=0.8, zorder=3)
    bars2 = ax1.bar(x + bar_width / 2, scores_exp2, bar_width, label=label_exp2,
                    color="#059669", edgecolor="#1f2937", linewidth=0.8, zorder=3)

    # แสดงตัวเลขบนแท่ง
    for bar in bars1:
        h = bar.get_height()
        ax1.annotate(f"{int(h)}", xy=(bar.get_x() + bar.get_width() / 2, h),
                     xytext=(0, 3), textcoords="offset points", ha="center", va="bottom",
                     fontsize=9, fontweight="bold", color="#1e3a8a")

    for bar in bars2:
        h = bar.get_height()
        ax1.annotate(f"{int(h)}", xy=(bar.get_x() + bar.get_width() / 2, h),
                     xytext=(0, 3), textcoords="offset points", ha="center", va="bottom",
                     fontsize=9, fontweight="bold", color="#065f46")

    ax1.set_title("Blind Evaluation: Pilot Scores across Evaluation Dimensions (N = 2)",
                  fontsize=13, fontweight="bold", pad=14)
    ax1.set_ylabel("Likert Score (1–5)", fontsize=11, fontweight="bold", labelpad=8)
    ax1.set_xlabel("Evaluation Criteria", fontsize=11, fontweight="bold", labelpad=8)
    ax1.set_xticks(x)
    ax1.set_xticklabels([k[1] for k in criteria_keys], fontsize=9.5, fontweight="semibold")
    ax1.set_ylim(0, 5.8)
    ax1.set_yticks(np.arange(1, 6, 1))

    ax1.grid(axis="y", linestyle="--", alpha=0.4, color="#9ca3af", zorder=0)
    ax1.set_axisbelow(True)
    ax1.legend(loc="upper right", frameon=True, framealpha=0.95, edgecolor="#d1d5db", fontsize=8.5)

    # กล่องข้อความแจ้งเตือนข้อจำกัดข้อมูลอย่างโปร่งใส (Academic Transparency Note)
    notice_text = (
        "Methodological Note (Pilot Data):\n"
        "• Data reflects N = 2 evaluations available in the repository (both evaluated 'Plan A' under SC-01).\n"
        "• Paired 'Plan B' evaluations are currently absent; A/B comparative win-rate is not computable."
    )
    ax1.text(0.02, 0.04, notice_text, transform=ax1.transAxes,
             fontsize=8, verticalalignment='bottom', bbox=dict(boxstyle='round,pad=0.5', facecolor='#f8fafc', edgecolor='#cbd5e1', alpha=0.9))

    ax1.spines["top"].set_visible(False)
    ax1.spines["right"].set_visible(False)

    fig1_sub = os.path.join(output_dir, "fig_4_8_1_blind_evaluation_scores.png")
    fig1_root = os.path.join(root_dir, "fig_4_8_1_blind_evaluation_scores.png")
    fig1.savefig(fig1_sub, dpi=300, bbox_inches="tight")
    fig1.savefig(fig1_root, dpi=300, bbox_inches="tight")
    plt.close(fig1)
    print(f"  [+] Graph 1 successfully created: {fig1_sub}")
    print(f"  [+] Graph 1 successfully created: {fig1_root}")

    # --------------------------------------------------------------------------
    # กราฟที่ 2: Plan Preference Distribution (ข้ามตามหลักวิชาการ)
    # --------------------------------------------------------------------------
    print("\n  [-] Graph 2 (fig_4_8_2_plan_preference.png): SKIPPED.")
    print("      Reason: Dataset lacks paired A/B decisions (only Plan A evaluated).")
    print("      Generating a win/loss chart would fabricate unverified scientific conclusions.")

    print("\n" + "=" * 80)
    print("AUDIT & VISUALIZATION COMPLETE")
    print(f"Figures & Reports written to:\n  - {output_dir}\n  - {root_dir}")
    print("=" * 80)

if __name__ == "__main__":
    main()
