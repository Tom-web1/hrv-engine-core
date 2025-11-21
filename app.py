# app.py
# ================================
# HRV-TCM Engine Web Demo
# ================================

from __future__ import annotations

import base64
import io

from flask import (
    Flask,
    render_template,
    request,
    send_file,
    redirect,
    url_for,
)

from engine_core import run_engine_from_xml
from plot.draw_quadrant import generate_quadrant_plot_base64

try:
    from PIL import Image
except ImportError:
    Image = None


app = Flask(
    __name__,
    static_folder="static",
    template_folder="templates",
)


def run_engine(xml_text: str) -> dict:
    """封裝 engine_core.run_engine_from_xml，統一轉成 dict。"""
    result = run_engine_from_xml(xml_text)

    if isinstance(result, dict):
        return result
    if hasattr(result, "model_dump"):
        return result.model_dump()
    if hasattr(result, "dict"):
        return result.dict()
    raise TypeError("引擎回傳結果不是 dict，請檢查 engine_core.run_engine_from_xml。")


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "GET":
        return render_template("index.html", error=None, xml_text="")

    # 1) 讀取 XML（檔案優先，否則用 textarea）
    xml_file = request.files.get("xml_file")
    xml_text = (request.form.get("xml_text") or "").strip()

    if xml_file and xml_file.filename:
        try:
            xml_bytes = xml_file.read()
            xml_text = xml_bytes.decode("utf-8", errors="ignore")
        except Exception as e:
            return render_template("index.html", error=f"讀取上傳檔案失敗：{e}", xml_text="")

    if not xml_text:
        return render_template(
            "index.html",
            error="請上傳 XML 檔案或貼上一筆 <Patient ... /> 內容。",
            xml_text="",
        )

    # 2) 呼叫 HRV 引擎
    try:
        result = run_engine(xml_text)
    except Exception as e:
        return render_template(
            "index.html",
            error=f"HRV 引擎執行失敗：{e}",
            xml_text=xml_text,
        )

    # 3) 整理給前端用的 report 物件
    base_report = result.get("report_data") or {}

    vector = result.get("vector") or {}
    pattern = result.get("pattern") or {}

    report = dict(base_report)
    report["vector"] = vector
    report["pattern"] = pattern

    # 4) 象限圖 base64 —— 一律由 draw_quadrant 產生
    try:
        plot_base64 = generate_quadrant_plot_base64(report)
    except Exception as e:
        # 為了避免整頁炸掉，象限圖錯誤時先印 console、前端顯示文字
        print("Quadrant plot failed:", e)
        plot_base64 = ""

    return render_template(
        "report.html",
        report=report,          # report.meta / report.features / report.vector / report.pattern
        plot_base64=plot_base64,
        xml_text=xml_text,
    )


@app.post("/download_jpg")
def download_jpg():
    """下載象限圖 JPEG 檔。"""
    xml_text = (request.form.get("xml_text") or "").strip()
    if not xml_text:
        return redirect(url_for("index"))

    try:
        result = run_engine(xml_text)
    except Exception:
        return redirect(url_for("index"))

    base_report = result.get("report_data") or {}
    report = dict(base_report)

    # 這裡同樣直接呼叫繪圖函式，不再依賴 result 裡是否有 plot_base64
    try:
        plot_base64 = generate_quadrant_plot_base64(report)
    except Exception as e:
        print("Quadrant plot for JPG failed:", e)
        return redirect(url_for("index"))

    if not plot_base64:
        return redirect(url_for("index"))

    if Image is None:
        return "伺服器尚未安裝 Pillow，無法產生 JPG 檔案。", 500

    img_bytes = base64.b64decode(plot_base64)
    img = Image.open(io.BytesIO(img_bytes)).convert("RGB")

    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=90)
    buf.seek(0)

    name = str(report.get("meta", {}).get("name", "HRV"))
    date = str(report.get("meta", {}).get("test_date", "")).replace("/", "-")
    filename = f"HRV_{name}_{date}.jpg"

    return send_file(
        buf,
        mimetype="image/jpeg",
        as_attachment=True,
        download_name=filename,
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
