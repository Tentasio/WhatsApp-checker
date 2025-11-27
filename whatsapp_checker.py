import pandas as pd
import requests
import os
import sys

# --- Function to check WhatsApp ---
def check_whatsapp(number):
    url = f"https://wa.me/{number}"
    try:
        r = requests.get(url, timeout=10)
        text = r.text.lower()
        if "continue to chat" in text:
            return "Registered"
        elif "phone number shared via url is invalid" in text:
            return "Not Registered"
        else:
            return "Unknown"
    except requests.RequestException:
        return "Error"

# --- Load CSV from repo ---
csv_file = os.getenv("INPUT_CSV_FILE", "numbers.csv")
csv_numbers = []
if os.path.exists(csv_file):
    try:
        df_csv = pd.read_csv(csv_file)
        if "number" in df_csv.columns:
            csv_numbers = [str(n) for n in df_csv["number"] if str(n).strip()]
        else:
            print(f"[!] CSV must have a column named 'number'", file=sys.stderr)
    except Exception as e:
        print(f"[!] Error reading CSV: {e}", file=sys.stderr)
else:
    print(f"[!] CSV file '{csv_file}' not found. Using only manual input.")

# --- Manual input via workflow input ---
manual_numbers_str = os.getenv("INPUT_MANUAL_NUMBERS", "")
manual_numbers = [n.strip() for n in manual_numbers_str.split(",") if n.strip()]

# Combine numbers
all_numbers = list(set(manual_numbers + csv_numbers))
if not all_numbers:
    print("[!] No numbers provided. Exiting.")
    sys.exit(0)

# --- Check numbers ---
results = []
for num in all_numbers:
    status = check_whatsapp(num)
    print(f"{num}: {status}")
    results.append({"number": num, "status": status})

# --- Save results ---
output_file = "results.csv"
pd.DataFrame(results).to_csv(output_file, index=False)
print(f"\n✅ Results saved to {output_file}")
