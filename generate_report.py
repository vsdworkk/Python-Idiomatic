from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.colors import HexColor, white
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, KeepTogether, CondPageBreak
)
from reportlab.platypus.flowables import Flowable
from reportlab.platypus.tableofcontents import TableOfContents
from reportlab.pdfbase import pdfmetrics
import os
import re

from report_design_system import (
    ChartLayoutSpec,
    ChartSpec,
    CoverSpec,
    KpiSpec,
    Lines,
    PageChromeSpec,
    PageSpec,
    Panel,
    Radii,
    Spacing,
    StoryRhythmSpec,
    VisualTextSpec,
    BAR_TRACK,
    BAR_TRACK_MUTED_GREEN,
    COMPARISON_NEUTRAL,
    COVER_MUTED_GREEN,
    FOGGED_EUCALYPTUS,
    FOGGED_GRAPHITE,
    KEY_FINDING_BACKGROUND,
    build_paragraph_styles,
    draw_wrapped_text,
    draw_panel_background,
    access_evidence_table_style,
    fit_text_size,
    make_visual_styles,
    register_fonts,
    DEWR_GREEN,
    DEWR_DARK_GREEN,
    DEWR_DARK_GREY,
    DEWR_NAVY,
    DEWR_TEAL,
    DEWR_GREY,
    DEWR_LIGHT_GREY,
    DEWR_LIME,
    OCE_PLUM,
    DEWR_RED,
    DEWR_OFF_WHITE,
    DEWR_SOFT_LINE,
    DEWR_TEXT_GREY,
    DEWR_MUTED_GREY,
)

REPORT_FONTS = register_fonts()
FONT_REGULAR = REPORT_FONTS.regular
FONT_BOLD = REPORT_FONTS.bold
FONT_ITALIC = REPORT_FONTS.italic
FONT_BOLD_ITALIC = REPORT_FONTS.bold_italic
PAGE_SPEC = PageSpec()
SPACING = Spacing()
LINES = Lines()
RADII = Radii()
CHART = ChartSpec()
VISUAL_TEXT = VisualTextSpec()
VISUAL_STYLES = make_visual_styles(REPORT_FONTS)
RHYTHM = StoryRhythmSpec()
PANEL_TOKENS = Panel()
KPI = KpiSpec()
CHART_LAYOUT = ChartLayoutSpec()
PAGE_CHROME = PageChromeSpec()
COVER = CoverSpec()

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "Outputs")
OUTPUT_PATH = os.path.join(OUTPUT_DIR, "DEWR_Public_AI_B.pdf")
COVER_LOCKUP_PATH = os.path.join(os.path.dirname(__file__), "assets", "dewr_cover_lockup_white.png")
TABLE_HEADER_RULE_GAP = 4
COPILOT_TIME_SAVINGS_NOTE_PAGE = 5
COPILOT_TIME_SAVINGS_FOOTER_NOTES = [
    "Note: The DTA reported these as task-level approximations, rather than a single overall average daily gain, the comparison is best interpreted as directional context rather than a direct benchmark.",
    "APSC 2025, APS Remuneration Data 31 December 2024, median non-SES total remuneration.",
]


def text_bottom_y(baseline_y, font_name, font_size):
    """Return the bottom of drawn text from its ReportLab baseline."""
    return baseline_y + pdfmetrics.getDescent(font_name, font_size)


class LinkedContentsDocTemplate(SimpleDocTemplate):
    """Document template that turns marked headings into TOC entries and PDF bookmarks."""

    def afterFlowable(self, flowable):
        if not hasattr(flowable, "_toc_text"):
            return
        key = flowable._bookmark_name
        self.canv.bookmarkPage(key)
        self.canv.addOutlineEntry(flowable._toc_text, key, flowable._toc_level, closed=False)
        self.notify("TOCEntry", (flowable._toc_level, flowable._toc_text, self.page, key))


class FooterNoteMarker(Flowable):
    """Invisible marker that registers a footer note for the page it lands on.

    Place these in the story where a note logically belongs. At draw time the
    marker records its current page in the class-level registry. The footer
    renderer then renders the appropriate notes at the bottom of each page.
    """

    _registry = {}  # page_number -> [note_texts]

    def __init__(self, text):
        Flowable.__init__(self)
        self.text = text
        self.width = 0
        self.height = 0

    def wrap(self, availWidth, availHeight):
        return (0, 0)

    def draw(self):
        page = self.canv.getPageNumber()
        notes = FooterNoteMarker._registry.setdefault(page, [])
        if self.text not in notes:
            notes.append(self.text)


os.makedirs(OUTPUT_DIR, exist_ok=True)


def visual_style(name, role, **overrides):
    parent = overrides.pop("parent", VISUAL_STYLES[role])
    return ParagraphStyle(name, parent=parent, **overrides)


def visual_title_style(name, **overrides):
    return visual_style(name, "visual_title", **overrides)


def marked_value(new, old, suffix=""):
    return f"{new}{suffix}"


def red_markup(text):
    return text


def callout_text_style(name, text_color=white):
    return visual_style(
        name,
        "card_body",
        fontName=FONT_BOLD,
        fontSize=VISUAL_TEXT.callout_text,
        leading=VISUAL_TEXT.callout_text_leading,
        textColor=text_color,
    )


def horizontal_callout_text_style(name):
    return visual_style(
        name,
        "card_body",
        fontSize=VISUAL_TEXT.horizontal_callout_text,
        leading=VISUAL_TEXT.horizontal_callout_text_leading,
        textColor=DEWR_DARK_GREY,
    )


def key_finding_style(name):
    return visual_style(
        name,
        "card_body",
        fontName=FONT_BOLD,
        fontSize=VISUAL_TEXT.key_finding,
        leading=VISUAL_TEXT.key_finding_leading,
        textColor=DEWR_DARK_GREY,
    )


def draw_delta_dot_plot(
    c,
    width,
    height,
    rows,
    high_label,
    low_label,
    decimal_places=0,
    delta_position="right",
):
    """Draw the shared two-series dot/delta plot used across the report."""
    pad = PANEL_TOKENS.inset_md
    label_w = width * (0.24 if delta_position == "midline" else 0.33)
    axis_x = pad + label_w
    delta_w = 56 if delta_position == "right" else 0
    axis_w = width - axis_x - delta_w - pad
    top_y = height - (52 if delta_position == "midline" else 44)
    row_gap = 30
    marker_y_offset = 3
    value_gap = 7

    def fmt(value):
        if decimal_places:
            return f"{value:.{decimal_places}f}%"
        return f"{round(value):.0f}%"

    def delta_fmt(high, low):
        delta = high - low
        if decimal_places:
            return f"+{delta:.{decimal_places}f} pts"
        return f"+{round(delta):.0f} pts"

    c.setFillColor(DEWR_DARK_GREY)
    c.setFont(FONT_BOLD, VISUAL_TEXT.panel_header_small)
    c.drawString(pad, height - 20, "MEASURE")

    c.setFont(FONT_REGULAR, VISUAL_TEXT.chart_legend_compact)
    legend_y = height - 19
    low_w = c.stringWidth(low_label, FONT_REGULAR, VISUAL_TEXT.chart_legend_compact)
    high_w = c.stringWidth(high_label, FONT_REGULAR, VISUAL_TEXT.chart_legend_compact)
    high_text_x = width - pad - high_w
    high_marker_x = high_text_x - 7
    low_text_x = high_marker_x - 18 - low_w
    low_marker_x = low_text_x - 7
    c.setFillColor(DEWR_DARK_GREEN)
    c.circle(high_marker_x, legend_y + 2, 3, fill=1, stroke=0)
    c.setFillColor(DEWR_DARK_GREY)
    c.drawString(high_text_x, legend_y - 1, high_label)
    c.circle(low_marker_x, legend_y + 2, 3, fill=1, stroke=0)
    c.drawString(low_text_x, legend_y - 1, low_label)

    def x_for(value):
        return axis_x + axis_w * value / 100

    for row_idx, row in enumerate(rows):
        label, high, low = row[:3]
        old_high = None
        old_low = None
        muted = False
        if len(row) >= 6:
            old_high, old_low, muted = row[3:6]
        elif len(row) == 5:
            old_high, old_low = row[3:5]
        elif len(row) == 4:
            muted = bool(row[3])
        high_color = FOGGED_EUCALYPTUS if muted else DEWR_DARK_GREEN
        low_color = FOGGED_GRAPHITE if muted else DEWR_DARK_GREY
        y = top_y - row_idx * row_gap
        c.setFillColor(DEWR_DARK_GREY)
        c.setFont(FONT_REGULAR, VISUAL_TEXT.table_label)
        c.drawString(pad, y, label)

        low_x = x_for(low)
        high_x = x_for(high)
        c.setStrokeColor(high_color)
        c.setLineWidth(1.0)
        c.line(low_x, y + marker_y_offset, high_x, y + marker_y_offset)

        c.setFillColor(low_color)
        c.circle(low_x, y + marker_y_offset, 3.2, fill=1, stroke=0)
        c.setFillColor(high_color)
        c.circle(high_x, y + marker_y_offset, 3.8, fill=1, stroke=0)

        low_text = marked_value(fmt(low), fmt(old_low)) if old_low is not None else fmt(low)
        high_text = marked_value(fmt(high), fmt(old_high)) if old_high is not None else fmt(high)
        c.setFont(FONT_BOLD, VISUAL_TEXT.table_value)
        c.setFillColor(low_color)
        c.drawRightString(low_x - value_gap, y - 1, low_text)
        c.setFillColor(high_color)
        c.drawString(high_x + value_gap, y - 1, high_text)
        c.setFillColor(high_color)
        if delta_position == "midline":
            c.drawCentredString((low_x + high_x) / 2, y + 12, delta_fmt(high, low))
        else:
            c.drawRightString(width - pad, y, delta_fmt(high, low))


class CalloutBox(Flowable):
    """A colored callout box with text."""
    def __init__(
        self,
        text,
        width,
        bg_color=DEWR_DARK_GREY,
        text_color=white,
        font_size=VISUAL_TEXT.callout_text,
        padding=PANEL_TOKENS.inset_sm,
    ):
        Flowable.__init__(self)
        self.text = text
        self.box_width = width
        self.bg_color = bg_color
        self.text_color = text_color
        self.font_size = font_size
        self.padding = padding
        self._height = None

    def wrap(self, availWidth, availHeight):
        self.box_width = availWidth
        style = callout_text_style("callout_measure", self.text_color)
        if self.font_size != VISUAL_TEXT.callout_text:
            style.fontSize = self.font_size
        p = Paragraph(self.text, style)
        w, h = p.wrap(self.box_width - 2 * self.padding, availHeight)
        self._height = h + 2 * self.padding
        return self.box_width, self._height

    def draw(self):
        c = self.canv
        c.saveState()
        c.setFillColor(self.bg_color)
        c.rect(0, 0, self.box_width, self._height, fill=1, stroke=0)
        style = callout_text_style("callout_draw", self.text_color)
        if self.font_size != VISUAL_TEXT.callout_text:
            style.fontSize = self.font_size
        draw_wrapped_text(
            c,
            self.text,
            style,
            self.padding,
            self._height - self.padding,
            self.box_width - 2 * self.padding,
            self._height,
        )
        c.restoreState()


class StatBox(Flowable):
    """A stat highlight box."""
    def __init__(self, stat, label, width, color=DEWR_NAVY):
        Flowable.__init__(self)
        self.stat = stat
        self.label = label
        self.box_width = width
        self.color = color

    def wrap(self, availWidth, availHeight):
        return self.box_width, KPI.stat_box_height

    def draw(self):
        self.canv.setFillColor(self.color)
        self.canv.roundRect(
            0,
            0,
            self.box_width,
            KPI.stat_box_height,
            KPI.stat_box_radius,
            fill=1,
            stroke=0,
        )
        self.canv.setFillColor(white)
        stat_size = VISUAL_TEXT.stat_value
        max_stat_width = self.box_width - 24
        while (
            stat_size > VISUAL_TEXT.stat_value_min
            and self.canv.stringWidth(self.stat, FONT_BOLD, stat_size) > max_stat_width
        ):
            stat_size -= 1
        self.canv.setFont(FONT_BOLD, stat_size)
        self.canv.drawString(12, 28, self.stat)
        self.canv.setFont(FONT_REGULAR, VISUAL_TEXT.stat_label)
        self.canv.drawString(12, 12, self.label)


class ComparisonCard(Flowable):
    """A clean comparison card: metric label on top, two values side-by-side.
    The 'highlight' value is shown in navy and visually emphasised; the 'compare'
    value is shown in muted grey for instant contrast."""
    def __init__(self, metric_label, highlight_value, highlight_label,
                 compare_value, compare_label, width,
                 highlight_color=DEWR_NAVY, compare_color=DEWR_GREY):
        Flowable.__init__(self)
        self.metric_label = metric_label
        self.h_value = highlight_value
        self.h_label = highlight_label
        self.c_value = compare_value
        self.c_label = compare_label
        self.box_width = width
        self.h_color = highlight_color
        self.c_color = compare_color
        self._height = 110

    def wrap(self, availWidth, availHeight):
        return self.box_width, self._height

    def draw(self):
        c = self.canv

        # Metric label (top) - drawn in uppercase, so measure uppercase width
        c.setFillColor(DEWR_DARK_GREY)
        label_font = FONT_BOLD
        label_size = VISUAL_TEXT.card_title
        c.setFont(label_font, label_size)
        words = self.metric_label.upper().split()
        inset = 6
        max_w = self.box_width - 2 * inset
        line1, line2 = "", ""
        for w in words:
            test = (line1 + " " + w).strip()
            if c.stringWidth(test, label_font, label_size) <= max_w:
                line1 = test
            else:
                test2 = (line2 + " " + w).strip()
                line2 = test2
        title_y = self._height - 20
        c.drawString(inset, title_y, line1)
        if line2:
            c.drawString(inset, title_y - 12, line2)

        # Divider
        c.setStrokeColor(DEWR_LIGHT_GREY)
        c.setLineWidth(LINES.fine)
        line_y = self._height - 43
        c.line(inset, line_y, self.box_width - inset, line_y)

        # Two halves
        half = self.box_width / 2
        # Highlight side (left)
        c.setFillColor(self.h_color)
        c.setFont(FONT_BOLD, VISUAL_TEXT.kpi_value_medium)
        c.drawCentredString(half / 2, 34, self.h_value)
        c.setFillColor(DEWR_DARK_GREY)
        c.setFont(FONT_REGULAR, VISUAL_TEXT.panel_header)
        c.drawCentredString(half / 2, 16, self.h_label)

        # Vertical divider
        c.setStrokeColor(DEWR_LIGHT_GREY)
        c.line(half, 14, half, line_y - 5)

        # Compare side (right)
        c.setFillColor(self.c_color)
        c.setFont(FONT_BOLD, VISUAL_TEXT.kpi_value_medium)
        c.drawCentredString(half + half / 2, 34, self.c_value)
        c.setFillColor(DEWR_DARK_GREY)
        c.setFont(FONT_REGULAR, VISUAL_TEXT.panel_header)
        c.drawCentredString(half + half / 2, 16, self.c_label)


class ValueSignalsPanel(Flowable):
    """Full-width grey evidence panel with headline value signals."""
    def __init__(self, width, items, title=None, primary_count=None):
        Flowable.__init__(self)
        self.box_width = width
        self.items = items
        self.title = title
        self.primary_count = len(items) if primary_count is None else primary_count
        self._height = 88 if title else 74

    def wrap(self, availWidth, availHeight):
        self.box_width = availWidth
        return self.box_width, self._height

    def draw(self):
        c = self.canv
        c.saveState()
        w = self.box_width
        h = self._height
        pad = PANEL_TOKENS.inset_md

        draw_panel_background(c, 0, 0, w, h, stroke_width=0, radius=0)

        top_offset = 20 if self.title else 0
        if self.title:
            c.setFillColor(DEWR_DARK_GREY)
            c.setFont(FONT_BOLD, VISUAL_TEXT.visual_title)
            c.drawString(pad, h - 20, self.title)

        col_w = (w - 2 * pad) / len(self.items)
        value_y = h - (34 if not self.title else 46)
        label_top_y = value_y - 10.5
        for i, (value, label) in enumerate(self.items):
            x = pad + i * col_w
            cx = x + col_w / 2
            value_color = DEWR_RED if "(" in value else (DEWR_GREEN if i < self.primary_count else DEWR_DARK_GREY)
            c.setFillColor(value_color)
            value_size = VISUAL_TEXT.kpi_value_medium if len(value) <= 8 else VISUAL_TEXT.kpi_value_compact
            c.setFont(FONT_BOLD, value_size)
            c.drawCentredString(cx, value_y, value)
            label_style = visual_style(
                "value_signal_label",
                "kpi_caption",
                alignment=TA_CENTER,
                textColor=DEWR_DARK_GREY,
            )
            draw_wrapped_text(c, label, label_style, x + 7, label_top_y, col_w - 14, 41)
        c.restoreState()


class CalloutSignalsPanel(Flowable):
    """Graphite takeaway callout with embedded KPI evidence strip."""
    def __init__(self, text, width, items, primary_count=None, bg_color=DEWR_DARK_GREY, note=None):
        Flowable.__init__(self)
        self.text = text
        self.box_width = width
        self.items = items
        self.primary_count = len(items) if primary_count is None else primary_count
        self.bg_color = bg_color
        self.note = note
        self.padding = PANEL_TOKENS.inset_sm
        self.card_height = KPI.panel_height + (15 if note else 0)
        self.gap = 0
        self._height = None
        self._text_height = None

    def wrap(self, availWidth, availHeight):
        self.box_width = availWidth
        style = callout_text_style("callout_signals_measure")
        p = Paragraph(self.text, style)
        _, self._text_height = p.wrap(self.box_width - 2 * self.padding, availHeight)
        self._height = self._text_height + self.card_height + self.gap + 2 * self.padding
        return self.box_width, self._height

    def draw(self):
        c = self.canv
        c.saveState()
        w = self.box_width
        h = self._height
        pad = self.padding

        c.setFillColor(DEWR_OFF_WHITE)
        c.rect(0, 0, w, self.card_height, fill=1, stroke=0)
        c.setFillColor(self.bg_color)
        c.rect(0, self.card_height, w, h - self.card_height, fill=1, stroke=0)

        draw_wrapped_text(
            c,
            self.text,
            callout_text_style("callout_signals_draw"),
            pad,
            h - pad,
            w - 2 * pad,
            self._text_height,
        )

        card_x = 0
        card_y = 0
        card_w = w
        card_h = self.card_height

        inner_pad = PANEL_TOKENS.inset_sm
        col_w = (card_w - 2 * pad) / len(self.items)
        if self.note:
            c.setFillColor(DEWR_TEXT_GREY)
            c.setFont(FONT_BOLD, VISUAL_TEXT.note)
            c.drawString(card_x + pad, card_y + card_h - 17, self.note)
        value_y = card_y + 41
        label_top_y = card_y + 27
        for i, (value, label) in enumerate(self.items):
            x = card_x + pad + i * col_w
            cx = x + col_w / 2
            if i:
                c.setStrokeColor(DEWR_LIGHT_GREY)
                c.setLineWidth(LINES.fine)
                c.line(x, card_y + 11, x, card_y + card_h - (27 if self.note else 11))
            c.setFillColor(DEWR_RED if "(" in value else (DEWR_GREEN if i < self.primary_count else DEWR_DARK_GREY))
            value_size = VISUAL_TEXT.kpi_value_medium if len(value) <= 8 else VISUAL_TEXT.kpi_value_compact
            c.setFont(FONT_BOLD, value_size)
            c.drawCentredString(cx, value_y, value)
            label_style = visual_style(
                "callout_signal_label",
                "kpi_caption",
                alignment=TA_CENTER,
                textColor=DEWR_DARK_GREY,
            )
            draw_wrapped_text(c, label, label_style, x + 7, label_top_y, col_w - 14, 28)
        c.restoreState()


