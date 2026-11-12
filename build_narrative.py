#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
《以我见人：从生活到素材的记叙文写作》HTML 生成器。

读取 narrative-writing-guide/book 下的全部 md，按文件名序号排序，
生成单页 HTML：侧边栏目录、滚动高亮、字号/行距/主题调节、阅读位置记忆。
"""

import os
import re
import markdown
from html import escape

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
BOOK_DIR = os.path.join(PROJECT_DIR, "narrative-writing-guide", "book")
OUTPUT_FILE = os.path.join(PROJECT_DIR, "以我见人：从生活到素材的记叙文写作.html")
BOOK_TITLE = "以我见人：从生活到素材的记叙文写作"
SUBTITLE = "从生活到素材的记叙文写作"


def collect_files():
    """收集 book 目录下的 md，前言在最前，其余按路径排序（文件名序号决定顺序）。"""
    files = []
    for root, dirs, names in os.walk(BOOK_DIR):
        dirs.sort()
        for name in sorted(names):
            if name.lower().endswith(".md"):
                files.append(os.path.join(root, name))

    def key(path):
        base = os.path.basename(path)
        if base.startswith("前言"):
            return (0, "")
        return (1, path.replace("\\", "/"))

    return sorted(files, key=key)


def chapter_title(md_text, fallback):
    """取第一个 ## 标题作为章节名。"""
    m = re.search(r"^##\s+(.+)$", md_text, re.MULTILINE)
    return m.group(1).strip() if m else fallback


def render_markdown(md_text):
    return markdown.markdown(
        md_text,
        extensions=["tables", "fenced_code", "sane_lists"],
    )


def build_sections(files):
    sections = []
    toc = []
    for idx, path in enumerate(files):
        with open(path, "r", encoding="utf-8-sig") as f:
            md_text = f.read()

        fallback = os.path.splitext(os.path.basename(path))[0]
        title = chapter_title(md_text, fallback)
        anchor = "ch%d" % idx

        sections.append(
            '<section class="chapter-card" id="%s">\n%s\n</section>'
            % (anchor, render_markdown(md_text))
        )
        toc.append(
            '<li class="toc-item" data-anchor="%s"><a href="#%s">%s</a></li>'
            % (anchor, anchor, escape(title))
        )

    # 前言不计入章数
    chapter_count = len([
        p for p in files if not os.path.basename(p).startswith("前言")
    ])
    return "\n".join(sections), "\n".join(toc), chapter_count


