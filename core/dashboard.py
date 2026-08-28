"""
Renders reports/risk_report.json into a self-contained HTML dashboard.
No external CDN / JS framework required, so it works fully offline.
"""
import json
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPORT_JSON = os.path.join(BASE_DIR, "reports", "risk_report.json")
OUT_HTML = os.path.join(BASE_DIR, "reports", "dashboard.html")

LEVEL_COLOR = {
    "Critical": "#dc2626",
    "High": "#f97316",
    "Medium": "#eab308",
    "Low": "#22c55e",
}


def render(report):
    s = report["summary"]
    findings = report["findings"]

    level_rows = "".join(
        f'<div class="bar-row"><span class="bar-label">{lvl}</span>'
        f'<div class="bar-track"><div class="bar-fill" style="width:{(s["risk_level_breakdown"].get(lvl,0)/max(s["total_tools_discovered"],1))*100:.1f}%;background:{LEVEL_COLOR[lvl]}"></div></div>'
        f'<span class="bar-count">{s["risk_level_breakdown"].get(lvl,0)}</span></div>'
        for lvl in ["Critical", "High", "Medium", "Low"]
    )

    table_rows = ""
    for f in findings:
        color = LEVEL_COLOR[f["risk_level"]]
        source_tag = "Network" if f["source"] == "network_log" else "Extension"
        users = ", ".join(f["affected_users"])
        sanctioned = "Sanctioned" if f["sanctioned"] else "Unsanctioned"
        sanction_class = "ok" if f["sanctioned"] else "warn"
        table_rows += f"""
        <tr>
          <td><span class="pill" style="background:{color}22;color:{color};border:1px solid {color}55">{f['risk_level']}</span></td>
          <td class="score">{f['risk_score']}</td>
          <td>{f['service']}<div class="muted">{f['vendor']}</div></td>
          <td>{source_tag}</td>
          <td>{f['category'].replace('_',' ').title()}</td>
          <td><span class="pill {sanction_class}">{sanctioned}</span></td>
          <td class="muted">{users}</td>
        </tr>"""

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Shadow AI Sentinel — Risk Dashboard</title>
<style>
  :root {{
    --bg: #0b0f1a; --panel: #131a2b; --panel2: #0f1524; --border: #223051;
    --text: #e7ecf7; --muted: #8a96b3; --accent: #38bdf8;
  }}
  * {{ box-sizing: border-box; }}
  body {{
    margin: 0; padding: 32px; background: var(--bg); color: var(--text);
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
  }}
  h1 {{ font-size: 22px; margin: 0 0 4px; }}
  .subtitle {{ color: var(--muted); font-size: 13px; margin-bottom: 28px; }}
  .cards {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; margin-bottom: 28px; }}
  .card {{
    background: var(--panel); border: 1px solid var(--border); border-radius: 12px;
    padding: 18px 20px;
  }}
  .card .num {{ font-size: 28px; font-weight: 700; }}
  .card .lbl {{ font-size: 12px; color: var(--muted); margin-top: 4px; }}
  .panel {{
    background: var(--panel); border: 1px solid var(--border); border-radius: 12px;
    padding: 22px; margin-bottom: 24px;
  }}
  .panel h2 {{ font-size: 14px; margin: 0 0 16px; color: var(--muted); text-transform: uppercase; letter-spacing: .05em; }}
  .bar-row {{ display: flex; align-items: center; gap: 12px; margin-bottom: 10px; }}
  .bar-label {{ width: 64px; font-size: 13px; }}
  .bar-track {{ flex: 1; background: var(--panel2); border-radius: 6px; height: 14px; overflow: hidden; }}
  .bar-fill {{ height: 100%; border-radius: 6px; }}
  .bar-count {{ width: 24px; text-align: right; font-size: 13px; color: var(--muted); }}
  table {{ width: 100%; border-collapse: collapse; font-size: 13px; }}
  th {{ text-align: left; color: var(--muted); font-weight: 600; font-size: 11px; text-transform: uppercase;
        letter-spacing: .04em; padding: 8px 10px; border-bottom: 1px solid var(--border); }}
  td {{ padding: 10px; border-bottom: 1px solid var(--border); vertical-align: top; }}
  .muted {{ color: var(--muted); font-size: 12px; }}
  .score {{ font-weight: 700; font-variant-numeric: tabular-nums; }}
  .pill {{ padding: 2px 9px; border-radius: 999px; font-size: 11px; font-weight: 600; }}
  .pill.ok {{ background: #22c55e22; color: #22c55e; border: 1px solid #22c55e55; }}
  .pill.warn {{ background: #dc262622; color: #f87171; border: 1px solid #dc262655; }}
  footer {{ color: var(--muted); font-size: 11px; margin-top: 20px; }}
</style>
</head>
<body>
  <h1>🛰️ Shadow AI Sentinel — Discovery &amp; Risk Dashboard</h1>
  <div class="subtitle">Generated {report['generated_at']} · lightweight fingerprint-based discovery over network logs and browser extension inventories</div>

  <div class="cards">
    <div class="card"><div class="num">{s['total_tools_discovered']}</div><div class="lbl">AI tools discovered</div></div>
    <div class="card"><div class="num" style="color:#f87171">{s['unsanctioned_tools_discovered']}</div><div class="lbl">Unsanctioned tools</div></div>
    <div class="card"><div class="num">{s['distinct_users_involved']}</div><div class="lbl">Users involved</div></div>
    <div class="card"><div class="num" style="color:#dc2626">{s['risk_level_breakdown'].get('Critical',0)+s['risk_level_breakdown'].get('High',0)}</div><div class="lbl">High + Critical findings</div></div>
  </div>

  <div class="panel">
    <h2>Risk level distribution</h2>
    {level_rows}
  </div>

  <div class="panel">
    <h2>Discovered tools — ranked by risk</h2>
    <table>
      <thead><tr><th>Level</th><th>Score</th><th>Tool</th><th>Source</th><th>Category</th><th>Status</th><th>Users</th></tr></thead>
      <tbody>{table_rows}
      </tbody>
    </table>
  </div>

  <footer>Shadow AI Sentinel prototype · fingerprint DB v1 · scores are heuristic (0-100), not a certified security assessment.</footer>
</body>
</html>"""
    with open(OUT_HTML, "w") as f:
        f.write(html)
    return OUT_HTML


if __name__ == "__main__":
    with open(REPORT_JSON) as f:
        report = json.load(f)
    path = render(report)
    print(f"Dashboard written to: {path}")