class TimeSavingsPanel(Flowable):
    """Hero comparison panel for reported Copilot time savings."""
    def __init__(self, width):
        Flowable.__init__(self)
        self.box_width = width
        self._height = 104

    def wrap(self, availWidth, availHeight):
        self.box_width = availWidth
        return self.box_width, self._height

    def draw(self):
        c = self.canv
        c.saveState()
        w = self.box_width
        h = self._height
        pad = PANEL_TOKENS.inset_md

        draw_panel_background(c, 0, 0, w, h, stroke_width=0, radius=0)

        label_w = w * 0.24
        bar_x = pad + label_w
        bar_w = w - bar_x - 150
        bar_h = CHART_LAYOUT.bar_height_medium
        max_value = 75
        rows = [
            ("M365 Copilot", 67.9, marked_value("68", "69", " minutes per day"), "5.7 hours per week", DEWR_DARK_GREEN),
            ("Copilot Chat", 33.5, marked_value("34", "34", " minutes per day"), "2.8 hours per week", DEWR_DARK_GREY),
        ]
        for i, (label, value, daily_label, weekly, color) in enumerate(rows):
            y = h - 41 - i * 35
            c.setFillColor(DEWR_DARK_GREY)
            c.setFont(FONT_BOLD, VISUAL_TEXT.time_savings_label)
            c.drawString(pad, y + 1, label)

            c.setFillColor(color)
            c.rect(bar_x, y, bar_w * (value / max_value), bar_h, fill=1, stroke=0)
            c.setFillColor(color)
            c.setFont(FONT_BOLD, VISUAL_TEXT.time_savings_value)
            c.drawRightString(w - pad, y + 2, weekly)
            c.setFillColor(DEWR_RED if "(" in daily_label else DEWR_DARK_GREY)
            context_size = VISUAL_TEXT.time_savings_context - 0.3 if "(" in daily_label else VISUAL_TEXT.time_savings_context
            c.setFont(FONT_REGULAR, context_size)
            c.drawRightString(w - pad, y - 12, daily_label)
        c.restoreState()


class M365ValueAndReachTable(Flowable):
    """Single-section matrix showing Copilot value and M365 reach."""
    def __init__(self, width, section_title, rows):
        Flowable.__init__(self)
        self.box_width = width
        self.section_title = section_title
        self.rows = rows
        self.columns = ["M365 Copilot", "Copilot Chat", "M365 Value", "M365 Licence"]
        self.row_h = PANEL_TOKENS.row_h_matrix + SPACING.xs
        self.pad = PANEL_TOKENS.inset_lg
        self._height = 2 * self.pad + 40 + self.row_h * len(rows)

    def wrap(self, availWidth, availHeight):
        self.box_width = availWidth
        return self.box_width, self._height

    def _draw_centered(self, c, text, x, y, font, size, color, max_width):
        c.setFillColor(color)
        fitted = fit_text_size(c, text, font, size, max_width, min_size=5.8)
        c.setFont(font, fitted)
        c.drawCentredString(x, y, text)

    def draw(self):
        c = self.canv
        c.saveState()
        w = self.box_width
        h = self._height
        pad = self.pad

        draw_panel_background(c, 0, 0, w, h, stroke_width=0, radius=0)

        first_w = (w - 2 * pad) * 0.35
        col_w = (w - 2 * pad - first_w) / 4
        title_y = h - pad - 4
        header_y = title_y - 18
        subheader_y = header_y - 12
        subheader_size = VISUAL_TEXT.note - 1
        rule_y = text_bottom_y(subheader_y, FONT_ITALIC, subheader_size) - TABLE_HEADER_RULE_GAP

        c.setFillColor(DEWR_TEXT_GREY)
        c.setFont(FONT_BOLD, VISUAL_TEXT.visual_title)
        c.drawString(pad, title_y, self.section_title)

        for idx, col in enumerate(self.columns):
            cx = pad + first_w + col_w * idx + col_w / 2
            self._draw_centered(
                c,
                col.upper(),
                cx,
                header_y,
                FONT_BOLD,
                VISUAL_TEXT.column_header,
                DEWR_TEXT_GREY,
                col_w - 6,
            )

        self._draw_centered(
            c,
            "Average weekly hours saved per user",
            pad + first_w + col_w,
            subheader_y,
            FONT_ITALIC,
            subheader_size,
            DEWR_TEXT_GREY,
            2 * col_w - 6,
        )

        c.setStrokeColor(DEWR_LIGHT_GREY)
        c.setLineWidth(LINES.fine)
        c.line(pad, rule_y, w - pad, rule_y)

        label_style = visual_style(
            "value_reach_label",
            "table_label",
            fontName=FONT_REGULAR,
            fontSize=VISUAL_TEXT.value_reach_label,
            leading=VISUAL_TEXT.value_reach_label_leading,
            textColor=DEWR_DARK_GREY,
        )
        label_style_bold = visual_style(
            "value_reach_label_bold",
            "table_label",
            parent=label_style,
            textColor=DEWR_DARK_GREEN,
        )

        for row_idx, (label, m365, chat, multiplier, coverage, emphasis) in enumerate(self.rows):
            row_top = rule_y - self.row_h * row_idx
            row_bottom = row_top - self.row_h
            baseline = row_bottom + 8

            p = Paragraph(label, label_style_bold if emphasis else label_style)
            _, label_h = p.wrap(first_w - 8, self.row_h - 4)
            p.drawOn(c, pad, row_bottom + (self.row_h - label_h) / 2)

            values = [
                (m365, FONT_BOLD, DEWR_DARK_GREY, VISUAL_TEXT.value_reach_value),
                (chat, FONT_BOLD, DEWR_DARK_GREY, VISUAL_TEXT.value_reach_value),
                (multiplier, FONT_BOLD, DEWR_DARK_GREEN, VISUAL_TEXT.value_reach_value),
                (coverage, FONT_BOLD, DEWR_DARK_GREY, VISUAL_TEXT.value_reach_value),
            ]
            for idx, (value, font, color, size) in enumerate(values):
                cx = pad + first_w + col_w * idx + col_w / 2
                self._draw_centered(c, value, cx, baseline, font, size, color, col_w - 8)
        c.restoreState()


class M365ValueReachExhibit(Flowable):
    """Separate editorial sub-tables for distinct workforce cuts."""
    def __init__(self, width, sections, show_section_titles=True):
        Flowable.__init__(self)
        self.box_width = width
        self.sections = sections
        self.show_section_titles = show_section_titles
        self.pad = PANEL_TOKENS.inset_lg
        self.row_h = 24
        self.section_gap = 24
        self.header_h = PANEL_TOKENS.header_h_tall if show_section_titles else PANEL_TOKENS.header_h_default
        total_rows = sum(len(rows) for _, rows in sections)
        self._height = sum(self.header_h + self.row_h * len(rows) + 11 for _, rows in sections) + self.section_gap * (len(sections) - 1) + 10

    def wrap(self, availWidth, availHeight):
        self.box_width = availWidth
        return self.box_width, self._height

    def draw(self):
        c = self.canv
        c.saveState()
        w = self.box_width
        h = self._height
        pad = self.pad

        table_w = w - 2 * pad
        col_ws = [
            table_w * 0.38,
            table_w * 0.16,
            table_w * 0.16,
            table_w * 0.16,
            table_w * 0.14,
        ]
        col_x = [pad]
        for col_w in col_ws[:-1]:
            col_x.append(col_x[-1] + col_w)

        headers = ["M365 COPILOT", "COPILOT CHAT", "M365 VALUE", "M365 LICENCE"]

        y = h - 8
        label_style = visual_style(
            "value_reach_exhibit_label",
            "table_label",
            fontName=FONT_REGULAR,
            fontSize=VISUAL_TEXT.value_reach_label,
            leading=VISUAL_TEXT.value_reach_label_leading,
            textColor=DEWR_DARK_GREY,
        )

        for section_idx, (section_title, rows) in enumerate(self.sections):
            block_top = y
            block_bottom = block_top - self.header_h - self.row_h * len(rows) - 11
            if self.show_section_titles:
                c.setFillColor(DEWR_TEXT_GREY)
                c.setFont(FONT_BOLD, VISUAL_TEXT.column_header)
                c.drawString(0, block_top - 8, section_title)

            table_top = block_top - (14 if self.show_section_titles else 0)
            table_h = self.header_h + self.row_h * len(rows) + 11
            draw_panel_background(c, 0, table_top - table_h, w, table_h, stroke_width=0, radius=0)

            header_y = table_top - 18
            c.setFillColor(DEWR_DARK_GREY)
            c.setFont(FONT_BOLD, VISUAL_TEXT.panel_header_small)
            c.drawString(pad, header_y, section_title if not self.show_section_titles else "SEGMENT")
            for idx, header in enumerate(headers, start=1):
                cx = col_x[idx] + col_ws[idx] / 2
                c.drawCentredString(cx, header_y, header)
            c.setFont(FONT_ITALIC, VISUAL_TEXT.note - 1)
            c.setFillColor(DEWR_TEXT_GREY)
            subheader_y = header_y - 12
            c.drawCentredString(col_x[1] + (col_ws[1] + col_ws[2]) / 2, subheader_y, "Average weekly hours saved per user")
            rule_y = text_bottom_y(subheader_y, FONT_ITALIC, VISUAL_TEXT.note - 1) - TABLE_HEADER_RULE_GAP
            c.setStrokeColor(DEWR_LIGHT_GREY)
            c.setLineWidth(LINES.fine)
            c.line(pad, rule_y, w - pad, rule_y)

            y = header_y - 42

            for row_idx, (label, m365, chat, multiplier, coverage, emphasis) in enumerate(rows):
                row_mid = y + 9
                p = Paragraph(label, label_style)
                _, label_h = p.wrap(col_ws[0] - 10, self.row_h - 2)
                p.drawOn(c, pad, row_mid - label_h / 2)

                row_values = [
                    (m365, DEWR_DARK_GREY, VISUAL_TEXT.value_reach_value),
                    (chat, DEWR_DARK_GREY, VISUAL_TEXT.value_reach_value),
                    (multiplier, DEWR_DARK_GREEN, VISUAL_TEXT.value_reach_value + 1),
                    (coverage, DEWR_DARK_GREY, VISUAL_TEXT.value_reach_value),
                ]
                for idx, (text, color, size) in enumerate(row_values, start=1):
                    c.setFillColor(color)
                    c.setFont(FONT_BOLD, size)
                    c.drawCentredString(col_x[idx] + col_ws[idx] / 2, row_mid - 4, text)

                y -= self.row_h

            y = block_bottom - self.section_gap

        c.restoreState()


class CopilotEngagementDeltaPanel(Flowable):
    """Engagement comparison by Copilot version."""
    def __init__(self, width):
        Flowable.__init__(self)
        self.box_width = width
        self.rows = [
            ("Rated at least very useful", 68, 35, 67, 37),
            ("Used at least weekly", 81, 55, 80, 56),
            ("Used at least daily", 65, 25, 63, 27),
        ]
        self._height = 126

    def wrap(self, availWidth, availHeight):
        self.box_width = availWidth
        return self.box_width, self._height

    def draw(self):
        c = self.canv
        c.saveState()
        w = self.box_width
        h = self._height

        draw_panel_background(c, 0, 0, w, h, stroke_width=0, radius=0)
        draw_delta_dot_plot(c, w, h, self.rows, "M365 Copilot", "Copilot Chat", delta_position="right")
        c.restoreState()


class EvidenceMatrixPanel(Flowable):
    """Compact grey matrix for comparing metrics across groups or tools."""
    def __init__(
        self,
        width,
        title,
        columns,
        rows,
        first_col_ratio=0.42,
        first_header=None,
        visual_title_text=None,
        row_h=24,
        header_body_gap=0,
    ):
        Flowable.__init__(self)
        self.box_width = width
        self.title = visual_title_text
        self.first_header = first_header or title
        self.columns = columns
        self.rows = rows
        self.first_col_ratio = first_col_ratio
        self.row_h = row_h
        self.header_body_gap = header_body_gap
        if self.title:
            self.header_h = PANEL_TOKENS.header_h_tall
        else:
            self.header_h = PANEL_TOKENS.header_h_default
        self._height = self.header_h + self.row_h * len(rows) + 6

    def wrap(self, availWidth, availHeight):
        self.box_width = availWidth
        return self.box_width, self._height

    def draw(self):
        c = self.canv
        c.saveState()
        w = self.box_width
        h = self._height
        pad = PANEL_TOKENS.inset_lg

        draw_panel_background(c, 0, 0, w, h, stroke_width=0, radius=0)

        table_w = w - 2 * pad
        first_w = table_w * self.first_col_ratio
        data_x = pad + first_w
        data_w = table_w - first_w
        col_w = data_w / len(self.columns)
        if self.title:
            title_y = h - 18
            header_y = h - 38

            c.setFillColor(DEWR_DARK_GREY)
            c.setFont(FONT_BOLD, VISUAL_TEXT.visual_title)
            c.drawString(pad, title_y, self.title)
        else:
            header_y = h - 18

        column_header_style = visual_style(
            "matrix_column_header",
            "table_header",
            alignment=TA_CENTER,
            textColor=DEWR_DARK_GREY,
        )
        first_header_style = visual_style(
            "matrix_first_header",
            "table_header",
            textColor=DEWR_DARK_GREY,
        )
        first_header = Paragraph(self.first_header.upper(), first_header_style)
        _, first_header_h = first_header.wrap(first_w - 10, 24)
        header_bottoms = [header_y - first_header_h / 2]
        first_header.drawOn(c, pad, header_bottoms[0])
        for i, col in enumerate(self.columns):
            header_text = col.replace("<br/>", "\n").upper().replace("\n", "<br/>")
            p = Paragraph(header_text, column_header_style)
            _, ph = p.wrap(col_w - 6, 26)
            header_bottom = header_y - ph / 2
            header_bottoms.append(header_bottom)
            p.drawOn(c, data_x + i * col_w + 3, header_bottom)

        rule_y = min(header_bottoms) - TABLE_HEADER_RULE_GAP
        first_row_y = rule_y - 26 - self.header_body_gap

        c.setStrokeColor(DEWR_LIGHT_GREY)
        c.setLineWidth(LINES.fine)
        c.line(pad, rule_y, w - pad, rule_y)

        for r_idx, row in enumerate(self.rows):
            label, values, highlight_idx = row
            row_top = first_row_y - r_idx * self.row_h
            row_mid = row_top + self.row_h / 2 - 3

            if values is None:
                c.setFillColor(DEWR_DARK_GREY)
                c.setFont(FONT_BOLD, VISUAL_TEXT.table_header)
                c.drawString(pad, row_mid - 4, label)
                continue

            p = Paragraph(label, visual_style(
                "matrix_label",
                "table_label",
                textColor=DEWR_DARK_GREY,
            ))
            _, label_h = p.wrap(first_w - 10, self.row_h - 2)
            p.drawOn(c, pad, row_mid - label_h / 2)

            c.setFont(FONT_BOLD, VISUAL_TEXT.table_value)
            for i, value in enumerate(values):
                highlighted = (
                    highlight_idx == "all"
                    or (isinstance(highlight_idx, (list, tuple, set)) and i in highlight_idx)
                    or i == highlight_idx
                )
                c.setFillColor(DEWR_RED if "(" in value else (DEWR_DARK_GREEN if highlighted else DEWR_DARK_GREY))
                c.drawCentredString(data_x + i * col_w + col_w / 2, row_mid - 4, value)
        c.restoreState()


class ContinuationDemandPanel(Flowable):
    """Continuation demand summary for public generative AI."""
    def __init__(self, width):
        Flowable.__init__(self)
        self.box_width = width
        self._height = 106
        self.tools = [
            ("Claude", 63, DEWR_DARK_GREEN),
            ("ChatGPT", 54, DEWR_DARK_GREY),
            ("Gemini", 43, DEWR_MUTED_GREY),
        ]

    def wrap(self, availWidth, availHeight):
        self.box_width = availWidth
        return self.box_width, self._height

    def draw(self):
        c = self.canv
        c.saveState()
        w = self.box_width
        h = self._height
        pad = PANEL_TOKENS.inset_lg

        draw_panel_background(c, 0, 0, w, h, stroke_width=0, radius=0)

        chart_top = h - 29
        label_x = pad
        bar_x = pad + 96
        bar_w = w - bar_x - pad - 142
        value_x = bar_x + bar_w + 12
        gap_x = value_x + 36
        bar_h = 9
        row_gap = 25
        max_value = 70
        leader_value = self.tools[0][1]

        for idx, (tool, value, color) in enumerate(self.tools):
            y = chart_top - idx * row_gap
            filled_w = bar_w * value / max_value

            c.setFillColor(DEWR_DARK_GREY)
            c.setFont(FONT_BOLD if idx == 0 else FONT_REGULAR, VISUAL_TEXT.table_label)
            c.drawString(label_x, y - 3, tool)

            c.setFillColor(color)
            c.rect(bar_x, y - bar_h / 2, filled_w, bar_h, fill=1, stroke=0)

            c.setFillColor(color if idx == 0 else DEWR_DARK_GREY)
            c.setFont(FONT_BOLD, VISUAL_TEXT.table_value)
            c.drawString(value_x, y - 4, f"{value}%")

            if idx:
                c.setFillColor(DEWR_TEXT_GREY)
                c.setFont(FONT_BOLD, VISUAL_TEXT.note)
                c.drawString(gap_x, y - 3, f"-{leader_value - value} pp vs Claude")

        c.restoreState()


class MarginalValuePanel(Flowable):
    """Compact two-part panel for public-tool marginal value signals."""
    def __init__(self, width):
        Flowable.__init__(self)
        self.box_width = width
        self._height = 122

    def wrap(self, availWidth, availHeight):
        self.box_width = availWidth
        return self.box_width, self._height

    def draw(self):
        c = self.canv
        c.saveState()
        w = self.box_width
        h = self._height
        pad = PANEL_TOKENS.inset_md

        draw_panel_background(c, 0, 0, w, h, stroke_width=0, radius=0)
        c.setStrokeColor(DEWR_LIGHT_GREY)
        c.setLineWidth(LINES.fine)
        c.line(pad, h / 2, w - pad, h / 2)

        c.setFillColor(DEWR_DARK_GREY)
        c.setFont(FONT_BOLD, VISUAL_TEXT.panel_header)
        c.drawString(pad, h - 20, "ACCESS EFFECT")
        c.drawString(pad, h / 2 - 17, "TOOL EFFECT")

        metric_x = pad
        chat_x = w * 0.55
        m365_x = w * 0.78

        c.setFont(FONT_BOLD, VISUAL_TEXT.chart_value_label)
        c.drawCentredString(chat_x, h - 20, "COPILOT CHAT")
        c.drawCentredString(m365_x, h - 20, "M365 COPILOT")

        for y, metric, chat_value, m365_value, highlight_idx in [
            (h - 43, "Added value beyond Copilot", "75.0%", "82.1%", 0),
            (h - 61, "Used weekly+", "54.5%", "50.0%", None),
        ]:
            c.setFillColor(DEWR_DARK_GREY)
            c.setFont(FONT_REGULAR, VISUAL_TEXT.micro_label)
            c.drawString(metric_x, y, metric)
            c.setFont(FONT_BOLD, VISUAL_TEXT.micro_label)
            c.setFillColor(DEWR_DARK_GREEN)
            c.drawCentredString(chat_x, y, chat_value)
            c.setFillColor(DEWR_DARK_GREEN)
            c.drawCentredString(m365_x, y, m365_value)

        c.setFont(FONT_BOLD, VISUAL_TEXT.chart_value_label)
        c.setFillColor(DEWR_DARK_GREY)
        c.drawCentredString(chat_x, h / 2 - 17, "COPILOT CHAT")
        c.drawCentredString(m365_x, h / 2 - 17, "M365 COPILOT")

        c.setFont(FONT_REGULAR, VISUAL_TEXT.micro_label)
        c.drawString(metric_x, h / 2 - 40, "Strongest tool signal")
        c.setFont(FONT_BOLD, VISUAL_TEXT.micro_value)
        c.setFillColor(DEWR_DARK_GREEN)
        c.drawCentredString(chat_x, h / 2 - 41, "47%")
        c.drawCentredString(m365_x, h / 2 - 41, "44%")
        c.setFont(FONT_REGULAR, VISUAL_TEXT.kpi_caption)
        c.setFillColor(DEWR_DARK_GREY)
        c.drawCentredString(chat_x, h / 2 - 56, "ChatGPT")
        c.drawCentredString(m365_x, h / 2 - 56, "Claude")
        c.restoreState()


