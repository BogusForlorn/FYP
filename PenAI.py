#!/usr/bin/env python3
# PenAI.py
import subprocess
import json
import os
import sys
import re
import glob

MAX_SUMMARY_LEN = 300
VERBOSE = True

DEFAULT_TIMEOUT = 300
LONG_TIMEOUT = 3600
LONG_TIMEOUT_TOOLS = ['ffuf', 'sqlmap', 'gobuster']

def run_tool(command, capture=True, show_output=True):
    if command.startswith('$'):
        command = command[1:].strip()

    timeout = DEFAULT_TIMEOUT
    for tool in LONG_TIMEOUT_TOOLS:
        if tool in command:
            timeout = LONG_TIMEOUT
            break

    print(f"[+] Executing: {command}  (timeout={timeout}s)")
    try:
        res = subprocess.run(
            command,
            shell=True,
            capture_output=capture,
            text=True,
            timeout=timeout
        )
        if show_output or VERBOSE:
            if res.stdout:
                print(res.stdout)
            if res.stderr:
                print(res.stderr)
        if res.returncode != 0:
            print(f"[!] Warning: exit code {res.returncode}")
        return res.stdout.strip()
    except subprocess.TimeoutExpired:
        print(f"[!] Command timed out after {timeout}s: {command}")
        return ""
    except Exception as e:
        print(f"[!] Error running command: {e}")
        return ""

def strip_html_tags(text):
    return re.sub(r'<[^>]+>', '', text)

def summarize_page(html):
    low = html.lower()
    if 'phpinfo' in low or 'php version' in low:
        return "PHP info page detected (skipped)"
    if '<form' in low and 'login' in low:
        return "Possible login form"
    if '<form' in low:
        return "Generic form detected"
    if 'maintenance' in low:
        return "Maintenance page"
    plain = strip_html_tags(html).strip()
    first = ' '.join(plain.splitlines()[:3]).strip()
    summary = f"Content: {first}"
    return (summary[:MAX_SUMMARY_LEN] + '...') if len(summary) > MAX_SUMMARY_LEN else summary

def save_json(obj, path):
    try:
        with open(path, 'w') as f:
            json.dump(obj, f, indent=2)
    except Exception as e:
        print(f"[!] Failed saving {path}: {e}")

def load_json(path):
    if not os.path.exists(path):
        return {}
    try:
        with open(path) as f:
            return json.load(f)
    except Exception as e:
        print(f"[!] Failed loading {path}: {e}")
        return {}

def zap_ajax_spider(target):
    print("[+] Starting ZAP AJAX Spider...")
    zap_cmd = (
        f"curl -s "
        f"-H 'Accept: application/json' "
        f"-X POST 'http://localhost:8080/JSON/spider/action/scan/?url=http://{target}'"
    )
    out = run_tool(zap_cmd)
    try:
        js = json.loads(out)
        scan = js.get('scan', {})
        return scan.get('urls', [])
    except Exception:
        print("[!] ZAP returned non‑JSON or no URLs.")
        return []

def phase_0_recon(target, aggressive, zap_urls):
    recon = {"target": target, "dirs": [], "page_summaries": {}}
    if aggressive:
        cmd = (
            f"ffuf -u 'http://{target}/FUZZ' "
            "-w /usr/share/wordlists/dirb/common.txt "
            "-o ffuf_out.json -of json -t 50"
        )
        run_tool(cmd)
        if os.path.exists('ffuf_out.json'):
            try:
                data = json.load(open('ffuf_out.json'))
                recon['dirs'] = [
                    r['url'] for r in data.get('results', [])
                    if 200 <= r.get('status', 0) < 300
                ]
            except Exception as e:
                print(f"[!] Failed to parse ffuf output: {e}")

    recon['dirs'].extend(zap_urls)
    recon['dirs'] = list(set(recon['dirs'])) or [f"http://{target}/"]

    print("[+] Recon done; summarizing pages")
    for url in recon['dirs']:
        html = run_tool(f"curl -s '{url}'", show_output=False)
        safe = url.replace('/', '_').replace(':', '').replace('?', '_')
        if html:
            open(f"raw_{safe}.html", 'w').write(html)
        recon['page_summaries'][url] = summarize_page(html)

    save_json(recon, 'recon.json')
    return recon

def loop1_manual():
    print("[+] Loop 1: Manual injections")
    os.environ['PHASE'] = '1'
    os.environ.pop('AGGRESSIVE', None)
    run_tool("node chatgpt_wrapper.js recon.json manual.json")
    plan = load_json('manual.json')
    results = []
    for cmd in plan.get('commands', []):
        if cmd.startswith('print:'):
            print(cmd.split('print:',1)[1])
        else:
            out = run_tool(cmd)
            results.append({'cmd': cmd, 'output': out})
    save_json(results, 'manual_results.json')
    return results

def loop2_brute():
    print("[+] Loop 2: Aggressive brute")
    os.environ['PHASE'] = '2'
    os.environ['AGGRESSIVE'] = '1'
    run_tool("node chatgpt_wrapper.js recon.json bruteplan.json")
    plan = load_json('bruteplan.json')
    brute = {'commands': [], 'results': []}
    for cmd in plan.get('commands', []):
        if cmd.startswith('print:'):
            print(cmd.split('print:',1)[1])
        else:
            out = run_tool(cmd)
            brute['commands'].append(cmd)
            brute['results'].append(out)
    save_json(brute, 'brute_results.json')
    return brute

def loop3_report():
    print("[+] Loop 3: Final Report")
    manual = load_json('manual_results.json')
    brute = load_json('brute_results.json')
    combined = {'manual': manual, 'brute': brute}
    save_json(combined, 'combined_results.json')

    os.environ['PHASE'] = '3'
    run_tool("node chatgpt_wrapper.js combined_results.json final_report.json")

    final = load_json('final_report.json')
    report_text = final.get('report', 'No report generated.')

    print("\n=== Final Report ===")
    print(report_text)
    report_files = sorted(glob.glob("PenAI_PenTest_Report-*.txt"))
    next_num = 1
    if report_files:
        nums = [
            int(re.search(r"Report-(\d+)\.txt", f).group(1))
            for f in report_files if re.search(r"Report-(\d+)\.txt", f)
        ]
        if nums:
            next_num = max(nums) + 1
    filename = f"PenAI_PenTest_Report-{next_num:02}.txt"
    with open(filename, 'w') as f:
        f.write(report_text)
    print(f"[+] Report saved as: {filename}")
    return final

def main():
    if len(sys.argv) < 2:
        print("Usage: PenAI.py <target>")
        sys.exit(1)
    target = sys.argv[1].rstrip('/')
    aggressive = input("Enable aggressive mode (Loop 2)? (y/n): ").lower().startswith('y')
    use_zap = input("Use ZAP AJAX Spider? (y/n): ").lower().startswith('y')

    zap_urls = zap_ajax_spider(target) if use_zap else []
    phase_0_recon(target, aggressive, zap_urls)
    loop1_manual()
    if aggressive:
        loop2_brute()
    else:
        print("[+] Skipping Loop 2 (not aggressive).")
    loop3_report()

if __name__ == '__main__':
    main()
