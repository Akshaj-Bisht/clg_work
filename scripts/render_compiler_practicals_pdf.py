#!/usr/bin/env python3
"""Render the Compiler Design practicals Markdown as a styled PDF."""

import html
import json
import re
import subprocess
from pathlib import Path

import cairo
import gi

gi.require_version("Pango", "1.0")
gi.require_version("PangoCairo", "1.0")
from gi.repository import Pango, PangoCairo


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "compiler-design" / "practicals" / "Compiler Design Practicals.md"
OUTPUT = SOURCE.with_suffix(".pdf")
PAGE_W, PAGE_H = 595.28, 841.89  # A4, PDF points
MARGIN = 48
CONTENT_W = PAGE_W - 2 * MARGIN
NAVY = (0.08, 0.15, 0.25)
BLUE = (0.10, 0.36, 0.65)
MUTED = (0.40, 0.46, 0.53)
INK = (0.14, 0.18, 0.23)
CODE_BG = (0.965, 0.973, 0.985)
CODE_BORDER = (0.85, 0.88, 0.92)

TOKEN_RE = re.compile(
    r'("(?:\\.|[^"\\])*"|\'(?:\\.|[^\'\\])*\'|//.*|/\*.*?\*/|'
    r'\b(?:alignas|alignof|and|asm|auto|bool|break|case|catch|char|class|'
    r'const|constexpr|continue|default|delete|do|double|else|enum|explicit|'
    r'extern|false|float|for|friend|if|inline|int|long|namespace|new|noexcept|'
    r'nullptr|operator|private|protected|public|return|short|signed|sizeof|'
    r'static|struct|switch|template|this|throw|true|try|typedef|typename|'
    r'union|unsigned|using|virtual|void|volatile|while|cout|cin|endl|std)\b|'
    r'\b\d+(?:\.\d+)?\b|#[A-Za-z_][^\n]*|\b[A-Z][A-Z0-9_]*\b)'
)
COLORS = {
    "kw": "#7040a0",
    "str": "#237a57",
    "comment": "#77818c",
    "num": "#b45518",
    "pp": "#9a3d55",
    "const": "#9a3d55",
    "plain": "#273445",
}
KEYWORDS = set(
    "alignas alignof and asm auto bool break case catch char class const constexpr "
    "continue default delete do double else enum explicit extern false float for "
    "friend if inline int long namespace new noexcept nullptr operator private "
    "protected public return short signed sizeof static struct switch template this "
    "throw true try typedef typename union unsigned using virtual void volatile while "
    "cout cin endl std".split()
)


def inline_markup(nodes):
    output = []
    for node in nodes:
        kind, value = node["t"], node.get("c", "")
        if kind == "Str":
            output.append(html.escape(value))
        elif kind in ("Space", "SoftBreak"):
            output.append(" ")
        elif kind == "LineBreak":
            output.append("<br/>")
        elif kind == "Strong":
            output.append("<b>" + inline_markup(value) + "</b>")
        elif kind == "Emph":
            output.append("<i>" + inline_markup(value) + "</i>")
        elif kind == "Code":
            output.append('<span foreground="#6941a5" font_family="monospace">'
                          + html.escape(value[1]) + "</span>")
        elif kind in ("Link", "Image"):
            output.append(inline_markup(value[1]))
        elif kind == "Span":
            output.append(inline_markup(value[1]))
        else:
            output.append(html.escape(str(value)) if isinstance(value, str) else "")
    return "".join(output)


def highlight(line, language):
    if language not in {"cpp", "c", "sh", "bash"}:
        return html.escape(line)
    pieces = []
    end = 0
    for match in TOKEN_RE.finditer(line):
        if match.start() > end:
            pieces.append('<span foreground="{}">{}</span>'.format(
                COLORS["plain"], html.escape(line[end:match.start()])))
        token = match.group(0)
        if token.startswith(("//", "/*")):
            color = COLORS["comment"]
        elif token.startswith(("\"", "'")):
            color = COLORS["str"]
        elif token.startswith("#"):
            color = COLORS["pp"]
        elif token[0].isdigit():
            color = COLORS["num"]
        elif token in KEYWORDS:
            color = COLORS["kw"]
        else:
            color = COLORS["const"]
        pieces.append('<span foreground="{}">{}</span>'.format(color, html.escape(token)))
        end = match.end()
    if end < len(line):
        pieces.append('<span foreground="{}">{}</span>'.format(
            COLORS["plain"], html.escape(line[end:])))
    return "".join(pieces) or " "


