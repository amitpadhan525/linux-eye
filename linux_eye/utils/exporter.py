import os
import csv
import json
from datetime import datetime

def export_logs_to_csv(input_log_path, output_csv_path):
    """
    Export linux-eye JSONL log entries into a structured CSV file.
    """
    if not os.path.exists(input_log_path):
        return 0

    fieldnames = ['timestamp', 'severity', 'source', 'message', 'details']
    count = 0

    with open(input_log_path, 'r', encoding='utf-8') as infile, \
         open(output_csv_path, 'w', newline='', encoding='utf-8') as outfile:
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()

        for line in infile:
            line = line.strip()
            if not line:
                continue
            try:
                data = json.loads(line)
                details_str = json.dumps(data.get('details')) if data.get('details') else ''
                writer.writerow({
                    'timestamp': data.get('timestamp', ''),
                    'severity': data.get('severity', ''),
                    'source': data.get('source', ''),
                    'message': data.get('message', ''),
                    'details': details_str
                })
                count += 1
            except json.JSONDecodeError:
                continue

    return count

def generate_log_summary(input_log_path):
    """
    Generate an analytical summary dictionary from the security event logs.
    """
    summary = {
        'total_events': 0,
        'by_severity': {'INFO': 0, 'WARNING': 0, 'CRITICAL': 0},
        'by_source': {},
        'generated_at': datetime.now().isoformat()
    }

    if not os.path.exists(input_log_path):
        return summary

    with open(input_log_path, 'r', encoding='utf-8') as infile:
        for line in infile:
            line = line.strip()
            if not line:
                continue
            try:
                data = json.loads(line)
                summary['total_events'] += 1
                sev = data.get('severity', 'INFO')
                summary['by_severity'][sev] = summary['by_severity'].get(sev, 0) + 1

                source = data.get('source', 'unknown')
                summary['by_source'][source] = summary['by_source'].get(source, 0) + 1
            except json.JSONDecodeError:
                continue

    return summary