CSS = """
:root {
    --bg-page: #faf8f5;
    --bg-card: #fffef9;
    --bg-sidebar: #f3efe8;
    --bg-quote: #fdf9ed;
    --bg-table-head: #e8e2d3;
    --bg-table-alt: #f9f6f0;

    --color-text: #333333;
    --color-heading: #1a1a2e;
    --color-secondary: #7a7a7a;
    --color-accent: #1e5668;
    --color-border: #d8d2c5;

    --font-body: "KaiTi", "STKaiti", "楷体", "Songti SC", "Noto Serif SC", serif;
    --font-heading: "SimHei", "STHeiti", "黑体", "PingFang SC", "Microsoft YaHei", sans-serif;

    --fs: 18px;
    --lh: 2.0;
    --sidebar-width: 210px;
    --content-width: 780px;
}

body.theme-paper {
    --bg-page: #fdfaf3;
    --bg-card: #ffffff;
    --bg-sidebar: #f7f3ea;
    --bg-quote: #fbf5e6;
    --color-accent: #5a3c1e;
    --color-border: #ddd2bb;
}

body.theme-sepia {
    --bg-page: #f4ecd8;
    --bg-card: #faf3e0;
    --bg-sidebar: #ede0c8;
    --bg-quote: #f3e7cd;
    --bg-table-head: #e4d5b4;
    --color-text: #4a3a28;
    --color-heading: #2a1a08;
    --color-secondary: #8a7a60;
    --color-accent: #6b4a1e;
    --color-border: #c8b898;
}

body.theme-dark {
    --bg-page: #1a1a2e;
    --bg-card: #232340;
    --bg-sidebar: #1e1e36;
    --bg-quote: #2a2840;
    --bg-table-head: #2a2a48;
    --bg-table-alt: #1f1f38;
    --color-text: #c8c8d8;
    --color-heading: #e8e8f8;
    --color-secondary: #8a8aa8;
    --color-accent: #6cb8d0;
    --color-border: #3a3a58;
}

* { margin: 0; padding: 0; box-sizing: border-box; }

html { scroll-behavior: smooth; scroll-padding-top: 24px; }

body {
    font-family: var(--font-body);
    background: var(--bg-page);
    color: var(--color-text);
    font-size: var(--fs);
    line-height: var(--lh);
    letter-spacing: 0.02em;
}

.page-header {
    background: linear-gradient(135deg, #1a3a4a 0%, #1e5668 100%);
    padding: 56px 20px 46px;
    text-align: center;
}

.page-header h1 {
    font-family: var(--font-heading);
    font-size: 1.9em;
    color: #f2e6c8;
    letter-spacing: 0.06em;
}

.page-header .subtitle {
    margin-top: 10px;
    color: rgba(255, 255, 255, 0.62);
    font-size: 0.85em;
    letter-spacing: 0.12em;
}

.layout { display: flex; align-items: flex-start; }

#sidebar {
    position: sticky;
    top: 0;
    width: var(--sidebar-width);
    height: 100vh;
    flex-shrink: 0;
    overflow-y: auto;
    background: var(--bg-sidebar);
    border-right: 1px solid var(--color-border);
    padding-bottom: 40px;
}

.sidebar-header {
    padding: 22px 20px 14px;
    border-bottom: 1px solid var(--color-border);
}

.sidebar-header h2 {
    font-family: var(--font-heading);
    font-size: 14px;
    color: var(--color-heading);
    letter-spacing: 0.2em;
}

.toc { list-style: none; padding: 8px 0; }

.toc-item > a {
    display: block;
    padding: 5px 18px;
    font-size: 0.78em;
    color: var(--color-text);
    text-decoration: none;
    border-left: 3px solid transparent;
    line-height: 1.6;
}

.toc-item > a:hover { color: var(--color-accent); }

.toc-item.active > a {
    color: var(--color-accent);
    border-left-color: var(--color-accent);
    font-weight: 600;
}

#main {
    flex: 1;
    min-width: 0;
    padding: 34px 0 90px;
}

.wrapper {
    width: var(--content-width);
    max-width: 94vw;
    min-width: 420px;
    margin: 0 auto;
    padding: 0 36px;
    position: relative;
    border-left: 2px dashed var(--color-border);
    border-right: 2px dashed var(--color-border);
}

/* 右边缘拖拽把手 */
.drag-handle {
    position: absolute;
    top: 0;
    right: -14px;
    width: 26px;
    height: 100%;
    cursor: ew-resize;
    z-index: 10;
}

.drag-handle::after {
    content: "";
    position: absolute;
    right: 10px;
    top: 0;
    bottom: 0;
    width: 3px;
    border-radius: 2px;
    background: var(--color-accent);
    opacity: 0;
    transition: opacity 0.2s;
}

.wrapper:hover .drag-handle::after,
.drag-handle:active::after { opacity: 0.5; }

.chapter-card {
    background: var(--bg-card);
    border-radius: 10px;
    box-shadow: 0 2px 14px rgba(0, 0, 0, 0.06);
    padding: 40px 44px 44px;
    margin-bottom: 34px;
}

.chapter-card > h2:first-child {
    font-family: var(--font-heading);
    font-size: 1.5em;
    color: var(--color-heading);
    line-height: 1.5;
    padding-bottom: 14px;
    margin-bottom: 26px;
    border-bottom: 2px solid var(--color-accent);
    letter-spacing: 0.02em;
}

.chapter-card h3 {
    font-family: var(--font-heading);
    font-size: 1.06em;
    color: var(--color-accent);
    margin: 30px 0 12px;
}

.chapter-card h4 {
    font-family: var(--font-heading);
    font-size: 0.96em;
    color: var(--color-heading);
    margin: 22px 0 8px;
}

.chapter-card p {
    margin-bottom: 0.9em;
    text-align: justify;
    text-indent: 2em;
}

.chapter-card blockquote {
    background: var(--bg-quote);
    border-left: 4px solid var(--color-accent);
    border-radius: 0 6px 6px 0;
    padding: 16px 22px;
    margin: 18px 0 22px;
}

.chapter-card blockquote p:last-child { margin-bottom: 0; }

.chapter-card table {
    width: 100%;
    border-collapse: collapse;
    margin: 16px 0 22px;
    font-size: 0.82em;
    line-height: 1.7;
}

.chapter-card thead { background: var(--bg-table-head); }

.chapter-card th {
    font-family: var(--font-heading);
    font-weight: 700;
    text-align: left;
    color: var(--color-heading);
    padding: 9px 12px;
    border-bottom: 2px solid var(--color-border);
}

.chapter-card td {
    padding: 8px 12px;
    border-bottom: 1px solid var(--color-border);
    vertical-align: top;
    text-indent: 0;
}

.chapter-card tbody tr:nth-child(even) { background: var(--bg-table-alt); }

.chapter-card strong { font-weight: 700; color: var(--color-heading); }

.chapter-card a { color: var(--color-accent); }

.chapter-card p.signature {
    text-align: center;
    text-indent: 0;
    margin-top: 6px;
    font-size: 0.8em;
    color: var(--color-secondary);
    letter-spacing: 0.04em;
}

#reading-bar {
    position: fixed;
    bottom: 0;
    left: 0;
    right: 0;
    height: 42px;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 4px;
    background: var(--bg-card);
    border-top: 1px solid var(--color-border);
    z-index: 95;
}

#reading-bar button {
    height: 28px;
    padding: 0 10px;
    font-family: var(--font-heading);
    font-size: 12px;
    color: var(--color-text);
    background: transparent;
    border: 1px solid var(--color-border);
    border-radius: 4px;
    cursor: pointer;
}

#reading-bar button:hover {
    color: var(--color-accent);
    border-color: var(--color-accent);
}

#reading-bar .label {
    font-family: var(--font-heading);
    font-size: 11px;
    color: var(--color-secondary);
    padding: 0 2px;
}

#reading-bar .sep {
    width: 1px;
    height: 18px;
    background: var(--color-border);
    margin: 0 6px;
}

#to-top {
    position: fixed;
    right: 26px;
    bottom: 58px;
    width: 38px;
    height: 38px;
    border: none;
    border-radius: 50%;
    background: var(--color-accent);
    color: #fff;
    font-size: 16px;
    cursor: pointer;
    opacity: 0;
    visibility: hidden;
    transition: all 0.25s ease;
    z-index: 90;
}

#to-top.visible { opacity: 1; visibility: visible; }

@media (max-width: 900px) {
    #sidebar { display: none; }
    .wrapper { padding: 0 18px; }
    .chapter-card { padding: 26px 20px 30px; }
}
"""

