#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
中学作文人物素材库 HTML 生成器。

特性：
- 75 位人物素材 + 42 道真题整合为单页 HTML
- 人物按 中/外 → 时代 → 生年 排序
- 侧边栏目录 + 标签索引，自动高亮当前章节
- 底部悬浮工具栏：字号 / 行距 / 字体 / 主题 实时调节
- 虚线边框 + 拖拽调节内容区宽度
- 阅读位置记忆
- 响应式设计，支持移动端
"""

import os
import re
import markdown
from html import escape
from datetime import datetime

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
FIGURES_DIR = os.path.join(PROJECT_DIR, "chinese-essay-figures", "figures")
EXAMPLES_DIR = os.path.join(PROJECT_DIR, "chinese-essay-figures", "examples")
OUTPUT_FILE = os.path.join(PROJECT_DIR, "中学作文人物素材库.html")
BOOK_TITLE = "中学作文人物素材库"

# ============================================================
# 人物元数据：姓名、显示日期、生年（负数=公元前）、标签
# 生年用于排序，约数取中值
# ============================================================

FIGURE_META = {
    # ── 中国 · 春秋战国 ──
    "伯牙与钟子期（春秋时期）":    ("伯牙与钟子期", "春秋时期",   -600, ["友谊", "孤独", "合作"]),
    "陈不占（春秋时期）":          ("陈不占",       "春秋时期",   -550, ["勇气", "责任感", "智慧"]),
    "齐国太史兄弟（春秋时期）":    ("齐国太史兄弟", "春秋时期",   -548, ["勇气", "气节", "责任感"]),

    "墨子（约前468-前376年）":     ("墨子",         "约前468-前376年", -468, ["兼爱", "创新", "实践"]),

    # ── 中国 · 两汉 ──
    "司马迁（前145年-前86年）":    ("司马迁",       "前145年-前86年",  -145, ["坚持", "突破", "传承", "勇气"]),
    "班超（32-102年）":            ("班超",         "32-102年",         32, ["开拓", "勇气", "投笔从戎"]),

    # ── 中国 · 魏晋南北朝 ──
    "羊祜（221-278年）":           ("羊祜",         "221-278年",       221, ["胸怀", "气度"]),
    "祖逖（266-321年）":           ("祖逖",         "266-321年",       266, ["勤奋", "坚持", "报国"]),
    "庾亮（289-340年）":           ("庾亮",         "289-340年",       289, ["风度", "镇定"]),
    "顾荣（西晋时期）":            ("顾荣",         "西晋时期",        280, ["感恩", "平凡", "智慧"]),
    "陶渊明（约365-427）":         ("陶渊明",       "约365-427年",     365, ["选择", "自由", "归隐"]),
    "郦道元（约472-527年）":       ("郦道元",       "约472-527年",     472, ["探索", "实践", "严谨"]),

    # ── 中国 · 唐宋 ──
    "玄奘（602-664年）":           ("玄奘",         "602-664年",       602, ["坚持", "探索", "信仰"]),
    "鉴真（688-763年）":           ("鉴真",         "688-763年",       688, ["坚持", "信念", "奉献"]),
    "颜真卿（709-784年）":         ("颜真卿",       "709-784年",       709, ["气节", "书法", "忠诚"]),
    "韩愈（768-824年）":           ("韩愈",         "768-824年",       768, ["勇气", "直言", "师道"]),
    "柳宗元（773-819年）":         ("柳宗元",       "773-819年",       773, ["孤独", "坚守", "山水"]),
    "李贺（790-816年）":           ("李贺",         "790-816年",       790, ["才华", "苦吟", "独特"]),
    "范仲淹（989-1052年）":        ("范仲淹",       "989-1052年",      989, ["坚守", "责任感", "家国"]),
    "狄青（1008-1057年）":         ("狄青",         "1008-1057年",    1008, ["奋斗", "突破", "出身"]),
    "张载（1020-1077年）":         ("张载",         "1020-1077年",    1020, ["担当", "理想", "哲学"]),
    "沈括（1031-1095年）":         ("沈括",         "1031-1095年",    1031, ["博学", "实践", "科学"]),
    "李清照（1084-约1155年）":     ("李清照",       "1084-约1155年",  1084, ["坚守", "孤独", "家国"]),
    "陆游（1125-1210年）":         ("陆游",         "1125-1210年",    1125, ["爱国", "坚持", "悲愤"]),
    "辛弃疾（1140-1207）":         ("辛弃疾",       "1140-1207年",    1140, ["爱国", "豪放", "壮志未酬"]),
    "黄道婆（约1245-1330年）":     ("黄道婆",       "约1245-1330年",  1245, ["创新", "奉献", "平凡", "传承"]),
    "文天祥（1236-1283）":         ("文天祥",       "1236-1283年",    1236, ["气节", "家国", "不屈"]),

    # ── 中国 · 元明 ──
    "于谦（1398-1457年）":         ("于谦",         "1398-1457年",    1398, ["忠诚", "担当", "清白"]),
    "王阳明（1472-1529）":         ("王阳明",       "1472-1529年",    1472, ["坚持", "突破", "创新", "智慧"]),
    "杨慎（1488-1559年）":         ("杨慎",         "1488-1559年",    1488, ["豁达", "智慧", "逆境"]),
    "归有光（1507-1571年）":       ("归有光",       "1507-1571年",    1507, ["深情", "平淡", "细节"]),
    "海瑞（1514-1587年）":         ("海瑞",         "1514-1587年",    1514, ["清廉", "刚直", "为民"]),
    "李时珍（1518-1593年）":       ("李时珍",       "1518-1593年",    1518, ["实践", "坚持", "创新"]),
    "徐渭（1521-1593年）":         ("徐渭",         "1521-1593年",    1521, ["才华", "孤独", "疯癫"]),
    "戚继光（1528-1588年）":       ("戚继光",       "1528-1588年",    1528, ["创新", "责任", "抗倭"]),
    "徐霞客（1587-1641）":         ("徐霞客",       "1587-1641年",    1587, ["坚持", "创新", "选择", "孤独"]),
    "谈迁（1594-1657）":           ("谈迁",         "1594-1657年",    1594, ["坚持", "韧性", "重来"]),
    "张岱（1597-1680）":           ("张岱",         "1597-1680年",    1597, ["回忆", "沧桑", "文化坚守"]),
    "顾炎武（1613-1682年）":       ("顾炎武",       "1613-1682年",    1613, ["责任", "经世致用"]),
    "李定国（1621-1662年）":       ("李定国",       "1621-1662年",    1621, ["忠诚", "悲壮", "气节"]),

    # ── 中国 · 清至近现代 ──
    "蒲松龄（1640-1715年）":       ("蒲松龄",       "1640-1715年",    1640, ["坚持", "孤独", "寄托"]),
    "郑板桥（1693-1766年）":       ("郑板桥",       "1693-1766年",    1693, ["清高", "为民", "艺术"]),
    "袁枚（1716-1798年）":         ("袁枚",         "1716-1798年",    1716, ["随性", "真性情", "美食"]),
    "林则徐（1785-1850年）":       ("林则徐",       "1785-1850年",    1785, ["担当", "爱国", "开眼看世界"]),
    "左宗棠（1812-1885年）":       ("左宗棠",       "1812-1885年",    1812, ["担当", "实干", "收复新疆"]),
    "谭嗣同（1865-1898）":         ("谭嗣同",       "1865-1898年",    1865, ["英雄", "责任感", "传承", "悲壮"]),
    "鲁迅（1881-1936年）":         ("鲁迅",         "1881-1936年",    1881, ["悲悯", "清醒", "责任"]),
    "史铁生（1951-2010年）":       ("史铁生",       "1951-2010年",    1951, ["突破", "坚持", "智慧", "孤独"]),

    # ── 外国 · 古代至文艺复兴 ──
    "马可·奥勒留（121-180年）":    ("马可·奥勒留",     "121-180年",    121,  ["智慧", "自省", "定力"]),
    "达·芬奇（1452-1519年）":      ("达·芬奇",         "1452-1519年",  1452, ["创新", "探索", "智慧"]),
    "维萨里（1514-1564年）":       ("维萨里",          "1514-1564年",  1514, ["创新", "勇气", "突破"]),
    "蒙田（1533-1592年）":         ("蒙田",            "1533-1592年",  1533, ["自省", "诚实", "智慧"]),
    "塞万提斯（1547-1616年）":     ("塞万提斯",        "1547-1616年",  1547, ["失败", "坚持", "孤独", "智慧"]),
    "伽利略（1564-1642年）":       ("伽利略",          "1564-1642年",  1564, ["真理", "坚持", "勇气"]),

    # ── 外国 · 近现代 ──
    "巴赫（1685-1750年）":         ("巴赫",            "1685-1750年",  1685, ["专注", "极致", "信仰"]),
    "南丁格尔（1820-1910年）":     ("南丁格尔",        "1820-1910年",  1820, ["奉献", "创新", "仁爱"]),
    "陀思妥耶夫斯基（1821-1881年）": ("陀思妥耶夫斯基", "1821-1881年",  1821, ["突破", "孤独", "智慧"]),
    "尼古拉·特斯拉（1856-1943年）": ("尼古拉·特斯拉",  "1856-1943年",  1856, ["创新", "孤独", "奉献"]),
    "契诃夫（1860-1904年）":       ("契诃夫",          "1860-1904年",  1860, ["悲悯", "克制", "日常中的深刻"]),
    "泰戈尔（1861-1941年）":       ("泰戈尔",          "1861-1941年",  1861, ["诗意", "哲思", "文化桥梁"]),
    "阿蒙森（1872-1928年）":       ("阿蒙森",          "1872-1928年",  1872, ["探索", "智慧", "坚持", "合作"]),
    "卡夫卡（1883-1924年）":       ("卡夫卡",          "1883-1924年",  1883, ["孤独", "坚持", "突破"]),
    "维克多·弗兰克尔（1905-1997年）": ("维克多·弗兰克尔", "1905-1997年", 1905, ["突破", "坚持", "智慧", "选择"]),
    "罗莎琳德·富兰克林（1920-1958年）": ("罗莎琳德·富兰克林", "1920-1958年", 1920, ["创新", "孤独", "气节"]),
}


def get_era(name, birth_year):
    """根据生年判断时代。"""
    # 外国人物识别
    foreign_names = {
        "马可·奥勒留", "达·芬奇", "蒙田", "维萨里", "塞万提斯", "伽利略",
        "巴赫", "南丁格尔", "陀思妥耶夫斯基", "阿蒙森", "泰戈尔", "契诃夫",
        "尼古拉·特斯拉", "卡夫卡", "维克多·弗兰克尔", "罗莎琳德·富兰克林",
    }

    if name in foreign_names:
        if birth_year <= 1600:
            return ("外国", "古代至文艺复兴")
        else:
            return ("外国", "近现代")
    else:
        if birth_year < -221:
            return ("中国", "春秋战国")
        elif birth_year < 220:
            return ("中国", "两汉")
        elif birth_year < 589:
            return ("中国", "魏晋南北朝")
        elif birth_year < 1279:
            return ("中国", "唐宋")
        elif birth_year < 1644:
            return ("中国", "元明")
        else:
            return ("中国", "清至近现代")


# ============================================================
# 排序键：朝代顺序
# ============================================================

ERA_ORDER_CN = {"春秋战国": 0, "两汉": 1, "魏晋南北朝": 2, "唐宋": 3, "元明": 4, "清至近现代": 5}
ERA_ORDER_FN = {"古代至文艺复兴": 0, "近现代": 1}
REGION_ORDER = {"中国": 0, "外国": 1}


def sort_key_figure(item):
    """排序键：(region_order, era_order, birth_year)"""
    region, era, birth_year, _, _ = item
    return (REGION_ORDER[region], ERA_ORDER_CN.get(era, ERA_ORDER_FN.get(era, 99)), birth_year)


# ============================================================
# 各人物热门指数解析
# ============================================================

def extract_popularity(md_text):
    """从 md 中提取热门指数完整文本（含括号评价）。"""
    m = re.search(r'###\s+热门指数[：:]\s*(.+)', md_text)
    if m:
        return m.group(1).strip()
    return ""


def strip_popularity_section(md_text):
    """从 md 中移除 ### 热门指数 行。"""
    return re.sub(r'\n*###\s+热门指数[：:].*\n?', '\n', md_text)