class TwoEvidenceCardsPanel(Flowable):
    """Concise proof-point cards for executive evidence."""
    def __init__(self, width, cards):
        Flowable.__init__(self)
        self.box_width = width
        self.cards = cards
        self._height = 104

    def wrap(self, availWidth, availHeight):
        self.box_width = availWidth
        return self.box_width, self._height

    def draw(self):
        c = self.canv
        c.saveState()
        w = self.box_width
        h = self._height
        gap = PANEL_TOKENS.gutter
        card_count = len(self.cards)
        card_w = (w - gap * (card_count - 1)) / card_count

        label_style = visual_style(
            "evidence_card_label",
            "card_body",
            textColor=DEWR_DARK_GREY,
            alignment=TA_CENTER,
        )
        vs_style = visual_style(
            "evidence_card_vs",
            "card_body",
            fontName=FONT_BOLD,
            textColor=DEWR_DARK_GREY,
            alignment=TA_CENTER,
        )

        for idx, card in enumerate(self.cards):
            x = idx * (card_w + gap)
            draw_panel_background(c, x, 0, card_w, h, stroke_width=0, radius=0)

            c.setFillColor(DEWR_DARK_GREY)
            c.setFont(FONT_BOLD, VISUAL_TEXT.panel_header_small)
            c.drawCentredString(x + card_w / 2, h - 18, card["metric"].upper())
            c.setStrokeColor(DEWR_LIGHT_GREY)
            c.setLineWidth(LINES.fine)
            c.line(x + PANEL_TOKENS.divider_inset, h - 30, x + card_w - PANEL_TOKENS.divider_inset, h - 30)

            c.setFillColor(DEWR_DARK_GREEN)
            c.setFont(FONT_BOLD, VISUAL_TEXT.kpi_value)
            c.drawCentredString(x + card_w / 2, h - 56, card["value"])

            label = Paragraph(card["label"], label_style)
            label.wrap(card_w - 34, 24)
            label.drawOn(c, x + 17, h - 80)

            vs = Paragraph(card["comparison"], vs_style)
            vs.wrap(card_w - 34, 18)
            vs.drawOn(c, x + 17, 9)
        c.restoreState()


class HorizontalEvidenceCallout(Flowable):
    """Full-width callout with a large value and concise supporting sentence."""
    def __init__(self, width, metric, value, text, comparison):
        Flowable.__init__(self)
        self.box_width = width
        self.value = value
        self.text = text
        self.comparison = comparison
        self._height = 58

    def wrap(self, availWidth, availHeight):
        self.box_width = availWidth
        return self.box_width, self._height

    def draw(self):
        c = self.canv
        c.saveState()
        w = self.box_width
        h = self._height
        pad = PANEL_TOKENS.inset_md + SPACING.xs
        value_w = 92

        draw_panel_background(c, 0, 0, w, h, stroke_width=0, radius=0)

        c.setFillColor(DEWR_DARK_GREEN)
        c.setFont(FONT_BOLD, VISUAL_TEXT.kpi_value_medium)
        c.drawCentredString(value_w / 2 + 4, 22, self.value)

        c.setStrokeColor(DEWR_LIGHT_GREY)
        c.setLineWidth(LINES.regular)
        c.line(value_w + 8, 16, value_w + 8, h - 16)

        text_style = horizontal_callout_text_style("horizontal_callout_text")
        text = Paragraph(f"{self.text} <b>{self.comparison}</b>", text_style)
        _, text_h = text.wrap(w - value_w - pad * 2, 34)
        text.drawOn(c, value_w + pad, (h - text_h) / 2)
        c.restoreState()


class PublicAIUsefulnessVisual(Flowable):
    """
    Two-column bar comparison showing which tool each access group rated more useful.
    """

    def __init__(self, width=None):
        Flowable.__init__(self)
        self.box_width = width
        self.box_height = 94

    def wrap(self, availWidth, availHeight):
        if self.box_width is None:
            self.box_width = availWidth
        return self.box_width, self.box_height

    def _para(self, text, x, y_top, width, size=7, leading=None,
              font=FONT_REGULAR, color=DEWR_DARK_GREY, bold=False):
        role = "card_title" if bold else "card_body"
        style = visual_style(
            "tmp",
            role,
            fontName=FONT_BOLD if bold else font,
            fontSize=size,
            leading=leading or size + 2,
            textColor=color,
        )
        draw_wrapped_text(self.canv, text, style, x, y_top, width, 1000)

    def draw(self):
        c = self.canv
        c.saveState()
        w = self.box_width
        h = self.box_height

        draw_panel_background(
            c,
            0.75,
            0.75,
            w - 1.5,
            h - 1.5,
            radius=RADII.lg,
            stroke_width=LINES.hairline,
        )

        pad = PANEL_TOKENS.inset_xxl
        inner_w = w - 2 * pad
        gap = 28
        col_w = (inner_w - gap) / 2
        left_x = pad
        right_x = pad + col_w + gap
        divider_x = pad + col_w + gap / 2

        # Column divider
        c.setStrokeColor(DEWR_SOFT_LINE)
        c.setLineWidth(LINES.regular)
        c.line(divider_x, 10, divider_x, h - 10)

        def draw_group(x, title, rows):
            title_y = h - 14
            label_w = 50
            bar_x = x + label_w + 10
            value_gap = 6
            bar_w = col_w - label_w - 48
            bar_h = CHART_LAYOUT.bar_height_medium + 1
            max_value = 100

            c.setFillColor(DEWR_DARK_GREY)
            c.setFont(FONT_BOLD, VISUAL_TEXT.stat_label)
            title_para = Paragraph(title, visual_style(
                "usefulness_group_title",
                "card_title",
                fontSize=VISUAL_TEXT.usefulness_title,
                leading=VISUAL_TEXT.usefulness_title_leading,
                textColor=DEWR_DARK_GREY,
            ))
            title_para.wrap(col_w - 8, 22)
            title_para.drawOn(c, x, title_y - 12)

            for i, (label, value, display_value, color) in enumerate(rows):
                y = title_y - 32 - i * 21
                c.setFillColor(DEWR_DARK_GREY)
                c.setFont(FONT_REGULAR, VISUAL_TEXT.card_body)
                c.drawString(x, y + 2, label)
                c.setFillColor(color)
                c.rect(bar_x, y, bar_w * value / max_value, bar_h, fill=1, stroke=0)
                c.setFillColor(DEWR_DARK_GREEN)
                c.setFont(FONT_BOLD, VISUAL_TEXT.usefulness_value)
                c.drawString(bar_x + bar_w * value / max_value + value_gap, y + 2, display_value)

        comparison_grey = COMPARISON_NEUTRAL
        draw_group(
            left_x,
            "Copilot Chat",
            [
                ("Public Generative AI", 81.8, "81.8% (82.4%)", DEWR_DARK_GREEN),
                ("Copilot", 69.7, "69.7%", comparison_grey),
            ],
        )
        draw_group(
            right_x,
            "M365 Copilot",
            [
                ("Copilot", 92.9, "92.9%", DEWR_DARK_GREY),
                ("Public Generative AI", 78.6, "78.6% (77.8%)", comparison_grey),
            ],
        )
        c.restoreState()


class PriorExperienceComparisonPanel(Flowable):
    """Three-column comparison panel for prior Gen AI experience groups."""
    def __init__(self, width):
        Flowable.__init__(self)
        self.box_width = width
        self._height = 96

    def wrap(self, availWidth, availHeight):
        self.box_width = availWidth
        return self.box_width, self._height

    def draw(self):
        c = self.canv
        c.saveState()
        w = self.box_width
        h = self._height
        pad = PANEL_TOKENS.inset_md
        inner_top = h - 14
        col_w = (w - 2 * pad) / 3

        draw_panel_background(c, 0, 0, w, h, stroke_width=0, radius=0)

        c.setStrokeColor(DEWR_LIGHT_GREY)
        c.setLineWidth(LINES.fine)
        for i in (1, 2):
            x = pad + i * col_w
            c.line(x, 14, x, inner_top)

        columns = [
            ("Experienced or highly experienced", "91%", "reported at some or significant added value over Copilot", DEWR_DARK_GREEN),
            ("Some prior experience", "73%", "reported at some or significant added value over Copilot", DEWR_DARK_GREY),
            ("No or basic experience", "67%", "reported at some or significant added value over Copilot", DEWR_DARK_GREY),
        ]
        label_style = visual_style(
            "prior_experience_comparison_label",
            "kpi_caption",
            alignment=TA_CENTER,
            textColor=DEWR_DARK_GREY,
        )
        for i, (name, value, label, color) in enumerate(columns):
            x = pad + i * col_w
            cx = x + col_w / 2
            c.setFillColor(DEWR_DARK_GREY)
            c.setFont(FONT_BOLD, VISUAL_TEXT.chart_tick)
            c.drawCentredString(cx, h - 21, name)
            c.setFillColor(color)
            c.setFont(FONT_BOLD, VISUAL_TEXT.kpi_value)
            c.drawCentredString(cx, h - 51, value)
            p = Paragraph(label, label_style)
            _, label_h = p.wrap(col_w - 24, 22)
            p.drawOn(c, x + 12, 25 - label_h / 2)
        c.restoreState()


class HorizontalBarPanel(Flowable):
    """Full-width grey panel with labelled horizontal bars."""
    def __init__(self, width, title, items, max_value=100, primary_count=0, value_suffix="%", row_h=CHART_LAYOUT.row_height_compact):
        Flowable.__init__(self)
        self.box_width = width
        self.title = title
        self.items = items
        self.max_value = max_value
        self.primary_count = primary_count
        self.value_suffix = value_suffix
        self.row_h = row_h
        self.has_title = bool(title)
        self._height = (56 if self.has_title else 32) + self.row_h * len(items)

    def wrap(self, availWidth, availHeight):
        self.box_width = availWidth
        return self.box_width, self._height

    def draw(self):
        c = self.canv
        c.saveState()
        w = self.box_width
        h = self._height
        pad = PANEL_TOKENS.inset_md

        draw_panel_background(c, 0, 0, w, h, stroke_width=0, radius=0)

        if self.has_title:
            c.setFillColor(DEWR_DARK_GREY)
            c.setFont(FONT_BOLD, VISUAL_TEXT.panel_header)
            c.drawString(pad, h - 22, self.title)
            c.setStrokeColor(DEWR_LIGHT_GREY)
            c.setLineWidth(LINES.fine)
            c.line(pad, h - 36, w - pad, h - 36)

        label_w = w * 0.47
        bar_x = pad + label_w
        bar_w = w - bar_x - 44
        bar_h = CHART_LAYOUT.bar_height_compact if self.row_h < 18 else CHART_LAYOUT.bar_height

        for i, (label, value) in enumerate(self.items):
            y = h - (55 if self.has_title else 22) - i * self.row_h
            c.setFillColor(DEWR_NAVY)
            c.setFont(FONT_REGULAR, VISUAL_TEXT.chart_label)
            p = Paragraph(label, visual_style(
                "bar_label",
                "chart_label",
                textColor=DEWR_NAVY,
            ))
            p.wrap(label_w - 8, 16)
            p.drawOn(c, pad, y - 3)

            c.setFillColor(BAR_TRACK)
            c.rect(bar_x, y, bar_w, bar_h, fill=1, stroke=0)
            c.setFillColor(DEWR_DARK_GREEN if i < self.primary_count else DEWR_DARK_GREY)
            c.rect(bar_x, y, bar_w * (value / self.max_value), bar_h, fill=1, stroke=0)
            c.setFillColor(DEWR_NAVY)
            c.setFont(FONT_BOLD, VISUAL_TEXT.chart_value_label)
            c.drawRightString(w - pad, y - 1, f"{value:g}{self.value_suffix}")
        c.restoreState()


class ComfortDataHandlingPanel(Flowable):
    """Dot plot for data-handling behaviour by comfort using public generative AI."""
    def __init__(self, width):
        Flowable.__init__(self)
        self.box_width = width
        self._height = 98
        self.rows = [
            ("Copied and pasted information", 71.7, 66.7, True),
            ("Uploaded documents", 47.8, 26.7, False),
        ]

    def wrap(self, availWidth, availHeight):
        self.box_width = availWidth
        return self.box_width, self._height

    def draw(self):
        c = self.canv
        c.saveState()
        w = self.box_width
        h = self._height

        draw_panel_background(c, 0, 0, w, h, stroke_width=0, radius=0)
        draw_delta_dot_plot(
            c,
            w,
            h,
            self.rows,
            "Comfortable or very comfortable",
            "Uncomfortable",
        )
        c.restoreState()


class PublicToolTaskProfilePanel(Flowable):
    """Task-by-tool dot plot showing how public generative AI were used for different work types."""
    def __init__(self, width):
        Flowable.__init__(self)
        self.box_width = width
        self.rows = [
            ("Summarising", [55.4, 56.8, 56.1]),
            ("Editing and revision", [50.0, 56.8, 51.2]),
            ("Drafting", [51.8, 48.6, 53.7]),
            ("Research, problem solving or ideation", [60.7, 67.6, 73.2]),
            ("General administrative tasks", [21.4, 24.3, 22.0]),
            ("Planning or meeting preparation", [10.7, 8.1, 19.5]),
            ("Coding or data work", [10.7, 13.5, 26.8]),
        ]
        self.series = [
            ("ChatGPT", DEWR_DARK_GREY),
            ("Gemini", DEWR_LIME),
            ("Claude", DEWR_DARK_GREEN),
        ]
        self.max_value = 100
        self.row_h = CHART_LAYOUT.row_height
        self._height = 214

    def wrap(self, availWidth, availHeight):
        self.box_width = availWidth
        return self.box_width, self._height

    def draw(self):
        c = self.canv
        c.saveState()
        w = self.box_width
        h = self._height
        pad = PANEL_TOKENS.inset_xl

        draw_panel_background(c, 0, 0, w, h, stroke_width=0, radius=0)

        label_w = w * CHART_LAYOUT.label_width_ratio
        axis_x = pad + label_w
        axis_w = w - axis_x - pad
        head_y = h - 18
        tick_y = h - 36
        top_y = h - 43
        bottom_y = top_y - self.row_h * (len(self.rows) - 1) - 6

        c.setFillColor(DEWR_DARK_GREY)
        c.setFont(FONT_BOLD, VISUAL_TEXT.panel_header_small)
        c.drawString(pad, head_y, "TASK")

        c.setFont(FONT_REGULAR, VISUAL_TEXT.chart_legend)
        marker_gap = 8
        item_gap = 18
        legend_x = w - pad
        for name, color in reversed(self.series):
            text_w = c.stringWidth(name, FONT_REGULAR, VISUAL_TEXT.chart_legend)
            text_x = legend_x - text_w
            marker_x = text_x - marker_gap
            c.setFillColor(color)
            c.circle(marker_x, h - 16, CHART_LAYOUT.legend_marker_radius, fill=1, stroke=0)
            c.setFillColor(DEWR_DARK_GREY)
            c.drawString(text_x, h - 19, name)
            legend_x = marker_x - item_gap

        c.setStrokeColor(DEWR_LIGHT_GREY)
        c.setLineWidth(LINES.fine)
        c.line(pad, h - 25, w - pad, h - 25)

        c.setFont(FONT_REGULAR, VISUAL_TEXT.chart_tick)
        c.setFillColor(DEWR_GREY)
        for tick, label in [(0, "0%"), (25, "25%"), (50, "50%"), (75, "75%"), (100, "100%")]:
            x = axis_x + axis_w * (tick / self.max_value)
            c.drawCentredString(x, tick_y, label)
            c.setStrokeColor(DEWR_LIGHT_GREY)
            c.setLineWidth(LINES.hairline)
            c.line(x, tick_y - 4, x, bottom_y)

        label_style = visual_style(
            "public_tool_task_label",
            "chart_label",
            textColor=DEWR_NAVY,
        )
        label_bold_style = visual_style(
            "public_tool_task_label_bold",
            "chart_label",
            parent=label_style,
            fontName=FONT_BOLD,
        )

        for r_idx, (label, values) in enumerate(self.rows):
            y = top_y - r_idx * self.row_h

            important_label = label in {
                "Research, problem solving or ideation",
                "Coding or data work",
            }
            p = Paragraph(label, label_bold_style if important_label else label_style)
            p.wrap(label_w - 8, 18)
            p.drawOn(c, pad, y - 6)

            max_value = max(values)
            positions = [axis_x + axis_w * (value / self.max_value) for value in values]
            min_gap = 7
            ordered = sorted(range(len(positions)), key=lambda idx: positions[idx])
            for left_idx, right_idx in zip(ordered, ordered[1:]):
                gap = positions[right_idx] - positions[left_idx]
                if gap < min_gap:
                    adjust = (min_gap - gap) / 2
                    positions[left_idx] -= adjust
                    positions[right_idx] += adjust

            for i, value in enumerate(values):
                highlighted = value == max_value
                color = self.series[i][1]
                x = positions[i]
                c.setFillColor(color)
                c.circle(x, y, CHART_LAYOUT.dot_radius, fill=1, stroke=0)

                if highlighted:
                    label_text = f"{value:.1f}%"
                    c.setFont(FONT_BOLD, VISUAL_TEXT.chart_value_label)
                    text_w = c.stringWidth(label_text, FONT_BOLD, VISUAL_TEXT.chart_value_label)
                    label_x = x + 5
                    c.setFillColor(color)
                    if label_x + text_w > axis_x + axis_w + 38:
                        c.drawRightString(x - 5, y - 2, label_text)
                    else:
                        c.drawString(label_x, y - 2, label_text)
        c.restoreState()


