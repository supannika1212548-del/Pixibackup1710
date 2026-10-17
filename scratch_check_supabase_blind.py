import requests
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')
url = 'https://txrurmkeabftgjhzcbty.supabase.co'
key = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InR4cnVybWtlYWJmdGdqaHpjYnR5Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODE0MjQ5ODQsImV4cCI6MjA5NzAwMDk4NH0.W4Ko43wTHsyfQ3ipsRk0uT7wETnQ66zZvQXzQZdqAXU'
headers = {'apikey': key, 'Authorization': f'Bearer {key}'}

try:
    r_eval = requests.get(f'{url}/rest/v1/blind_evaluations?select=*', headers=headers, timeout=10)
    evals = r_eval.json()
    print(f'=== Supabase blind_evaluations (Total: {len(evals)}) ===')
    for e in evals:
        print(f"ID: {e.get('id')}, Scenario: {e.get('scenario_id')}, Label: {e.get('blind_label')}, Model: {e.get('actual_model')}, Expert: {e.get('expert_name')}, Pick: {e.get('overall_pick')}, Scores: {e.get('scores')}")

    r_comp = requests.get(f'{url}/rest/v1/blind_comparisons?select=*', headers=headers, timeout=10)
    comps = r_comp.json()
    print(f'\n=== Supabase blind_comparisons (Total: {len(comps)}) ===')
    for c in comps:
        print(f"ID: {c.get('id')}, Scenario: {c.get('scenario_id')}, Expert: {c.get('expert_name')}, Rankings: {c.get('rankings')}, Best: {c.get('best_for_practical_use')}")
except Exception as ex:
    print('Error:', ex)
