import os
import sys
import pandas as pd
import numpy as np

sys.stdout.reconfigure(encoding='utf-8')

print("================================================================================")
print("COMPREHENSIVE AUDIT REPORT: QWEN MODEL IN PIXINERARY PROJECT")
print("================================================================================")

# 1. Config & Identity Check
print("\n[1] MODEL IDENTITY & ROUTING CHECK:")
print("  - Backend model string mappings in backend/clip_server.py:")
print("      'qwen-25-vl-72b' -> 'qwen/qwen2.5-vl-72b-instruct'")
print("      'qwen-38-flash'  -> 'qwen/qwen2.5-vl-72b-instruct'")
print("  - Frontend model string mappings in AIProviderContext.tsx:")
print("      'qwen-25-vl-72b': Label 'Qwen 2.5 VL 72B', description: 'qwen/qwen2.5-vl-72b-instruct'")
print("      'qwen-38-flash': Alias to 'qwen-25-vl-72b'")
print("  - Pricing rates: $0.80 / 1M prompt tokens, $1.00 / 1M completion tokens")

# 2. EXP 1
try:
    df1 = pd.read_csv('experiment/exp1_prompt_sensitivity.csv')
    q1 = df1[df1['Model'] == 'qwen-25-vl-72b']
    q1_corr = q1['Is Correct'].astype(str).str.lower().isin(['true', '1'])
    print("\n[2] EXP 1: PROMPT SENSITIVITY ANALYSIS (N = 200 runs):")
    print(f"  - Overall Accuracy: {q1_corr.mean()*100:.2f}% (Ranking: 6th of 6 models)")
    print("  - Accuracy by Prompt Variant:")
    for p, grp in q1.groupby('Prompt Variant ID'):
        p_name = grp['Prompt Variant Name'].iloc[0] if 'Prompt Variant Name' in grp.columns else ''
        acc = grp['Is Correct'].astype(str).str.lower().isin(['true', '1']).mean() * 100
        print(f"      {p} ({p_name}): {acc:.1f}% (N = {len(grp)})")
    print(f"  - Mean Latency: {q1['Time MS'].mean():.1f} ms")
    print(f"  - Mean Cost per Inference: ${q1['Cost USD'].mean():.6f}")
    print(f"  - Mean Throughput: {q1['Tokens Per Sec'].mean():.2f} TPS")
except Exception as e:
    print(f"  - EXP 1 Error: {e}")

# 3. EXP 2
try:
    df2 = pd.read_csv('experiment/exp2_model_benchmark.csv')
    q2 = df2[df2['Model'] == 'qwen-25-vl-72b']
    q2_corr = q2['Is Correct'].astype(str).str.lower().isin(['true', '1'])
    print("\n[3] EXP 2: BENCHMARK ACROSS 4 LANDMARK TIERS (N = 100 runs):")
    print(f"  - Overall Benchmark Accuracy: {q2_corr.mean()*100:.2f}%")
    print("  - Accuracy by Tier:")
    for t, grp in q2.groupby('Tier'):
        acc = grp['Is Correct'].astype(str).str.lower().isin(['true', '1']).mean() * 100
        print(f"      {t:<16}: {acc:.1f}% (N = {len(grp)})")
except Exception as e:
    print(f"  - EXP 2 Error: {e}")

# 4. EXP 3
try:
    df3 = pd.read_csv('experiment/exp3_pipeline_comparison.csv')
    q3 = df3[df3['Model'] == 'qwen-25-vl-72b']
    q3_corr = q3['Is Correct'].astype(str).str.lower().isin(['true', '1'])
    print("\n[4] EXP 3: PIPELINE COMPARISON (N = 24 runs):")
    for pipe, grp in q3.groupby('Pipeline'):
        acc = grp['Is Correct'].astype(str).str.lower().isin(['true', '1']).mean() * 100
        print(f"      Pipeline '{pipe}': {acc:.1f}% (N = {len(grp)})")
except Exception as e:
    print(f"  - EXP 3 Error: {e}")

# 5. EXP 4
try:
    df4 = pd.read_csv('experiment/exp4_robustness.csv')
    q4 = df4[df4['Model'] == 'qwen-25-vl-72b']
    print("\n[5] EXP 4: ENVIRONMENTAL ROBUSTNESS TEST (N = 75 runs):")
    print("  - Accuracy under Image Perturbations:")
    for cond, grp in q4.groupby('Condition Category'):
        acc = grp['Is Correct'].astype(str).str.lower().isin(['true', '1']).mean() * 100
        print(f"      {cond:<15}: {acc:.1f}% (N = {len(grp)})")
except Exception as e:
    print(f"  - EXP 4 Error: {e}")

# 6. EXP 5
try:
    df5 = pd.read_csv('experiment/exp5_consistency.csv')
    q5 = df5[df5['Model'] == 'qwen-25-vl-72b']
    print("\n[6] EXP 5: TEMPERATURE CONSISTENCY (N = 120 runs):")
    for temp, grp in q5.groupby('Temperature'):
        acc = grp['Is Correct'].astype(str).str.lower().isin(['true', '1']).mean() * 100
        print(f"      Temp {temp}: {acc:.1f}% (N = {len(grp)})")
    # Drop
    t01 = q5[q5['Temperature'] == 0.1]['Is Correct'].astype(str).str.lower().isin(['true', '1']).mean() * 100
    t07 = q5[q5['Temperature'] == 0.7]['Is Correct'].astype(str).str.lower().isin(['true', '1']).mean() * 100
    print(f"      Change from T0.1 to T0.7: {t07 - t01:+.1f} pp")
except Exception as e:
    print(f"  - EXP 5 Error: {e}")

# 7. EXP 6
try:
    df6 = pd.read_csv('experiment/exp6_plan_evaluation.csv')
    q6 = df6[df6['Model'].isin(['qwen-38-flash', 'qwen-25-vl-72b'])]
    print("\n[7] EXP 6: TRAVEL PLAN QUALITY BENCHMARK (N = 12 plans):")
    print(f"      Model Label in Exp 6: '{q6['Model Label'].iloc[0]}'")
    dim_cols = [
        ('Dim1_ConstraintSatisfaction', 'Constraint Compliance'),
        ('Dim2_ActivityRelevance', 'Activity Relevance'),
        ('Dim3_Spatiality', 'Spatial Feasibility'),
        ('Dim4_AccuracyValidity', 'Accuracy & Validity'),
        ('Dim5_OverallQuality', 'Overall Quality'),
        ('Total Score', 'Total Average Score')
    ]
    for col, name in dim_cols:
        print(f"      {name:<24}: {q6[col].mean():.2f} / 5.00")
    print(f"      Mean Generation Latency : {q6['Gen Latency MS'].mean()/1000.0:.1f} s ({q6['Gen Latency MS'].mean():,.0f} ms)")
except Exception as e:
    print(f"  - EXP 6 Error: {e}")

print("\n================================================================================")
print("AUDIT COMPLETE")
print("================================================================================")
