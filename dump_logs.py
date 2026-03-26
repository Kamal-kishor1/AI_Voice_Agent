import subprocess
try:
    logs = subprocess.check_output(['docker', 'logs', 'infra-api-1'], stderr=subprocess.STDOUT).decode('utf-8', errors='ignore')
    with open('debug_logs.txt', 'w', encoding='utf-8') as f:
        f.write(logs)
except Exception as e:
    with open('debug_logs.txt', 'w', encoding='utf-8') as f:
        f.write(str(e))
