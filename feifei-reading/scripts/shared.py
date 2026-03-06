"""飞飞共读 · 触感透镜共享模块：字体、分句、词库。"""
import os
import re
import tempfile
import platform
import matplotlib
matplotlib.use("Agg")  # 非交互后端，避免 GUI segfault
import matplotlib.pyplot as plt


# ── 中文字体自适应 ──────────────────────────────────────────
def setup_font():
    system = platform.system()
    if system == "Darwin":
        fonts = ["PingFang SC", "Heiti SC", "STHeiti", "Arial Unicode MS"]
    elif system == "Windows":
        fonts = ["Microsoft YaHei", "SimHei", "SimSun"]
    else:
        fonts = ["WenQuanYi Micro Hei", "Noto Sans CJK SC", "DejaVu Sans"]
    matplotlib.rcParams["font.sans-serif"] = fonts + ["sans-serif"]
    matplotlib.rcParams["axes.unicode_minus"] = False


# ── 输出路径 ──────────────────────────────────────────────
FEIFEI_TMP = os.path.join(tempfile.gettempdir(), "feifei")
os.makedirs(FEIFEI_TMP, exist_ok=True)


def tmp_path(name: str, ext: str = ".png") -> str:
    """返回临时目录下的输出路径。"""
    return os.path.join(FEIFEI_TMP, f"{name}{ext}")


# ── 分句 ───────────────────────────────────────────────────
def split_sentences(text: str) -> list[str]:
    """按中英文句末标点切分，保留标点。"""
    parts = re.split(r"([。！？；\n!?;])", text)
    sentences = []
    buf = ""
    for p in parts:
        if re.fullmatch(r"[。！？；\n!?;]", p):
            buf += p
            if buf.strip():
                sentences.append(buf.strip())
            buf = ""
        else:
            if buf.strip():
                sentences.append(buf.strip())
            buf = p
    if buf.strip():
        sentences.append(buf.strip())
    return sentences


# ── 分词（jieba 可选，退化为字级） ─────────────────────────
def segment(text: str) -> list[str]:
    try:
        import jieba
        return list(jieba.cut(text))
    except ImportError:
        return list(text)


# ── 词库 ───────────────────────────────────────────────────
# 同时包含单字和常见复合词，匹配时用子串策略兜底
WARM = set(
    "爱 温暖 热情 欢乐 喜悦 幸福 甜蜜 拥抱 光明 希望 笑 美好 春天 阳光 "
    "火 燃烧 热 炽 激动 兴奋 快乐 温柔 亲密 心跳 红 金 灿烂 绽放 盛开 "
    "热烈 澎湃 沸腾 柔软 明亮 生机 蓬勃 欣喜 感动 真挚 "
    "温馨 暖意 热忱 热心 炽热 炙热 明媚 和煦 和暖 晴朗 "
    "美丽 佳处 好得多".split()
)
COLD = set(
    "冷 寒 冰 孤独 死 悲伤 阴暗 寂寞 凄凉 苍白 空虚 沉默 灰 黑暗 "
    "绝望 恐惧 麻木 僵 冻 霜 雪 冬 枯 萎 消逝 凋零 破碎 遗忘 荒凉 "
    "苍茫 颤抖 窒息 坍塌 废墟 阴冷 惨淡 暗淡 "
    "严寒 冷风 阴晦 悲凉 萧索 荒村 活气 深冬 苍黄 凄冷 "
    "寒冷 冰冷 凛冽 阴沉 惨白 凄惨 哀伤 忧伤 愁 悲 哀".split()
)
HEAVY = set(
    "命运 死亡 永恒 沉重 宿命 深渊 坟墓 牺牲 毁灭 罪 苦难 历史 真理 "
    "虚无 存在 灵魂 坠落 沉沦 压迫 枷锁 荒诞 挣扎 审判 赎罪 "
    "终结 根基 本源 天命 沧桑 故乡 二十年 记得 心情 改变".split()
)
LIGHT = set(
    "轻 飘 风 蝴蝶 泡泡 云 梦 羽毛 微风 呢喃 低语 细 薄 淡 浅 "
    "掠过 拂过 飞 舞 轻盈 涟漪 叹息 若有若无 恍惚 朦胧 仿佛 如此".split()
)
TURN = set(
    "但 但是 却 然而 可是 不过 偏偏 竟 竟然 反而 忽然 突然 谁知 "
    "没想到 其实 事实上 只是 尽管 虽然 虽 即使 殊不知 岂料".split()
)


def _match_lexicon(word: str, lexicon: set) -> bool:
    """词库匹配：精确匹配 → 词包含词库项 → 词库项包含词（单字）。"""
    if word in lexicon:
        return True
    # 复合词中含有词库单字（如 "严寒" 含 "寒"）
    if len(word) >= 2:
        for item in lexicon:
            if len(item) == 1 and item in word:
                return True
    # 词库复合词包含当前词（如词库 "严寒" 匹配分词 "严寒"）
    return False


# ── 打分函数 ───────────────────────────────────────────────
def score_temperature(words: list[str]) -> float:
    """温度得分 [-1, 1]，正=暖，负=冷。"""
    w = sum(1 for t in words if _match_lexicon(t, WARM))
    c = sum(1 for t in words if _match_lexicon(t, COLD))
    return (w - c) / max(w + c, 1)


def score_weight(sentence: str, words: list[str]) -> float:
    """重力得分 [0, 1]。"""
    length_s = min(len(sentence) / 60, 1.0)
    h = sum(1 for t in words if _match_lexicon(t, HEAVY))
    l = sum(1 for t in words if _match_lexicon(t, LIGHT))
    ratio = h / max(h + l, 1)
    punct = len(re.findall(r"[，。、；：！？…—,.;:!?]", sentence))
    density = min(punct / max(len(sentence), 1) * 8, 1.0)
    return 0.4 * length_s + 0.4 * ratio + 0.2 * density


def find_turns(words: list[str]) -> list[str]:
    """返回句中出现的转折词。"""
    return [w for w in words if w in TURN]


# ── 统一画布风格 ──────────────────────────────────────────
def physics_style(fig, ax):
    """物理笔记本风格：浅网格、干净边框。"""
    ax.set_facecolor("#fafaf5")
    fig.patch.set_facecolor("#fafaf5")
    ax.grid(True, linewidth=0.3, alpha=0.4, color="#aaa")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    for spine in ax.spines.values():
        spine.set_color("#888")
        spine.set_linewidth(0.6)
