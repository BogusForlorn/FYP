// chatgpt_wrapper.js
import fs from 'fs';
import OpenAI from 'openai';
import dotenv from 'dotenv';

dotenv.config();
const openai = new OpenAI({ apiKey: process.env.OPENAI_API_KEY });

function isValidJSON(str) {
  try {
    JSON.parse(str);
    return true;
  } catch {
    return false;
  }
}

async function main() {
  const [inputFile = 'recon.json', outputFile = 'report.json'] = process.argv.slice(2);
  const phase = process.env.PHASE || '1';
  const aggressive = process.env.AGGRESSIVE === '1';
  const data = JSON.parse(fs.readFileSync(inputFile, 'utf-8'));

  let prompt = '';
  if (phase === '1') {
    // Loop 1: manual injections only
    prompt = `
You are an AI pentesting assistant (Phase 1: Manual Injection).
Recon data:
${JSON.stringify(data, null, 2)}

Generate up to 5 manual injection payloads for common vulnerabilities (SQLi, XSS, parameter tampering) using simple curl or HTTP commands. Do NOT suggest automated tools like sqlmap or ffuf. Prefix each command with "$ ".
If you are suggesting curl to test XSS, don't use <script>alert(1)</script> as it will not prompt any response on curl. Instead, use -X Post -d "content=<script>alert(1)</script>"
Return valid JSON:
{
  "commands": ["$ command1", ...],
  "report": "One‑line summary of what these manual tests cover",
  "done": true
}
Only output this JSON.`;
  } else if (phase === '2') {
    // Loop 2: aggressive tools only
    prompt = `
You are an AI pentesting assistant (Phase 2: Aggressive Brute Forcing).
Recon data:
${JSON.stringify(data, null, 2)}

Generate up to 3 commands for aggressive brute‑forcing tools (e.g. sqlmap, ffuf) recommended for pentesting this target. Prefix each with "$ ". If you need a wordlist, use /usr/share/wordlists/rockyou.txt for passwords and /usr/share/dirb/wordlists/common.txt for directory enumeration.
Do not use burpsuite as an aggressive brute-forcing tool.
If an admin login page was found, attempt to use "admin" as the username.
Do not enumerate directories and use tools such as ffuf, gobuster, dirb, etc to enumerate directories. Ffuf may be used to fuzz parameters or objects if necessary.
Do not recommend the same tool with the same arguments or parameters twice. Provide only the necessary tools; if there are no other tools then you may stop at providing only 1 or 2 tools.
If you are suggesting to use a bruteforce tool to enumerate or fuzz a parameter or field such as hydra or ffuf, provide only one and do not suggest another tool. (e.g.: do not suggest both ffuf and hydra to fuzz user accounts as they provide the same function. For instance, if you have already suggested hydra, do not suggest ffuf). Ensure that there are variety within the tools suggested. If no other tools seem likely, then do not provide at all. Provide only one.
If there is a specific vulnerability indicated from loop 1 such as SQLi or XSS, you may use the respective tools to further test for the payload such as sqlmap.

Return valid JSON:
{
  "commands": ["$ command1", ...],
  "report": "One‑line summary of the tools used",
  "done": true
}
Only output this JSON.`;
  } else if (phase === '3') {
    // Loop 3: final report
    prompt = `
You are an AI pentesting assistant (Phase 3: Reporting).
Combined results:
${JSON.stringify(data, null, 2)}

Produce a concise, readable final report summarizing all findings.
Write your report of the test using the following format:

### Tools used
** provide the full command that was previously used including the arguments, options, and parameters.

### Summary of Findings
...

### Conclusion
...

### Recommendations
...

Return valid JSON:
{
  "report": "Your final report goes here",
  "done": true
}
Only output this JSON.`;
  } else {
    console.error('[!] Unknown PHASE:', phase);
    process.exit(1);
  }

  const res = await openai.chat.completions.create({
    model: 'gpt-4o-mini',
    messages: [{ role: 'user', content: prompt }]
  });
  const reply = res.choices[0].message.content.trim();

  if (isValidJSON(reply)) {
    fs.writeFileSync(outputFile, reply);
    console.log(`[+] Written to ${outputFile}`);
  } else {
    console.error('[!] LLM returned invalid JSON.');
    fs.writeFileSync(
      outputFile,
      JSON.stringify({ report: 'Error: invalid LLM output', done: true }, null, 2)
    );
  }
}

main();