class AllToolTaskProfilePanel(Flowable):
    """Task-by-tool dot plot comparing public generative AI and Copilot versions."""
    def __init__(self, width):
        Flowable.__init__(self)
        self.box_width = width
        self.rows = [
            ("Summarising", [55.4, 56.8, 56.1, 83.9, 74.4], [None, None, None, 83.3, 73.2]),
            ("Editing and revision", [50.0, 56.8, 51.2, 71.0, 64.1], [None, None, None, 70.0, 63.4]),
            ("Drafting", [51.8, 48.6, 53.7, 71.0, 66.7], [None, None, None, 70.0, 65.9]),
            ("Research, problem solving or ideation", [60.7, 67.6, 73.2, 67.7, 43.6], [None, None, None, 66.7, 43.9]),
            ("General administrative tasks", [21.4, 24.3, 22.0, 48.4, 41.0], [None, None, None, 46.7, 41.5]),
            ("Planning or meeting preparation", [10.7, 8.1, 19.5, 35.5, 12.8], [None, None, None, 33.3, 14.6]),
            ("Coding or data work", [10.7, 13.5, 26.8, 22.6, 20.5], [None, None, None, 23.3, 19.5]),
        ]
        self.series = [
            ("ChatGPT", DEWR_DARK_GREY),
            ("Gemini", DEWR_LIME),
            ("Claude", DEWR_DARK_GREEN),
            ("M365 Copilot", DEWR_TEAL),
            ("Copilot Chat", DEWR_GREY),
        ]
        self.max_value = 100
        self.row_h = CHART_LAYOUT.row_height
        self._height = 214

    def wrap(self, availWidth, availHeight):
        self.box_width = availWidth
        return self.box_width, self._height

    def draw(self):
        c = self.canv
        c.saveState()
        w = self.box_width
        h = self._height
        pad = PANEL_TOKENS.inset_xl

        draw_panel_background(c, 0, 0, w, h, stroke_width=0, radius=0)

        label_w = w * CHART_LAYOUT.label_width_ratio
        axis_x = pad + label_w
        axis_w = w - axis_x - pad
        head_y = h - 18
        tick_y = h - 36
        top_y = h - 43
        bottom_y = top_y - self.row_h * (len(self.rows) - 1) - 6

        c.setFillColor(DEWR_DARK_GREY)
        c.setFont(FONT_BOLD, VISUAL_TEXT.panel_header_small)
        c.drawString(pad, head_y, "TASK")

        c.setFont(FONT_REGULAR, VISUAL_TEXT.chart_legend_compact)
        marker_gap = 6
        item_gap = 10
        legend_x = w - pad
        for name, color in reversed(self.series):
            text_w = c.stringWidth(name, FONT_REGULAR, VISUAL_TEXT.chart_legend_compact)
            text_x = legend_x - text_w
            marker_x = text_x - marker_gap
            c.setFillColor(color)
            c.circle(marker_x, h - 16, CHART_LAYOUT.legend_marker_radius_compact, fill=1, stroke=0)
            c.setFillColor(DEWR_DARK_GREY)
            c.drawString(text_x, h - 19, name)
            legend_x = marker_x - item_gap

        c.setStrokeColor(DEWR_LIGHT_GREY)
        c.setLineWidth(LINES.fine)
        c.line(pad, h - 25, w - pad, h - 25)

        c.setFont(FONT_REGULAR, VISUAL_TEXT.chart_tick)
        c.setFillColor(DEWR_GREY)
        for tick, label in [(0, "0%"), (25, "25%"), (50, "50%"), (75, "75%"), (100, "100%")]:
            x = axis_x + axis_w * (tick / self.max_value)
            c.drawCentredString(x, tick_y, label)
            c.setStrokeColor(DEWR_LIGHT_GREY)
            c.setLineWidth(LINES.hairline)
            c.line(x, tick_y - 4, x, bottom_y)

        label_style = visual_style(
            "all_tool_task_label",
            "chart_label",
            textColor=DEWR_NAVY,
        )
        label_bold_style = visual_style(
            "all_tool_task_label_bold",
            "chart_label",
            parent=label_style,
            fontName=FONT_BOLD,
        )

        for r_idx, (label, values, old_values) in enumerate(self.rows):
            y = top_y - r_idx * self.row_h
            important_label = label in {
                "Research, problem solving or ideation",
                "Coding or data work",
            }
            p = Paragraph(label, label_bold_style if important_label else label_style)
            p.wrap(label_w - 8, 18)
            p.drawOn(c, pad, y - 6)

            max_value = max(values)
            positions = [axis_x + axis_w * (value / self.max_value) for value in values]
            min_gap = 5.8
            ordered = sorted(range(len(positions)), key=lambda idx: positions[idx])
            for left_idx, right_idx in zip(ordered, ordered[1:]):
                gap = positions[right_idx] - positions[left_idx]
                if gap < min_gap:
                    adjust = (min_gap - gap) / 2
                    positions[left_idx] -= adjust
                    positions[right_idx] += adjust

            for i, value in enumerate(values):
                highlighted = value == max_value
                color = self.series[i][1]
                x = positions[i]
                c.setFillColor(color)
                c.circle(x, y, CHART_LAYOUT.dot_radius, fill=1, stroke=0)

                if highlighted:
                    label_text = marked_value(f"{value:.1f}%", f"{old_values[i]:.1f}%") if old_values[i] is not None else f"{value:.1f}%"
                    c.setFont(FONT_BOLD, VISUAL_TEXT.chart_value_label_compact)
                    text_w = c.stringWidth(label_text, FONT_BOLD, VISUAL_TEXT.chart_value_label_compact)
                    label_x = x + 5
                    c.setFillColor(color)
                    if label_x + text_w > axis_x + axis_w + 38:
                        c.drawRightString(x - 5, y - 2, label_text)
                    else:
                        c.drawString(label_x, y - 2, label_text)
        c.restoreState()


class SafeguardPrioritiesPanel(Flowable):
    """Three-column safeguard framework panel."""
    def __init__(self, width):
        Flowable.__init__(self)
        self.box_width = width
        self._height = 128
        self.items = [
            ("Information classification boundaries", "Users described uncertainty about what information was appropriate to enter."),
            ("Output validation", "Users pointed to the need to check outputs before relying on them."),
            ("APS-specific sensitivity and safeguards", "Some responses highlighted differences between public generative AI and Copilot safeguards."),
        ]

    def wrap(self, availWidth, availHeight):
        self.box_width = availWidth
        return self.box_width, self._height

    def draw(self):
        c = self.canv
        c.saveState()
        w = self.box_width
        h = self._height
        pad = PANEL_TOKENS.inset_md

        draw_panel_background(c, 0, 0, w, h, stroke_width=0, radius=0)

        c.setFillColor(DEWR_DARK_GREY)
        c.setFont(FONT_BOLD, VISUAL_TEXT.panel_header)
        c.drawString(pad, h - 19, "PRACTICAL JUDGEMENT BOUNDARIES")
        c.setStrokeColor(DEWR_LIGHT_GREY)
        c.setLineWidth(LINES.fine)
        c.line(pad, h - 32, w - pad, h - 32)

        col_w = (w - 2 * pad) / 3
        for i, (title, text) in enumerate(self.items):
            x = pad + i * col_w
            if i:
                c.setStrokeColor(DEWR_LIGHT_GREY)
                c.line(x, 16, x, h - 42)

            title_p = Paragraph(title, visual_style(
                "safeguard_title",
                "safeguard_title",
                textColor=DEWR_DARK_GREY,
            ))
            title_p.wrap(col_w - 22, 28)
            title_p.drawOn(c, x + 10, h - 66)
            p = Paragraph(text, visual_style(
                "safeguard_text",
                "safeguard_body",
                textColor=DEWR_DARK_GREY,
            ))
            p.wrap(col_w - 22, 42)
            p.drawOn(c, x + 10, h - 108)
        c.restoreState()


class UncertaintyAreasPanel(Flowable):
    """Three-column panel for uncertainty themes in open-text responses."""
    def __init__(self, width):
        Flowable.__init__(self)
        self.box_width = width
        self._height = 130
        self.items = [
            ("Information boundaries",
             "Uncertainty about what information was appropriate to enter, including unclassified but sensitive material."),
            ("Commercial sensitivity",
             "Some respondents avoided uploading material that was allowed by classification but felt commercially sensitive."),
            ("Validation and APS safeguards",
             "Respondents raised the need to check outputs and noted differences between public generative AI and Copilot safeguards."),
        ]

    def wrap(self, availWidth, availHeight):
        self.box_width = availWidth
        return self.box_width, self._height

    def draw(self):
        c = self.canv
        c.saveState()
        w = self.box_width
        h = self._height
        pad = PANEL_TOKENS.inset_lg

        draw_panel_background(c, 0, 0, w, h, stroke_width=0, radius=0)

        c.setFillColor(DEWR_DARK_GREY)
        c.setFont(FONT_BOLD, VISUAL_TEXT.panel_header_small)
        c.drawString(pad, h - 19, "THEMES OF UNCERTAINTY IN OPEN-TEXT RESPONSES")
        c.setStrokeColor(DEWR_LIGHT_GREY)
        c.setLineWidth(LINES.fine)
        c.line(pad, h - 32, w - pad, h - 32)

        col_w = (w - 2 * pad) / 3
        title_top = h - 52
        body_top = h - 80
        bottom_y = 14
        for i, (title, text) in enumerate(self.items):
            x = pad + i * col_w
            if i:
                c.setStrokeColor(DEWR_LIGHT_GREY)
                c.line(x, bottom_y, x, h - 42)

            title_p = Paragraph(title, visual_style(
                "uncertainty_title",
                "theme_title",
                textColor=DEWR_DARK_GREY,
            ))
            title_w = col_w - 30
            title_h = title_p.wrap(title_w, 32)[1]
            title_p.drawOn(c, x + 10, title_top - title_h)
            p = Paragraph(text, visual_style(
                "uncertainty_text",
                "theme_body",
                textColor=DEWR_DARK_GREY,
            ))
            _, text_h = p.wrap(title_w, 54)
            p.drawOn(c, x + 10, body_top - text_h)
        c.restoreState()


class SafeguardModelPanel(Flowable):
    """Four-part safeguard model for future rollout."""
    def __init__(self, width):
        Flowable.__init__(self)
        self.box_width = width
        self._height = 116
        self.items = [
            ("Guide", "Clear rules and examples for what can be entered."),
            ("Remind", "Point-of-use splash screens to reinforce boundaries."),
            ("Block", "DLP upload controls as a technical backstop."),
            ("Assure", "Logs and monitoring to verify control performance."),
        ]

    def wrap(self, availWidth, availHeight):
        self.box_width = availWidth
        return self.box_width, self._height

    def draw(self):
        c = self.canv
        c.saveState()
        w = self.box_width
        h = self._height
        pad = PANEL_TOKENS.inset_md

        draw_panel_background(c, 0, 0, w, h, stroke_width=0, radius=0)

        c.setFillColor(DEWR_DARK_GREY)
        c.setFont(FONT_BOLD, VISUAL_TEXT.panel_header)
        c.drawString(pad, h - 19, "SAFEGUARD OPERATING MODEL")
        c.setStrokeColor(DEWR_LIGHT_GREY)
        c.setLineWidth(LINES.fine)
        c.line(pad, h - 32, w - pad, h - 32)

        col_w = (w - 2 * pad) / 4
        for i, (title, text) in enumerate(self.items):
            x = pad + i * col_w
            if i:
                c.setStrokeColor(DEWR_LIGHT_GREY)
                c.line(x, 16, x, h - 42)

            c.setFillColor(DEWR_DARK_GREEN if i < 2 else DEWR_DARK_GREY)
            c.setFont(FONT_BOLD, VISUAL_TEXT.callout_text)
            c.drawString(x + 9, h - 54, title)
            p = Paragraph(text, visual_style(
                "safeguard_model_text",
                "model_body",
                textColor=DEWR_DARK_GREY,
            ))
            p.wrap(col_w - 20, 42)
            p.drawOn(c, x + 9, h - 94)
        c.restoreState()


class ConcernClusterMap(Flowable):
    """Two-cluster map for open-text concern themes."""
    def __init__(self, width):
        Flowable.__init__(self)
        self.box_width = width
        self._height = 144
        self.clusters = [
            ("COMMON PRACTICAL CONCERNS", [
                (3, "Tool access, integration and cost (17)"),
                (2, "Data privacy, confidentiality and public-tool data use (13)"),
                (1, "Accuracy, hallucination and validation (8)"),
            ]),
            ("BROADER TRUST AND IMPACT CONCERNS", [
                (1, "Environmental impact (5)"),
                (1, "Workforce, capability and civic reliance (4)"),
                (1, "Other: bias, ethics, governance (2)"),
            ]),
        ]

    def wrap(self, availWidth, availHeight):
        self.box_width = availWidth
        return self.box_width, self._height

    def draw(self):
        c = self.canv
        c.saveState()
        w = self.box_width
        h = self._height
        pad = PANEL_TOKENS.inset_md
        cluster_gap = 20
        cluster_w = (w - 2 * pad - cluster_gap) / 2

        draw_panel_background(c, 0, 0, w, h, stroke_width=0, radius=0)

        for cluster_idx, (title, rows) in enumerate(self.clusters):
            x = pad + cluster_idx * (cluster_w + cluster_gap)
            if cluster_idx:
                c.setStrokeColor(DEWR_LIGHT_GREY)
                c.setLineWidth(LINES.fine)
                c.line(x - cluster_gap / 2, 16, x - cluster_gap / 2, h - 16)

            c.setFillColor(DEWR_DARK_GREY)
            c.setFont(FONT_BOLD, VISUAL_TEXT.panel_header_small)
            c.drawString(x, h - 20, title)
            c.setStrokeColor(DEWR_LIGHT_GREY)
            c.line(x, h - 33, x + cluster_w, h - 33)

            row_y = h - 56
            for row_idx, (dot_count, label) in enumerate(rows):
                y = row_y - row_idx * 25
                dot_center_y = y + 4
                for dot_idx in range(3):
                    c.setFillColor(DEWR_DARK_GREEN if dot_idx < dot_count and cluster_idx == 0 else
                                   DEWR_DARK_GREY if dot_idx < dot_count else BAR_TRACK)
                    c.circle(x + 6 + dot_idx * 10, dot_center_y, CHART_LAYOUT.dot_radius_small, fill=1, stroke=0)
                p = Paragraph(label, visual_style(
                    "concern_cluster_label",
                    "model_body",
                    leading=VISUAL_TEXT.theme_body_leading,
                    textColor=DEWR_NAVY,
                ))
                _, label_h = p.wrap(cluster_w - 40, 24)
                p.drawOn(c, x + 38, dot_center_y - label_h / 2)
        c.restoreState()


class GroupedBarChart(Flowable):
    """Horizontal grouped bar chart with left-aligned category labels,
    section headers to group categories, a legend, and direct value labels.
    Follows OCE viz guidelines."""
    def __init__(self, title, subtitle, sections, series_a_label,
                 series_b_label, width, source_text="",
                 series_a_color=DEWR_GREEN, series_b_color=DEWR_DARK_GREY,
                 max_value=100):
        """sections is a list of (section_title, [(cat, a_val, b_val), ...])"""
        Flowable.__init__(self)
        self.title = title
        self.subtitle = subtitle
        self.sections = sections
        self.a_label = series_a_label
        self.b_label = series_b_label
        self.box_width = width
        self.source_text = source_text
        self.a_color = series_a_color
        self.b_color = series_b_color
        self.max_value = max_value

        self.bar_h = CHART_LAYOUT.bar_height_large
        self.bar_gap = 4
        self.group_gap = 18
        self.section_gap = 14
        self.label_w = 165

    def wrap(self, availWidth, availHeight):
        self.box_width = availWidth
        per_group = (self.bar_h * 2) + self.bar_gap + self.group_gap
        body_h = 0
        for sec_title, cats in self.sections:
            body_h += 22       # section header + spacing
            body_h += per_group * len(cats)
            body_h += self.section_gap
        # title(18) + subtitle(16) + legend(38) + gap(10) + body + source(20)
        self._height = 18 + 16 + 38 + 10 + body_h + 20
        return self.box_width, self._height

    def draw(self):
        c = self.canv
        c.saveState()
        w = self.box_width
        h = self._height

        # Title
        c.setFillColor(DEWR_DARK_GREY)
        c.setFont(FONT_BOLD, VISUAL_TEXT.card_title)
        c.drawString(0, h - 14, self.title)
        # Subtitle
        c.setFont(FONT_REGULAR, VISUAL_TEXT.chart_label)
        c.setFillColor(DEWR_GREY)
        c.drawString(0, h - 32, self.subtitle)

        # Legend (right-aligned, below subtitle)
        leg_y = h - 18 - 16 - 6
        # measure label widths to right-align cleanly
        c.setFont(FONT_REGULAR, VISUAL_TEXT.chart_legend)
        a_text_w = c.stringWidth(self.a_label, FONT_REGULAR, VISUAL_TEXT.chart_legend)
        b_text_w = c.stringWidth(self.b_label, FONT_REGULAR, VISUAL_TEXT.chart_legend)
        max_text_w = max(a_text_w, b_text_w)
        leg_block_w = 14 + max_text_w
        leg_x = w - leg_block_w

        c.setFillColor(self.a_color)
        c.rect(leg_x, leg_y, 11, 11, fill=1, stroke=0)
        c.setFillColor(DEWR_DARK_GREY)
        c.setFont(FONT_REGULAR, VISUAL_TEXT.chart_legend)
        c.drawString(leg_x + 16, leg_y + 2, self.a_label)
        leg_y -= 16
        c.setFillColor(self.b_color)
        c.rect(leg_x, leg_y, 11, 11, fill=1, stroke=0)
        c.setFillColor(DEWR_DARK_GREY)
        c.setFont(FONT_REGULAR, VISUAL_TEXT.chart_legend)
        c.drawString(leg_x + 16, leg_y + 2, self.b_label)

        # Bar area
        bar_area_x = self.label_w
        bar_area_w = w - self.label_w - 40
        cur_y = h - 18 - 16 - 38 - 10

        # Bottom of all bars (for baseline)
        baseline_top = cur_y
        baseline_bottom = 20  # leave room for source

        for sec_idx, (sec_title, cats) in enumerate(self.sections):
            # Section header (with divider above)
            if sec_idx > 0:
                # spacer already added, draw divider
                pass
            c.setStrokeColor(DEWR_LIGHT_GREY)
            c.setLineWidth(LINES.fine)
            c.line(0, cur_y, w, cur_y)
            cur_y -= 4
            c.setFillColor(DEWR_DARK_GREY)
            c.setFont(FONT_BOLD, VISUAL_TEXT.chart_label)
            c.drawString(0, cur_y - 11, sec_title)
            cur_y -= 18

            for cat, a_val, b_val in cats:
                bar_top = cur_y

                # Series A bar
                a_w = bar_area_w * (a_val / self.max_value)
                c.setFillColor(self.a_color)
                c.rect(bar_area_x, cur_y - self.bar_h, a_w, self.bar_h,
                       fill=1, stroke=0)
                c.setFillColor(DEWR_DARK_GREY)
                c.setFont(FONT_BOLD, VISUAL_TEXT.chart_value_label)
                c.drawString(bar_area_x + a_w + 6, cur_y - self.bar_h + 4,
                             f"{a_val}%")
                cur_y -= self.bar_h + self.bar_gap

                # Series B bar
                b_w = bar_area_w * (b_val / self.max_value)
                c.setFillColor(self.b_color)
                c.rect(bar_area_x, cur_y - self.bar_h, b_w, self.bar_h,
                       fill=1, stroke=0)
                c.setFillColor(DEWR_DARK_GREY)
                c.setFont(FONT_BOLD, VISUAL_TEXT.chart_value_label)
                c.drawString(bar_area_x + b_w + 6, cur_y - self.bar_h + 4,
                             f"{b_val}%")

                # Category label (vertically centred between the two bars)
                label_mid_y = bar_top - self.bar_h - (self.bar_gap / 2)
                c.setFillColor(DEWR_DARK_GREY)
                c.setFont(FONT_REGULAR, VISUAL_TEXT.chart_label)
                words = cat.split()
                lines = []
                current_line = ""
                for word in words:
                    test = (current_line + " " + word).strip()
                    if c.stringWidth(test, FONT_REGULAR, VISUAL_TEXT.chart_label) <= self.label_w - 12:
                        current_line = test
                    else:
                        if current_line:
                            lines.append(current_line)
                        current_line = word
                if current_line:
                    lines.append(current_line)
                total_text_h = len(lines) * 12
                label_start_y = label_mid_y + total_text_h / 2 - 4
                for li, line in enumerate(lines):
                    c.drawRightString(self.label_w - 12, label_start_y - li * 12, line)

                cur_y -= self.bar_h + self.group_gap

            # remove trailing group_gap, add section_gap
            cur_y += self.group_gap - self.section_gap

        baseline_bottom_actual = cur_y

        # Subtle baseline at 0% (vertical anchor)
        c.setStrokeColor(DEWR_LIGHT_GREY)
        c.setLineWidth(LINES.fine)
        c.line(bar_area_x, baseline_top - 2, bar_area_x, baseline_bottom_actual + self.section_gap)

        # Source
        if self.source_text:
            c.setFillColor(DEWR_GREY)
            c.setFont(FONT_ITALIC, VISUAL_TEXT.note)
            c.drawString(0, 4, self.source_text)
        c.restoreState()