def extract_tags(md_text):
    """从 md 中提取适配标签列表。"""
    m = re.search(r'适配标签[：:]\s*(.+)', md_text)
    if m:
        tags_str = m.group(1).strip()
        # 清理加粗标记和多余空白
        tags_str = re.sub(r'\*+', '', tags_str)
        tags = [t.strip() for t in re.split(r'[、，,]', tags_str) if t.strip()]
        return tags
    return []


# ============================================================
# Markdown 转 HTML（简化版，不涉及公式保护）
# ============================================================

def process_markdown(md_text, chapter_idx):
    """将 markdown 转换为 HTML，为标题添加锚点 id。"""
    lines = md_text.split('\n')
    processed_lines = []
    in_code_block = False
    h_counter = 0

    for line in lines:
        stripped = line.strip()
        if stripped.startswith('```'):
            in_code_block = not in_code_block
            processed_lines.append(line)
            continue

        if not in_code_block:
            m = re.match(r'^(#{1,3})\s+(.+)', line)
            if m:
                level = len(m.group(1))
                title = m.group(2).strip()
                anchor_id = f"ch{chapter_idx}-h{h_counter}"
                h_counter += 1
                tag = f'h{level}'
                processed_lines.append(f'<{tag} id="{anchor_id}">{escape(title)}</{tag}>')
                continue

        processed_lines.append(line)

    md_text_processed = '\n'.join(processed_lines)

    html = markdown.markdown(
        md_text_processed,
        extensions=['tables', 'fenced_code', 'sane_lists'],
    )
    return html


# ============================================================
# 解析人物文件
# ============================================================

