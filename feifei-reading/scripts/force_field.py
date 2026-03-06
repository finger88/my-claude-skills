#!/usr/bin/env python3
"""飞飞共读 · 力场图：把文本中的关键意象画成引力与斥力的星图。"""
import sys, os, argparse, math
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

sys.path.insert(0, os.path.dirname(__file__))
from shared import (
    setup_font, split_sentences, segment,
    score_temperature, _match_lexicon, WARM, COLD, HEAVY, LIGHT, physics_style,
)


def extract_keywords(sentences: list[str], top_n: int = 12) -> list[dict]:
    """提取关键词并标注其属性（温度、重量、所在句位置）。"""
    try:
        import jieba.analyse
        full = "".join(sentences)
        kws = jieba.analyse.extract_tags(full, topK=top_n, withWeight=True)
    except ImportError:
        # 退化：按词频取高频词
        from collections import Counter
        all_words = []
        for s in sentences:
            all_words.extend(segment(s))
        all_words = [w for w in all_words if len(w) > 1]
        freq = Counter(all_words).most_common(top_n)
        kws = [(w, c / max(len(all_words), 1)) for w, c in freq]

    results = []
    for word, weight in kws:
        # 定位首次出现的句子位置
        pos = 0
        for i, s in enumerate(sentences):
            if word in s:
                pos = i
                break
        # 分类（使用子串匹配）
        is_warm = _match_lexicon(word, WARM)
        is_cold = _match_lexicon(word, COLD)
        is_heavy = _match_lexicon(word, HEAVY)
        is_light = _match_lexicon(word, LIGHT)
        temp = 1 if is_warm else (-1 if is_cold else 0)
        mass = 1 if is_heavy else (-1 if is_light else 0)
        results.append(dict(
            word=word, weight=weight, pos=pos,
            temp=temp, mass=mass,
        ))
    return results


def force_field(text: str, output: str):
    setup_font()
    sentences = split_sentences(text)
    if not sentences:
        print("没有可分析的句子。")
        return

    keywords = extract_keywords(sentences)
    if not keywords:
        print("未提取到关键词。")
        return

    n = len(keywords)
    fig, ax = plt.subplots(figsize=(9, 9))
    physics_style(fig, ax)
    ax.grid(False)

    # 布局：以文本位置为角度、权重为半径的极坐标 → 笛卡尔
    max_pos = max(k["pos"] for k in keywords) or 1
    coords = []
    for k in keywords:
        angle = (k["pos"] / max_pos) * 2 * math.pi * 0.85 + 0.3
        r = 0.3 + k["weight"] * 3
        r = min(r, 1.8)
        cx = r * math.cos(angle)
        cy = r * math.sin(angle)
        coords.append((cx, cy))

    # 画连线：同温度属性=引力（实线），异温度=斥力（虚线）
    for i in range(n):
        for j in range(i + 1, n):
            ki, kj = keywords[i], keywords[j]
            # 只在同句或相邻句出现过的词之间连线
            if abs(ki["pos"] - kj["pos"]) > 2:
                continue
            x0, y0 = coords[i]
            x1, y1 = coords[j]
            same_pole = (ki["temp"] == kj["temp"] and ki["temp"] != 0)
            diff_pole = (ki["temp"] * kj["temp"] < 0)
            if same_pole:
                ax.plot([x0, x1], [y0, y1], "-", color="#555", lw=0.6, alpha=0.5)
            elif diff_pole:
                ax.plot([x0, x1], [y0, y1], "--", color="#c44", lw=0.6, alpha=0.5)

    # 画节点
    for i, k in enumerate(keywords):
        cx, cy = coords[i]
        if k["temp"] > 0:
            color, edge = "#ef4444", "#b91c1c"
        elif k["temp"] < 0:
            color, edge = "#3b82f6", "#1d4ed8"
        else:
            color, edge = "#999", "#666"
        size = 200 + k["weight"] * 1500
        ax.scatter(cx, cy, s=size, c=color, edgecolors=edge,
                   linewidths=1.2, alpha=0.75, zorder=3)
        ax.text(cx, cy, k["word"], ha="center", va="center",
                fontsize=10, fontweight="bold", color="white", zorder=4)

    # 图例
    legend_items = [
        mpatches.Patch(color="#ef4444", label="暖词"),
        mpatches.Patch(color="#3b82f6", label="冷词"),
        mpatches.Patch(color="#999", label="中性词"),
    ]
    ax.legend(handles=legend_items, loc="upper right", fontsize=9,
              framealpha=0.8, edgecolor="#ccc")

    ax.set_xlim(-2.5, 2.5)
    ax.set_ylim(-2.5, 2.5)
    ax.set_aspect("equal")
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_title("文本力场图  —— 意象的引力与斥力", fontsize=13, pad=12)

    fig.tight_layout()
    fig.savefig(output, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"力场图已保存 → {output}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="文本力场图")
    parser.add_argument("--text", type=str, help="待分析文本")
    parser.add_argument("--file", type=str, help="从文件读取文本")
    parser.add_argument("--output", type=str, default=tmp_path("force_field"))
    args = parser.parse_args()

    if args.file:
        text = open(args.file, encoding="utf-8").read()
    elif args.text:
        text = args.text
    else:
        text = sys.stdin.read()

    force_field(text, args.output)