class TaskFootprintExhibit(Flowable):
    """Full task-footprint dumbbell with the largest access-type gaps highlighted."""
    def __init__(self, width):
        Flowable.__init__(self)
        self.box_width = width
        self._height = 246
        # Corrected task-use values supplied from the validated survey table.
        self.rows = [
            ("Summarising", 83.9, 83.3, 74.4, 73.2, False),
            ("Editing and revision", 71.0, 70.0, 64.1, 63.4, False),
            ("Drafting", 71.0, 70.0, 66.7, 65.9, False),
            ("Research, problem solving or ideation", 67.7, 66.7, 43.6, 43.9, True),
            ("General administrative tasks", 48.4, 46.7, 41.0, 41.5, False),
            ("Planning or meeting preparation", 35.5, 33.3, 12.8, 14.6, True),
            ("Coding or data work", 22.6, 23.3, 20.5, 19.5, False),
        ]

    def wrap(self, availWidth, availHeight):
        self.box_width = availWidth
        return self.box_width, self._height

    def draw(self):
        c = self.canv
        c.saveState()
        w = self.box_width
        h = self._height
        pad = PANEL_TOKENS.inset_xl
        label_w = w * CHART_LAYOUT.dumbbell_label_width_ratio
        axis_x = pad + label_w
        axis_w = w - axis_x - pad
        tick_y = h - 42
        top_y = h - 49
        row_gap = CHART_LAYOUT.row_height
        fogged_m365 = FOGGED_EUCALYPTUS
        fogged_chat = FOGGED_GRAPHITE

        draw_panel_background(c, 0, 0, w, h, stroke_width=0, radius=0)

        c.setFillColor(DEWR_DARK_GREY)
        c.setFont(FONT_BOLD, VISUAL_TEXT.panel_header_small)
        c.drawString(pad, h - 20, "TASK")

        c.setFont(FONT_REGULAR, VISUAL_TEXT.chart_legend)
        m365_label = "M365 Copilot"
        chat_label = "Copilot Chat"
        marker_gap = 8
        item_gap = 18
        m365_w = c.stringWidth(m365_label, FONT_REGULAR, VISUAL_TEXT.chart_legend)
        chat_w = c.stringWidth(chat_label, FONT_REGULAR, VISUAL_TEXT.chart_legend)
        legend_right = w - pad
        m365_text_x = legend_right - m365_w
        m365_marker_x = m365_text_x - marker_gap
        chat_text_x = m365_marker_x - item_gap - chat_w
        chat_marker_x = chat_text_x - marker_gap
        c.setFillColor(DEWR_DARK_GREEN)
        c.circle(m365_marker_x, h - 18, CHART_LAYOUT.legend_marker_radius, fill=1, stroke=0)
        c.setFillColor(DEWR_DARK_GREY)
        c.drawString(m365_text_x, h - 21, m365_label)
        c.setFillColor(DEWR_DARK_GREY)
        c.circle(chat_marker_x, h - 18, CHART_LAYOUT.legend_marker_radius, fill=1, stroke=0)
        c.drawString(chat_text_x, h - 21, chat_label)

        c.setStrokeColor(DEWR_LIGHT_GREY)
        c.setLineWidth(LINES.fine)
        c.line(pad, h - 28, w - pad, h - 28)

        c.setFont(FONT_REGULAR, VISUAL_TEXT.chart_tick)
        c.setFillColor(DEWR_GREY)
        for tick, label in [(0, "0%"), (25, "25%"), (50, "50%"), (75, "75%"), (100, "100%")]:
            x = axis_x + axis_w * (tick / 100)
            c.setStrokeColor(DEWR_LIGHT_GREY)
            c.setLineWidth(LINES.hairline)
            c.line(x, tick_y - 4, x, top_y - row_gap * (len(self.rows) - 1) - 8)
            c.drawCentredString(x, tick_y, label)

        for i, (label, m365, old_m365, chat, old_chat, highlight) in enumerate(self.rows):
            y = top_y - i * row_gap
            p = Paragraph(label, visual_style(
                "full_task_dumbbell_label",
                "chart_label",
                fontName=FONT_BOLD if highlight else FONT_REGULAR,
                textColor=DEWR_DARK_GREY,
            ))
            p.wrap(label_w - 10, 22)
            p.drawOn(c, pad, y - 7)

            chat_x = axis_x + axis_w * (chat / 100)
            m365_x = axis_x + axis_w * (m365 / 100)
            line_color = DEWR_DARK_GREEN if highlight else DEWR_LIGHT_GREY
            m365_color = DEWR_DARK_GREEN if highlight else fogged_m365
            chat_color = DEWR_DARK_GREY if highlight else fogged_chat

            c.setStrokeColor(line_color)
            c.setLineWidth(
                CHART_LAYOUT.dumbbell_line_width_highlight
                if highlight
                else CHART_LAYOUT.dumbbell_line_width
            )
            c.line(chat_x, y, m365_x, y)
            c.setFillColor(chat_color)
            c.circle(chat_x, y, CHART_LAYOUT.dot_radius_small if highlight else CHART_LAYOUT.dot_radius_compact, fill=1, stroke=0)
            c.setFillColor(m365_color)
            c.circle(m365_x, y, CHART_LAYOUT.dot_radius_highlight if highlight else CHART_LAYOUT.dot_radius_compact, fill=1, stroke=0)

            c.setFont(FONT_BOLD, VISUAL_TEXT.chart_value_label_compact)
            chat_text = marked_value(f"{chat:.0f}%", f"{old_chat:.0f}%")
            m365_text = marked_value(f"{m365:.0f}%", f"{old_m365:.0f}%")
            chat_w = c.stringWidth(chat_text, FONT_BOLD, VISUAL_TEXT.chart_value_label_compact)
            m365_w = c.stringWidth(m365_text, FONT_BOLD, VISUAL_TEXT.chart_value_label_compact)

            c.setFillColor(chat_color)
            if chat_x - 6 - chat_w < axis_x:
                c.drawString(chat_x + 6, y - 3, chat_text)
            else:
                c.drawRightString(chat_x - 6, y - 3, chat_text)
            c.setFillColor(m365_color)
            if m365_x + 6 + m365_w > axis_x + axis_w + 4:
                c.drawRightString(m365_x - 6, y - 3, m365_text)
            else:
                c.drawString(m365_x + 6, y - 3, m365_text)
        c.restoreState()


class KeyFindingBar(Flowable):
    """A left-bordered key finding highlight."""
    def __init__(self, text, width, border_color=DEWR_GREEN, bg_color=None):
        Flowable.__init__(self)
        self.text = text
        self.box_width = width
        self.border_color = border_color
        self.bg_color = bg_color or KEY_FINDING_BACKGROUND
        self._height = None

    def wrap(self, availWidth, availHeight):
        self.box_width = availWidth
        style = key_finding_style("kf_measure")
        p = Paragraph(self.text, style)
        w, h = p.wrap(self.box_width - 24, availHeight)
        self._height = h + 20
        return self.box_width, self._height

    def draw(self):
        c = self.canv
        c.saveState()
        c.setFillColor(self.bg_color)
        c.rect(0, 0, self.box_width, self._height, fill=1, stroke=0)
        c.setFillColor(self.border_color)
        c.rect(0, 0, 4, self._height, fill=1, stroke=0)
        draw_wrapped_text(c, self.text, key_finding_style("kf_draw"), 16, self._height - 10, self.box_width - 24, self._height)
        c.restoreState()


class KeyFindingPillarCard(Flowable):
    """A premium numbered key-finding card with left accent bar and large number."""

    _ACCENT_W = 0.0
    _NUM_SIZE_HERO = 28
    _NUM_SIZE_STD = 24
    _PAD_LEFT = PANEL_TOKENS.inset_md
    _PAD_RIGHT = PANEL_TOKENS.inset_md

    def __init__(self, number, title, bullets, card_width,
                 is_hero=False, accent_color=None, numbered_bullets=False):
        Flowable.__init__(self)
        self.num_str = f"{number:02d}"
        self.title_text = title
        self.bullet_texts = bullets
        self.card_width = card_width
        self.is_hero = is_hero
        self.accent_color = accent_color or DEWR_GREEN
        self.numbered_bullets = numbered_bullets
        self._height = 0
        self._title_para = None
        self._bullet_paras = []
        self._num_h = 0

    def _content_x(self):
        return self._ACCENT_W + self._PAD_LEFT

    def _content_width(self):
        return self.card_width - self._content_x() - self._PAD_RIGHT

    def _build_paras(self):
        text_color = DEWR_DARK_GREY

        title_fs = 12
        title_ld = 15.0
        self._title_para = Paragraph(self.title_text, ParagraphStyle(
            "PillarTitle",
            fontName=FONT_BOLD,
            fontSize=title_fs,
            leading=title_ld,
            textColor=text_color,
            spaceBefore=0,
            spaceAfter=0,
        ))

        bullet_fs = 9.25
        bullet_ld = 11.45
        self._bullet_paras = []
        for b in self.bullet_texts:
            is_numbered = re.match(r"^\d+\.", b)
            prefix = "" if is_numbered else "<bullet>&bull;</bullet> "
            style = ParagraphStyle(
                "PillarBullet",
                fontName=FONT_REGULAR,
                fontSize=bullet_fs,
                leading=bullet_ld,
                textColor=text_color,
                leftIndent=0 if is_numbered else 8,
                firstLineIndent=0 if is_numbered else -8,
                spaceBefore=0,
                spaceAfter=0,
            )
            self._bullet_paras.append(Paragraph(f"{prefix}{b}", style))

    def wrap(self, availWidth, availHeight):
        self.card_width = availWidth
        self._build_paras()
        cw = self._content_width()

        _, th = self._title_para.wrap(cw, 10000)
        self._title_h = th
        total = th + 8

        bullet_gap = 3.4
        for bp in self._bullet_paras:
            _, bh = bp.wrap(cw, 10000)
            total += bh + bullet_gap

        pad_top = PANEL_TOKENS.inset_sm
        pad_bottom = PANEL_TOKENS.inset_sm
        self._height = total + pad_top + pad_bottom
        self.width = self.card_width
        self.height = self._height
        return (self.card_width, self._height)

    def draw(self):
        c = self.canv
        w = self.card_width
        h = self._height
        ax = self._ACCENT_W

        c.saveState()

        c.setFillColor(DEWR_OFF_WHITE)
        c.rect(ax, 0, w - ax, h, fill=1, stroke=0)

        c.setFillColor(self.accent_color)
        c.rect(0, 0, ax, h, fill=1, stroke=0)

        content_x = self._content_x()
        cw = self._content_width()
        pad_top = PANEL_TOKENS.inset_sm
        y = h - pad_top

        th = self._title_h
        self._title_para.drawOn(c, content_x, y - th)
        y -= th + 8

        bullet_gap = 3.4
        for bp in self._bullet_paras:
            _, bh = bp.wrap(cw, 10000)
            bp.drawOn(c, content_x, y - bh)
            y -= bh + bullet_gap

        c.restoreState()


def header_footer(canvas, doc):
    canvas.saveState()
    # Header line
    canvas.setStrokeColor(DEWR_NAVY)
    canvas.setLineWidth(PAGE_CHROME.header_line_width)
    canvas.line(doc.leftMargin, A4[1] - PAGE_CHROME.header_line_y, A4[0] - doc.rightMargin, A4[1] - PAGE_CHROME.header_line_y)

    # Header text
    canvas.setFont(FONT_REGULAR, PAGE_CHROME.header_text_size)
    canvas.setFillColor(DEWR_DARK_GREY)
    canvas.drawString(doc.leftMargin, A4[1] - PAGE_CHROME.header_text_y,
                      "Evaluation of the Public Generative AI Trial")

    # Footer
    canvas.setStrokeColor(DEWR_LIGHT_GREY)
    canvas.setLineWidth(PAGE_CHROME.footer_line_width)
    canvas.line(doc.leftMargin, PAGE_CHROME.footer_line_y, A4[0] - doc.rightMargin, PAGE_CHROME.footer_line_y)
    canvas.setFont(FONT_REGULAR, PAGE_CHROME.footer_text_size)
    canvas.setFillColor(DEWR_DARK_GREY)
    canvas.drawRightString(A4[0] - doc.rightMargin, PAGE_CHROME.footer_text_y,
                           f"Page {doc.page}")

    note_style = ParagraphStyle(
        "FooterSourceNote",
        fontName=FONT_REGULAR,
        fontSize=6.2,
        leading=7.2,
        textColor=DEWR_TEXT_GREY,
        spaceBefore=0,
        spaceAfter=0,
    )
    note_width = (A4[0] - doc.leftMargin - doc.rightMargin) - 40  # leave room for "Page X"

    footer_notes = []
    if doc.page == COPILOT_TIME_SAVINGS_NOTE_PAGE:
        footer_notes.extend(COPILOT_TIME_SAVINGS_FOOTER_NOTES)
    footer_notes.extend(FooterNoteMarker._registry.get(doc.page, []))

    # Render notes BELOW the footer line, top-down.
    top_y = PAGE_CHROME.footer_line_y - 4
    for note_text in footer_notes:
        note = Paragraph(note_text, note_style)
        _, note_h = note.wrap(note_width, 40)
        note.drawOn(canvas, doc.leftMargin, top_y - note_h)
        top_y -= note_h + 2
    canvas.restoreState()


def cover_page(canvas, doc):
    canvas.saveState()
    page_w, page_h = A4
    left = COVER.left
    cover_green = COVER_MUTED_GREEN

    canvas.setFillColor(DEWR_DARK_GREY)
    canvas.rect(0, 0, page_w, page_h, fill=1, stroke=0)

    canvas.setFillColor(DEWR_GREEN)
    canvas.rect(0, 0, page_w, COVER.bottom_bar_height, fill=1, stroke=0)

    if os.path.exists(COVER_LOCKUP_PATH):
        canvas.drawImage(
            COVER_LOCKUP_PATH,
            left,
            page_h - COVER.logo_y_offset,
            width=COVER.logo_width,
            height=COVER.logo_height,
            mask="auto",
        )
    else:
        canvas.setFillColor(white)
        canvas.setFont(FONT_BOLD, VISUAL_TEXT.cover_fallback_agency)
        canvas.drawString(left, page_h - COVER.fallback_agency_y_offset, "Australian Government")
        canvas.setLineWidth(COVER.fallback_rule_width_line)
        canvas.setStrokeColor(white)
        canvas.line(
            left,
            page_h - COVER.fallback_rule_y_offset,
            left + COVER.fallback_rule_width,
            page_h - COVER.fallback_rule_y_offset,
        )
        canvas.setFont(FONT_BOLD, VISUAL_TEXT.cover_fallback_department)
        canvas.drawString(left, page_h - COVER.fallback_department_y_offset, "Department of Employment")
        canvas.drawString(left, page_h - COVER.fallback_department_second_line_y_offset, "and Workplace Relations")

    title_style = ParagraphStyle(
        "CoverPageTitle",
        fontName=FONT_BOLD,
        fontSize=COVER.title_size,
        leading=COVER.title_leading,
        textColor=white,
    )
    title = Paragraph("Public Generative AI Trial", title_style)
    title.wrap(page_w - left - COVER.text_right_margin, 120)
    title.drawOn(canvas, left, page_h - COVER.title_y_offset)

    subtitle_style = ParagraphStyle(
        "CoverPageSubtitle",
        fontName=FONT_REGULAR,
        fontSize=COVER.subtitle_size,
        leading=COVER.subtitle_leading,
        textColor=cover_green,
    )
    subtitle = Paragraph("Evaluation Report", subtitle_style)
    subtitle.wrap(page_w - left - COVER.text_right_margin, 80)
    subtitle.drawOn(canvas, left, page_h - COVER.subtitle_y_offset)

    canvas.setFillColor(cover_green)
    canvas.setFont(FONT_REGULAR, COVER.date_size)
    canvas.drawString(left, page_h - COVER.date_y_offset, "May 2026")

    canvas.setFillColor(white)
    canvas.setFont(FONT_BOLD, 10)
    canvas.drawString(left, COVER.bottom_bar_height + 24, "Analytics Centre of Excellence")
    canvas.restoreState()


