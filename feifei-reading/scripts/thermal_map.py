#!/usr/bin/env python3
"""飞飞共读 · 温度热力图：逐句上色，看见文字的冷与热。"""
import sys, os, argparse
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap

sys.path.insert(0, os.path.dirname(__file__))
from shared import setup_font, split_sentences, segment, score_temperature, physics_style, tmp_path


def thermal_map(text: str, output: str):
    setup_font()
    sentences = split_sentences(text)
    if not sentences:
        print("没有可分析的句子。")
        return

    # 逐句打分
    scores = []
    for s in sentences:
        words = segment(s)
        scores.append(score_temperature(words))

    # 截断过长的句子用于标签显示
    labels = [s[:20] + "…" if len(s) > 20 else s for s in sentences]
    n = len(sentences)

    # 冷蓝 → 白 → 暖红
    cmap = LinearSegmentedColormap.from_list(
        "thermal", ["#3b82f6", "#e0e0d8", "#ef4444"]
    )

    fig_h = max(2.5, n * 0.45 + 1)
    fig, ax = plt.subplots(figsize=(10, fig_h))
    physics_style(fig, ax)
    ax.grid(False)

    y_pos = np.arange(n)
    norm_scores = [(s + 1) / 2 for s in scores]  # map [-1,1] → [0,1]
    colors = [cmap(v) for v in norm_scores]

    bars = ax.barh(y_pos, [1] * n, color=colors, height=0.8, edgecolor="none")
    ax.set_yticks(y_pos)
    ax.set_yticklabels(labels, fontsize=8)
    ax.set_xlim(0, 1)
    ax.set_xticks([])
    ax.invert_yaxis()

    # 在条上标注温度值
    for i, (bar, sc) in enumerate(zip(bars, scores)):
        temp_label = f"{sc:+.2f}"
        color = "#1e3a5f" if sc < 0 else "#5f1e1e" if sc > 0 else "#555"
        ax.text(0.5, i, temp_label, ha="center", va="center", fontsize=9,
                fontweight="bold", color=color)

    ax.set_title("温度热力图  [冷] <-- --> [暖]", fontsize=13, pad=12)
    fig.tight_layout()
    fig.savefig(output, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"热力图已保存 → {output}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="文本温度热力图")
    parser.add_argument("--text", type=str, help="待分析文本")
    parser.add_argument("--file", type=str, help="从文件读取文本")
    parser.add_argument("--output", type=str, default=tmp_path("thermal"))
    args = parser.parse_args()

    if args.file:
        text = open(args.file, encoding="utf-8").read()
    elif args.text:
        text = args.text
    else:
        text = sys.stdin.read()

    thermal_map(text, args.output)