JS = """
(function () {
    var bars = document.querySelectorAll('.toc-item');
    var anchors = [];
    bars.forEach(function (li) {
        var el = document.getElementById(li.dataset.anchor);
        if (el) anchors.push(el);
    });

    function highlight() {
        var current = anchors[0];
        for (var i = 0; i < anchors.length; i++) {
            if (anchors[i].getBoundingClientRect().top < 120) current = anchors[i];
        }
        bars.forEach(function (li) {
            li.classList.toggle('active', current && li.dataset.anchor === current.id);
        });
    }

    var toTop = document.getElementById('to-top');
    var timer = null;
    window.addEventListener('scroll', function () {
        toTop.classList.toggle('visible', window.scrollY > 400);
        if (timer) return;
        timer = setTimeout(function () { timer = null; highlight(); }, 120);
    });
    highlight();

    toTop.addEventListener('click', function () {
        window.scrollTo({ top: 0, behavior: 'smooth' });
    });

    var KEY = 'narrative_guide_settings';
    var FONTS = [
        ['"KaiTi", "STKaiti", "楷体", serif', '楷体'],
        ['"SimSun", "STSong", "宋体", serif', '宋体'],
        ['"SimHei", "STHeiti", "黑体", sans-serif', '黑体']
    ];
    var THEMES = [['', '默认'], ['paper', '纸张'], ['sepia', '护眼'], ['dark', '暗色']];
    var S = { fs: 18, lh: 2.0, font: 0, theme: 0 };

    try {
        var saved = JSON.parse(localStorage.getItem(KEY) || 'null');
        if (saved) S = saved;
    } catch (e) {}

    function apply() {
        var root = document.documentElement.style;
        root.setProperty('--fs', S.fs + 'px');
        root.setProperty('--lh', S.lh.toFixed(2));
        root.setProperty('--font-body', FONTS[S.font][0]);
        document.body.className = S.theme ? 'theme-' + THEMES[S.theme][0] : '';
        document.getElementById('fs-label').textContent = S.fs + 'px';
        document.getElementById('lh-label').textContent = S.lh.toFixed(2);
        document.getElementById('font-btn').textContent = '字体·' + FONTS[S.font][1];
        document.getElementById('theme-btn').textContent = '主题·' + THEMES[S.theme][1];
        localStorage.setItem(KEY, JSON.stringify(S));
    }

    document.getElementById('reading-bar').addEventListener('click', function (e) {
        var btn = e.target.closest('button');
        if (!btn) return;
        var act = btn.dataset.act;
        if (act === 'fs+') S.fs = Math.min(24, S.fs + 1);
        if (act === 'fs-') S.fs = Math.max(14, S.fs - 1);
        if (act === 'lh+') S.lh = Math.min(2.8, S.lh + 0.1);
        if (act === 'lh-') S.lh = Math.max(1.5, S.lh - 0.1);
        if (act === 'font') S.font = (S.font + 1) % FONTS.length;
        if (act === 'theme') S.theme = (S.theme + 1) % THEMES.length;
        apply();
    });

    apply();
})();

(function () {
    var container = document.getElementById('drag-container');
    var handle = document.getElementById('drag-handle');
    if (!container || !handle) return;

    var KEY = 'narrative_guide_width';
    var saved = parseInt(localStorage.getItem(KEY) || '0', 10);
    if (saved >= 420) container.style.width = saved + 'px';

    var dragging = false;
    var startX = 0;
    var startWidth = 0;

    handle.addEventListener('mousedown', function (e) {
        dragging = true;
        startX = e.clientX;
        startWidth = container.offsetWidth;
        document.body.style.cursor = 'ew-resize';
        document.body.style.userSelect = 'none';
        e.preventDefault();
    });

    document.addEventListener('mousemove', function (e) {
        if (!dragging) return;
        var width = startWidth + (e.clientX - startX);
        width = Math.max(420, Math.min(width, window.innerWidth * 0.94));
        container.style.width = width + 'px';
    });

    document.addEventListener('mouseup', function () {
        if (!dragging) return;
        dragging = false;
        document.body.style.cursor = '';
        document.body.style.userSelect = '';
        localStorage.setItem(KEY, container.offsetWidth);
    });
})();
"""