class PdfRenderer:
    def __init__(self, blocks):
        self.blocks = blocks
        self.pdf = cairo.PDFSurface(str(OUTPUT), PAGE_W, PAGE_H)
        self.pdf.set_metadata(cairo.PDF_METADATA_TITLE, "Compiler Design Practicals")
        self.pdf.set_metadata(cairo.PDF_METADATA_SUBJECT,
                              "Lex and C++ practicals with source code and sample output")
        self.ctx = cairo.Context(self.pdf)
        self.page = 0
        self.y = 0
        self.section = "Compiler Design Practicals"

    def layout(self, markup, font="DejaVu Sans 10", width=CONTENT_W):
        context = PangoCairo.create_context(self.ctx)
        PangoCairo.context_set_resolution(context, 72)
        layout = Pango.Layout.new(context)
        desc = Pango.FontDescription.from_string(font)
        layout.set_font_description(desc)
        layout.set_width(int(width * Pango.SCALE))
        layout.set_wrap(Pango.WrapMode.WORD_CHAR)
        layout.set_markup(markup, -1)
        return layout

    def show_text(self, markup, x, y, font="DejaVu Sans 10", width=CONTENT_W):
        layout = self.layout(markup, font, width)
        height = layout.get_pixel_size()[1]
        self.ctx.move_to(x, y)
        PangoCairo.show_layout(self.ctx, layout)
        return height

    def chrome(self):
        self.ctx.set_source_rgb(*NAVY)
        self.ctx.rectangle(0, 0, PAGE_W, 7)
        self.ctx.fill()
        self.ctx.set_source_rgb(*MUTED)
        self.show_text("COMPILER DESIGN  /  PRACTICALS", MARGIN, 27,
                       "DejaVu Sans Bold 8")
        self.ctx.set_source_rgb(*CODE_BORDER)
        self.ctx.set_line_width(0.6)
        self.ctx.move_to(MARGIN, 42)
        self.ctx.line_to(PAGE_W - MARGIN, 42)
        self.ctx.stroke()
        self.ctx.set_source_rgb(*MUTED)
        self.show_text(f"Compiler Design Practicals  •  {self.page}",
                       MARGIN, PAGE_H - 29, "DejaVu Sans 8")
        self.ctx.set_source_rgb(*CODE_BORDER)
        self.ctx.move_to(MARGIN, PAGE_H - 38)
        self.ctx.line_to(PAGE_W - MARGIN, PAGE_H - 38)
        self.ctx.stroke()

    def new_page(self):
        if self.page:
            self.pdf.show_page()
        self.page += 1
        self.chrome()
        self.y = 62

    def ensure(self, height):
        if self.y + height > PAGE_H - 55:
            self.new_page()

    def cover(self, headings):
        self.new_page()
        self.ctx.set_source_rgb(*BLUE)
        self.ctx.rectangle(MARGIN, 123, 5, 105)
        self.ctx.fill()
        self.ctx.set_source_rgb(*MUTED)
        self.show_text("LEX AND C++ LAB WORKBOOK", MARGIN + 23, 129,
                       "DejaVu Sans Bold 10")
        self.ctx.set_source_rgb(*NAVY)
        title = self.layout("Compiler Design\nPracticals", "DejaVu Sans Bold 30",
                            CONTENT_W - 30)
        self.ctx.set_source_rgb(*NAVY)
        self.ctx.move_to(MARGIN + 21, 158)
        PangoCairo.show_layout(self.ctx, title)
        self.ctx.set_source_rgb(*MUTED)
        self.show_text("Seven practicals with build commands, source code, and sample output.",
                       MARGIN + 22, 250, "DejaVu Sans 11")
        self.ctx.set_source_rgb(*CODE_BORDER)
        self.ctx.set_line_width(0.8)
        self.ctx.move_to(MARGIN + 22, 286)
        self.ctx.line_to(PAGE_W - MARGIN, 286)
        self.ctx.stroke()
        self.ctx.set_source_rgb(*BLUE)
        self.show_text("CONTENTS", MARGIN + 22, 309, "DejaVu Sans Bold 9")
        self.y = 335
        for heading in headings:
            title = inline_markup(heading["c"][2])
            self.ctx.set_source_rgb(*BLUE)
            self.show_text("•", MARGIN + 20, self.y - 1, "DejaVu Sans Bold 10")
            self.ctx.set_source_rgb(*INK)
            h = self.show_text(title, MARGIN + 40, self.y,
                               "DejaVu Sans 10", CONTENT_W - 55)
            self.y += max(h, 14) + 10

    def draw_heading(self, block):
        self.new_page()
        heading_markup = inline_markup(block["c"][2])
        self.ctx.set_source_rgb(*BLUE)
        self.ctx.rectangle(MARGIN, self.y, 4, 38)
        self.ctx.fill()
        self.ctx.set_source_rgb(*NAVY)
        height = self.show_text(heading_markup, MARGIN + 15, self.y + 3,
                                "DejaVu Sans Bold 17", CONTENT_W - 18)
        self.y += max(height, 29) + 20

    def draw_paragraph(self, block):
        markup = inline_markup(block["c"])
        layout = self.layout(markup, "DejaVu Sans 10")
        height = layout.get_pixel_size()[1]
        self.ensure(height + 15)
        self.ctx.set_source_rgb(*INK)
        self.ctx.move_to(MARGIN, self.y)
        PangoCairo.show_layout(self.ctx, layout)
        self.y += height + 12

    def draw_code(self, block):
        attr, source = block["c"]
        classes = attr[1]
        language = classes[0] if classes else "text"
        lines = source.rstrip("\n").split("\n") or [""]
        code_font = "DejaVu Sans Mono 7.7"
        gutter = 29 if language in {"cpp", "c"} else 13
        inner_w = CONTENT_W - 22 - gutter
        line_h = 11.2
        padding = 9
        self.ensure(2 * padding + line_h + 6)
        box_x = MARGIN
        box_w = CONTENT_W
        for number, line in enumerate(lines, 1):
            markup = highlight(line.expandtabs(4), language)
            layout = self.layout(markup, code_font, inner_w)
            row_h = max(line_h, layout.get_pixel_size()[1])
            if self.y + padding + row_h + padding > PAGE_H - 54:
                self.new_page()
            self.ctx.set_source_rgb(*CODE_BG)
            self.ctx.rectangle(box_x, self.y, box_w, row_h + 1)
            self.ctx.fill()
            if number == 1:
                self.ctx.set_source_rgb(*CODE_BORDER)
                self.ctx.set_line_width(0.6)
                self.ctx.move_to(box_x, self.y)
                self.ctx.line_to(box_x + box_w, self.y)
                self.ctx.stroke()
            if language in {"cpp", "c"}:
                self.ctx.set_source_rgb(0.56, 0.60, 0.66)
                self.show_text(str(number), box_x + 7, self.y + 1,
                               "DejaVu Sans Mono 7", gutter - 8)
            self.ctx.set_source_rgb(*INK)
            self.ctx.move_to(box_x + 11 + gutter, self.y + 1)
            PangoCairo.show_layout(self.ctx, layout)
            self.y += row_h + 1
        self.ctx.set_source_rgb(*CODE_BORDER)
        self.ctx.set_line_width(0.6)
        self.ctx.move_to(box_x, self.y)
        self.ctx.line_to(box_x + box_w, self.y)
        self.ctx.stroke()
        self.y += 15

    def render(self):
        headings = [b for b in self.blocks if b["t"] == "Header"]
        self.cover(headings)
        for block in self.blocks:
            kind = block["t"]
            if kind == "Header":
                self.draw_heading(block)
            elif kind in ("Para", "Plain"):
                self.draw_paragraph(block)
            elif kind == "CodeBlock":
                self.draw_code(block)
            elif kind == "HorizontalRule":
                self.ensure(14)
                self.ctx.set_source_rgb(*CODE_BORDER)
                self.ctx.set_line_width(0.6)
                self.ctx.move_to(MARGIN, self.y)
                self.ctx.line_to(PAGE_W - MARGIN, self.y)
                self.ctx.stroke()
                self.y += 15
        self.pdf.show_page()
        self.pdf.finish()


def main():
    ast = json.loads(subprocess.check_output(
        ["pandoc", str(SOURCE), "--from=markdown", "--to=json"], text=True))
    PdfRenderer(ast["blocks"]).render()
    print(f"Created {OUTPUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
