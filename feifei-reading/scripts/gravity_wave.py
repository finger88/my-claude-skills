#!/usr/bin/env python3
"""飞飞共读 · 重力波形：画出文字的脉搏，看见哪里沉、哪里轻、哪里屏住了气。"""
import sys, os, argparse
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection

sys.path.insert(0, os.path.dirname(__file__))
from shared import setup_font, split_sentences, segment, score_weight, physics_style, tmp_path


def gravity_wave(text: str, output: str):
    setup_font()
    sentences = split_sentences(text)
    if not sentences:
        print("没有可分析的句子。")
        return

    weights = []
    for s in sentences:
        words = segment(s)
        weights.append(score_weight(s, words))

    x = np.arange(len(sentences))
    y = np.array(weights)

    # 平滑曲线（简单移动平均）
    if len(y) >= 3:
        y_smooth = np.convolve(y, [0.2, 0.6, 0.2], mode="same")
        y_smooth[0], y_smooth[-1] = y[0], y[-1]
    else:
        y_smooth = y

    fig, ax = plt.subplots(figsize=(12, 4))
    physics_style(fig, ax)

    # 用渐变色线段：轻=浅灰，重=深黑
    points = np.array([x, y_smooth]).T.reshape(-1, 1, 2)
    segments = np.concatenate([points[:-1], points[1:]], axis=1)
    lc = LineCollection(segments, linewidths=2.5)
    lc.set_array(y_smooth[:-1])
    lc.set_cmap("Greys")
    lc.set_clim(0, 1)
    ax.add_collection(lc)

    # 填充：重力越大区域越深
    ax.fill_between(x, y_smooth, alpha=0.12, color="#333")

    # 标注最重和最轻的句子
    i_max = int(np.argmax(y))
    i_min = int(np.argmin(y))
    max_label = sentences[i_max][:15] + "…" if len(sentences[i_max]) > 15 else sentences[i_max]
    min_label = sentences[i_min][:15] + "…" if len(sentences[i_min]) > 15 else sentences[i_min]

    ax.annotate(f"▼ 最沉  {max_label}", xy=(i_max, y_smooth[i_max]),
                xytext=(i_max, y_smooth[i_max] + 0.12),
                fontsize=8, ha="center", color="#222",
                arrowprops=dict(arrowstyle="->", color="#555", lw=0.8))
    ax.annotate(f"△ 最轻  {min_label}", xy=(i_min, y_smooth[i_min]),
                xytext=(i_min, max(y_smooth[i_min] - 0.15, -0.05)),
                fontsize=8, ha="center", color="#888",
                arrowprops=dict(arrowstyle="->", color="#aaa", lw=0.8))

    ax.set_xlim(-0.5, len(sentences) - 0.5)
    ax.set_ylim(-0.05, 1.1)
    ax.set_xlabel("句序", fontsize=10)
    ax.set_ylabel("重力", fontsize=10)
    ax.set_title("重力波形  —— 文字的脉搏", fontsize=13, pad=12)

    fig.tight_layout()
    fig.savefig(output, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"重力波形已保存 → {output}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="文本重力波形")
    parser.add_argument("--text", type=str, help="待分析文本")
    parser.add_argument("--file", type=str, help="从文件读取文本")
    parser.add_argument("--output", type=str, default=tmp_path("gravity"))
    args = parser.parse_args()

    if args.file:
        text = open(args.file, encoding="utf-8").read()
    elif args.text:
        text = args.text
    else:
        text = sys.stdin.read()

    gravity_wave(text, args.output)