def parse_figure(filepath):
    """解析一个人物 .md 文件，返回 (name, display_dates, tags, popularity, html)。"""
    with open(filepath, 'r', encoding='utf-8-sig') as f:
        md_text = f.read()

    tags = extract_tags(md_text)
    popularity = extract_popularity(md_text)

    return tags, popularity, md_text


# ============================================================
# 解析真题文件
# ============================================================

def parse_exam(filepath):
    """解析一个真题 .md 文件，返回 md 原文。"""
    with open(filepath, 'r', encoding='utf-8-sig') as f:
        md_text = f.read()
    return md_text


# ============================================================
# 提取标题
# ============================================================

def extract_main_title(md_text):
    """提取第一个 ## 标题。"""
    m = re.search(r'^##\s+(.+)', md_text, re.MULTILINE)
    if m:
        return m.group(1).strip()
    return ""


# ============================================================
# 构建素材内容
# ============================================================

def build_figures_content(all_figures_sorted):
    """构建人物素材区域的 HTML。"""
    content_parts = []
    chapter_idx = 0
    tag_figure_map = {}  # tag → [figure_name, ...]
    all_heading_anchors = []

    current_region = None
    current_era = None

    for region, era, birth_year, meta, filepath in all_figures_sorted:
        name, display_dates, _, _ = meta

        # 区域/时代分割线
        if region != current_region or era != current_era:
            current_region = region
            current_era = era
            content_parts.append(
                f'<div class="part-divider"><span>{region} · {era}</span></div>'
            )

        if not os.path.exists(filepath):
            content_parts.append(f'<p class="placeholder">文件未找到：{filepath}</p>')
            continue

        tags, popularity, md_text = parse_figure(filepath)
        md_text = strip_popularity_section(md_text)
        html = process_markdown(md_text, chapter_idx)

        # 构建标签徽章
        tag_badges = ''.join(
            f'<span class="tag-badge" data-tag="{escape(t)}">{escape(t)}</span>'
            for t in tags
        )

        # 记录标签→人物映射
        for t in tags:
            tag_figure_map.setdefault(t, []).append(name)

        # 构建人物卡片
        card_id = f"fig-{chapter_idx}"
        all_heading_anchors.append(card_id)

        content_parts.append(f'''
        <section class="chapter-card figure-card" id="{card_id}" data-tags="{escape(','.join(tags))}">
            <div class="figure-card-header">
                <div class="figure-name-row">
                    <span class="figure-name">{escape(name)}</span>
                    {f'<span class="figure-freq-label">热门指数：{escape(popularity)}</span>' if popularity else ''}
                </div>
                <div class="figure-tags">{tag_badges}</div>
            </div>
            <div class="figure-body">
                {html}
            </div>
        </section>''')

        chapter_idx += 1

    content = '\n'.join(content_parts)
    return content, chapter_idx, tag_figure_map, all_heading_anchors


def build_exams_content(exam_groups, start_chapter_idx):
    """构建真题解析区域的 HTML。"""
    content_parts = []
    chapter_idx = start_chapter_idx
    all_heading_anchors = []

    for group_title, exam_files in exam_groups:
        content_parts.append(
            f'<div class="part-divider"><span>{escape(group_title)}</span></div>'
        )

        for filepath in exam_files:
            if not os.path.exists(filepath):
                continue

            md_text = parse_exam(filepath)
            title = extract_main_title(md_text)
            html = process_markdown(md_text, chapter_idx)

            card_id = f"exam-{chapter_idx}"
            all_heading_anchors.append(card_id)

            content_parts.append(f'''
            <section class="chapter-card exam-card" id="{card_id}">
                {html}
            </section>''')

            chapter_idx += 1

    content = '\n'.join(content_parts)
    return content, chapter_idx, all_heading_anchors


# ============================================================
# 侧边栏目录
# ============================================================

def build_sidebar_toc(figures_sorted, exam_groups, tag_figure_map):
    """构建侧边栏目录 HTML。"""
    toc_items = []

    # ── 人物素材 ──
    toc_items.append('<li class="toc-part">人物素材</li>')

    current_region = None
    current_era = None
    fig_idx = 0

    for region, era, birth_year, meta, filepath in figures_sorted:
        name, _, _, _ = meta

        if region != current_region:
            current_region = region
            current_era = None
            toc_items.append(
                f'<li class="toc-region">{escape(region)}</li>'
            )

        if era != current_era:
            current_era = era
            toc_items.append(
                f'<li class="toc-era">{escape(era)}</li>'
            )

        anchor_id = f"fig-{fig_idx}"
        toc_items.append(
            f'<li class="toc-chapter" data-anchor="{anchor_id}">'
            f'<a href="#{anchor_id}">{escape(name)}</a></li>'
        )
        fig_idx += 1

    # ── 真题解析 ──
    toc_items.append('<li class="toc-part">真题解析</li>')
    exam_idx = fig_idx

    for group_title, exam_files in exam_groups:
        toc_items.append(
            f'<li class="toc-era">{escape(group_title)}</li>'
        )
        for filepath in exam_files:
            if not os.path.exists(filepath):
                continue
            exam_idx += 1

    # 收集所有 anchor
    all_anchors = []
    for i in range(fig_idx):
        all_anchors.append(f"fig-{i}")
    for i in range(fig_idx, exam_idx):
        all_anchors.append(f"exam-{i}")

    return '\n'.join(toc_items), all_anchors



# ============================================================
# HTML 模板
# ============================================================

