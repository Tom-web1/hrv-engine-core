# plot/draw_quadrant.py
# ==========================================
# HRV 四象限圖（陰陽 × 虛實）+ Healthy Zone (lnTP μ±SD, Kuo 1999)
# 風格調整版：配合 PDF 報告視覺
# ==========================================

import os
import io
import math
import base64

import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties
import matplotlib.patches as patches


# ===== 年齡 × 性別 TP 常模 (ln 值, Kuo 1999) =====
# (age_max, mu_ln, sd_ln)
TP_BASE = {
    "男": [
        (29, 6.8, 0.5),
        (39, 6.5, 0.5),
        (49, 6.2, 0.6),
        (59, 5.8, 0.6),
        (69, 5.5, 0.7),
        (200, 5.2, 0.7),
    ],
    "女": [
        (29, 6.6, 0.5),
        (39, 6.4, 0.5),
        (49, 6.0, 0.5),
        (59, 5.6, 0.5),
        (69, 5.2, 0.5),
        (200, 4.9, 0.5),
    ],
}


# ------------------------------------------
# 字型設定：強制使用專案內 NotoSansTC-Regular.ttf
# ------------------------------------------
def _font_path() -> str:
    root_dir = os.path.dirname(os.path.dirname(__file__))  # 專案根目錄
    primary = os.path.join(root_dir, "fonts", "NotoSansTC-Regular.ttf")
    if os.path.exists(primary):
        return primary

    # fallback：系統字型
    candidates = [
        "/System/Library/Fonts/PingFang.ttc",      # macOS
        "C:/Windows/Fonts/msjh.ttc",               # Windows 微軟正黑體
    ]
    for c in candidates:
        if os.path.exists(c):
            return c

    raise FileNotFoundError(f"找不到可用的中文字型檔案（嘗試：{primary} 等）")


FONT_PATH = _font_path()
FONT_PROP = FontProperties(fname=FONT_PATH)

# 套用到整個 matplotlib
plt.rcParams["font.family"] = FONT_PROP.get_name()
plt.rcParams["font.sans-serif"] = [FONT_PROP.get_name()]
plt.rcParams["axes.unicode_minus"] = False


# ------------------------------------------
# 小工具
# ------------------------------------------
def _get_nested(d, *keys, default=None):
    cur = d
    for k in keys:
        if not isinstance(cur, dict):
            return default
        cur = cur.get(k)
        if cur is None:
            return default
    return cur


def _extract_x(report: dict) -> float:
    """抓 ln(LF/HF) 作為 X。"""
    features = report.get("features") or {}
    vector = report.get("vector") or {}

    x_keys = [
        ("features", "x"),
        ("features", "ln_lf_hf"),
        ("features", "ln_LF_HF"),
        ("features", "ln_ratio"),
        ("vector", "x"),
        ("vector", "ln_lf_hf"),
    ]

    x_val = None
    for scope, key in x_keys:
        if scope == "features":
            v = features.get(key)
        elif scope == "vector":
            v = vector.get(key)
        else:
            v = _get_nested(report, scope, key)
        if v is not None:
            x_val = v
            break

    if x_val is None:
        raise ValueError("無法從 report 取得 ln(LF/HF)")

    x = float(x_val)
    if math.isnan(x):
        raise ValueError("ln(LF/HF) 為 NaN")

    return x


def _extract_tp_ln(report: dict) -> float:
    """抓 ln(TP) 作為 Y。"""
    features = report.get("features") or {}
    vector = report.get("vector") or {}

    tp_ln_keys = [
        ("features", "tp_ln"),
        ("features", "ln_tp"),
        ("features", "TP_LN"),
        ("features", "tp_log"),
        ("vector", "tp_ln"),
    ]
    tp_ln = None
    for scope, key in tp_ln_keys:
        if scope == "features":
            v = features.get(key)
        elif scope == "vector":
            v = vector.get(key)
        else:
            v = _get_nested(report, scope, key)
        if v is not None:
            tp_ln = v
            break

    if tp_ln is None:
        raise ValueError("無法從 report 取得 ln(TP)")

    y = float(tp_ln)
    if math.isnan(y):
        raise ValueError("ln(TP) 為 NaN")

    return y


def _get_tp_norm(age, sex: str):
    """從 TP_BASE 取得對應 (mu_ln, sd_ln, age_band_max)。"""
    if age is None or sex is None:
        return None

    try:
        age_f = float(age)
    except Exception:
        return None

    sex = str(sex).strip()
    if sex not in TP_BASE:
        return None

    for age_max, mu, sd in TP_BASE[sex]:
        if age_f <= age_max:
            return mu, sd, age_max
    return None


