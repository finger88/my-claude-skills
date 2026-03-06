#!/usr/bin/env python3
"""飞飞共读 · 扭矩标注：找到叙事被扭转的地方，画出隐形的箭头。"""
import sys, os, argparse
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as FancyArrowPatch

sys.path.insert(0, os.path.dirname(__file__))
from shared import (
    setup_font, split_sentences, segment,
    score_temperature, find_turns, physics_style,
)


def torque_annotate(text: str, output: str):
    setup_font()
    sentences = split_sentences(text)
    if not sentences:
        print("没有可分析的句子。")
        return

    # 逐句分析：温度 + 转折词
    data = []
    for s in sentences:
        words = segment(s)
        temp = score_temperature(words)
        turns = find_turns(words)
        data.append(dict(sentence=s, temp=temp, turns=turns, words=words))

    # 计算相邻句之间的扭矩（温度差 × 是否有转折词）
    torques = []
    for i in range(1, len(data)):
        delta_temp = data[i]["temp"] - data[i - 1]["temp"]
        has_turn = len(data[i]["turns"]) > 0
        torque = abs(delta_temp) * (2.0 if has_turn else 0.5)
        torques.append(dict(
            index=i, torque=torque, delta=delta_temp,
            turn_words=data[i]["turns"],
        ))

    # ── 绘图 ──
    n = len(sentences)
    fig_h = max(4, n * 0.6 + 2)
    fig, (ax_text, ax_torque) = plt.subplots(
        1, 2, figsize=(14, fig_h),
        gridspec_kw={"width_ratios": [3, 1]}, sharey=True,
    )
    physics_style(fig, ax_text)
    physics_style(fig, ax_torque)

    y_pos = np.arange(n)

    # 左栏：原文，背景色按温度
    for i, d in enumerate(data):
        # 背景色：冷蓝 / 暖红 / 中性灰
        if d["temp"] > 0.1:
            bg = "#fde8e8"
        elif d["temp"] < -0.1:
            bg = "#dbeafe"
        else:
            bg = "#f5f5f0"
        ax_text.barh(i, 1, color=bg, height=0.9, edgecolor="none")

        label = d["sentence"][:35] + "…" if len(d["sentence"]) > 35 else d["sentence"]
        # 高亮转折词
        ax_text.text(0.02, i, label, ha="left", va="center", fontsize=8.5,
                     color="#333", clip_on=True)

        # 转折词标记
        if d["turns"]:
            tag = " ".join(d["turns"])
            ax_text.text(0.98, i, f">> {tag}", ha="right", va="center",
                         fontsize=7.5, color="#b91c1c", fontstyle="italic")

    ax_text.set_xlim(0, 1)
    ax_text.set_xticks([])
    ax_text.set_yticks(y_pos)
    ax_text.set_yticklabels([f"{i+1}" for i in range(n)], fontsize=7, color="#999")
    ax_text.invert_yaxis()
    ax_text.set_title("原文（背景 = 温度）", fontsize=11, pad=10)

    # 右栏：扭矩柱状图
    torque_vals = [0] + [t["torque"] for t in torques]  # 第一句无扭矩
    colors = []
    for i, tv in enumerate(torque_vals):
        if i == 0:
            colors.append("#ddd")
        elif torques[i - 1]["delta"] > 0:
            colors.append("#ef4444")  # 升温
        elif torques[i - 1]["delta"] < 0:
            colors.append("#3b82f6")  # 降温
        else:
            colors.append("#999")

    ax_torque.barh(y_pos, torque_vals, color=colors, height=0.6, edgecolor="none")

    # 标注高扭矩点
    if torques:
        threshold = np.percentile([t["torque"] for t in torques], 70)
        for t in torques:
            if t["torque"] >= threshold and t["torque"] > 0.1:
                turn_str = ",".join(t["turn_words"]) if t["turn_words"] else "Δ"
                ax_torque.text(
                    t["torque"] + 0.02, t["index"], f"← {turn_str}",
                    va="center", fontsize=7.5, color="#b91c1c", fontweight="bold",
                )

    ax_torque.set_xlabel("扭矩", fontsize=10)
    ax_torque.set_title("扭矩强度", fontsize=11, pad=10)
    ax_torque.invert_yaxis()

    fig.suptitle("扭矩标注  —— 叙事在哪里被扭了一下", fontsize=13, y=1.01)
    fig.tight_layout()
    fig.savefig(output, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"扭矩标注图已保存 → {output}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="文本扭矩标注")
    parser.add_argument("--text", type=str, help="待分析文本")
    parser.add_argument("--file", type=str, help="从文件读取文本")
    parser.add_argument("--output", type=str, default=tmp_path("torque"))
    args = parser.parse_args()

    if args.file:
        text = open(args.file, encoding="utf-8").read()
    elif args.text:
        text = args.text
    else:
        text = sys.stdin.read()

    torque_annotate(text, args.output)