def generate_html():
    """生成完整的 HTML 文件。"""

    # ── 收集并排序所有人物 ──
    all_figures = []
    for filename, meta in FIGURE_META.items():
        name, display_dates, birth_year, _tags_hint = meta
        region, era = get_era(name, birth_year)
        filepath = os.path.join(FIGURES_DIR, filename + ".md")
        all_figures.append((region, era, birth_year, meta, filepath))

    all_figures.sort(key=sort_key_figure)

    # ── 收集真题 ──
    exam_groups = []
    exam_files_high = []
    exam_files_junior = []

    high_dir = os.path.join(EXAMPLES_DIR, "高中")
    junior_dir = os.path.join(EXAMPLES_DIR, "初中")

    if os.path.isdir(high_dir):
        files = sorted([
            os.path.join(high_dir, f) for f in os.listdir(high_dir)
            if f.endswith('.md')
        ], key=lambda p: os.path.basename(p))
        exam_files_high = files

    if os.path.isdir(junior_dir):
        files = sorted([
            os.path.join(junior_dir, f) for f in os.listdir(junior_dir)
            if f.endswith('.md')
        ], key=lambda p: os.path.basename(p))
        exam_files_junior = files

    if exam_files_high:
        exam_groups.append(("高考真题", exam_files_high))
    if exam_files_junior:
        exam_groups.append(("中考真题", exam_files_junior))

    # ── 构建内容 ──
    figures_html, fig_count, tag_figure_map, fig_anchors = build_figures_content(all_figures)
    exams_html, total_count, exam_anchors = build_exams_content(exam_groups, fig_count)

    # ── 构建侧边栏 ──
    toc_html, all_anchors = build_sidebar_toc(all_figures, exam_groups, tag_figure_map)

    # ── 合并正文 ──
    content_html = f'''
    {figures_html}
    {exams_html}
    '''

    gen_date = datetime.now().strftime('%Y年%m月%d日')
    all_anchors_json = '[' + ', '.join(f'"{a}"' for a in all_anchors) + ']'

    # ============================================================
    # 完整 HTML
    # ============================================================
    html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{escape(BOOK_TITLE)}</title>

    <style>
        /* ============================================================
           CSS 自定义属性
           ============================================================ */
        :root {{
            /* 配色 */
            --bg-page: #faf8f5;
            --bg-card: #fffef9;
            --bg-sidebar: #f3efe8;
            --bg-code: #1e1e2e;
            --bg-code-inline: #efeae0;
            --bg-blockquote: #fdf9ed;
            --bg-table-head: #e8e2d3;
            --bg-table-alt: #f9f6f0;
            --bg-header-start: #1a3a4a;
            --bg-header-end: #1e5668;
            --bg-toc-active: rgba(30, 86, 104, 0.10);
            --toc-active-color: #1e5668;

            --color-text: #333333;
            --color-heading: #1a1a2e;
            --color-secondary: #777777;
            --color-accent: #1e5668;
            --color-accent-light: #2a7a8a;
            --color-gold: #1e5668;
            --color-link: #1e5668;
            --color-link-hover: #144052;
            --color-border: #d8d2c5;
            --color-blockquote-border: #1e5668;
            --color-code-text: #e0e0e0;
            --color-placeholder: #999999;
            --color-tag-bg: #e8f0f4;
            --color-tag-text: #1e5668;
            --color-tag-border: #c4dce4;

            /* 字体 */
            --font-body: "KaiTi", "STKaiti", "楷体", "Noto Serif SC", "Songti SC", serif;
            --font-heading: "SimHei", "STHeiti", "黑体", "PingFang SC", "Microsoft YaHei", sans-serif;
            --font-code: "Fira Code", "JetBrains Mono", "Consolas", "Courier New", monospace;

            /* 尺寸 */
            --sidebar-width: 195px;
            --content-max-width: 820px;
            --font-size-body: 17px;
            --line-height-body: 1.95;
            --letter-spacing-body: 0.03em;
            --card-radius: 12px;
            --card-shadow: 0 2px 16px rgba(0, 0, 0, 0.06);
            --transition: 0.3s ease;
        }}

        /* 暗色模式（自动跟随系统） */
        @media (prefers-color-scheme: dark) {{
            :root {{
                --bg-page: #1a1a2e;
                --bg-card: #232340;
                --bg-sidebar: #1e1e36;
                --bg-code: #0d0d1a;
                --bg-code-inline: #2a2a48;
                --bg-blockquote: #2a2840;
                --bg-table-head: #2a2a48;
                --bg-table-alt: #1f1f38;
                --bg-header-start: #0d1f2a;
                --bg-header-end: #142a36;
                --bg-toc-active: rgba(46, 150, 180, 0.15);
                --toc-active-color: #5cb8d4;

                --color-text: #c8c8d8;
                --color-heading: #e0e0f0;
                --color-secondary: #8888a8;
                --color-border: #3a3a58;
                --color-blockquote-border: #4a8a9a;
                --color-link: #5cb8d4;
                --color-link-hover: #7cc8e0;
                --color-tag-bg: #223344;
                --color-tag-text: #7cc8e0;
                --color-tag-border: #334455;
            }}
        }}

        /* ── 手动主题覆盖 ── */

        /* 纸张 / 暖白 */
        body.theme-paper {{
            --bg-page: #fdfaf3;
            --bg-card: #ffffff;
            --bg-sidebar: #f7f3ea;
            --bg-header-start: #3a2f28;
            --bg-header-end: #5a4030;
            --color-accent: #5a3c1e;
            --color-gold: #8b6914;
            --color-link: #5a3c1e;
            --color-link-hover: #8b4513;
            --color-blockquote-border: #8b6914;
            --color-tag-bg: #f5eed8;
            --color-tag-text: #6b5020;
            --color-tag-border: #d4c8a0;
            --bg-toc-active: rgba(139, 105, 20, 0.12);
            --toc-active-color: #8b6914;
        }}

        /* 护眼 / sepia */
        body.theme-sepia {{
            --bg-page: #f4ecd8;
            --bg-card: #faf3e0;
            --bg-sidebar: #ede0c8;
            --bg-header-start: #3a3020;
            --bg-header-end: #504830;
            --color-text: #4a3a28;
            --color-heading: #2a1a08;
            --color-secondary: #8a7a60;
            --color-accent: #6b4a1e;
            --color-link: #6b4a1e;
            --color-link-hover: #8b5a2e;
            --color-blockquote-border: #8a7a4a;
            --color-border: #c8b898;
            --color-tag-bg: #e8d8b0;
            --color-tag-text: #5a3a18;
            --color-tag-border: #c8b080;
            --bg-toc-active: rgba(107, 74, 30, 0.10);
            --toc-active-color: #6b4a1e;
        }}

        /* 暗色（手动） */
        body.theme-dark {{
            --bg-page: #1a1a2e !important;
            --bg-card: #232340 !important;
            --bg-sidebar: #1e1e36 !important;
            --bg-code: #0d0d1a !important;
            --bg-code-inline: #2a2a48 !important;
            --bg-blockquote: #2a2840 !important;
            --bg-table-head: #2a2a48 !important;
            --bg-table-alt: #1f1f38 !important;
            --bg-header-start: #0d1f2a !important;
            --bg-header-end: #142a36 !important;
            --bg-toc-active: rgba(46, 150, 180, 0.15) !important;
            --toc-active-color: #5cb8d4 !important;

            --color-text: #c8c8d8 !important;
            --color-heading: #e0e0f0 !important;
            --color-secondary: #8888a8 !important;
            --color-border: #3a3a58 !important;
            --color-blockquote-border: #4a8a9a !important;
            --color-link: #5cb8d4 !important;
            --color-link-hover: #7cc8e0 !important;
            --color-tag-bg: #223344 !important;
            --color-tag-text: #7cc8e0 !important;
            --color-tag-border: #334455 !important;
        }}

        /* ============================================================
           基础重置
           ============================================================ */
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        html {{
            scroll-behavior: smooth;
            scroll-padding-top: 30px;
        }}

        body {{
            font-family: var(--font-body);
            background: var(--bg-page);
            color: var(--color-text);
            font-size: var(--font-size-body);
            line-height: var(--line-height-body);
            letter-spacing: var(--letter-spacing-body);
            -webkit-font-smoothing: antialiased;
            -moz-osx-font-smoothing: grayscale;
        }}

        /* ============================================================
           页头
           ============================================================ */
        .page-header {{
            background: linear-gradient(135deg, var(--bg-header-start) 0%, var(--bg-header-end) 100%);
            padding: 60px 20px 50px;
            text-align: center;
            margin-bottom: 0;
        }}

        .page-header h1 {{
            font-family: var(--font-heading);
            font-size: 2.2em;
            font-weight: 800;
            background: linear-gradient(135deg, #e8c860 0%, #f0e0a0 50%, #e8c860 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            letter-spacing: 0.08em;
            margin-bottom: 12px;
        }}

        .page-header .subtitle {{
            color: rgba(255, 255, 255, 0.65);
            font-size: 0.95em;
            letter-spacing: 0.1em;
        }}

        /* ============================================================
           布局
           ============================================================ */
        .layout {{
            display: flex;
            align-items: flex-start;
        }}

        /* ============================================================
           侧边栏
           ============================================================ */
        #sidebar {{
            position: sticky;
            top: 0;
            width: var(--sidebar-width);
            height: 100vh;
            background: var(--bg-sidebar);
            border-right: 1px solid var(--color-border);
            overflow-y: auto;
            flex-shrink: 0;
            z-index: 100;
            transition: transform var(--transition);
        }}

        #sidebar::-webkit-scrollbar {{
            width: 5px;
        }}
        #sidebar::-webkit-scrollbar-track {{
            background: transparent;
        }}
        #sidebar::-webkit-scrollbar-thumb {{
            background: #c0b8a0;
            border-radius: 3px;
        }}

        .sidebar-header {{
            padding: 24px 20px 16px;
            border-bottom: 1px solid var(--color-border);
        }}

        .sidebar-header h2 {{
            font-family: var(--font-heading);
            font-size: 16px;
            color: var(--color-heading);
            letter-spacing: 0.05em;
        }}

        .toc-nav {{
            padding: 8px 0 40px;
        }}

        .toc-nav ul {{
            list-style: none;
        }}

        .toc-part {{
            padding: 14px 20px 6px;
            font-size: 13px;
            font-weight: 700;
            font-family: var(--font-heading);
            color: var(--color-secondary);
            letter-spacing: 1.5px;
        }}

        .toc-region {{
            padding: 8px 20px 4px 16px;
            font-size: 14px;
            font-weight: 700;
            font-family: var(--font-heading);
            color: var(--color-accent);
            letter-spacing: 0.08em;
        }}

        .toc-era {{
            padding: 4px 20px 6px 24px;
            font-size: 13px;
            font-family: var(--font-heading);
            color: var(--color-secondary);
            letter-spacing: 0.05em;
        }}

        .toc-chapter {{
            position: relative;
        }}

        .toc-chapter > a {{
            display: block;
            padding: 4px 20px 4px 32px;
            font-size: 14px;
            color: var(--color-text);
            text-decoration: none;
            transition: all 0.15s ease;
            border-left: 3px solid transparent;
            line-height: 1.5;
            font-family: var(--font-body);
        }}

        .toc-chapter > a:hover {{
            background: var(--bg-toc-active);
            color: var(--toc-active-color);
        }}

        .toc-chapter.active > a {{
            background: var(--bg-toc-active);
            border-left-color: var(--toc-active-color);
            color: var(--toc-active-color);
            font-weight: 600;
        }}

        .tag-count {{
            font-size: 10px;
            color: var(--color-secondary);
            background: var(--bg-table-head);
            padding: 1px 6px;
            border-radius: 8px;
        }}

        /* ============================================================
           主内容区
           ============================================================ */
        #main {{
            flex: 1;
            padding: 30px 0 80px;
            min-width: 0;
        }}

        .content-wrapper {{
            width: var(--content-max-width);
            min-width: 360px;
            max-width: 95vw;
            margin: 0 auto;
            padding: 0 40px;
            position: relative;
            border-left: 2px dashed var(--color-border);
            border-right: 2px dashed var(--color-border);
            border-bottom: 2px dashed var(--color-border);
            border-bottom-left-radius: 8px;
            border-bottom-right-radius: 8px;
        }}

        /* 右边缘拖拽把手 */
        .drag-handle {{
            position: absolute;
            top: 0;
            right: -12px;
            width: 24px;
            height: 100%;
            cursor: ew-resize;
            z-index: 10;
            background: transparent;
        }}

        .drag-handle::after {{
            content: "";
            position: absolute;
            right: 6px;
            top: 50%;
            transform: translateY(-50%);
            width: 3px;
            height: 60px;
            border-radius: 2px;
            background: var(--color-secondary);
            opacity: 0.2;
            transition: opacity 0.2s;
        }}

        .content-wrapper:hover .drag-handle::after,
        .drag-handle:active::after {{
            opacity: 0.6;
        }}

        /* 篇分割线 */
        .part-divider {{
            text-align: center;
            margin: 50px 0 30px;
        }}

        .part-divider span {{
            display: inline-block;
            background: var(--color-accent);
            color: #fff;
            padding: 6px 24px;
            font-size: 14px;
            font-family: var(--font-heading);
            font-weight: 600;
            letter-spacing: 2px;
            border-radius: 3px;
        }}

        /* 章节卡片 */
        .chapter-card {{
            background: var(--bg-card);
            border-radius: var(--card-radius);
            box-shadow: var(--card-shadow);
            padding: 36px 40px;
            margin-bottom: 30px;
            scroll-margin-top: 20px;
        }}

        /* ── 人物卡片特有样式 ── */
        .figure-card-header {{
            border-bottom: 2px solid var(--color-accent);
            padding-bottom: 16px;
            margin-bottom: 20px;
        }}

        .figure-name-row {{
            display: flex;
            align-items: baseline;
            gap: 10px;
            flex-wrap: wrap;
            margin-bottom: 8px;
        }}

        .figure-name {{
            font-family: var(--font-heading);
            font-size: 1.7em;
            font-weight: 800;
            color: var(--color-heading);
            letter-spacing: 0.02em;
        }}

        .figure-freq-label {{
            font-size: 0.85em;
            color: var(--color-secondary);
        }}

        .figure-popularity {{
            font-size: 0.8em;
            color: #c8a030;
        }}

        .figure-tags {{
            display: flex;
            flex-wrap: wrap;
            gap: 6px;
        }}

        .tag-badge {{
            display: inline-block;
            background: var(--color-tag-bg);
            color: var(--color-tag-text);
            border: 1px solid var(--color-tag-border);
            padding: 2px 10px;
            border-radius: 12px;
            font-size: 12px;
            font-family: var(--font-heading);
            letter-spacing: 0.03em;
        }}

        /* ── 标题 ── */
        .chapter-card h1 {{
            font-family: var(--font-heading);
            font-size: 1.7em;
            font-weight: 800;
            color: var(--color-heading);
            line-height: 1.4;
            padding-bottom: 14px;
            margin-bottom: 24px;
            border-bottom: 2px solid var(--color-gold);
            letter-spacing: 0.02em;
        }}

        .chapter-card h2 {{
            font-family: var(--font-heading);
            font-size: 1.3em;
            font-weight: 700;
            color: var(--color-heading);
            margin-top: 40px;
            margin-bottom: 14px;
            line-height: 1.5;
        }}

        .chapter-card h3 {{
            font-family: var(--font-heading);
            font-size: 1.1em;
            font-weight: 700;
            color: var(--color-accent);
            margin-top: 28px;
            margin-bottom: 10px;
        }}

        .chapter-card h4 {{
            font-family: var(--font-heading);
            font-size: 1em;
            font-weight: 700;
            color: var(--color-heading);
            margin-top: 20px;
            margin-bottom: 8px;
        }}

        /* 段落 + 首行缩进 */
        .chapter-card p {{
            margin-bottom: 1.1em;
            text-align: justify;
            line-height: var(--line-height-body);
            text-indent: 2em;
        }}

        .chapter-card blockquote p,
        .chapter-card li p,
        .chapter-card pre p,
        .figure-card-header p {{
            text-indent: 0;
        }}

        /* 引用块 */
        .chapter-card blockquote {{
            background: var(--bg-blockquote);
            border-left: 4px solid var(--color-blockquote-border);
            margin: 20px 0;
            padding: 14px 22px;
            border-radius: 0 6px 6px 0;
            color: var(--color-text);
        }}

        .chapter-card blockquote p:last-child {{
            margin-bottom: 0;
        }}

        /* 表格 */
        .chapter-card table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
            font-size: 0.9em;
            border-radius: 6px;
            overflow: hidden;
        }}

        .chapter-card thead {{
            background: var(--bg-table-head);
        }}

        .chapter-card th {{
            padding: 10px 14px;
            text-align: left;
            font-weight: 700;
            font-family: var(--font-heading);
            color: var(--color-heading);
            border-bottom: 2px solid var(--color-border);
            white-space: nowrap;
        }}

        .chapter-card td {{
            padding: 8px 14px;
            border-bottom: 1px solid var(--color-border);
        }}

        .chapter-card tbody tr:nth-child(even) {{
            background: var(--bg-table-alt);
        }}

        .chapter-card tbody tr:hover {{
            background: #eef2f7;
        }}

        /* 列表 */
        .chapter-card ul,
        .chapter-card ol {{
            margin: 12px 0 18px 0;
            padding-left: 28px;
        }}

        .chapter-card li {{
            margin-bottom: 5px;
            line-height: 1.85;
        }}

        /* 行内代码 */
        .chapter-card code {{
            font-family: var(--font-code);
            font-size: 0.85em;
            background: var(--bg-code-inline);
            color: #c0392b;
            padding: 2px 5px;
            border-radius: 3px;
        }}

        /* 代码块 */
        .chapter-card pre {{
            background: var(--bg-code);
            border-radius: 8px;
            padding: 16px 18px;
            overflow-x: auto;
            margin: 18px 0;
            font-size: 0.82em;
            line-height: 1.6;
        }}

        .chapter-card pre code {{
            background: none;
            color: var(--color-code-text);
            padding: 0;
            font-size: inherit;
            border-radius: 0;
        }}

        /* 分割线 */
        .chapter-card hr {{
            border: none;
            text-align: center;
            margin: 32px 0;
        }}

        .chapter-card hr::after {{
            content: '· · ·';
            color: var(--color-gold);
            font-size: 1.2em;
            letter-spacing: 0.5em;
        }}

        /* 链接 */
        .chapter-card a {{
            color: var(--color-link);
            text-decoration: none;
            border-bottom: 1px dashed var(--color-link);
            transition: all 0.15s;
        }}

        .chapter-card a:hover {{
            color: var(--color-link-hover);
            border-bottom: 1px solid var(--color-link-hover);
        }}

        /* 强调 */
        .chapter-card strong {{
            font-weight: 700;
            color: var(--color-heading);
        }}

        /* 人物卡片中 h1 的特殊处理（隐藏 "## 人物名" 标题，因为已在卡片头显示） */
        .figure-card .figure-body > h1:first-child,
        .figure-card .figure-body > h2:first-child {{
            display: none;
        }}

        /* 真题卡片中标题的处理 */
        .exam-card .figure-body > h2:first-child {{
            font-family: var(--font-heading);
            font-size: 1.7em;
            font-weight: 800;
            color: var(--color-heading);
            line-height: 1.4;
            padding-bottom: 14px;
            margin-bottom: 24px;
            border-bottom: 2px solid var(--color-gold);
            letter-spacing: 0.02em;
        }}

        /* 占位文字 */
        .placeholder {{
            text-align: center;
            color: var(--color-placeholder);
            font-style: italic;
            padding: 40px;
            background: var(--bg-blockquote);
            border-radius: 8px;
        }}

        /* ============================================================
           页脚
           ============================================================ */
        .page-footer {{
            background: var(--bg-sidebar);
            border-top: 1px solid var(--color-border);
            padding: 30px 20px;
            text-align: center;
            font-size: 0.82em;
            color: var(--color-secondary);
            line-height: 1.8;
        }}

        .page-footer p {{
            margin: 4px 0;
        }}

        /* ============================================================
           回到顶部按钮
           ============================================================ */
        #back-to-top {{
            position: fixed;
            bottom: 60px;
            right: 30px;
            width: 44px;
            height: 44px;
            background: linear-gradient(135deg, #1e5668 0%, #144052 100%);
            color: #fff;
            border: none;
            border-radius: 50%;
            font-size: 20px;
            cursor: pointer;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
            z-index: 90;
            opacity: 0;
            visibility: hidden;
            transition: all var(--transition);
            display: flex;
            align-items: center;
            justify-content: center;
        }}

        #back-to-top.visible {{
            opacity: 1;
            visibility: visible;
        }}

        #back-to-top:hover {{
            transform: translateY(-3px);
            box-shadow: 0 6px 16px rgba(0, 0, 0, 0.3);
        }}

        /* ============================================================
           底部阅读工具栏
           ============================================================ */
        #reading-bar {{
            position: fixed;
            bottom: 0;
            left: 0;
            right: 0;
            height: 44px;
            background: var(--bg-card);
            border-top: 1px solid var(--color-border);
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 2px;
            z-index: 95;
            padding: 0 12px;
            box-shadow: 0 -2px 8px rgba(0, 0, 0, 0.05);
        }}

        #reading-bar button {{
            height: 32px;
            padding: 0 12px;
            border: 1px solid var(--color-border);
            background: var(--bg-card);
            color: var(--color-text);
            font-size: 13px;
            font-family: var(--font-heading);
            cursor: pointer;
            border-radius: 4px;
            transition: all 0.15s;
            white-space: nowrap;
        }}

        #reading-bar button:hover {{
            background: var(--bg-toc-active);
            color: var(--toc-active-color);
            border-color: var(--toc-active-color);
        }}

        #reading-bar .rb-sep {{
            width: 1px;
            height: 20px;
            background: var(--color-border);
            margin: 0 4px;
        }}

        #reading-bar .rb-label {{
            font-size: 11px;
            color: var(--color-secondary);
            font-family: var(--font-heading);
            padding: 0 4px;
        }}

        /* ============================================================
           移动端汉堡菜单
           ============================================================ */
        #menu-toggle {{
            display: none;
            position: fixed;
            top: 14px;
            left: 14px;
            z-index: 150;
            background: var(--color-accent);
            color: #fff;
            border: none;
            border-radius: 6px;
            padding: 8px 14px;
            font-size: 14px;
            cursor: pointer;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
        }}

        #overlay {{
            display: none;
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.4);
            z-index: 99;
        }}

        #overlay.visible {{
            display: block;
        }}

        /* ============================================================
           响应式
           ============================================================ */

        @media (max-width: 768px) {{
            :root {{
                --sidebar-width: 195px;
            }}

            .content-wrapper {{
                padding: 0 24px;
            }}

            .chapter-card {{
                padding: 28px 26px;
            }}

            .page-header h1 {{
                font-size: 1.8em;
            }}

            #reading-bar {{
                gap: 1px;
            }}

            #reading-bar button {{
                font-size: 11px;
                padding: 0 8px;
            }}
        }}

        @media (max-width: 480px) {{
            :root {{
                --font-size-body: 15px;
            }}

            #menu-toggle {{
                display: block;
            }}

            #sidebar {{
                position: fixed;
                top: 0;
                left: 0;
                transform: translateX(-100%);
                width: 80%;
                max-width: 300px;
                z-index: 110;
            }}

            #sidebar.open {{
                transform: translateX(0);
            }}

            .content-wrapper {{
                padding: 0 12px;
            }}

            .chapter-card {{
                padding: 20px 16px;
                border-radius: 8px;
            }}

            .chapter-card h1 {{
                font-size: 1.5em;
            }}

            .chapter-card h2 {{
                font-size: 1.25em;
            }}

            .chapter-card h3 {{
                font-size: 1.1em;
            }}

            .page-header {{
                padding: 50px 16px 36px;
            }}

            .page-header h1 {{
                font-size: 1.5em;
            }}

            .part-divider span {{
                font-size: 12px;
                padding: 5px 18px;
            }}

            #reading-bar {{
                gap: 0;
                padding: 0 4px;
            }}

            #reading-bar button {{
                font-size: 10px;
                padding: 0 6px;
            }}

            #reading-bar .rb-sep {{
                margin: 0 2px;
            }}

            #reading-bar .rb-label {{
                display: none;
            }}
        }}

        /* 打印样式 */
        @media print {{
            #sidebar, #back-to-top, #menu-toggle, #overlay, #reading-bar {{
                display: none !important;
            }}

            .layout {{
                display: block;
            }}

            #main {{
                padding: 0;
            }}

            .content-wrapper {{
                max-width: 100%;
                padding: 0;
                border: none;
            }}

            .chapter-card {{
                box-shadow: none;
                border-radius: 0;
                page-break-after: always;
            }}

            .page-header {{
                background: none;
                color: #000;
                padding: 20px 0;
            }}

            .page-header h1 {{
                -webkit-text-fill-color: #000;
                color: #000;
            }}
        }}
    </style>
