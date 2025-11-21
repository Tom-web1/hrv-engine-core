# app_demo.py
# ==========================================================
# 簡易 Web Demo：
#   開啟 http://127.0.0.1:5000
#   貼上 <Patient .../> → 顯示文字報告 + JSON
# ==========================================================

from __future__ import annotations

import json
from flask import Flask, request, render_template_string

from engine_core import run_engine_from_xml

app = Flask(__name__)


PAGE_TEMPLATE = """
<!doctype html>
<html lang="zh-Hant">
<head>
  <meta charset="utf-8">
  <title>HRV Engine Demo</title>
  <style>
    body { font-family: -apple-system, BlinkMacSystemFont, "Noto Sans TC", "PingFang TC", sans-serif; margin: 20px; }
    textarea { width: 100%; height: 180px; font-family: monospace; }
    pre { background: #f5f5f5; padding: 12px; white-space: pre-wrap; word-wrap: break-word; }
    .container { max-width: 960px; margin: 0 auto; }
    .error { color: #c00; font-weight: bold; }
    h1 { margin-bottom: 8px; }
    h2 { margin-top: 24px; }
    button { padding: 8px 16px; font-size: 14px; }
  </style>
</head>
<body>
  <div class="container">
    <h1>HRV-TCM Engine Demo</h1>
    <p>請貼上單筆 <code>&lt;Patient ... /&gt;</code> XML 內容，送出後會由 Engine 產生文字報告與 JSON。</p>

    <form method="post">
      <textarea name="xml_text" placeholder="在此貼上 &lt;Patient ... /&gt; XML 內容">{{ xml_text }}</textarea>
      <br><br>
      <button type="submit">開始解析與判讀</button>
    </form>

    {% if error %}
      <p class="error">錯誤：{{ error }}</p>
    {% endif %}

    {% if text_report %}
      <h2>文字報告（Text Report）</h2>
      <pre>{{ text_report }}</pre>
    {% endif %}

    {% if json_output %}
      <h2>JSON 結構（Engine Output）</h2>
      <pre>{{ json_output }}</pre>
    {% endif %}
  </div>
</body>
</html>
"""


@app.route("/", methods=["GET", "POST"])
def index():
    xml_text = ""
    text_report = None
    json_output = None
    error = None

    if request.method == "POST":
        xml_text = (request.form.get("xml_text") or "").strip()
        if not xml_text:
            error = "請貼上一筆 <Patient .../> XML 內容。"
        else:
            try:
                result = run_engine_from_xml(xml_text)
                text_report = result.get("text_report", "")
                json_output = json.dumps(result, ensure_ascii=False, indent=2)
            except Exception as e:
                error = f"解析或運算失敗：{e}"

    return render_template_string(
        PAGE_TEMPLATE,
        xml_text=xml_text,
        text_report=text_report,
        json_output=json_output,
        error=error,
    )


if __name__ == "__main__":
    # 在 Codespace 或本機啟動
    app.run(host="0.0.0.0", port=5000, debug=True)