def build_report():
    doc = LinkedContentsDocTemplate(
        OUTPUT_PATH,
        pagesize=A4,
        leftMargin=PAGE_SPEC.left_margin,
        rightMargin=PAGE_SPEC.right_margin,
        topMargin=PAGE_SPEC.top_margin,
        bottomMargin=PAGE_SPEC.bottom_margin,
    )

    width = A4[0] - doc.leftMargin - doc.rightMargin
    story = []

    # --- Styles ---
    styles = build_paragraph_styles(REPORT_FONTS)
    title_style = styles["title"]
    subtitle_style = styles["subtitle"]
    h1 = styles["h1"]
    evaluation_h1 = styles["evaluation_h1"]
    h2 = styles["h2"]
    h3 = styles["h3"]
    h3_after_callout = ParagraphStyle("H3AfterCallout", parent=h3, spaceBefore=0)
    appendix_subheading = ParagraphStyle(
        "AppendixSubheading",
        parent=h3,
        leftIndent=0,
        firstLineIndent=0,
    )
    h4 = styles["h4"]
    mini_heading = styles["mini_heading"]
    metric_context = styles["metric_context"]
    body = styles["body"]
    section_intro = styles["section_intro"]
    body_bold = styles["body_bold"]
    bullet_style = styles["bullet"]
    evidence_bullet_style = styles["evidence_bullet"]
    quote_style = styles["quote"]
    note_style = styles["note"]
    chart_title = styles["chart_title"]
    copilot_section_header = ParagraphStyle(
        "CopilotSectionHeader",
        parent=h2,
        textColor=OCE_PLUM,
    )
    toc_level_0 = ParagraphStyle(
        "TOCLevel0",
        parent=body,
        fontName=FONT_BOLD,
        fontSize=10,
        leading=15,
        leftIndent=0,
        firstLineIndent=0,
        spaceBefore=5,
        textColor=DEWR_DARK_GREY,
    )
    toc_level_1 = ParagraphStyle(
        "TOCLevel1",
        parent=body,
        fontSize=9,
        leading=13,
        leftIndent=14,
        firstLineIndent=0,
        spaceBefore=2,
        textColor=DEWR_TEXT_GREY,
    )
    red_h2 = ParagraphStyle("RedH2", parent=h2, textColor=DEWR_RED)
    red_h3 = ParagraphStyle("RedH3", parent=h3, textColor=DEWR_RED)
    red_mini_heading = ParagraphStyle("RedMiniHeading", parent=mini_heading, textColor=DEWR_RED)
    red_body = ParagraphStyle("RedBody", parent=body, textColor=DEWR_RED)
    red_note_style = ParagraphStyle("RedNote", parent=note_style, textColor=DEWR_RED)

    def bullet(text):
        return Paragraph(f"<bullet>&bull;</bullet> {text}", bullet_style)

    toc_ids = {}

    def toc_heading(text, style, level=0, in_toc=True):
        base = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-") or "section"
        count = toc_ids.get(base, 0) + 1
        toc_ids[base] = count
        key = base if count == 1 else f"{base}-{count}"
        paragraph = Paragraph(text, style)
        if in_toc:
            paragraph._toc_text = text
            paragraph._toc_level = level
            paragraph._bookmark_name = key
        return paragraph

    def red_bullet(text):
        return Paragraph(f'<bullet><font color="#91040D">&bull;</font></bullet> <font color="#91040D">{text}</font>', bullet_style)

    def evidence_bullet(text):
        return Paragraph(f"<bullet>&bull;</bullet> {text}", evidence_bullet_style)

    limitation_bullet_style = ParagraphStyle(
        'LimitationBullet',
        parent=bullet_style,
        leading=VISUAL_TEXT.callout_text_leading,
        spaceAfter=7,
    )

    def limitation_bullet(text):
        return Paragraph(f"<bullet>&bull;</bullet> {text}", limitation_bullet_style)

    def callout(text, color=DEWR_DARK_GREY):
        return CalloutBox(text, width, bg_color=color)

    def key_finding(text, color=DEWR_GREEN):
        return KeyFindingBar(text, width, border_color=color)

    def visual_title(text):
        return Paragraph(text, VISUAL_STYLES["visual_title"])

    figure_counter = {"value": 0}

    figure_label_style = ParagraphStyle(
        "BainFigureLabel",
        parent=VISUAL_STYLES["visual_title"],
        fontName=FONT_BOLD,
        fontSize=8.5,
        leading=11,
        textColor=DEWR_DARK_GREY,
        alignment=TA_CENTER,
        spaceBefore=2,
        spaceAfter=4,
    )
    figure_label_grey_style = ParagraphStyle(
        "BainFigureLabelGrey",
        parent=figure_label_style,
        textColor=DEWR_DARK_GREY,
    )
    figure_label_center_style = ParagraphStyle(
        "BainFigureLabelCenter",
        parent=figure_label_grey_style,
        alignment=TA_CENTER,
    )

    def figure_label(text, style=figure_label_style):
        figure_counter["value"] += 1
        number = figure_counter["value"]
        return Paragraph(
            f"Figure {number}: {text}",
            style,
        )

    source_note_style = ParagraphStyle(
        "SourceNoteIndented",
        parent=note_style,
        fontName=FONT_REGULAR,
        fontSize=8,
        leftIndent=0,
        rightIndent=8,
        leading=8.5,
        spaceBefore=0,
        spaceAfter=5,
    )

    def source_note(text):
        return Paragraph(text, source_note_style)

    def section_divider():
        table = Table([[""]], colWidths=[width])
        table.setStyle(TableStyle([
            ("LINEABOVE", (0, 0), (-1, 0), LINES.fine, DEWR_LIGHT_GREY),
            ("TOPPADDING", (0, 0), (-1, -1), 0),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
            ("LEFTPADDING", (0, 0), (-1, -1), 0),
            ("RIGHTPADDING", (0, 0), (-1, -1), 0),
        ]))
        return table

    def access_evidence_table(red=False):
        table_text_color = DEWR_RED if red else DEWR_DARK_GREY
        table_value_color = DEWR_RED if red else DEWR_DARK_GREY
        table_highlight_color = DEWR_RED if red else DEWR_DARK_GREEN
        header_style = visual_style(
            "AccessEvidenceHeader",
            "table_header",
            alignment=TA_CENTER,
            textColor=table_text_color,
        )
        measure_header_style = visual_style(
            "AccessEvidenceMeasureHeader",
            "table_header",
            parent=header_style,
            alignment=TA_LEFT,
        )
        measure_style = visual_style(
            "AccessEvidenceMeasure",
            "table_label",
            textColor=table_text_color,
        )
        value_style_dark = visual_style(
            "AccessEvidenceValueDark",
            "table_value",
            alignment=TA_CENTER,
            textColor=table_value_color,
        )
        value_style_green = visual_style(
            "AccessEvidenceValueGreen",
            "table_value",
            parent=value_style_dark,
            textColor=table_highlight_color,
        )
        value_style_red = visual_style(
            "AccessEvidenceValueRed",
            "table_value",
            parent=value_style_dark,
            textColor=DEWR_RED,
        )
        data = [
            [
                Paragraph("MEASURE", measure_header_style),
                Paragraph("COPILOT CHAT", header_style),
                Paragraph("M365 COPILOT", header_style),
                Paragraph("HIGH EXPERIENCE", header_style),
                Paragraph("LOW EXPERIENCE", header_style),
            ],
            [
                Paragraph("Public Generative AI rated at least moderately useful", measure_style),
                Paragraph(marked_value("81.8%", "82.4%"), value_style_green),
                Paragraph(marked_value("78.6%", "77.8%"), value_style_dark),
                Paragraph("90.9%", value_style_dark),
                Paragraph("74.4%", value_style_dark),
            ],
            [
                Paragraph("Copilot rated at least moderately useful", measure_style),
                Paragraph(marked_value("69.7%", "70.6%"), value_style_dark),
                Paragraph(marked_value("92.9%", "92.6%"), value_style_green),
                Paragraph("72.7%", value_style_dark),
                Paragraph("84.6%", value_style_dark),
            ],
            [
                Paragraph("Public Generative AI used weekly or more", measure_style),
                Paragraph(marked_value("54.5%", "52.9%"), value_style_green),
                Paragraph(marked_value("50.0%", "51.9%"), value_style_dark),
                Paragraph("77.3%", value_style_dark),
                Paragraph("35.9%", value_style_dark),
            ],
            [
                Paragraph("Copilot used weekly or more", measure_style),
                Paragraph(marked_value("57.6%", "58.8%"), value_style_dark),
                Paragraph(marked_value("85.7%", "85.2%"), value_style_green),
                Paragraph("81.8%", value_style_dark),
                Paragraph("64.1%", value_style_dark),
            ],
            [
                Paragraph("Public Generative AI added value beyond Copilot", measure_style),
                Paragraph(marked_value("75.0%", "73.5%"), value_style_dark),
                Paragraph(marked_value("82.1%", "81.5%"), value_style_green),
                Paragraph("90.9%", value_style_dark),
                Paragraph("69.2%", value_style_dark),
            ],
        ]
        first_w = width * 0.34
        col_w = (width - first_w) / 4
        table = Table(
            data,
            colWidths=[first_w, col_w, col_w, col_w, col_w],
            rowHeights=[44] + [36] * (len(data) - 1),
        )
        table.setStyle(access_evidence_table_style())
        return table

    def pillar_card(number, title, bullets, is_hero=False):
        return KeyFindingPillarCard(
            number, title, bullets, width,
            is_hero=is_hero, accent_color=DEWR_GREEN,
        )

    def sp(h=RHYTHM.paragraph_gap):
        return Spacer(1, h)

    def para_gap():
        return sp(RHYTHM.paragraph_gap)

    def tight_gap():
        return sp(RHYTHM.tight_gap)

    def visual_gap():
        return sp(RHYTHM.visual_gap)

    def note_gap():
        return sp(RHYTHM.note_gap)

    def after_note_gap():
        return sp(RHYTHM.after_note_gap)

    def section_gap():
        return sp(RHYTHM.section_gap)

    def visual_spacer():
        return sp(SPACING.lg)

    def after_figure_label_gap():
        return visual_spacer()

    # ==============================
    # COVER PAGE
    # ==============================
    story.append(visual_gap())
    story.append(PageBreak())

    # ==============================
    # CONTENTS
    # ==============================
    toc = TableOfContents()
    toc.dotsMinLevel = 0
    toc.levelStyles = [toc_level_0, toc_level_1]
    story.append(Paragraph("Contents", evaluation_h1))
    story.append(after_note_gap())
    story.append(toc)
    story.append(para_gap())
    story.append(PageBreak())

    # ==============================
    # EXECUTIVE SUMMARY
    # ==============================
    quote_author_style = ParagraphStyle(
        "ExecutiveSummaryQuoteAuthor",
        parent=quote_style,
        fontName=FONT_BOLD,
        textColor=DEWR_DARK_GREY,
        spaceBefore=0,
        leftIndent=0,
        rightIndent=0,
        borderPadding=0,
    )
    executive_quote_style = ParagraphStyle(
        "ExecutiveSummaryPullQuote",
        parent=quote_style,
        leftIndent=0,
        rightIndent=0,
        borderPadding=0,
        spaceAfter=8,
    )

    story.append(toc_heading("Executive summary", evaluation_h1, 0))
    executive_quote = Table(
        [[
            "",
            [
                Paragraph(
                    "“Australians deserve to benefit from the possibilities that new technologies bring. "
                    "Generative artificial intelligence (AI) provides us with the means to improve public "
                    "services, make it easier for people and businesses to interact with government, and to "
                    "help manage employee workloads.”",
                    executive_quote_style,
                ),
                Paragraph("Senator the Hon Katy Gallagher", quote_author_style),
            ],
        ]],
        colWidths=[5, width - 5],
        hAlign="LEFT",
    )
    executive_quote.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), DEWR_OFF_WHITE),
        ("BACKGROUND", (0, 0), (0, 0), DEWR_GREEN),
        ("LEFTPADDING", (0, 0), (0, 0), 0),
        ("RIGHTPADDING", (0, 0), (0, 0), 0),
        ("TOPPADDING", (0, 0), (-1, -1), PANEL_TOKENS.cell_pad_y),
        ("BOTTOMPADDING", (0, 0), (-1, -1), PANEL_TOKENS.cell_pad_y),
        ("LEFTPADDING", (1, 0), (1, 0), PANEL_TOKENS.cell_pad_x),
        ("RIGHTPADDING", (1, 0), (1, 0), PANEL_TOKENS.cell_pad_x),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ]))
    story.append(executive_quote)
    story.append(section_gap())

    summary_finding_style = ParagraphStyle(
        "StructuredSummaryFinding",
        parent=body,
        spaceBefore=0,
        spaceAfter=0,
    )
    summary_number_style = ParagraphStyle(
        "StructuredSummaryFindingNumber",
        parent=body,
        fontName=FONT_BOLD,
        fontSize=body.fontSize,
        leading=body.leading,
        textColor=DEWR_DARK_GREY,
    )

    def structured_finding(number, label, text):
        finding_table = Table(
            [[
                Paragraph(str(number), summary_number_style),
                Paragraph(f"<b>{label}:</b> {text}", summary_finding_style),
            ]],
            colWidths=[20, width - 20],
            hAlign="LEFT",
        )
        finding_table.setStyle(TableStyle([
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("LEFTPADDING", (0, 0), (-1, -1), 0),
            ("RIGHTPADDING", (0, 0), (-1, -1), 0),
            ("TOPPADDING", (0, 0), (-1, -1), 0),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
        ]))
        return finding_table

    story.append(toc_heading("Preface", copilot_section_header, 1, in_toc=False))
    story.append(Paragraph(
        "The AI Plan for the Australian Public Service outlines a clear expectation that the APS "
        "will utilise AI to improve the way we deliver for the Australian Public. It also outlines "
        "an expectation that the APS will utilise Public Generative AI safely and ethically. The "
        "insights from this trial of Public Generative AI tools will support DEWR to make strategic decisions about the future "
        "AI services available to our people and will inform DEWR’s AI Strategy.",
        body))
    story.append(Paragraph(
        "DEWR currently provides all employees with access to Generative AI. All employees can "
        "access the free Microsoft Copilot Chat and just under 10% can access the paid M365 "
        "Copilot with greater integration capability. In March 2026, nearly 90% of all staff used "
        "one of these tools, entering over 250,000 prompts, or about 4 prompts per person every "
        "workday.",
        body))
    story.append(Paragraph(
        "In January 2026, DEWR ran a trial in which 5% of employees were provided access to "
        "Public Generative AI, in addition to their existing copilot access, for a period "
        "of 6 weeks. The trial cohort was selected at random and stratified to ensure "
        "representation across Groups, across Copilot Chat and M365 Copilot users, and across APS "
        "levels. The tools were the free versions of Open AI’s ChatGPT, Google’s Gemini, and "
        "Anthropic’s Claude, which could be accessed in web browsers. Staff were provided with "
        "both technical and governance instruction, including on what could be uploaded to the "
        "tools (unclassified information only). Technical protections were established to reduce "
        "the likelihood of classified (i.e., OFFICIAL - sensitive or PROTECTED) being uploaded to "
        "the tools.",
        body))
    story.append(CondPageBreak(180))
    story.append(Paragraph(
        "At the conclusion of the trial period, all participants were invited to complete a "
        "voluntary survey about their experience using Microsoft Copilot and the Public "
        "Generative AI tools. The trial was intended to assess:",
        body))
    story.append(Paragraph("1. the current productivity of Copilot (both versions)", body))
    story.append(Paragraph(
        "2. whether the Public Generative AI provided additional value beyond Copilot",
        body))
    story.append(Paragraph(
        "3. the relative utility of each of the selected Public Generative AI",
        body))
    story.append(Paragraph(
        "4. the potential productivity benefits from the Public Generative AI",
        body))
    story.append(Paragraph(
        "5. the risks and degree of concern around the Public Generative AI and AI generally",
        body))
    story.append(Paragraph(
        "In total, 104 trial participants (52%) responded to the survey.",
        body))
    story.append(PageBreak())

    # ==============================
    # KEY FINDINGS
    # ==============================
    story.append(KeepTogether([
        toc_heading("Key findings", copilot_section_header, 1, in_toc=False),
        after_note_gap(),
        pillar_card(
            1,
            "Microsoft Copilot",
            [
                "<b>Copilot already saves us 3 to 6 hours per week.</b> M365 Copilot users saved nearly 6 hours a week (about 15%), almost double the 2.8 hours a week (about 8%) reported by Copilot Chat users. As a result, an M365 licence pays for itself within the first two weeks.",
                "<b>All versions of Copilot were used for summarising, editing and revision, and drafting.</b> Compared to Copilot Chat, M365 Copilot was used more for complex knowledge work such as research, problem solving and ideation (67.7% of users, compared to 43.6% of Chat users), and for planning or meeting preparation (35.5% of users compared to 12.8% of Chat).",
                "<b>M365 Copilot is associated with higher reported productivity across both workforce segments and organisational groups.</b> Corporate and Enabling, Employment and Workforce, and Skills groups reported the largest relative uplifts (2.5x, 2.2x, and 1.9x respectively), while Workplace Relations reported only slightly higher productivity over Copilot Chat (1.2x). Across the department, EL users reported M365 Copilot time savings at 2.7x the rate of Copilot Chat users, compared with 1.7x for APS users.",
            ],
            is_hero=True,
        ),
        Spacer(1, 10),
        pillar_card(
            2,
            "Public Generative AI: ChatGPT, Gemini, and Claude",
            [
                "<b>Public Generative AI were used mainly for core knowledge-work tasks, especially research, summarising, editing and drafting.</b> Claude had the strongest research profile, with 73.2% of Claude users using it for research, problem solving or ideation, while ChatGPT and Gemini were used more broadly across common writing and information tasks. Public Generative AI was used much less for planning and meeting preparation, highlighting a key limitation of public generative AI for tasks that depend on integration with department systems.",
                "<b>ChatGPT had the widest uptake (92% of users), but Claude showed the strongest usefulness signal.</b> Claude was rated at least very useful by 46.3% of users (compared to 29.7% for Gemini and 28.6% for ChatGPT), and was the most requested tool to continue after the trial (63%, compared to 54% and 43% for ChatGPT and Gemini). Overall, demand for continued access to at least one of public generative AI was strong (72%), with experienced or highly experienced AI users more emphatic than less experienced users. This suggests staff benefit from access to different tools for different types of work, rather than there being a single best option.",
                "<b>Most users (92%) reported at least one limitation from public generative AI.</b> The main barriers were a lack of integration with department systems (49%) and the usage limits of the free tools (41%). Usage caps were especially common among experienced users (60%), indicating that the free versions were most likely to constrain staff who had the capability to identify higher-value use cases and use the tools more productively.",
                "<b>Most respondents (75%) were comfortable using the tools, but key concerns were raised.</b> Ethical considerations were more commonly reported (12% of respondents) than security concerns (3% of respondents). Users who were more comfortable with the tools were more likely to use more 'risky' features such as uploading files (48%) than users who were not comfortable (27%). Education and training play a key role in building comfort. Key concerns related to uncertainty about what information could be entered and how to validate results. Similarly, staff who rated the introductory guidance and splash screens as effective were more likely to be comfortable (82.5%) than those who did not (60%). Future risk mitigation may benefit more from clearer guidance, clarifying boundary cases and strengthening user judgement than from expanding technical controls alone.",
            ],
        ),
    ]))
    story.append(PageBreak())

    # ==============================
    # EVALUATION FINDINGS
    # ==============================
    story.append(toc_heading("Evaluation findings", evaluation_h1, 0))

    # Section 1: Microsoft M365 Copilot and Copilot Chat
    story.append(toc_heading("Microsoft M365 Copilot and Copilot Chat", copilot_section_header, 1))
    story.append(CalloutSignalsPanel(
        "Copilot already delivers material productivity value, but benefits are tiered by "
        "access: compared with Copilot Chat, integrated M365 Copilot produced stronger time "
        "savings, deeper engagement and a broader task footprint:",
        width,
        [
            ("2.0x", "More weekly time saved"),
            (marked_value("1.9x", "1.8x"), "More likely to rate very or extremely useful"),
            (marked_value("1.5x", "1.4x"), "More likely to use weekly or more often"),
        ],
        primary_count=1,
        note="M365 Copilot relative to Copilot Chat",
    ))
    story.append(sp(9))
    story.append(Paragraph(
        "A total of 71 survey respondents indicated that they used copilot and answered questions "
        "about how they used it, how often, and how much time they believed it saved them.",
        section_intro))

    # Time savings
    story.append(Paragraph("M365 Copilot users reported substantially higher time savings", h3))
    story.append(Paragraph(
        "M365 Copilot users reported average time savings of 5.7 hours per week, compared with "
        "2.8 hours per week for Copilot Chat users. This means M365 Copilot users reported "
        "roughly twice the weekly time savings of Copilot Chat users.", body))
    story.append(visual_spacer())
    story.append(TimeSavingsPanel(width))
    story.append(tight_gap())
    story.append(figure_label("Average weekly time saved by Copilot version", figure_label_center_style))
    story.append(after_figure_label_gap())
    story.append(Paragraph(
        f"The reported {red_markup(marked_value('68 minutes per day', '69 minutes per day'))} for M365 Copilot users is in the same broad range as the "
        "DTA whole-of-government Copilot trial, which identified around an hour a day of perceived "
        "savings in high-frequency tasks such as summarising, drafting and meeting support.",
        body))
    story.append(Paragraph(
        "As of 1 July 2026, the cost for an M365 licence is expected to be $299.54 per year. The "
        "average APS employee earns $114,938 per year, which, spread across approximately 250 "
        "working days, equates to approximately $61 per hour. Given that M365 Copilot saves an "
        "additional 2.9 hours per week compared to Copilot Chat, a licence starts to deliver "
        "productivity increases by the end of the second week.",
        body))
    story.append(PageBreak())

    # Usefulness and frequency
    story.append(KeepTogether([
        Paragraph("Higher time savings were matched by deeper engagement", h3),
        Paragraph(
            "The productivity gap was reinforced by engagement signals. M365 Copilot users were "
            "more likely to rate Copilot as highly useful and to use it more frequently.", body),
        visual_spacer(),
        CopilotEngagementDeltaPanel(width),
        tight_gap(),
        figure_label("Copilot engagement and value signals by version"),
    ]))

    # Department usage and value
    story.append(KeepTogether([
        Paragraph("Copilot usage and value across the department", h3),
        Paragraph(
            "M365 Copilot is associated with higher reported productivity across both workforce segments and organisational groups. EL and APS users both reported greater weekly time savings with M365 Copilot than with Copilot Chat, with the productivity improvements strongest for EL users who reported M365 Copilot time savings at 2.7x the rate of Copilot Chat users.",
            body),
        Paragraph(
            "A similar pattern appears across organisational groups, where Corporate and Enabling, Employment and Workforce, and Skills groups reported the largest relative uplifts (2.5x, 2.2x, and 1.9x respectively), while Workplace Relations reported only slightly higher productivity over Copilot Chat (1.2x).",
            body),
        visual_spacer(),
    ]))
    story.append(Paragraph("By employee classification", body_bold))
    story.append(sp(4))
    story.append(M365ValueReachExhibit(
        width,
        [
            ("CLASSIFICATION LEVEL", [
                ("EL level", "5.4 hrs", "2.0 hrs", "2.7x", "10%", True),
                ("APS level", "6.0 hrs", "3.5 hrs", "1.7x", "5%", False),
            ]),
        ],
        show_section_titles=False,
    ))
    story.append(tight_gap())
    story.append(figure_label("M365 Copilot Time Savings and Licence Reach by APS Level"))
    story.append(FooterNoteMarker(
        "Note: M365 Value = The relative time savings reported for M365 licence holders compared to Copilot Chat users. "
        "M365 licence = The proportion of each group who have an M365 licence."))
    story.append(PageBreak())
    story.append(Paragraph("By Group", body_bold))
    story.append(sp(4))
    story.append(M365ValueReachExhibit(
        width,
        [
            ("ORGANISATIONAL GROUP", [
                ("Corporate and Enabling", "6.3 hrs", "2.5 hrs", "2.5x", "8%", True),
                ("Employment and Workforce", "6.3 hrs", "2.9 hrs", "2.2x", "7%", False),
                ("Skills and Training", "5.4 hrs", "2.9 hrs", "1.9x", "6%", False),
                ("Workplace Relations", "5.0 hrs", "4.0 hrs", "1.2x", "11%", False),
            ]),
        ],
        show_section_titles=False,
    ))
    story.append(tight_gap())
    story.append(figure_label("M365 Copilot value and licence reach by organisational group"))
    story.append(FooterNoteMarker(
        "Note: M365 value = relative time savings for M365 licence holders vs Copilot Chat users; "
        "M365 licence = proportion of each group with an M365 licence. "
        "Jobs and Skills Australia was excluded because of low sample size."))
    story.append(after_figure_label_gap())

    # Task types
    story.append(KeepTogether([
        Paragraph("M365 Copilot users reported a broader task footprint", h3),
        sp(RHYTHM.heading_gap),
        Paragraph(
            "All versions of Copilot were used most often for summarising, editing and revision, "
            "and drafting, but M365 Copilot users reported greater use across more task types on "
            "average than Copilot Chat users.", body),
        sp(6),
        evidence_bullet(
            "M365 Copilot users were more likely to use it for research, problem solving and "
            "ideation, and for planning or meeting preparation."),
        evidence_bullet(
            "These tasks are typically more complex than drafting or summarising alone, suggesting "
            "M365 Copilot access may be associated with broader use in higher-value knowledge-work "
            "activities."),
        visual_spacer(),
        TaskFootprintExhibit(width),
        tight_gap(),
        figure_label("Task footprint by Copilot version"),
    ]))

    # Section 2: Public Generative AI
    story.append(PageBreak())
    story.append(toc_heading("Public Generative AI uptake and use", copilot_section_header, 1))
    story.append(callout(
        "Public Generative AI provided additional value beyond Copilot, especially for broad knowledge work, "
        "but the benefit was capability-dependent and constrained by lack of integration, free-tool "
        "limits, and user uncertainty at practical risk boundaries."))
    story.append(ValueSignalsPanel(width, [
        ("80%", "Rated at least one public generative AI useful"),
        ("72%", "Said public generative AI add value beyond Copilot"),
        ("72%", "Wanted continued access"),
        ("53%", "Used public generative AI at least weekly"),
    ], primary_count=1))
    story.append(sp(9))
    story.append(Paragraph(
        "A total of 61 survey respondents indicated that they used Public Generative AI "
        "during the trial and answered questions about how they used it, how often, and how "
        "much time they believed it saved them.", section_intro))

    # Tool comparison
    story.append(Paragraph("ChatGPT had the widest reach; Claude had the strongest value signals", h3))
    story.append(Paragraph(
        "ChatGPT was the access point for most trial users, while Claude showed the strongest "
        "usefulness signal, with:",
        body))
    story.append(bullet("46.3% of Claude users rating it very or extremely useful, compared with"))
    story.append(bullet("29.7% for Gemini and"))
    story.append(bullet("28.6% for ChatGPT."))
    story.append(sp(4))
    story.append(Paragraph(
        "This suggests the public-tool choice was not simply about uptake; different tools played different roles.",
        body))
    story.append(visual_spacer())
    story.append(EvidenceMatrixPanel(
        width,
        "MEASURE",
        ["ChatGPT", "Claude", "Gemini"],
        [
            ("Used tool during trial", ["92%", "67%", "61%"], 0),
            ("Rated at least moderately useful", ["62.5%", "70.7%", "64.9%"], 1),
            ("Rated very or extremely useful", ["28.6%", "46.3%", "29.7%"], 1),
            ("Wanted continued access", ["54%", "63%", "43%"], 1),
        ],
        first_col_ratio=0.43,
    ))
    story.append(tight_gap())
    story.append(figure_label("Public Generative AI Tool Usage and Usefulness by Tool"))

    # Task types
    story.append(CondPageBreak(320))
    story.append(Paragraph("Public Generative AI were mainly used for broad knowledge work", h3))
    story.append(Paragraph(
        "Use clustered around general knowledge-work tasks rather than specialised or "
        "administrative workflows. Research, summarising, editing and drafting were the "
        "dominant use cases for public generative AI, while Copilot was still more commonly used for "
        "summarising, editing and revision, and drafting tasks.", body))
    story.append(visual_spacer())
    story.append(AllToolTaskProfilePanel(width))
    story.append(tight_gap())
    story.append(figure_label("Task Footprint across Public Generative AI Tools and Copilot Versions"))
    story.append(after_figure_label_gap())
    story.append(Paragraph(
        "Tool use profiles varied by task. Claude had the strongest research profile, with "
        "73.2% of Claude users using it for research, problem solving or generating ideas. "
        "This placed it ahead of M365 Copilot and significantly ahead of Copilot Chat.",
        body))
    story.append(bullet(
        "<b>Coding or data work:</b> Claude was notably higher at 26.8%, compared with "
        "13.5% for Gemini and 10.7% for ChatGPT, suggesting a stronger specialist-use profile."))
    story.append(bullet(
        "<b>Research, problem solving and ideation:</b> Claude reached 73.2%, ahead of "
        "M365 Copilot and well ahead of Copilot Chat, suggesting public generative AI can compete "
        "with licensed tools for complex knowledge work."))
    story.append(bullet(
        "<b>Planning and meeting preparation:</b> M365 Copilot was substantially higher than "
        "Copilot Chat and public generative AI, suggesting integration with email, SharePoint "
        "and meetings remains a clear M365 advantage."))

    story.append(CondPageBreak(220))
    story.append(Paragraph("Most staff want to continue using the Public Generative AI", h3))
    story.append(Paragraph(
        "<b>72% of respondents</b> wanted continued access to at least one public generative AI, but "
        "demand was uneven across tools and user groups.",
        body))
    story.append(Paragraph(
        "Claude recorded the highest continuation demand, followed by ChatGPT and then Gemini, "
        "showing a clear step-down in interest across the three public generative AI.",
        body))
    story.append(visual_spacer())
    story.append(ContinuationDemandPanel(width))
    story.append(tight_gap())
    story.append(figure_label("Demand for Continued Access by Public Generative AI Tool"))
    story.append(after_figure_label_gap())
    story.append(bullet(
        "M365 Copilot users were less likely to want to continue using public generative AI "
        "than Copilot Chat users."))
    story.append(bullet(
        "Claude was the most requested tool to continue after the trial, and interest in "
        "continuing Claude was higher among M365 Copilot users than Copilot Chat users."))
    story.append(PageBreak())
    story.append(toc_heading("Productivity from Public Generative AI", copilot_section_header, 1))
    story.append(callout(
        "Public Generative AI productivity gains were real but capability-dependent: value was strongest "
        "among experienced AI users, staff without M365 Copilot access, and tasks where public "
        "generative AI offered capability beyond Copilot, positioning it as a complement to enterprise "
        "AI rather than a replacement."))
    story.append(sp(9))
    story.append(Paragraph("Copilot Chat and M365 Copilot users get different value from Public Generative AI", h3_after_callout))
    story.append(Paragraph(
        "Overall, both M365 Copilot and Copilot Chat users rated the Public Generative AI as useful at "
        "comparable levels. M365 licence holders, who were more likely to rate Copilot as useful and to use it "
        "more frequently, were also more likely to report getting more value out of the Public Generative AI on top "
        "of Copilot.",
        body))
    story.append(Paragraph(
        "Furthermore, while they reported value from Public Generative AI, they used it at a comparable rate "
        "to Copilot Chat users. This suggests that M365 Copilot users, who tend to be more experienced AI users, "
        "were better equipped to find complementary use cases for public generative AI while continuing to use Copilot "
        "frequently. In contrast, Copilot Chat users may have been more likely to substitute Copilot for the "
        "Public Generative AI.",
        body))
    story.append(visual_spacer())
    story.append(KeepTogether([
        access_evidence_table(),
        tight_gap(),
        figure_label("Public Generative AI and Copilot Ratings"),
        FooterNoteMarker(
            "Note: High Experience = Highly Experienced or Experienced; "
            "Low Experience = Some or No or Basic Experience."
        ),
    ]))
    story.append(para_gap())

    # Prior experience variation
    story.append(CondPageBreak(250))
    story.append(KeepTogether([
        Paragraph("Experienced users gained more value", h3),
        Paragraph(
            "Prior Gen AI experience was also associated with stronger reported outcomes. Experienced and highly "
            "experienced respondents were more likely to report significant added value from public generative AI than "
            "respondents with lower levels of prior Gen AI experience. Higher-experience users also reported "
            "deeper usefulness: 73% rated at least one public generative AI very or extremely useful, compared with 46% "
            "some prior Gen AI experience and 39% no/basic prior Gen AI experience.", body),
        visual_spacer(),
        EvidenceMatrixPanel(
            width,
            "MEASURE",
            [
                "Experienced or highly<br/>experienced",
                "Some prior<br/>experience",
                "No or basic<br/>experience",
            ],
            [
                ("Reported some or significant added value over Copilot", ["91%", "73%", "67%"], 0),
                ("Rated at least one public generative AI very or extremely useful", ["73%", "46%", "39%"], 0),
                ("Strongly wanted continued access", ["55%", "31%", "15%"], 0),
                ("Rated a public generative AI better than Copilot on at least one dimension", ["86%", "69%", "69%"], 0),
            ],
            first_col_ratio=0.44,
            row_h=30,
            header_body_gap=8,
        ),
        tight_gap(),
        figure_label("Prior AI experience was the clearest signal of public-tool value"),
    ]))
    story.append(after_figure_label_gap())
    story.append(Paragraph(
        "They were also more likely to rate at least one public generative AI better than Copilot on at least one "
        "comparison dimension, such as output quality, time savings or responsiveness, and to strongly want "
        "continued access.",
        body))
    story.append(Paragraph(
        "This pattern is consistent with experience acting as an enabling factor for value realisation. While "
        "the results are not causal, they suggest that capability uplift may increase the likelihood that staff "
        "can identify higher-value use cases and realise more benefits from both enterprise and public generative AI, "
        "although some of this relationship may also reflect differences in role, task complexity, or pre-existing "
        "digital capability.",
        body))

    # Other segment variation
    story.append(KeepTogether([
        Paragraph("Executive level employees got more value from the tools than APS staff", h3),
        tight_gap(),
        Paragraph(
            "EL users were more likely than APS users to say public generative AI added value beyond Copilot, "
            "despite similar usage frequency, while APS users were more likely to rate public generative AI "
            "as at least moderately useful.",
            body),
        visual_spacer(),
        EvidenceMatrixPanel(
            width,
            "MEASURE",
            ["APS level", "EL level"],
            [
                ("Added value beyond Copilot", ["66.7%", "78.6%"], 1),
                ("Public Generative AI used weekly or more", ["51.5%", "53.6%"], 1),
                ("Public Generative AI rated at least moderately useful", ["87.9%", "71.4%"], 0),
                ("Copilot rated at least moderately useful", ["84.8%", "75.0%"], 0),
            ],
            first_col_ratio=0.58,
            row_h=28,
            header_body_gap=6,
        ),
        tight_gap(),
        figure_label("Public Generative AI and Copilot Ratings by APS Level"),
    ]))
    story.append(after_figure_label_gap())
    story.append(Paragraph(
        "This difference may reflect variation in work type across classification levels, including "
        "task complexity and exposure to higher-value knowledge work, differences in capability, or "
        "familiarity with AI tools. Further research is required to disentangle these factors.",
        body))
    story.append(para_gap())
    story.append(CondPageBreak(330))
    story.append(KeepTogether([
        Paragraph("Organisational group", mini_heading),
        tight_gap(),
        Paragraph(
            "Group-level results suggest that Copilot usefulness and perceived added value from Public Generative AI "
            "were not always aligned. Workplace Relations recorded the strongest added-value result, with "
            "85.7% saying Public Generative AI provided value beyond Copilot, compared with 78.6% rating Copilot "
            "as at least moderately useful.", body),
        sp(4),
        Paragraph(
            "By contrast, Corporate and Enabling and Employment and Workforce recorded high Copilot "
            "usefulness but lower added-value results for Public Generative AI. Skills and Training recorded the "
            "weakest results on both measures, suggesting lower perceived value across both Copilot and "
            "Public Generative AI rather than a pattern specific to Public Generative AI alone.", body),
        visual_spacer(),
        EvidenceMatrixPanel(
            width,
            "GROUP",
            ["Added value beyond Copilot", "Rated Copilot at least moderately useful"],
            [
                ("Corporate and Enabling", ["66.7%", "83.3%"], 1),
                ("Employment and Workforce", ["73.7%", "84.2%"], 1),
                ("Skills and Training", ["53.8%", "69.2%"], None),
                ("Workplace Relations", ["85.7%", "78.6%"], 0),
            ],
            first_col_ratio=0.32,
        ),
        tight_gap(),
        figure_label("Copilot Ratings by Organisational Group"),
        FooterNoteMarker("Note: Jobs and Skills Australia was excluded because of low sample size."),
    ]))

    # 2.6 Barriers
    story.append(CondPageBreak(260))
    story.append(Paragraph("Limitations were common and clustered around two broad signals", h3))
    story.append(tight_gap())
    story.append(Paragraph(
        "<b><font color=\"#404246\">92%</font></b> of respondents reported at least one limitation "
        "with at least one public generative AI. Limitations were widespread but concentrated in two "
        "practical barriers.",
        body))
    story.append(Paragraph("Integration was a common barrier", mini_heading))
    story.append(bullet("49% of survey respondents reported lack of integration as a barrier."))
    story.append(bullet(
        "This prevented users from seamlessly working between DEWR systems and the Public Generative AI."))
    story.append(bullet(
        "Lack of integration was common across all three tools, affecting 48% of ChatGPT users, "
        "49% of Gemini users and 51% of Claude users."))
    story.append(Paragraph("Request limits were the main access constraint", mini_heading))
    story.append(bullet(
        "41% of survey respondents reported the prompt/request limits offered by the free tools as a barrier."))
    story.append(bullet("This included instances where a limit was reached and work needed to stop."))
    story.append(bullet(
        "Limits were more acute for experienced users, with 59.1% of experienced and highly experienced AI users "
        "reporting caps as an issue when using public generative AI."))
    story.append(bullet("This compares with only 30.8% of less experienced users reporting this limitation."))
    story.append(bullet(
        "Free prompt or request limits were more concentrated in ChatGPT, reported by 36% of ChatGPT users, "
        "compared with 20% of Claude users and 5% of Gemini users."))
    story.append(visual_spacer())
    story.append(HorizontalBarPanel(width, None, [
        ("Lack of integration with internal systems or Microsoft 365 products", 49),
        ("Free prompt or request limits", 41),
        ("Misinterpreted prompts", 34),
        ("Difficulty with specialised topics", 34),
        ("Slow responses", 28),
        ("Fabricated content or hallucinations", 15),
    ], max_value=100, primary_count=2, row_h=CHART_LAYOUT.row_height_dense))
    story.append(tight_gap())
    story.append(figure_label("Reported Limitations of Public Generative AI Tools"))

    # Concerns, risks and safeguards
    story.append(CondPageBreak(300))
    story.append(toc_heading("Concerns, risks and safeguards", copilot_section_header, 1))
    story.append(callout(
        "Most survey respondents were comfortable and reported security concerns were rare. Survey "
        "results suggest safety communications and splash screens supported cautious use, while "
        "data-handling risks were mainly visible through copy and paste behaviour and user judgement."))
    story.append(ValueSignalsPanel(width, [
        ("75%", "Comfortable or very comfortable using public generative AI"),
        ("25%", "Uncomfortable using public generative AI"),
        (marked_value("12%", "11%"), "Ethical concerns encountered"),
        ("3%", "Reported specific security concerns"),
    ], primary_count=1))
    story.append(sp(9))
    story.append(Paragraph(
        "All respondents were asked about any concerns they have with public generative AI. They were "
        "also provided an opportunity to opt out of using the tools if they had concerns. The "
        "results suggest that future risk mitigation may benefit more from clarifying boundary "
        "cases and strengthening user judgement than from further restricting access or expanding "
        "technical controls alone.",
        section_intro))
    story.append(para_gap())

    story.append(Paragraph(
        "Most respondents were comfortable with the tools, though concerns were raised and guidance quality shaped perceptions.",
        h3))
    story.append(Paragraph(
        "75% of respondents were comfortable or very comfortable using public generative AI; 25% "
        "were uncomfortable. Concerns and comfort were not mutually exclusive, two-thirds of "
        "respondents who raised concerns were still comfortable using the tools. Of all "
        "respondents:",
        body))
    story.append(bullet(f"{red_markup(marked_value('12%', '11%'))} raised ethical concerns"))
    story.append(bullet("3% raised specific security concerns"))
    story.append(Paragraph(
        "Guidance quality appears to influence how staff feel about using the tools : 82.5% of "
        "respondents who rated both the introductory email and splash screens effective were "
        f"comfortable using the tools, compared with {red_markup(marked_value('60%', '61.9%'))} of those who did not.", body))

    story.append(Paragraph("Respondent comments showed uncertainty at practical boundaries", h3))
    story.append(Paragraph(
        "Respondents who indicated they had security or ethical concerns were provided an opportunity "
        "to explain these in free text responses. Their comments pointed to three practical "
        "uncertainty areas:", body))
    story.append(sp(4))
    story.append(bullet(
        "<b>Information boundaries:</b> uncertainty about what information was appropriate to enter, "
        "including unclassified but sensitive material."))
    story.append(bullet(
        "<b>Commercial sensitivity:</b> hesitation around material that was allowed by classification "
        "but still felt commercially sensitive."))
    story.append(bullet(
        "<b>Validation and safeguards:</b> need to check outputs and understand differences between "
        "public-tool and Copilot safeguards."))
    story.append(sp(4))
    story.append(Paragraph(
        "These suggest that further support is required to effectively triage and manage data and "
        "information for use with AI and that future risk mitigation may benefit more from clarifying "
        "boundary cases and strengthening user judgement than from further restricting access or "
        "expanding technical controls alone.", body))

    story.append(Paragraph("Comfort shaped data-sharing behaviour when using public generative AI", h3))
    story.append(Paragraph(
        "Users were advised not to upload classified information and Data Loss Protection was established "
        "to ensure classified information could not be uploaded. All users preferred copy-and-paste to "
        "document upload, and copy-and-paste rates were similar across comfort levels. Document upload, "
        "however, varied with comfort: comfortable users uploaded more than uncomfortable users, "
        "suggesting comfort increases willingness to use features that feel riskier.", body))
    story.append(visual_spacer())
    story.append(ComfortDataHandlingPanel(width))
    story.append(tight_gap())
    story.append(figure_label("Data Sharing Behaviour by Comfort with Public Generative AI Tools"))
    story.append(Paragraph("Safety communications were rated effective by most survey respondents", h3))
    story.append(tight_gap())
    story.append(ValueSignalsPanel(width, [
        ("74%", "Rated introductory emails at least moderately effective"),
        ("72%", "Rated splash screens at least moderately effective"),
        ("67%", "Rated both introductory emails and splash screens at least moderately effective"),
    ], primary_count=1))
    story.append(visual_spacer())
    story.append(Paragraph(
        "Most respondents rated the safety communications positively: the introductory email was rated "
        "moderately or highly effective by 74% of respondents, while splash screens were rated moderately "
        "or highly effective by 72%. Two-thirds of respondents rated both the email and splash screens "
        "effective.",
        body))
    story.append(Paragraph(
        "Upload blockers were less visible in the survey results: 16.7% of respondents noticed or rated "
        "upload blockers as effective, and no respondent rated upload blockers ineffective.",
        body))
    story.append(para_gap())

    def appendix_table(headers, rows, widths=None):
        header_style = visual_style(
            "AppendixTableHeader",
            "table_header",
            alignment=TA_LEFT,
            textColor=white,
        )
        cell_style = ParagraphStyle(
            "AppendixTableCell",
            parent=body,
            fontSize=7.5,
            leading=9.2,
            textColor=DEWR_DARK_GREY,
        )
        data = [[Paragraph(str(cell), header_style) for cell in headers]]
        data.extend([[Paragraph(str(cell), cell_style) for cell in row] for row in rows])
        table = Table(data, colWidths=widths or [width / len(headers)] * len(headers), repeatRows=1)
        table.hAlign = "LEFT"
        table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), DEWR_DARK_GREEN),
            ("TEXTCOLOR", (0, 0), (-1, 0), white),
            ("FONTNAME", (0, 0), (-1, 0), FONT_BOLD),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("LINEBELOW", (0, 0), (-1, 0), 0.5, DEWR_LIGHT_GREY),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [white, DEWR_OFF_WHITE]),
            ("LEFTPADDING", (0, 0), (-1, -1), PANEL_TOKENS.cell_pad_x_tight),
            ("RIGHTPADDING", (0, 0), (-1, -1), PANEL_TOKENS.cell_pad_x_tight),
            ("TOPPADDING", (0, 0), (-1, -1), PANEL_TOKENS.cell_pad_y_tight),
            ("BOTTOMPADDING", (0, 0), (-1, -1), PANEL_TOKENS.cell_pad_y_tight),
            ("BOTTOMPADDING", (0, 0), (-1, 0), TABLE_HEADER_RULE_GAP),
        ]))
        return table

    # Appendix
    story.append(PageBreak())
    story.append(toc_heading("Appendices", evaluation_h1, 0))
    story.append(toc_heading("Appendix 1: APS-level results", copilot_section_header, 1))
    story.append(Paragraph("EL level", appendix_subheading))
    story.append(appendix_table(
        ["Metric", "M365 Copilot", "Copilot Chat"],
        [
            ("% with M365 licence", "46%", "n/a"),
            ("Average weekly hours saved per user", "5.4 hrs", "2.0 hrs"),
            ("Rated Copilot very/extremely useful", "69%", "32%"),
            ("Used Copilot at least weekly", "75%", "53%"),
            ("Used Copilot daily", "75%", "21%"),
        ],
        [width * 0.52, width * 0.24, width * 0.24],
    ))
    story.append(para_gap())
    story.append(Paragraph("APS level", appendix_subheading))
    story.append(appendix_table(
        ["Metric", "M365 Copilot", "Copilot Chat"],
        [
            ("% with M365 licence", "42%", "n/a"),
            ("Average weekly hours saved per user", "6.0 hrs", "3.5 hrs"),
            ("Rated Copilot very/extremely useful", "67%", "38%"),
            ("Used Copilot at least weekly", "87%", "57%"),
            ("Used Copilot daily", "53%", "29%"),
        ],
        [width * 0.52, width * 0.24, width * 0.24],
    ))

    story.append(PageBreak())
    story.append(toc_heading("Appendix 2: Group-level results", copilot_section_header, 1))
    for group_name, group_rows in [
        ("Corporate and Enabling", [
            ("% with M365 licence", "33%", "n/a"),
            ("Average weekly hours saved per user", "6.2 hrs", "2.5 hrs"),
            ("Rated Copilot very/extremely useful", "80%", "50%"),
            ("Used Copilot at least weekly", "80%", "60%"),
            ("Used Copilot daily", "80%", "20%"),
        ]),
        ("Employment and Workforce", [
            ("% with M365 licence", "38%", "n/a"),
            ("Average weekly hours saved per user", "6.3 hrs", "2.9 hrs"),
            ("Rated Copilot very/extremely useful", "67%", "40%"),
            ("Used Copilot at least weekly", "78%", "53%"),
            ("Used Copilot daily", "67%", "33%"),
        ]),
        ("Skills and Training", [
            ("% with M365 licence", "57%", "n/a"),
            ("Average weekly hours saved per user", "5.4 hrs", "2.9 hrs"),
            ("Rated Copilot very/extremely useful", "75%", "17%"),
            ("Used Copilot at least weekly", "88%", "50%"),
            ("Used Copilot daily", "62%", "33%"),
        ]),
        ("Workplace Relations", [
            ("% with M365 licence", "64%", "n/a"),
            ("Average weekly hours saved per user", "5.0 hrs", "4.0 hrs"),
            ("Rated Copilot very/extremely useful", "56%", "20%"),
            ("Used Copilot at least weekly", "78%", "60%"),
            ("Used Copilot daily", "56%", "20%"),
        ]),
    ]:
        story.append(Paragraph(group_name, appendix_subheading))
        story.append(appendix_table(["Metric", "M365 Copilot", "Copilot Chat"], group_rows, [width * 0.52, width * 0.24, width * 0.24]))
        story.append(para_gap())

    story.append(PageBreak())
    story.append(toc_heading("Appendix 3: Trial methodology", copilot_section_header, 1))
    story.append(Paragraph("Goal and scope", appendix_subheading))
    for text in [
        "The Public Generative AI Trial was designed to provide an evidence base to inform departmental decisions on the adoption and governance of publicly available generative AI tools within DEWR.",
        "The primary goal of the trial was to assess whether access to selected public generative AI, specifically ChatGPT, Gemini, and Claude, provided additional value to staff when used alongside existing enterprise-supported tools (Microsoft Copilot Chat and M365 Copilot), including their perceived impact on productivity and common knowledge-work tasks.",
        "The trial also aimed to compare the relative utility of different public generative AI, and to identify key risks, limitations and user concerns associated with their use in a government context, including the effectiveness of safeguards and guidance.",
        "The trial did not seek to establish causal estimates of productivity impacts or to measure realised efficiency gains at an organisational level. Instead, it focused on capturing self-reported measures of usefulness, time savings, and behavioural patterns, alongside qualitative signals on risks and limitations. Findings should therefore be interpreted as indicative of user experience and perceived value.",
        "Collectively, the trial was intended to inform DEWR's broader AI strategy, including decisions on future access to public generative AI, their role relative to enterprise tools, and the governance settings required to support safe use.",
    ]:
        story.append(Paragraph(text, body))
    story.append(Paragraph("Sampling", appendix_subheading))
    for text in [
        "Employee records were obtained for the full department to establish a comprehensive population baseline. The cohort was restricted to APS employees who were actively employed at the time of analysis and had completed the required mandatory training modules, including AI in Government and security awareness.",
        "From this population, a stratified sampling approach was applied to ensure representation across key characteristics such as organisational group, APS classification level, and licensed Copilot status. Within each stratum, a random sample was drawn to maintain proportional representation. A roughly equal split between employees with and without a Copilot licence was also applied to support meaningful comparison between these groups.",
        "At a high level, the final sample of 200 employees reflected the composition of the department, with representation broadly aligned to workforce distribution across divisions (e.g. Enterprise Technology Division ~11%, Digital Experience and Solutions ~10%). The sample also maintained balance across APS levels and included an approximate 50% / 50% split between licensed and non-licensed Copilot users.",
        "This approach ensured the final cohort was representative of the APS workforce while being structured to support analysis of training outcomes and differences in Copilot usage between licensed and non-licensed employees.",
        "A small number of additional participants were added after the start of the trial; these did not have a significant impact on the results. A small number of SES participants participated in the trial and results are aggregated with EL staff.",
    ]:
        story.append(Paragraph(text, body))

    story.append(PageBreak())
    story.append(toc_heading("Appendix 4: Survey Design and Response", copilot_section_header, 1))
    story.append(Paragraph("Survey design and administration", appendix_subheading))
    for text in [
        "The survey was developed to capture participants' experiences of the Public Generative AI trial and to inform senior executive consideration of whether DEWR should enable or expand access to public generative AI as part of its broader AI Strategy. The questionnaire assessed participants' views on the tools' effectiveness, usability, perceived productivity benefits, risks, and strategic value.",
        "The survey was administered through Microsoft Forms. A survey link was emailed to trial participants' DEWR email addresses on 3 March, in the week following the conclusion of the trial. The invitation was sent from the Chief Data Officer and AI Accountable Official's mailbox and requested responses by 13 March. The survey was extended to 20 March and reminder emails were sent to participants who had not yet responded on 11 March and 18 March.",
        "At the close of the survey period, responses were exported from Microsoft Forms in CSV format. A de-identified copy, with respondent names and email addresses removed, was then used for analysis.",
    ]:
        story.append(Paragraph(text, body))
    story.append(Paragraph("Overall response rates", appendix_subheading))
    story.append(Paragraph(
        "A total of 104 staff completed the survey, representing an approximate 52% response rate based on the trial cohort of approximately 200 staff. Response rates broadly aligned with sampling stratification and so weighting was not applied to the analysis.",
        body))
    story.append(Paragraph("Response alignment with stratified sample", appendix_subheading))
    story.append(appendix_table(
        ["Characteristic", "Stratified sample", "Survey respondents"],
        [
            ("<b>Level</b>", "", ""),
            ("EL", "45%", "50%"),
            ("APS", "55%", "50%"),
            ("<b>Copilot licence type</b>", "", ""),
            ("M365 Copilot", "43%", "54%"),
            ("Copilot Chat", "58%", "46%"),
            ("<b>Group</b>", "", ""),
            ("Corporate", "27%", "22%"),
            ("Employment", "34%", "34%"),
            ("WR", "14%", "19%"),
            ("Skills", "21%", "20%"),
        ],
        [width * 0.42, width * 0.29, width * 0.29],
    ))
    story.append(sp(8))
    story.append(FooterNoteMarker("Note: Jobs and Skills Australia and Unique Student Identifier staff were included in the trial, but at not at sufficient numbers to be reported separately."))
    story.append(PageBreak())
    story.append(Paragraph("Respondent profile from survey-only fields", appendix_subheading))
    story.append(appendix_table(
        ["Characteristic", "Survey respondents"],
        [
            ("<b>Prior experience with Generative AI</b>", ""),
            ("No prior experience", "7%"),
            ("Basic familiarity", "32%"),
            ("Some experience", "34%"),
            ("Experienced", "23%"),
            ("Highly experienced", "5%"),
            ("<b>Role</b>", ""),
            ("Policy", "19%"),
            ("Portfolio, Program and Project Management", "18%"),
            ("Data and Research", "13%"),
            ("ICT and Digital", "13%"),
            ("Communications and Engagement", "11%"),
            ("Service Delivery", "9%"),
            ("Compliance and Regulation", "7%"),
            ("Business and Organisational Management", "5%"),
            ("Legal and Parliamentary", "4%"),
            ("Engineering and Technical", "1%"),
            ("Human Resources", "1%"),
        ],
        [width * 0.68, width * 0.32],
    ))

    story.append(para_gap())
    story.append(Paragraph("Sub-populations", appendix_subheading))
    story.append(appendix_table(
        ["Sub-population", "Definition used in analysis"],
        [
            (
                "<b>Participants in the trial</b>",
                "61 respondents (59%) used at least one public generative AI during the trial. "
                "Respondents were treated as participating if they answered yes to Q6 and also "
                "reported using ChatGPT, Gemini or Claude.",
            ),
            (
                "<b>Non-participants in the trial</b>",
                "33 respondents (31.7%) did not use any Public Generative AI during the trial. "
                "They were still asked general questions and final survey questions.",
            ),
            (
                "<b>Users of Copilot</b>",
                "Copilot usage was analysed for the 61 respondents who said they participated in the trial. "
                "This included 30 respondents with M365 Copilot (42%) and 31 with Copilot Chat only (58%).",
            ),
            (
                "<b>Users with concerns about AI</b>",
                "Included trial participants who raised concerns about Public Generative AI and non-participants "
                "who declined to participate because of security, confidentiality or related concerns.",
            ),
        ],
        [width * 0.30, width * 0.70],
    ))
    story.append(para_gap())
    story.append(Paragraph("Additional breakdowns", appendix_subheading))
    story.append(Paragraph(
        "The analysis used additional breakdowns where sample size allowed, including:", body))
    story.append(bullet("EL employees, including a small number of SES; APS employees; employees by group; and employees by experience level."))
    story.append(Paragraph(
        "Some survey breakdowns were not reported because the sample was too small, including:", body))
    story.append(bullet("Employees by division and employees by job family."))

    story.append(PageBreak())
    story.append(toc_heading("Appendix 5: Questionnaire", copilot_section_header, 1))
    story.append(Paragraph(
        "Questions requiring an answer are denoted with an asterisk (*). Some responses automatically directed participants to later questions. The action is denoted in the survey below by “skip to”.",
        body))
    story.append(appendix_table(
        ["Section", "Question", "Response options"],
        [
            ("Section 1: General questions", "<b>1. What is your APS level?*</b> Single choice", "Select your answer (APS2–SES)"),
            ("Section 1: General questions", "<b>2. What Group are you in?*</b> Single choice", "Corporate and Enabling; Employment and Workforce; Jobs and Skills Australia; Skills and Training; Workplace Relations"),
            ("Section 1: General questions", "<b>3. What is your Job Family?*</b> As per the APS Job Family Framework. Single choice", "Select your answer (From 15 Job Families)"),
            ("Section 1: General questions", "<b>4. What is your Job Title?*</b> Single line text", "Free text"),
            ("Section 1: General questions", "<b>5. Before the trial, what was your level of experience using Gen AI tools, at work or in your own personal time?*</b> Likert", "No experience at all; Basic familiarity; Some experience; Experienced; Highly experienced"),
            ("Section 1: General questions", "<b>6. Did you participate in the Public Generative AI Trial by using any of the tools?*</b> The public generative AI in the trial included ChatGPT, Gemini, and Claude. Single choice", "Yes — skip to Q8; No"),
            ("Section 1: General questions", "<b>7. If you did not use the Public Generative AI, what were the reasons?*</b> Multiple choice", "Didn’t have time; Wasn’t sure what I could use them for; Concerned about security/confidentiality; Didn’t know how to use them; Other. Any answer skip to Section 5 Q42 “Final Section”"),
            ("Section 1: General questions", "<b>8. How frequently did you use the Public Generative AI during the trial?*</b> Single choice", "Not at all; A few times a month; A few times a week; A few times a day; Most of the day"),
            ("Section 1: General questions", "<b>9. Over the course of the trial, did your level of experience with Gen AI improve?*</b> Likert", "Not at All; A Little; Moderately; A Lot; Significantly"),
            ("Section 1: General questions", "<b>10. Did you upload documents to the Public Generative AI?*</b> Such as word documents, pdfs, or powerpoint presentations. Single choice", "Yes; No"),
            ("Section 1: General questions", "<b>11. Did you copy and paste information into the Public Generative AI?*</b> Such as text from emails, meeting notes, code, data, images. Single choice", "Yes; No"),
            ("Section 2: Copilot questions", "<b>12. Do you have access to M365 Copilot at work?</b> All DEWR staff have access to Microsoft Copilot Chat. M365 Copilot is the subscription version of Copilot available to some staff. M365 Copilot has more functionality and cross application integration than Microsoft Copilot Chat. Single choice", "Yes; No; Unknown"),
            ("Section 2: Copilot questions", "<b>13. How frequently do you use Copilot at work?*</b> For this question and questions that follow, “Copilot” is used as a combined term covering both Microsoft Copilot Chat and M365 Copilot. Single choice", "Not at all; A few times a month; A few times a week; A few times a day; Most of the day"),
            ("Section 2: Copilot questions", "<b>14. What do you use Copilot for?</b> Select all that apply. Multiple choice", "Drafting; Summarising; Editing and Revision; Research, Problem Solving or Generating Ideas; Planning and Meeting Preparation; Coding or Data Work; General Administrative Tasks; Other"),
            ("Section 2: Copilot questions", "<b>15. Overall, how useful is Copilot for your work?</b> Likert", "Not useful at all; Slightly useful; Moderately useful; Very useful; Extremely useful"),
            ("Section 2: Copilot questions", "<b>16. On average, how many hours per day has Copilot helped you save in the following areas?</b> Likert", "Searching for information required for a task; Summarising existing information; Preparing meeting minutes; Preparing first drafts; Undertaking preliminary data analysis; Preparing slides; Communicating through digital means; Attending meetings; Writing or reviewing code; Scale: Copilot has added time to this activity / 0 / 0.5–1 / 1–2 / 2–3 / 3+ / N/A"),
            ("Section 2: Copilot questions", "<b>17. Thinking about Copilot use across your average workday, how many minutes/hours does it save you?*</b> Single choice", "No time saved; 5 minutes saved; 10 minutes saved; 15 minutes saved; 30 minutes saved; 45 minutes saved; 1 hour saved; 1.5 hours saved; 2 or more hours saved"),
            ("Section 3: ChatGPT/Gemini/Claude", "<b>18. Did you use ChatGPT (for work) during the trial?*</b> Single choice", "Yes; No — skip to Q25 (Gemini Section)"),
            ("Section 3: ChatGPT/Gemini/Claude", "<b>19. How frequently did you use ChatGPT during the trial?*</b> Single choice", "Not at all; A few times a month; A few times a week; A few times a day; Most of the day"),
            ("Section 3: ChatGPT/Gemini/Claude", "<b>20. What did you use ChatGPT for?</b> Select all that apply. Multiple choice", "Drafting; Summarising; Editing and Revision; Research, Problem Solving or Generating Ideas; Planning and Meeting Preparation; Coding or Data Work; General Administrative Tasks; Other"),
            ("Section 3: ChatGPT/Gemini/Claude", "<b>21. Overall, how useful was ChatGPT during the trial?</b> Likert", "Not useful at all; Slightly useful; Moderately useful; Very useful; Extremely useful"),
            ("Section 3: ChatGPT/Gemini/Claude", "<b>22. Thinking about your experience, how did ChatGPT compare with Copilot on each of the following dimensions?</b> Likert", "Overall output quality; Amount of time saved; How well it supported your work; Speed of responses; How well it understood your input. Scale: Much Worse / A little worse / About the Same / A little better / Much Better"),
            ("Section 3: ChatGPT/Gemini/Claude", "<b>23. Compared with using Copilot alone, how much additional value did ChatGPT provide for the following tasks?</b> The previous question asked about overall performance. This question focuses on specific areas where ChatGPT may have added value beyond Copilot. Likert", "Drafting; Summarising; Editing; Research; Planning; Coding or Data Work; Admin tasks. Scale: No added value / Minor added value / Some added value / Significant added value / Not Applicable"),
            ("Section 3: ChatGPT/Gemini/Claude", "<b>24. What limitations did you experience when using ChatGPT?</b> Select all that apply. Multiple choice", "Ran out of free prompts; Lacked integration; Slow response; Misinterpreted prompts; Made up facts; Struggled with specialised topics; Other"),
            ("Section 3: ChatGPT/Gemini/Claude", "<b>25. To what extent do you agree with the statement: “I want to continue using ChatGPT after the trial”?</b> Likert", "Strongly disagree; Disagree; Neutral; Agree; Strongly Agree"),
            ("Section 3: ChatGPT/Gemini/Claude", "Gemini questions mirror those asked at 19–25 for ChatGPT", ""),
            ("Section 3: ChatGPT/Gemini/Claude", "Claude questions mirror those asked at 19–25 for ChatGPT", ""),
            ("Section 4: Final questions", "<b>42. The free versions of these Gen AI tools have limited functionality and no integration with our department’s enterprise systems (e.g., Microsoft Outlook, Excel, PowerPoint, etc). If you had continued access to these free public generative AI, would they continue to provide value in your work, over and above Copilot?*</b> Single choice", "Yes; No; Not Applicable – I didn’t use any of the Public Generative AI"),
            ("Section 4: Final questions", "<b>43. Thinking about security and confidentiality obligations, how confident did you feel using the Public Generative AI in your day-to-day work?*</b> Single choice", "I didn’t use the public generative AI; I was uncomfortable using them; I was comfortable using them; I was very comfortable using them"),
            ("Section 4: Final questions", "<b>44. How effective were the safety features at communicating the rules and risks associated with the Public Generative AI trial?</b> Likert", "Introductory Email; Splash Screens (shown before entering the Gen AI websites). Scale: Not Effective at All / Slightly Effective / Moderately Effective / Highly Effective"),
            ("Section 4: Final questions", "<b>45. How effective were the upload blockers used during the trial at blocking files classified OFFICIAL: Sensitive and above?</b> Single choice", "I didn’t notice them; Not Effective; Effective"),
            ("Section 4: Final questions", "<b>46. Did you encounter any security concerns while using the Generative AI tools?*</b> Single choice", "Yes; No — skip to Q48"),
            ("Section 4: Final questions", "<b>47. Briefly describe the security concerns.</b> Single line text", "Free text"),
            ("Section 4: Final questions", "<b>48. Did you encounter any ethical concerns while using the Generative AI tools?*</b> Single choice", "Yes; No — skip to Q50"),
            ("Section 4: Final questions", "<b>49. Briefly describe the ethical concerns.</b> Single line text", "Free text"),
            ("Section 4: Final questions", "<b>50. Do you have any other feedback?</b> Single choice", "Yes; No — skip to End of Survey"),
            ("Section 4: Final questions", "<b>51. Please provide your feedback below.</b> Multi line text", "Free text"),
        ],
        [width * 0.22, width * 0.43, width * 0.35],
    ))

    # Build
    doc.multiBuild(story, onFirstPage=cover_page, onLaterPages=header_footer)
    print(f"Report generated: {OUTPUT_PATH}")


if __name__ == "__main__":
    build_report()