# ------------------------------------------
# 主函式
# ------------------------------------------
def generate_quadrant_plot_base64(report: dict) -> str:
    """
    模式 A：Y 軸使用 ln(TP)，Healthy Zone 根據
    Kuo(1999) μ±SD 以橢圓呈現，風格對齊 PDF 報告。
    """
    x = _extract_x(report)
    y = _extract_tp_ln(report)

    meta = report.get("meta") or {}
    quadrant_info = report.get("quadrant") or {}

    name = meta.get("name") or ""
    age = meta.get("age")
    sex = meta.get("sex") or meta.get("gender") or ""
    quad_label = quadrant_info.get("label") or "未知"

    norm = _get_tp_norm(age, sex)
    if norm is None:
        raise ValueError("找不到對應的 Kuo(1999) TP 常模，請確認 sex 與 age。")

    mu_ln, sd_ln, age_band_max = norm
    tp_z = (y - mu_ln) / sd_ln  # 相對該年齡帶的 Z 分數

    # === 座標範圍 ===
    # 盡量涵蓋 μ±3SD 跟實際點位
    y_min = min(mu_ln - 3 * sd_ln, y - 1.0)
    y_max = max(mu_ln + 3 * sd_ln, y + 1.0)

    # padding
    y_margin = (y_max - y_min) * 0.1
    y_min -= y_margin
    y_max += y_margin

    # X 軸：-3 ~ 3，並包住點
    x_min = min(-3.0, x - 1.0)
    x_max = max(3.0, x + 1.0)

    fig, ax = plt.subplots(figsize=(5, 5), dpi=150)

    # --- 先畫四象限背景色塊（淡色） ---
    # 左下 (陰虛)
    ax.add_patch(
        patches.Rectangle(
            (x_min, y_min),
            width=0 - x_min,
            height=mu_ln - y_min,
            facecolor="#e4f5e9",   # 淡綠
            alpha=0.35,
            linewidth=0,
        )
    )
    # 右下 (陽虛)
    ax.add_patch(
        patches.Rectangle(
            (0, y_min),
            width=x_max - 0,
            height=mu_ln - y_min,
            facecolor="#f9f4e2",   # 淡米
            alpha=0.35,
            linewidth=0,
        )
    )
    # 左上 (陰實)
    ax.add_patch(
        patches.Rectangle(
            (x_min, mu_ln),
            width=0 - x_min,
            height=y_max - mu_ln,
            facecolor="#fbe4e8",   # 淡粉
            alpha=0.35,
            linewidth=0,
        )
    )
    # 右上 (陽實)
    ax.add_patch(
        patches.Rectangle(
            (0, mu_ln),
            width=x_max - 0,
            height=y_max - mu_ln,
            facecolor="#fff5d8",   # 淡黃
            alpha=0.35,
            linewidth=0,
        )
    )

    # === Healthy Zone 橢圓 (實心淡色) ===
    ellipse = patches.Ellipse(
        (0.0, mu_ln),
        width=2.0,               # x 方向 ±1
        height=2.0 * sd_ln,      # y 方向 ±1SD
        linewidth=1.5,
        edgecolor="#2f7ed8",
        facecolor="#d5e6ff",
        alpha=0.65,
        zorder=3,
    )
    ax.add_patch(ellipse)

    # === 中心線 (陰陽、虛實) ===
    ax.axvline(0, color="gray", linestyle="--", linewidth=1.2, zorder=2)
    ax.axhline(mu_ln, color="gray", linestyle="--", linewidth=1.2, zorder=2)

    # === 背景格線 ===
    ax.grid(True, linestyle=":", linewidth=0.6, alpha=0.6, zorder=1)

    # === 測量點（紅圈） ===
    ax.scatter(
        [x],
        [y],
        s=70,
        facecolors="#ff6666",
        edgecolors="white",
        linewidths=1.2,
        zorder=5,
    )

    # 測量點標示文字（改成「測量點」）
    ax.text(
        x + 0.05,
        y + 0.05,
        "測量點",
        ha="left",
        va="bottom",
        fontsize=9.5,
        fontproperties=FONT_PROP,
    )

    # === 四象限中文標籤 ===
    x_left = x_min + (x_max - x_min) * 0.18
    x_right = x_max - (x_max - x_min) * 0.18
    y_up = mu_ln + (y_max - mu_ln) * 0.28
    y_down = mu_ln - (mu_ln - y_min) * 0.28

    ax.text(
        x_left,
        y_up,
        "陰實型",
        fontsize=11,
        fontweight="bold",
        fontproperties=FONT_PROP,
    )
    ax.text(
        x_right,
        y_up,
        "陽實型",
        fontsize=11,
        fontweight="bold",
        ha="right",
        fontproperties=FONT_PROP,
    )
    ax.text(
        x_left,
        y_down,
        "陰虛型",
        fontsize=11,
        fontweight="bold",
        fontproperties=FONT_PROP,
    )
    ax.text(
        x_right,
        y_down,
        "陽虛型",
        fontsize=11,
        fontweight="bold",
        ha="right",
        fontproperties=FONT_PROP,
    )

    # === Kuo(1999) 說明文字 ===
    info_lines = [
        "TP ln μ±SD (Kuo 1999)",
        f"{sex}，年齡 ≦ {int(age_band_max)} 歲",
        f"μ = {mu_ln:.2f}，σ = {sd_ln:.2f}",
        f"ln(TP) = {y:.2f}，TP_Z = {tp_z:.2f}",
    ]
    ax.text(
        x_min + 0.1,
        y_max - 0.1,
        "\n".join(info_lines),
        ha="left",
        va="top",
        fontsize=8.5,
        fontproperties=FONT_PROP,
    )

    # === 軸範圍與標籤 ===
    ax.set_xlim(x_min, x_max)
    ax.set_ylim(y_min, y_max)

    ax.set_xlabel(
        "X：ln(LF/HF)（陰 ← → 陽）",
        fontsize=10,
        fontproperties=FONT_PROP,
    )
    ax.set_ylabel(
        "Y：ln(TP)（虛 ← → 實，相對年齡常模）",
        fontsize=10,
        fontproperties=FONT_PROP,
    )

    # === 標題 ===
    title = "HRV四象限圖"
    if name:
        if age is not None and sex:
            title = f"{name}（{sex}, {int(age)}歲） HRV四象限圖"
        elif sex:
            title = f"{name}（{sex}） HRV四象限圖"
        else:
            title = f"{name} HRV四象限圖"

    ax.set_title(
        title,
        fontsize=14,
        fontweight="bold",
        pad=12,
        fontproperties=FONT_PROP,
    )

    plt.tight_layout()

    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=150)
    plt.close(fig)
    buf.seek(0)
    return base64.b64encode(buf.read()).decode("utf-8")