def build_html():
    files = collect_files()
    sections_html, toc_html, count = build_sections(files)

    return (
        '<!DOCTYPE html>\n'
        '<html lang="zh-CN">\n<head>\n'
        '<meta charset="UTF-8">\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1.0">\n'
        "<title>%s</title>\n"
        "<style>%s</style>\n"
        "</head>\n<body>\n"
        '<header class="page-header">\n'
        "<h1>%s</h1>\n"
        '<p class="subtitle">%s · %d 章</p>\n'
        "</header>\n"
        '<div class="layout">\n'
        '<nav id="sidebar">\n'
        '<div class="sidebar-header"><h2>目 录</h2></div>\n'
        '<ul class="toc">\n%s\n</ul>\n'
        "</nav>\n"
        '<div id="main">\n<div class="wrapper" id="drag-container">\n'
        "%s\n"
        '<div class="drag-handle" id="drag-handle"></div>\n'
        "</div>\n</div>\n</div>\n"
        '<button id="to-top" title="回到顶部">↑</button>\n'
        '<div id="reading-bar">\n'
        '<span class="label">字号</span>'
        '<button data-act="fs-">A−</button>'
        '<span class="label" id="fs-label">18px</span>'
        '<button data-act="fs+">A＋</button>'
        '<span class="sep"></span>'
        '<span class="label">行距</span>'
        '<button data-act="lh-">−</button>'
        '<span class="label" id="lh-label">2.00</span>'
        '<button data-act="lh+">＋</button>'
        '<span class="sep"></span>'
        '<button data-act="font" id="font-btn">字体·楷体</button>'
        '<span class="sep"></span>'
        '<button data-act="theme" id="theme-btn">主题·默认</button>\n'
        "</div>\n"
        "<script>%s</script>\n"
        "</body>\n</html>\n"
    ) % (
        escape(BOOK_TITLE),
        CSS,
        escape(BOOK_TITLE),
        escape(SUBTITLE),
        count,
        toc_html,
        sections_html,
        JS,
    )


if __name__ == "__main__":
    html = build_html()
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(html)
    size = os.path.getsize(OUTPUT_FILE) / 1024
    print("HTML 已生成: %s" % OUTPUT_FILE)
    print("文件大小: %.1f KB" % size)