</head>
<body>

    <!-- 页头 -->
    <header class="page-header">
        <h1>{escape(BOOK_TITLE)}</h1>
        <p class="subtitle">75 位人物素材 · 42 道真题解析</p>
    </header>

    <!-- 移动端汉堡菜单 -->
    <button id="menu-toggle">☰ 目录</button>
    <div id="overlay"></div>

    <!-- 布局 -->
    <div class="layout">

        <!-- 侧边栏目录 -->
        <nav id="sidebar">
            <div class="sidebar-header">
                <h2>目 录</h2>
            </div>
            <div class="toc-nav">
                <ul>
                    {toc_html}
                </ul>
            </div>
        </nav>

        <!-- 主内容 -->
        <div id="main">
            <div class="content-wrapper" id="drag-container">
                {content_html}
                <div class="drag-handle" id="drag-handle"></div>
            </div>

            <!-- 页脚 -->
            <footer class="page-footer">
                <p><strong>{escape(BOOK_TITLE)}</strong></p>
                <p>生成日期：{gen_date}</p>
                <p>75 位中外历史人物素材 + 42 道真题解析</p>
            </footer>
        </div>

    </div>

    <!-- 回到顶部 -->
    <button id="back-to-top" title="回到顶部">↑</button>

    <!-- 底部阅读工具栏：字号 / 行距 / 字体 / 主题 -->
    <div id="reading-bar">
        <span class="rb-label">字号</span>
        <button data-act="font-" title="减小字号">A−</button>
        <span class="rb-label" id="rb-fs-label">17px</span>
        <button data-act="font+" title="增大字号">A＋</button>
        <span class="rb-sep"></span>
        <span class="rb-label">行距</span>
        <button data-act="lh-" title="减小行距">−</button>
        <span class="rb-label" id="rb-lh-label">1.95</span>
        <button data-act="lh+" title="增大行距">＋</button>
        <span class="rb-sep"></span>
        <button data-act="font" id="rb-font" title="切换正文字体">字体·楷体</button>
        <span class="rb-sep"></span>
        <button data-act="theme" id="rb-theme" title="切换阅读主题">主题·跟随系统</button>
    </div>

    <script>
        // ============================================================
        // 移动端菜单
        // ============================================================
        var menuToggle = document.getElementById('menu-toggle');
        var sidebar = document.getElementById('sidebar');
        var overlay = document.getElementById('overlay');

        function openMenu() {{
            sidebar.classList.add('open');
            overlay.classList.add('visible');
        }}
        function closeMenu() {{
            sidebar.classList.remove('open');
            overlay.classList.remove('visible');
        }}

        menuToggle.addEventListener('click', openMenu);
        overlay.addEventListener('click', closeMenu);

        document.querySelectorAll('#sidebar a').forEach(function(link) {{
            link.addEventListener('click', function() {{
                if (window.innerWidth <= 480) {{
                    closeMenu();
                }}
            }});
        }});

        // ============================================================
        // 回到顶部
        // ============================================================
        var backToTop = document.getElementById('back-to-top');
        window.addEventListener('scroll', function() {{
            if (window.pageYOffset > 400) {{
                backToTop.classList.add('visible');
            }} else {{
                backToTop.classList.remove('visible');
            }}
        }});
        backToTop.addEventListener('click', function() {{
            window.scrollTo({{ top: 0, behavior: 'smooth' }});
        }});

        // ============================================================
        // 目录高亮：滚动时自动高亮当前所在章节
        // ============================================================
        var allAnchors = {all_anchors_json};
        var anchorElements = allAnchors.map(function(id) {{
            return document.getElementById(id);
        }}).filter(function(el) {{ return el !== null; }});

        var tocItems = document.querySelectorAll('.toc-chapter');

        function highlightAnchor(id) {{
            tocItems.forEach(function(item) {{
                if (item.dataset.anchor === id) {{
                    item.classList.add('active');
                }} else {{
                    item.classList.remove('active');
                }}
            }});
        }}

        function findCurrentHeading() {{
            var bestId = null;
            var threshold = 100;

            for (var i = 0; i < anchorElements.length; i++) {{
                var top = anchorElements[i].getBoundingClientRect().top;
                if (top > threshold) {{
                    if (i > 0) return anchorElements[i - 1].id;
                    return anchorElements[0].id;
                }}
            }}

            return anchorElements[anchorElements.length - 1].id;
        }}

        var scrollTimer = null;
        window.addEventListener('scroll', function() {{
            if (scrollTimer) return;
            scrollTimer = setTimeout(function() {{
                scrollTimer = null;
                var currentId = findCurrentHeading();
                if (currentId) highlightAnchor(currentId);
            }}, 150);
        }});

        var currentId = findCurrentHeading();
        if (currentId) highlightAnchor(currentId);

        // ============================================================
        // 拖拽调整内容区宽度
        // ============================================================
        (function() {{
            var container = document.getElementById('drag-container');
            var handle = document.getElementById('drag-handle');
            if (!container || !handle) return;

            var WIDTH_KEY = 'essay_figures_width';

            var savedWidth = localStorage.getItem(WIDTH_KEY);
            if (savedWidth) {{
                var w = parseInt(savedWidth, 10);
                if (w >= 360) {{
                    container.style.width = w + 'px';
                }}
            }}

            var isDragging = false;
            var startX = 0;
            var startWidth = 0;

            handle.addEventListener('mousedown', function(e) {{
                isDragging = true;
                startX = e.clientX;
                startWidth = container.offsetWidth;
                document.body.style.cursor = 'ew-resize';
                document.body.style.userSelect = 'none';
                e.preventDefault();
            }});

            document.addEventListener('mousemove', function(e) {{
                if (!isDragging) return;
                var delta = e.clientX - startX;
                var newWidth = startWidth + delta;
                newWidth = Math.max(360, Math.min(newWidth, window.innerWidth * 0.95));
                container.style.width = newWidth + 'px';
            }});

            document.addEventListener('mouseup', function() {{
                if (isDragging) {{
                    isDragging = false;
                    document.body.style.cursor = '';
                    document.body.style.userSelect = '';
                    localStorage.setItem(WIDTH_KEY, container.offsetWidth);
                }}
            }});
        }})();

        // ============================================================
        // 阅读位置记忆
        // ============================================================
        (function() {{
            var STORAGE_KEY = 'essay_figures_scroll';
            var saveTimer = null;

            var saved = localStorage.getItem(STORAGE_KEY);
            if (saved) {{
                var pos = parseInt(saved, 10);
                if (pos > 0) {{
                    window.scrollTo(0, pos);
                    setTimeout(function() {{ window.scrollTo(0, pos); }}, 1500);
                }}
            }}

            window.addEventListener('scroll', function() {{
                if (saveTimer) return;
                saveTimer = setTimeout(function() {{
                    saveTimer = null;
                    localStorage.setItem(STORAGE_KEY, window.scrollY);
                }}, 500);
            }});

            window.addEventListener('beforeunload', function() {{
                localStorage.setItem(STORAGE_KEY, window.scrollY);
            }});
        }})();

        // ============================================================
        // 底部工具栏：字号 · 行距 · 字体 · 主题
        // ============================================================
        (function() {{
            var SETTINGS_KEY = 'essay_figures_settings';
            var FONT_ORDER = ['kai', 'song', 'hei'];
            var FONT_NAME = {{ 'kai': '楷体', 'song': '宋体', 'hei': '黑体' }};
            var FONT_CSS = {{
                'kai': '"KaiTi", "STKaiti", "楷体", "Noto Serif SC", "Songti SC", serif',
                'song': '"SimSun", "STSong", "宋体", "Noto Serif SC", serif',
                'hei': '"SimHei", "STHeiti", "黑体", "PingFang SC", "Microsoft YaHei", sans-serif'
            }};
            var THEME_ORDER = ['auto', 'paper', 'sepia', 'dark'];
            var THEME_NAME = {{ 'auto': '跟随系统', 'paper': '纸张', 'sepia': '护眼', 'dark': '暗色' }};

            var RB = {{ fs: 17, lh: 1.95, font: 'kai', theme: 'auto' }};

            // 读取保存的设置
            var saved = localStorage.getItem(SETTINGS_KEY);
            if (saved) {{
                try {{
                    var parsed = JSON.parse(saved);
                    if (typeof parsed.fs === 'number') RB.fs = parsed.fs;
                    if (typeof parsed.lh === 'number') RB.lh = parsed.lh;
                    if (FONT_ORDER.indexOf(parsed.font) >= 0) RB.font = parsed.font;
                    if (THEME_ORDER.indexOf(parsed.theme) >= 0) RB.theme = parsed.theme;
                }} catch(e) {{}}
            }}

            function apply() {{
                var r = document.documentElement.style;
                r.setProperty('--font-size-body', RB.fs + 'px');
                r.setProperty('--line-height-body', RB.lh);
                r.setProperty('--font-body', FONT_CSS[RB.font]);

                // 主题
                document.body.classList.remove('theme-paper', 'theme-sepia', 'theme-dark');
                if (RB.theme !== 'auto') document.body.classList.add('theme-' + RB.theme);

                // 更新标签
                var fl = document.getElementById('rb-fs-label'); if (fl) fl.textContent = RB.fs + 'px';
                var ll = document.getElementById('rb-lh-label'); if (ll) ll.textContent = RB.lh.toFixed(2);
                var fb = document.getElementById('rb-font'); if (fb) fb.textContent = '字体·' + FONT_NAME[RB.font];
                var tb = document.getElementById('rb-theme'); if (tb) tb.textContent = '主题·' + THEME_NAME[RB.theme];
            }}

            function save() {{
                localStorage.setItem(SETTINGS_KEY, JSON.stringify(RB));
            }}

            apply();

            // 工具栏按钮事件
            document.getElementById('reading-bar').addEventListener('click', function(e) {{
                var btn = e.target.closest('button');
                if (!btn) return;
                var act = btn.dataset.act;
                if (!act) return;

                if (act === 'font+') {{ RB.fs = Math.min(24, RB.fs + 1); }}
                else if (act === 'font-') {{ RB.fs = Math.max(12, RB.fs - 1); }}
                else if (act === 'lh+') {{ RB.lh = Math.min(3.0, +(RB.lh + 0.1).toFixed(2)); }}
                else if (act === 'lh-') {{ RB.lh = Math.max(1.3, +(RB.lh - 0.1).toFixed(2)); }}
                else if (act === 'font') {{
                    var idx = FONT_ORDER.indexOf(RB.font);
                    RB.font = FONT_ORDER[(idx + 1) % FONT_ORDER.length];
                }}
                else if (act === 'theme') {{
                    var idx = THEME_ORDER.indexOf(RB.theme);
                    RB.theme = THEME_ORDER[(idx + 1) % THEME_ORDER.length];
                }}

                apply();
                save();
            }});
        }})();
    </script>

</body>
</html>'''

    return html


if __name__ == '__main__':
    html_content = generate_html()
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write(html_content)
    file_size = os.path.getsize(OUTPUT_FILE) / 1024
    print(f"HTML 文件已生成: {OUTPUT_FILE}")
    print(f"文件大小: {file_size:.1f} KB")
