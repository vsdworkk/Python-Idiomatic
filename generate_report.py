from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.colors import white
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, KeepTogether
)
from reportlab.platypus.flowables import Flowable
import os

from report_design_system import (
    ChartLayoutSpec,
    ChartSpec,
    CoverSpec,
    KpiSpec,
    Lines,
    PageChromeSpec,
    PageSpec,
    PanelSpec,
    Radii,
    Spacing,
    TableSpec,
    VisualTextSpec,
    BAR_TRACK,
    BAR_TRACK_MUTED_GREEN,
    COMPARISON_NEUTRAL,
    COVER_MUTED_GREEN,
    FOGGED_EUCALYPTUS,
    FOGGED_GRAPHITE,
    KEY_FINDING_BACKGROUND,
    build_paragraph_styles,
    draw_panel_background,
    register_fonts,
    DEWR_GREEN,
    DEWR_DARK_GREEN,
    DEWR_DARK_GREY,
    DEWR_NAVY,
    DEWR_TEAL,
    DEWR_GREY,
    DEWR_LIGHT_GREY,
    DEWR_LIME,
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
PANEL = PanelSpec()
KPI = KpiSpec()
CHART_LAYOUT = ChartLayoutSpec()
TABLE_SPEC = TableSpec()
PAGE_CHROME = PageChromeSpec()
COVER = CoverSpec()

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "Outputs")
OUTPUT_PATH = os.path.join(OUTPUT_DIR, "DEWR_Public_AI_B.pdf")
COVER_LOCKUP_PATH = os.path.join(os.path.dirname(__file__), "assets", "dewr_cover_lockup_white.png")
os.makedirs(OUTPUT_DIR, exist_ok=True)


class CalloutBox(Flowable):
    """A colored callout box with text."""
    def __init__(
        self,
        text,
        width,
        bg_color=DEWR_NAVY,
        text_color=white,
        font_size=VISUAL_TEXT.callout_text,
        padding=PANEL.padding_callout,
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
        style = ParagraphStyle('callout_measure', fontName=FONT_BOLD,
                               fontSize=self.font_size, leading=self.font_size + 4,
                               textColor=self.text_color)
        p = Paragraph(self.text, style)
        w, h = p.wrap(self.box_width - 2 * self.padding, availHeight)
        self._height = h + 2 * self.padding
        return self.box_width, self._height

    def draw(self):
        self.canv.setFillColor(self.bg_color)
        self.canv.rect(0, 0, self.box_width, self._height, fill=1, stroke=0)
        style = ParagraphStyle('callout_draw', fontName=FONT_BOLD,
                               fontSize=self.font_size, leading=self.font_size + 4,
                               textColor=self.text_color)
        p = Paragraph(self.text, style)
        p.wrap(self.box_width - 2 * self.padding, self._height)
        p.drawOn(self.canv, self.padding, self.padding)


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
        self._height = 112 if title else 94

    def wrap(self, availWidth, availHeight):
        self.box_width = availWidth
        return self.box_width, self._height

    def draw(self):
        c = self.canv
        w = self.box_width
        h = self._height
        pad = PANEL.padding

        draw_panel_background(c, 0, 0, w, h, stroke_width=0, radius=0)

        top_offset = 20 if self.title else 0
        if self.title:
            c.setFillColor(DEWR_DARK_GREY)
            c.setFont(FONT_BOLD, VISUAL_TEXT.table_value)
            c.drawString(pad, h - 20, self.title)
            c.setStrokeColor(DEWR_LIGHT_GREY)
            c.setLineWidth(LINES.hairline)
            c.line(pad, h - 31, w - pad, h - 31)

        col_w = (w - 2 * pad) / len(self.items)
        value_y = h - (44 if not self.title else 54)
        label_top_y = value_y - 16
        for i, (value, label) in enumerate(self.items):
            x = pad + i * col_w
            cx = x + col_w / 2
            if i:
                c.setStrokeColor(DEWR_LIGHT_GREY)
                c.setLineWidth(LINES.fine)
                c.line(x, 12, x, h - 12 - top_offset)
            value_color = DEWR_RED if "(" in value else (DEWR_GREEN if i < self.primary_count else DEWR_DARK_GREY)
            c.setFillColor(value_color)
            value_size = VISUAL_TEXT.kpi_value_medium if len(value) <= 8 else VISUAL_TEXT.kpi_value_compact
            c.setFont(FONT_BOLD, value_size)
            c.drawCentredString(cx, value_y, value)
            p = Paragraph(label, ParagraphStyle(
                "value_signal_label",
                fontName=FONT_REGULAR,
                fontSize=VISUAL_TEXT.kpi_caption,
                leading=VISUAL_TEXT.kpi_caption_leading,
                alignment=TA_CENTER,
                textColor=DEWR_DARK_GREY,
            ))
            _, label_h = p.wrap(col_w - 14, 48)
            p.drawOn(c, x + 7, label_top_y - label_h)


class CalloutSignalsPanel(Flowable):
    """Green takeaway callout with embedded KPI evidence strip."""
    def __init__(self, text, width, items, primary_count=None, bg_color=DEWR_DARK_GREEN):
        Flowable.__init__(self)
        self.text = text
        self.box_width = width
        self.items = items
        self.primary_count = len(items) if primary_count is None else primary_count
        self.bg_color = bg_color
        self.padding = PANEL.padding_callout
        self.card_height = KPI.panel_height
        self.gap = PANEL.gutter
        self._height = None
        self._text_height = None

    def wrap(self, availWidth, availHeight):
        self.box_width = availWidth
        style = ParagraphStyle(
            "callout_signals_measure",
            fontName=FONT_BOLD,
            fontSize=VISUAL_TEXT.callout_text,
            leading=VISUAL_TEXT.callout_text_leading,
            textColor=white,
        )
        p = Paragraph(self.text, style)
        _, self._text_height = p.wrap(self.box_width - 2 * self.padding, availHeight)
        self._height = self._text_height + self.card_height + self.gap + 2 * self.padding
        return self.box_width, self._height

    def draw(self):
        c = self.canv
        w = self.box_width
        h = self._height
        pad = self.padding

        c.setFillColor(self.bg_color)
        c.rect(0, 0, w, h, fill=1, stroke=0)

        style = ParagraphStyle(
            "callout_signals_draw",
            fontName=FONT_BOLD,
            fontSize=VISUAL_TEXT.callout_text,
            leading=VISUAL_TEXT.callout_text_leading,
            textColor=white,
        )
        p = Paragraph(self.text, style)
        p.wrap(w - 2 * pad, self._text_height)
        p.drawOn(c, pad, h - pad - self._text_height)

        card_x = pad
        card_y = pad
        card_w = w - 2 * pad
        card_h = self.card_height
        draw_panel_background(c, card_x, card_y, card_w, card_h, radius=RADII.sm, stroke_width=0)

        inner_pad = PANEL.inner_padding
        col_w = (card_w - 2 * inner_pad) / len(self.items)
        value_y = card_y + 41
        label_top_y = card_y + 27
        for i, (value, label) in enumerate(self.items):
            x = card_x + inner_pad + i * col_w
            cx = x + col_w / 2
            if i:
                c.setStrokeColor(DEWR_LIGHT_GREY)
                c.setLineWidth(LINES.fine)
                c.line(x, card_y + 11, x, card_y + card_h - 11)
            c.setFillColor(DEWR_GREEN if i < self.primary_count else DEWR_DARK_GREY)
            value_size = VISUAL_TEXT.kpi_value_medium if len(value) <= 8 else VISUAL_TEXT.kpi_value_compact
            c.setFont(FONT_BOLD, value_size)
            c.drawCentredString(cx, value_y, value)
            label_p = Paragraph(label, ParagraphStyle(
                "callout_signal_label",
                fontName=FONT_REGULAR,
                fontSize=VISUAL_TEXT.kpi_caption,
                leading=VISUAL_TEXT.kpi_caption_leading,
                alignment=TA_CENTER,
                textColor=DEWR_DARK_GREY,
            ))
            _, label_h = label_p.wrap(col_w - 14, 28)
            label_p.drawOn(c, x + 7, label_top_y - label_h)


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
        w = self.box_width
        h = self._height
        pad = PANEL.padding

        draw_panel_background(c, 0, 0, w, h, stroke_width=0, radius=0)

        label_w = w * 0.24
        bar_x = pad + label_w
        bar_w = w - bar_x - 150
        bar_h = CHART_LAYOUT.bar_height_medium
        max_value = 75
        rows = [
            ("M365 Copilot", 67.9, "68 minutes per day", "5.7 hours per week", DEWR_DARK_GREEN),
            ("Copilot Chat", 33.5, "34 minutes per day", "2.8 hours per week", DEWR_DARK_GREY),
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
            c.setFillColor(DEWR_DARK_GREY)
            c.setFont(FONT_REGULAR, VISUAL_TEXT.time_savings_context)
            c.drawRightString(w - pad, y - 12, daily_label)


class M365LicenceCoveragePanel(Flowable):
    """Combined licence coverage overview by classification and group."""
    def __init__(self, width):
        Flowable.__init__(self)
        self.box_width = width
        self.group_rows = sorted([
            ("Corporate and Enabling", 990, 78, 7.9),
            ("Employment and Workforce", 1198, 73, 6.1),
            ("Workplace Relations", 377, 40, 10.6),
            ("Skills and Training", 584, 33, 5.7),
        ], key=lambda r: -r[3])
        self.stats = [
            ("6.8%", "Overall Staff", DEWR_DARK_GREEN),
            ("4.5%", "APS Level Staff", DEWR_DARK_GREY),
            ("9.9%", "EL Level Staff", DEWR_DARK_GREEN),
        ]
        self.max_value = 100.0
        self._height = 220

    def wrap(self, availWidth, availHeight):
        self.box_width = availWidth
        return self.box_width, self._height

    def draw(self):
        c = self.canv
        w = self.box_width
        h = self._height
        pad = PANEL.padding_large

        draw_panel_background(c, 0, 0, w, h, stroke_width=0, radius=0)

        content_top = h - 44
        content_bottom = 16
        content_h = content_top - content_bottom

        left_w = (w - 2 * pad) * 0.22
        gap = 22
        right_x = pad + left_w + gap
        right_w = w - pad - right_x

        div_x = pad + left_w + gap / 2
        c.setStrokeColor(DEWR_LIGHT_GREY)
        c.line(div_x, content_top, div_x, content_bottom)

        c.setFillColor(DEWR_DARK_GREY)
        c.setFont(FONT_BOLD, VISUAL_TEXT.panel_header_small)
        c.drawString(pad, h - 20, "M365 COPILOT LICENCE COVERAGE")

        c.setStrokeColor(DEWR_LIGHT_GREY)
        c.setLineWidth(LINES.fine)
        c.line(pad, h - 28, w - pad, h - 28)

        n_bars = len(self.group_rows)
        bar_slot_h = content_h / n_bars
        bar_h = CHART_LAYOUT.bar_height_large

        for idx, (label, _total_staff, _licence_count, pct) in enumerate(self.group_rows):
            slot_top = content_top - idx * bar_slot_h
            y_label = slot_top - 10
            y_bar = slot_top - bar_slot_h + 6
            color = DEWR_DARK_GREEN if idx == 0 else DEWR_DARK_GREY

            c.setFillColor(DEWR_DARK_GREY)
            c.setFont(FONT_BOLD, VISUAL_TEXT.stat_label)
            c.drawString(right_x, y_label, label)

            c.setFillColor(BAR_TRACK_MUTED_GREEN)
            c.rect(right_x, y_bar, right_w, bar_h, fill=1, stroke=0)

            fill_w = right_w * min(pct / self.max_value, 1)
            c.setFillColor(color)
            c.rect(right_x, y_bar, fill_w, bar_h, fill=1, stroke=0)

            c.setFillColor(color)
            c.setFont(FONT_BOLD, VISUAL_TEXT.stat_label)
            c.drawString(right_x + fill_w + 6, y_bar + 4, f"{pct:.1f}%")

        bar_top_visual = content_top - 3
        bar_bottom_visual = content_top - content_h + 6
        number_size = 22
        label_size = VISUAL_TEXT.card_body
        number_cap_h = number_size * 0.72
        label_cap_h = label_size * 0.72
        gap_in_stat = 14
        stat_h = number_cap_h + gap_in_stat + label_cap_h
        available_range = bar_top_visual - bar_bottom_visual
        stat_step = (available_range - stat_h) / (len(self.stats) - 1)

        cx = pad + left_w / 2
        for idx, (value, label, color) in enumerate(self.stats):
            top_y = bar_top_visual - idx * stat_step
            number_baseline = top_y - number_cap_h
            label_baseline = number_baseline - gap_in_stat - label_cap_h

            c.setFillColor(color)
            c.setFont(FONT_BOLD, number_size)
            c.drawCentredString(cx, number_baseline, value)

            c.setFillColor(DEWR_DARK_GREY)
            c.setFont(FONT_BOLD, label_size)
            c.drawCentredString(cx, label_baseline, label)


class CopilotEngagementDeltaPanel(Flowable):
    """Engagement comparison by Copilot access type."""
    def __init__(self, width):
        Flowable.__init__(self)
        self.box_width = width
        self.rows = [
            ("Rated very or extremely useful", "68%", "35%"),
            ("Used at least weekly", "81%", "55%"),
            ("Used daily or most of day", "65%", "25%"),
        ]
        self._height = 122

    def wrap(self, availWidth, availHeight):
        self.box_width = availWidth
        return self.box_width, self._height

    def draw(self):
        c = self.canv
        w = self.box_width
        h = self._height
        pad = PANEL.padding

        draw_panel_background(c, 0, 0, w, h, stroke_width=0, radius=0)

        first_w = w * 0.56
        col_w = (w - first_w - pad) / 2
        head_y = h - 22

        c.setFillColor(DEWR_DARK_GREY)
        c.setFont(FONT_BOLD, VISUAL_TEXT.panel_header_small)
        c.drawString(pad, head_y, "MEASURE")
        for i, col in enumerate(["M365", "CHAT"]):
            c.drawCentredString(first_w + i * col_w + col_w / 2, head_y, col)

        c.setStrokeColor(DEWR_LIGHT_GREY)
        c.setLineWidth(LINES.fine)
        c.line(pad, h - 36, w - pad, h - 36)

        row_h = TABLE_SPEC.matrix_row_height
        for r_idx, (label, m365, chat) in enumerate(self.rows):
            y = h - 58 - r_idx * row_h
            if r_idx:
                c.setStrokeColor(DEWR_LIGHT_GREY)
                c.line(pad, y + 16, w - pad, y + 16)

            c.setFillColor(DEWR_NAVY)
            c.setFont(FONT_BOLD, VISUAL_TEXT.table_label)
            c.drawString(pad, y, label)

            values = [m365, chat]
            for i, value in enumerate(values):
                c.setFillColor(DEWR_DARK_GREEN if i == 0 else DEWR_NAVY)
                c.setFont(FONT_BOLD, VISUAL_TEXT.table_value)
                c.drawCentredString(first_w + i * col_w + col_w / 2, y, value)


class EvidenceMatrixPanel(Flowable):
    """Compact grey matrix for comparing metrics across groups or tools."""
    def __init__(self, width, title, columns, rows, first_col_ratio=0.42):
        Flowable.__init__(self)
        self.box_width = width
        self.title = title
        self.columns = columns
        self.rows = rows
        self.first_col_ratio = first_col_ratio
        self.row_h = TABLE_SPEC.matrix_row_height
        self.header_h = TABLE_SPEC.matrix_header_height if len(rows) > 1 else TABLE_SPEC.matrix_header_height_single
        self._height = self.header_h + self.row_h * len(rows)

    def wrap(self, availWidth, availHeight):
        self.box_width = availWidth
        return self.box_width, self._height

    def draw(self):
        c = self.canv
        w = self.box_width
        h = self._height
        pad = PANEL.padding

        draw_panel_background(c, 0, 0, w, h, stroke_width=0, radius=0)

        first_w = w * self.first_col_ratio
        data_w = w - first_w - pad
        col_w = data_w / len(self.columns)
        head_y = h - 22

        c.setFillColor(DEWR_DARK_GREY)
        c.setFont(FONT_BOLD, VISUAL_TEXT.panel_header_small)
        c.drawString(pad, head_y, self.title)
        column_header_style = ParagraphStyle(
            "matrix_column_header",
            fontName=FONT_BOLD,
            fontSize=VISUAL_TEXT.table_header,
            leading=VISUAL_TEXT.table_header_leading,
            alignment=TA_CENTER,
            textColor=DEWR_DARK_GREY,
        )
        for i, col in enumerate(self.columns):
            header_text = col.replace("<br/>", "\n").upper().replace("\n", "<br/>")
            p = Paragraph(header_text, column_header_style)
            _, ph = p.wrap(col_w - 6, 26)
            p.drawOn(c, first_w + i * col_w + 3, h - 18 - ph / 2)

        c.setStrokeColor(DEWR_LIGHT_GREY)
        c.setLineWidth(LINES.fine)
        c.line(0, h - 36, w, h - 36)

        for r_idx, row in enumerate(self.rows):
            label, values, highlight_idx = row
            y = h - 57 - r_idx * self.row_h
            if r_idx:
                c.setStrokeColor(DEWR_SOFT_LINE)
                c.setLineWidth(LINES.fine)
                c.line(pad, y + 16, w - pad, y + 16)

            if values is None:
                c.setFillColor(DEWR_DARK_GREY)
                c.setFont(FONT_BOLD, VISUAL_TEXT.table_label)
                c.drawString(pad, y, label)
                continue

            p = Paragraph(label, ParagraphStyle(
                "matrix_label",
                fontName=FONT_BOLD,
                fontSize=VISUAL_TEXT.table_label,
                leading=VISUAL_TEXT.table_label_leading,
                textColor=DEWR_NAVY,
            ))
            _, label_h = p.wrap(first_w - pad - 4, 22)
            p.drawOn(c, pad, y - label_h / 2)

            c.setFont(FONT_BOLD, VISUAL_TEXT.table_value)
            for i, value in enumerate(values):
                highlighted = (
                    highlight_idx == "all"
                    or (isinstance(highlight_idx, (list, tuple, set)) and i in highlight_idx)
                    or i == highlight_idx
                )
                c.setFillColor(DEWR_DARK_GREEN if highlighted else DEWR_NAVY)
                c.drawCentredString(first_w + i * col_w + col_w / 2, y - 4, value)


class MarginalValuePanel(Flowable):
    """Compact two-part panel for public-tool marginal value signals."""
    def __init__(self, width):
        Flowable.__init__(self)
        self.box_width = width
        self._height = 132

    def wrap(self, availWidth, availHeight):
        self.box_width = availWidth
        return self.box_width, self._height

    def draw(self):
        c = self.canv
        w = self.box_width
        h = self._height
        pad = PANEL.padding

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
            c.setFillColor(DEWR_RED)
            c.drawCentredString(chat_x, y, chat_value)
            c.setFillColor(DEWR_RED)
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


class TwoEvidenceCardsPanel(Flowable):
    """Concise proof-point cards for executive evidence."""
    def __init__(self, width, cards):
        Flowable.__init__(self)
        self.box_width = width
        self.cards = cards
        self._height = 112

    def wrap(self, availWidth, availHeight):
        self.box_width = availWidth
        return self.box_width, self._height

    def draw(self):
        c = self.canv
        w = self.box_width
        h = self._height
        gap = PANEL.gutter
        card_count = len(self.cards)
        card_w = (w - gap * (card_count - 1)) / card_count

        label_style = ParagraphStyle(
            "evidence_card_label",
            fontName=FONT_REGULAR,
            fontSize=VISUAL_TEXT.card_body,
            leading=VISUAL_TEXT.card_body_leading,
            textColor=DEWR_DARK_GREY,
            alignment=TA_CENTER,
        )
        vs_style = ParagraphStyle(
            "evidence_card_vs",
            fontName=FONT_BOLD,
            fontSize=VISUAL_TEXT.card_body,
            leading=VISUAL_TEXT.card_body_leading,
            textColor=DEWR_DARK_GREY,
            alignment=TA_CENTER,
        )

        for idx, card in enumerate(self.cards):
            x = idx * (card_w + gap)
            draw_panel_background(c, x, 0, card_w, h, stroke_width=0, radius=0)

            c.setFillColor(DEWR_DARK_GREY)
            c.setFont(FONT_BOLD, VISUAL_TEXT.panel_header_small)
            c.drawCentredString(x + card_w / 2, h - 21, card["metric"].upper())
            c.setStrokeColor(DEWR_LIGHT_GREY)
            c.setLineWidth(LINES.fine)
            c.line(x + PANEL.divider_inset, h - 34, x + card_w - PANEL.divider_inset, h - 34)

            c.setFillColor(DEWR_DARK_GREEN)
            c.setFont(FONT_BOLD, VISUAL_TEXT.kpi_value)
            c.drawCentredString(x + card_w / 2, h - 63, card["value"])

            label = Paragraph(card["label"], label_style)
            label.wrap(card_w - 34, 24)
            label.drawOn(c, x + 17, h - 88)

            vs = Paragraph(card["comparison"], vs_style)
            vs.wrap(card_w - 34, 18)
            vs.drawOn(c, x + 17, 9)


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
        w = self.box_width
        h = self._height
        pad = PANEL.padding + SPACING.xs
        value_w = 92

        draw_panel_background(c, 0, 0, w, h, stroke_width=0, radius=0)

        c.setFillColor(DEWR_DARK_GREEN)
        c.setFont(FONT_BOLD, VISUAL_TEXT.kpi_value_medium)
        c.drawCentredString(value_w / 2 + 4, 22, self.value)

        c.setStrokeColor(DEWR_LIGHT_GREY)
        c.setLineWidth(LINES.regular)
        c.line(value_w + 8, 16, value_w + 8, h - 16)

        text_style = ParagraphStyle(
            "horizontal_callout_text",
            fontName=FONT_REGULAR,
            fontSize=VISUAL_TEXT.horizontal_callout_text,
            leading=VISUAL_TEXT.horizontal_callout_text_leading,
            textColor=DEWR_DARK_GREY,
        )
        text = Paragraph(f"{self.text} <b>{self.comparison}</b>", text_style)
        text_w, text_h = text.wrap(w - value_w - pad * 2, 34)
        text.drawOn(c, value_w + pad, (h - text_h) / 2)


class PublicAIUsefulnessVisual(Flowable):
    """
    Two-column bar comparison showing which tool each access group rated more useful.
    """

    def __init__(self, width=None):
        Flowable.__init__(self)
        self.box_width = width
        self.box_height = 104

    def wrap(self, availWidth, availHeight):
        if self.box_width is None:
            self.box_width = availWidth
        return self.box_width, self.box_height

    def _para(self, text, x, y_top, width, size=7, leading=None,
              font=FONT_REGULAR, color=DEWR_DARK_GREY, bold=False):
        style = ParagraphStyle(
            "tmp",
            fontName=FONT_BOLD if bold else font,
            fontSize=size,
            leading=leading or size + 2,
            textColor=color,
            alignment=TA_LEFT,
            spaceAfter=0,
            spaceBefore=0,
        )
        p = Paragraph(text, style)
        _, h = p.wrap(width, 1000)
        p.drawOn(self.canv, x, y_top - h)

    def draw(self):
        c = self.canv
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

        pad = PANEL.padding_xlarge
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
            title_y = h - 16
            label_w = 50
            bar_x = x + label_w + 10
            value_gap = 6
            bar_w = col_w - label_w - 48
            bar_h = CHART_LAYOUT.bar_height_medium + 1
            max_value = 100

            c.setFillColor(DEWR_DARK_GREY)
            c.setFont(FONT_BOLD, VISUAL_TEXT.stat_label)
            title_para = Paragraph(title, ParagraphStyle(
                "usefulness_group_title",
                fontName=FONT_BOLD,
                fontSize=VISUAL_TEXT.usefulness_title,
                leading=VISUAL_TEXT.usefulness_title_leading,
                textColor=DEWR_DARK_GREY,
            ))
            title_para.wrap(col_w - 8, 22)
            title_para.drawOn(c, x, title_y - 12)

            for i, (label, value, display_value, color) in enumerate(rows):
                y = title_y - 36 - i * 22
                c.setFillColor(DEWR_DARK_GREY)
                c.setFont(FONT_REGULAR, VISUAL_TEXT.card_body)
                c.drawString(x, y + 2, label)
                c.setFillColor(color)
                c.rect(bar_x, y, bar_w * value / max_value, bar_h, fill=1, stroke=0)
                c.setFillColor(DEWR_RED)
                c.setFont(FONT_BOLD, VISUAL_TEXT.usefulness_value)
                c.drawString(bar_x + bar_w * value / max_value + value_gap, y + 2, display_value)

        comparison_grey = COMPARISON_NEUTRAL
        draw_group(
            left_x,
            "Copilot Chat",
            [
                ("Public AI", 81.8, "81.8% (82.4%)", DEWR_DARK_GREEN),
                ("Copilot", 69.7, "69.7%", comparison_grey),
            ],
        )
        draw_group(
            right_x,
            "M365 Copilot",
            [
                ("Copilot", 92.9, "92.9%", DEWR_DARK_GREY),
                ("Public AI", 78.6, "78.6% (77.8%)", comparison_grey),
            ],
        )


class PriorExperienceComparisonPanel(Flowable):
    """Three-column comparison panel for prior Gen AI experience groups."""
    def __init__(self, width):
        Flowable.__init__(self)
        self.box_width = width
        self._height = 104

    def wrap(self, availWidth, availHeight):
        self.box_width = availWidth
        return self.box_width, self._height

    def draw(self):
        c = self.canv
        w = self.box_width
        h = self._height
        pad = PANEL.padding
        inner_top = h - 16
        col_w = (w - 2 * pad) / 3

        draw_panel_background(c, 0, 0, w, h, stroke_width=0, radius=0)

        c.setStrokeColor(DEWR_LIGHT_GREY)
        c.setLineWidth(LINES.fine)
        for i in (1, 2):
            x = pad + i * col_w
            c.line(x, 16, x, inner_top)

        columns = [
            ("Experienced or highly experienced", "91%", "reported at some or significant added value over Copilot", DEWR_DARK_GREEN),
            ("Some prior experience", "73%", "reported at some or significant added value over Copilot", DEWR_DARK_GREY),
            ("No or basic experience", "67%", "reported at some or significant added value over Copilot", DEWR_DARK_GREY),
        ]
        label_style = ParagraphStyle(
            "prior_experience_comparison_label",
            fontName=FONT_REGULAR,
            fontSize=VISUAL_TEXT.kpi_caption,
            leading=VISUAL_TEXT.kpi_caption_leading,
            alignment=TA_CENTER,
            textColor=DEWR_DARK_GREY,
        )
        for i, (name, value, label, color) in enumerate(columns):
            x = pad + i * col_w
            cx = x + col_w / 2
            c.setFillColor(DEWR_DARK_GREY)
            c.setFont(FONT_BOLD, VISUAL_TEXT.chart_tick)
            c.drawCentredString(cx, h - 24, name)
            c.setFillColor(color)
            c.setFont(FONT_BOLD, VISUAL_TEXT.kpi_value)
            c.drawCentredString(cx, h - 56, value)
            p = Paragraph(label, label_style)
            _, label_h = p.wrap(col_w - 24, 22)
            p.drawOn(c, x + 12, 27 - label_h / 2)


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
        self._height = 56 + self.row_h * len(items)

    def wrap(self, availWidth, availHeight):
        self.box_width = availWidth
        return self.box_width, self._height

    def draw(self):
        c = self.canv
        w = self.box_width
        h = self._height
        pad = PANEL.padding

        draw_panel_background(c, 0, 0, w, h, stroke_width=0, radius=0)

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
            y = h - 55 - i * self.row_h
            c.setFillColor(DEWR_NAVY)
            c.setFont(FONT_REGULAR, VISUAL_TEXT.chart_label)
            p = Paragraph(label, ParagraphStyle(
                "bar_label",
                fontName=FONT_REGULAR,
                fontSize=VISUAL_TEXT.chart_label,
                leading=VISUAL_TEXT.chart_label_leading,
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


class ComfortDataHandlingPanel(Flowable):
    """Grouped bars for data-handling behaviour by comfort using public tools."""
    def __init__(self, width):
        Flowable.__init__(self)
        self.box_width = width
        self._height = 112
        self.rows = [
            ("Copied and pasted information", 71.7, 66.7),
            ("Uploaded documents", 47.8, 26.7),
        ]

    def wrap(self, availWidth, availHeight):
        self.box_width = availWidth
        return self.box_width, self._height

    def draw(self):
        c = self.canv
        w = self.box_width
        h = self._height
        pad = PANEL.padding

        draw_panel_background(c, 0, 0, w, h, stroke_width=0, radius=0)

        c.setFillColor(DEWR_DARK_GREY)
        c.setFont(FONT_BOLD, VISUAL_TEXT.panel_header)
        c.drawString(pad, h - 20, "DATA HANDLING BY COMFORT USING PUBLIC TOOLS")

        legend_y = h - 20
        legend_x = w - pad - 190
        for x, color, label in [
            (legend_x, DEWR_DARK_GREEN, "Comfortable or very comfortable"),
            (legend_x + 112, DEWR_DARK_GREY, "Uncomfortable"),
        ]:
            c.setFillColor(color)
            c.circle(x, legend_y + 1.5, CHART_LAYOUT.legend_marker_radius, fill=1, stroke=0)
            c.setFillColor(DEWR_DARK_GREY)
            c.setFont(FONT_REGULAR, VISUAL_TEXT.chart_legend_compact)
            c.drawString(x + 7, legend_y - 1, label)

        c.setStrokeColor(DEWR_LIGHT_GREY)
        c.setLineWidth(LINES.fine)
        c.line(pad, h - 34, w - pad, h - 34)

        label_w = w * 0.38
        bar_x = pad + label_w
        bar_w = w - bar_x - 50
        bar_h = CHART_LAYOUT.bar_height_compact
        row_gap = CHART_LAYOUT.row_height + PANEL.gutter

        for i, (label, comfortable, uncomfortable) in enumerate(self.rows):
            y = h - 58 - i * row_gap
            c.setFillColor(DEWR_NAVY)
            c.setFont(FONT_REGULAR, VISUAL_TEXT.chart_label)
            c.drawString(pad, y - 1, label)

            for offset, value, color, sublabel in [
                (6, comfortable, DEWR_DARK_GREEN, "Comfortable"),
                (-6, uncomfortable, DEWR_DARK_GREY, "Uncomfortable"),
            ]:
                bar_y = y + offset
                c.setFillColor(BAR_TRACK)
                c.rect(bar_x, bar_y, bar_w, bar_h, fill=1, stroke=0)
                c.setFillColor(color)
                c.rect(bar_x, bar_y, bar_w * (value / 100), bar_h, fill=1, stroke=0)
                c.setFillColor(DEWR_DARK_GREY)
                c.setFont(FONT_REGULAR, VISUAL_TEXT.chart_legend_compact)
                c.drawRightString(bar_x - 6, bar_y - 1, sublabel)
                c.setFont(FONT_BOLD, VISUAL_TEXT.chart_value_label)
                c.drawString(bar_x + bar_w + 8, bar_y - 1, f"{value:.1f}%")


class PublicToolTaskProfilePanel(Flowable):
    """Task-by-tool dot plot showing how public tools were used for different work types."""
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
        self._height = 246

    def wrap(self, availWidth, availHeight):
        self.box_width = availWidth
        return self.box_width, self._height

    def draw(self):
        c = self.canv
        w = self.box_width
        h = self._height
        pad = PANEL.padding_large

        draw_panel_background(c, 0, 0, w, h, stroke_width=0, radius=0)

        label_w = w * CHART_LAYOUT.label_width_ratio
        axis_x = pad + label_w
        axis_w = w - axis_x - pad
        head_y = h - 20
        tick_y = h - 42
        top_y = h - 49
        bottom_y = top_y - self.row_h * (len(self.rows) - 1) - 8

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
            c.circle(marker_x, h - 18, CHART_LAYOUT.legend_marker_radius, fill=1, stroke=0)
            c.setFillColor(DEWR_DARK_GREY)
            c.drawString(text_x, h - 21, name)
            legend_x = marker_x - item_gap

        c.setStrokeColor(DEWR_LIGHT_GREY)
        c.setLineWidth(LINES.fine)
        c.line(pad, h - 28, w - pad, h - 28)

        c.setFont(FONT_REGULAR, VISUAL_TEXT.chart_tick)
        c.setFillColor(DEWR_GREY)
        for tick, label in [(0, "0%"), (25, "25%"), (50, "50%"), (75, "75%"), (100, "100%")]:
            x = axis_x + axis_w * (tick / self.max_value)
            c.drawCentredString(x, tick_y, label)
            c.setStrokeColor(DEWR_LIGHT_GREY)
            c.setLineWidth(LINES.hairline)
            c.line(x, tick_y - 4, x, bottom_y)

        label_style = ParagraphStyle(
            "public_tool_task_label",
            fontName=FONT_REGULAR,
            fontSize=VISUAL_TEXT.chart_label,
            leading=VISUAL_TEXT.chart_label_leading,
            textColor=DEWR_NAVY,
        )
        label_bold_style = ParagraphStyle(
            "public_tool_task_label_bold",
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


class AllToolTaskProfilePanel(Flowable):
    """Task-by-tool dot plot comparing public tools and Copilot access types."""
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
        self._height = 246

    def wrap(self, availWidth, availHeight):
        self.box_width = availWidth
        return self.box_width, self._height

    def draw(self):
        c = self.canv
        w = self.box_width
        h = self._height
        pad = PANEL.padding_large

        draw_panel_background(c, 0, 0, w, h, stroke_width=0, radius=0)

        label_w = w * CHART_LAYOUT.label_width_ratio
        axis_x = pad + label_w
        axis_w = w - axis_x - pad
        head_y = h - 20
        tick_y = h - 42
        top_y = h - 49
        bottom_y = top_y - self.row_h * (len(self.rows) - 1) - 8

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
            c.circle(marker_x, h - 18, CHART_LAYOUT.legend_marker_radius_compact, fill=1, stroke=0)
            c.setFillColor(DEWR_DARK_GREY)
            c.drawString(text_x, h - 21, name)
            legend_x = marker_x - item_gap

        c.setStrokeColor(DEWR_LIGHT_GREY)
        c.setLineWidth(LINES.fine)
        c.line(pad, h - 28, w - pad, h - 28)

        c.setFont(FONT_REGULAR, VISUAL_TEXT.chart_tick)
        c.setFillColor(DEWR_GREY)
        for tick, label in [(0, "0%"), (25, "25%"), (50, "50%"), (75, "75%"), (100, "100%")]:
            x = axis_x + axis_w * (tick / self.max_value)
            c.drawCentredString(x, tick_y, label)
            c.setStrokeColor(DEWR_LIGHT_GREY)
            c.setLineWidth(LINES.hairline)
            c.line(x, tick_y - 4, x, bottom_y)

        label_style = ParagraphStyle(
            "all_tool_task_label",
            fontName=FONT_REGULAR,
            fontSize=VISUAL_TEXT.chart_label,
            leading=VISUAL_TEXT.chart_label_leading,
            textColor=DEWR_NAVY,
        )
        label_bold_style = ParagraphStyle(
            "all_tool_task_label_bold",
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
                    label_text = f"{value:.1f}%"
                    c.setFont(FONT_BOLD, VISUAL_TEXT.chart_value_label_compact)
                    text_w = c.stringWidth(label_text, FONT_BOLD, VISUAL_TEXT.chart_value_label_compact)
                    label_x = x + 5
                    c.setFillColor(color)
                    if label_x + text_w > axis_x + axis_w + 38:
                        c.drawRightString(x - 5, y - 2, label_text)
                    else:
                        c.drawString(label_x, y - 2, label_text)


class SafeguardPrioritiesPanel(Flowable):
    """Three-column safeguard framework panel."""
    def __init__(self, width):
        Flowable.__init__(self)
        self.box_width = width
        self._height = 138
        self.items = [
            ("Information classification boundaries", "Users described uncertainty about what information was appropriate to enter."),
            ("Output validation", "Users pointed to the need to check outputs before relying on them."),
            ("APS-specific sensitivity and safeguards", "Some responses highlighted differences between public tools and Copilot safeguards."),
        ]

    def wrap(self, availWidth, availHeight):
        self.box_width = availWidth
        return self.box_width, self._height

    def draw(self):
        c = self.canv
        w = self.box_width
        h = self._height
        pad = PANEL.padding

        draw_panel_background(c, 0, 0, w, h, stroke_width=0, radius=0)

        c.setFillColor(DEWR_DARK_GREY)
        c.setFont(FONT_BOLD, VISUAL_TEXT.panel_header)
        c.drawString(pad, h - 22, "PRACTICAL JUDGEMENT BOUNDARIES")
        c.setStrokeColor(DEWR_LIGHT_GREY)
        c.setLineWidth(LINES.fine)
        c.line(pad, h - 36, w - pad, h - 36)

        col_w = (w - 2 * pad) / 3
        for i, (title, text) in enumerate(self.items):
            x = pad + i * col_w
            if i:
                c.setStrokeColor(DEWR_LIGHT_GREY)
                c.line(x, 18, x, h - 46)

            title_p = Paragraph(title, ParagraphStyle(
                "safeguard_title",
                fontName=FONT_BOLD,
                fontSize=VISUAL_TEXT.safeguard_title,
                leading=VISUAL_TEXT.safeguard_title_leading,
                textColor=DEWR_DARK_GREY,
            ))
            title_p.wrap(col_w - 22, 28)
            title_p.drawOn(c, x + 10, h - 72)
            p = Paragraph(text, ParagraphStyle(
                "safeguard_text",
                fontName=FONT_REGULAR,
                fontSize=VISUAL_TEXT.safeguard_body,
                leading=VISUAL_TEXT.safeguard_body_leading,
                textColor=DEWR_DARK_GREY,
            ))
            p.wrap(col_w - 22, 42)
            p.drawOn(c, x + 10, h - 116)


class UncertaintyAreasPanel(Flowable):
    """Three-column panel for uncertainty themes in open-text responses."""
    def __init__(self, width):
        Flowable.__init__(self)
        self.box_width = width
        self._height = 140
        self.items = [
            ("Information boundaries",
             "Uncertainty about what information was appropriate to enter, including unclassified but sensitive material."),
            ("Commercial sensitivity",
             "Some respondents avoided uploading material that was allowed by classification but felt commercially sensitive."),
            ("Validation and APS safeguards",
             "Respondents raised the need to check outputs and noted differences between public tools and Copilot safeguards."),
        ]

    def wrap(self, availWidth, availHeight):
        self.box_width = availWidth
        return self.box_width, self._height

    def draw(self):
        c = self.canv
        w = self.box_width
        h = self._height
        pad = PANEL.padding_medium

        draw_panel_background(c, 0, 0, w, h, stroke_width=0, radius=0)

        c.setFillColor(DEWR_DARK_GREY)
        c.setFont(FONT_BOLD, VISUAL_TEXT.panel_header_small)
        c.drawString(pad, h - 22, "THEMES OF UNCERTAINTY IN OPEN-TEXT RESPONSES")
        c.setStrokeColor(DEWR_LIGHT_GREY)
        c.setLineWidth(LINES.fine)
        c.line(pad, h - 36, w - pad, h - 36)

        col_w = (w - 2 * pad) / 3
        title_top = h - 58
        body_top = h - 88
        bottom_y = 16
        for i, (title, text) in enumerate(self.items):
            x = pad + i * col_w
            if i:
                c.setStrokeColor(DEWR_LIGHT_GREY)
                c.line(x, bottom_y, x, h - 48)

            title_p = Paragraph(title, ParagraphStyle(
                "uncertainty_title",
                fontName=FONT_BOLD,
                fontSize=VISUAL_TEXT.theme_title,
                leading=VISUAL_TEXT.theme_title_leading,
                textColor=DEWR_DARK_GREY,
            ))
            title_w = col_w - 30
            title_h = title_p.wrap(title_w, 32)[1]
            title_p.drawOn(c, x + 10, title_top - title_h)
            p = Paragraph(text, ParagraphStyle(
                "uncertainty_text",
                fontName=FONT_REGULAR,
                fontSize=VISUAL_TEXT.theme_body,
                leading=VISUAL_TEXT.theme_body_leading,
                textColor=DEWR_DARK_GREY,
            ))
            _, text_h = p.wrap(title_w, 54)
            p.drawOn(c, x + 10, body_top - text_h)


class SafeguardModelPanel(Flowable):
    """Four-part safeguard model for future rollout."""
    def __init__(self, width):
        Flowable.__init__(self)
        self.box_width = width
        self._height = 126
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
        w = self.box_width
        h = self._height
        pad = PANEL.padding

        draw_panel_background(c, 0, 0, w, h, stroke_width=0, radius=0)

        c.setFillColor(DEWR_DARK_GREY)
        c.setFont(FONT_BOLD, VISUAL_TEXT.panel_header)
        c.drawString(pad, h - 22, "SAFEGUARD OPERATING MODEL")
        c.setStrokeColor(DEWR_LIGHT_GREY)
        c.setLineWidth(LINES.fine)
        c.line(pad, h - 36, w - pad, h - 36)

        col_w = (w - 2 * pad) / 4
        for i, (title, text) in enumerate(self.items):
            x = pad + i * col_w
            if i:
                c.setStrokeColor(DEWR_LIGHT_GREY)
                c.line(x, 18, x, h - 46)

            c.setFillColor(DEWR_DARK_GREEN if i < 2 else DEWR_DARK_GREY)
            c.setFont(FONT_BOLD, VISUAL_TEXT.callout_text)
            c.drawString(x + 9, h - 60, title)
            p = Paragraph(text, ParagraphStyle(
                "safeguard_model_text",
                fontName=FONT_REGULAR,
                fontSize=VISUAL_TEXT.model_body,
                leading=VISUAL_TEXT.model_body_leading,
                textColor=DEWR_DARK_GREY,
            ))
            p.wrap(col_w - 20, 42)
            p.drawOn(c, x + 9, h - 102)


class ConcernClusterMap(Flowable):
    """Two-cluster map for open-text concern themes."""
    def __init__(self, width):
        Flowable.__init__(self)
        self.box_width = width
        self._height = 158
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
        w = self.box_width
        h = self._height
        pad = PANEL.padding
        cluster_gap = 20
        cluster_w = (w - 2 * pad - cluster_gap) / 2

        draw_panel_background(c, 0, 0, w, h, stroke_width=0, radius=0)

        for cluster_idx, (title, rows) in enumerate(self.clusters):
            x = pad + cluster_idx * (cluster_w + cluster_gap)
            if cluster_idx:
                c.setStrokeColor(DEWR_LIGHT_GREY)
                c.setLineWidth(LINES.fine)
                c.line(x - cluster_gap / 2, 18, x - cluster_gap / 2, h - 18)

            c.setFillColor(DEWR_DARK_GREY)
            c.setFont(FONT_BOLD, VISUAL_TEXT.panel_header_small)
            c.drawString(x, h - 24, title)
            c.setStrokeColor(DEWR_LIGHT_GREY)
            c.line(x, h - 38, x + cluster_w, h - 38)

            row_y = h - 62
            for row_idx, (dot_count, label) in enumerate(rows):
                y = row_y - row_idx * 28
                dot_center_y = y + 4
                for dot_idx in range(3):
                    c.setFillColor(DEWR_DARK_GREEN if dot_idx < dot_count and cluster_idx == 0 else
                                   DEWR_DARK_GREY if dot_idx < dot_count else BAR_TRACK)
                    c.circle(x + 6 + dot_idx * 10, dot_center_y, CHART_LAYOUT.dot_radius_small, fill=1, stroke=0)
                p = Paragraph(label, ParagraphStyle(
                    "concern_cluster_label",
                    fontName=FONT_REGULAR,
                    fontSize=VISUAL_TEXT.model_body,
                    leading=VISUAL_TEXT.theme_body_leading,
                    textColor=DEWR_NAVY,
                ))
                _, label_h = p.wrap(cluster_w - 40, 24)
                p.drawOn(c, x + 38, dot_center_y - label_h / 2)


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
        w = self.box_width
        h = self._height
        pad = PANEL.padding_large
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
        chat_text_x = legend_right - chat_w
        chat_marker_x = chat_text_x - marker_gap
        m365_text_x = chat_marker_x - item_gap - m365_w
        m365_marker_x = m365_text_x - marker_gap
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
            p = Paragraph(label, ParagraphStyle(
                "full_task_dumbbell_label",
                fontName=FONT_BOLD if highlight else FONT_REGULAR,
                fontSize=VISUAL_TEXT.chart_label,
                leading=VISUAL_TEXT.chart_label_leading,
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

            if highlight:
                c.setFont(FONT_BOLD, VISUAL_TEXT.chart_value_label)
                c.setFillColor(DEWR_DARK_GREY)
                c.drawRightString(chat_x - 6, y - 3, f"{chat:.1f}%")
                c.setFillColor(DEWR_DARK_GREEN)
                c.drawString(m365_x + 6, y - 3, f"{m365:.1f}%")


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
        style = ParagraphStyle('kf_measure', fontName=FONT_BOLD,
                               fontSize=VISUAL_TEXT.key_finding, leading=VISUAL_TEXT.key_finding_leading,
                               textColor=DEWR_DARK_GREY)
        p = Paragraph(self.text, style)
        w, h = p.wrap(self.box_width - 24, availHeight)
        self._height = h + 20
        return self.box_width, self._height

    def draw(self):
        self.canv.setFillColor(self.bg_color)
        self.canv.rect(0, 0, self.box_width, self._height, fill=1, stroke=0)
        self.canv.setFillColor(self.border_color)
        self.canv.rect(0, 0, 4, self._height, fill=1, stroke=0)
        style = ParagraphStyle('kf_draw', fontName=FONT_BOLD,
                               fontSize=VISUAL_TEXT.key_finding, leading=VISUAL_TEXT.key_finding_leading,
                               textColor=DEWR_DARK_GREY)
        p = Paragraph(self.text, style)
        p.wrap(self.box_width - 24, self._height)
        p.drawOn(self.canv, 16, 10)


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
    canvas.drawString(doc.leftMargin, PAGE_CHROME.footer_text_y,
                      "Department of Employment and Workplace Relations")
    canvas.drawRightString(A4[0] - doc.rightMargin, PAGE_CHROME.footer_text_y,
                           f"Page {doc.page}")
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
    canvas.restoreState()


def build_report():
    doc = SimpleDocTemplate(
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
    s1_h2 = styles["s1_h2"]
    s1_h3 = styles["s1_h3"]
    s1_body = styles["s1_body"]

    def bullet(text):
        return Paragraph(f"<bullet>&bull;</bullet> {text}", bullet_style)

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

    def callout(text, color=DEWR_DARK_GREEN):
        return CalloutBox(text, width, bg_color=color)

    def key_finding(text, color=DEWR_GREEN):
        return KeyFindingBar(text, width, border_color=color)

    def visual_title(text):
        return Paragraph(text, chart_title)

    def source_note(text):
        return Paragraph(f"<i>{text}</i>", note_style)

    def access_evidence_table():
        header_style = ParagraphStyle(
            "AccessEvidenceHeader",
            fontName=FONT_BOLD,
            fontSize=VISUAL_TEXT.table_header,
            leading=VISUAL_TEXT.table_header_leading,
            alignment=TA_CENTER,
            textColor=DEWR_DARK_GREY,
        )
        measure_header_style = ParagraphStyle(
            "AccessEvidenceMeasureHeader",
            parent=header_style,
            alignment=TA_LEFT,
        )
        measure_style = ParagraphStyle(
            "AccessEvidenceMeasure",
            fontName=FONT_BOLD,
            fontSize=VISUAL_TEXT.table_label,
            leading=VISUAL_TEXT.table_label_leading,
            textColor=DEWR_DARK_GREY,
        )
        value_style_dark = ParagraphStyle(
            "AccessEvidenceValueDark",
            fontName=FONT_BOLD,
            fontSize=VISUAL_TEXT.table_value,
            leading=VISUAL_TEXT.table_value_leading,
            alignment=TA_CENTER,
            textColor=DEWR_DARK_GREY,
        )
        value_style_green = ParagraphStyle(
            "AccessEvidenceValueGreen",
            parent=value_style_dark,
            textColor=DEWR_DARK_GREEN,
        )
        value_style_red = ParagraphStyle(
            "AccessEvidenceValueRed",
            parent=value_style_dark,
            textColor=DEWR_RED,
        )
        data = [
            [
                Paragraph("MEASURE", measure_header_style),
                Paragraph("COPILOT CHAT", header_style),
                Paragraph("M365 COPILOT", header_style),
            ],
            [
                Paragraph("Public AI rated at least moderately useful", measure_style),
                Paragraph("81.8%", value_style_green),
                Paragraph("78.6%", value_style_dark),
            ],
            [
                Paragraph("Copilot rated at least moderately useful", measure_style),
                Paragraph("69.7%", value_style_dark),
                Paragraph("92.9%", value_style_green),
            ],
            [
                Paragraph("Public AI used weekly or more", measure_style),
                Paragraph("54.5%", value_style_green),
                Paragraph("50.0%", value_style_dark),
            ],
            [
                Paragraph("Copilot used weekly or more", measure_style),
                Paragraph("57.6%", value_style_dark),
                Paragraph("85.7%", value_style_green),
            ],
            [
                Paragraph("Public AI added value beyond Copilot", measure_style),
                Paragraph("75.0%", value_style_dark),
                Paragraph("82.1%", value_style_green),
            ],
        ]
        first_w = width * 0.52
        col_w = (width - first_w) / 2
        table = Table(
            data,
            colWidths=[first_w, col_w, col_w],
            rowHeights=[TABLE_SPEC.access_header_height] + [TABLE_SPEC.access_row_height] * (len(data) - 1),
        )
        table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), DEWR_OFF_WHITE),
            ("LINEBELOW", (0, 0), (-1, 0), LINES.regular, DEWR_SOFT_LINE),
            ("LINEBELOW", (0, 1), (-1, 1), LINES.regular, DEWR_SOFT_LINE),
            ("LINEBELOW", (0, 2), (-1, 2), LINES.regular, DEWR_SOFT_LINE),
            ("LINEBELOW", (0, 3), (-1, 3), LINES.regular, DEWR_SOFT_LINE),
            ("LINEBELOW", (0, 4), (-1, 4), LINES.regular, DEWR_SOFT_LINE),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("ALIGN", (0, 0), (0, 0), "LEFT"),
            ("ALIGN", (1, 1), (-1, -1), "CENTER"),
            ("ALIGN", (0, 0), (0, -1), "LEFT"),
            ("LEFTPADDING", (0, 0), (-1, -1), TABLE_SPEC.cell_padding_x),
            ("RIGHTPADDING", (0, 0), (-1, -1), TABLE_SPEC.cell_padding_x),
            ("TOPPADDING", (0, 0), (-1, -1), TABLE_SPEC.cell_padding_y),
            ("BOTTOMPADDING", (0, 0), (-1, -1), TABLE_SPEC.cell_padding_y),
        ]))
        return table

    def sp(h=SPACING.sm + 2):
        return Spacer(1, h)

    def visual_spacer():
        return sp(SPACING.lg)

    # ==============================
    # COVER PAGE
    # ==============================
    story.append(PageBreak())

    # ==============================
    # EVALUATION FINDINGS
    # ==============================
    story.append(Paragraph("Evaluation findings", evaluation_h1))
    story.append(sp(10))

    # Section 1: Copilot
    story.append(Paragraph("1. Copilot usage and productivity", s1_h2))
    story.append(Paragraph(
        "A total of 71 survey respondents indicated that they used Copilot and answered questions "
        "about how they used it, how often, and how much time they believed it saved them.",
        section_intro))
    story.append(sp(4))
    story.append(callout(
        "Copilot already delivers material productivity value, but benefits are tiered by "
        "access: integrated M365 Copilot produces stronger time savings, deeper engagement "
        "and a broader task footprint than Copilot Chat."))
    story.append(ValueSignalsPanel(width, [
        ("2.0x", "M365 Copilot users reported twice as much average weekly time saved as Copilot Chat users"),
        ("1.9x", "M365 Copilot users were 1.9x as likely to rate Copilot very or extremely useful"),
        ("1.5x", "M365 Copilot users were 1.5x as likely to use Copilot weekly or more often"),
    ], primary_count=1))
    story.append(sp(12))

    # Time savings
    story.append(Paragraph("1.1 M365 Copilot users reported higher time savings", s1_h3))
    story.append(Paragraph(
        "M365 Copilot users reported average time savings of 5.7 hours per week, compared with "
        "2.8 hours per week for Copilot Chat users. This means M365 Copilot users reported "
        "roughly twice the weekly time savings of Copilot Chat users.", s1_body))
    story.append(visual_spacer())
    story.append(TimeSavingsPanel(width))
    story.append(sp(6))
    story.append(Paragraph(
        "The reported 68 minutes per day for M365 Copilot users is in the same broad range as the "
        "DTA whole-of-government Copilot trial, which identified around an hour a day of perceived "
        "savings in high-frequency tasks such as summarising, drafting and meeting support.",
        s1_body))
    story.append(source_note(
        "Note: The DTA reported these as task-level approximations, rather than a single overall "
        "average daily gain; the comparison is best interpreted as directional context rather than "
        "a direct benchmark."))
    story.append(sp(12))

    # Usefulness and frequency
    story.append(KeepTogether([
        Paragraph("1.2 Higher time savings were matched by deeper engagement", s1_h3),
        Paragraph(
            "The productivity gap was reinforced by engagement signals. M365 Copilot users were "
            "more likely to rate Copilot as highly useful and to use it more frequently.", s1_body),
        visual_spacer(),
        CopilotEngagementDeltaPanel(width),
    ]))
    story.append(sp(8))
    story.append(Paragraph("Average weekly time saved by cohort", mini_heading))
    story.append(EvidenceMatrixPanel(
        width,
        "CLASSIFICATION LEVEL",
        ["M365 Copilot", "Copilot Chat"],
        [
            ("APS level", ["6.0 hrs", "3.5 hrs"], 0),
            ("EL/SES level", ["5.4 hrs", "2.0 hrs"], 0),
        ],
        first_col_ratio=0.50,
    ))
    story.append(sp(8))
    story.append(Paragraph("Average weekly time saved by organisational group", mini_heading))
    story.append(EvidenceMatrixPanel(
        width,
        "ORGANISATIONAL GROUP",
        ["M365 Copilot", "Copilot Chat"],
        [
            ("Corporate and Enabling", ["6.3 hrs", "2.5 hrs"], 0),
            ("Employment and Workforce", ["6.3 hrs", "2.9 hrs"], 0),
            ("Skills and Training", ["5.4 hrs", "2.9 hrs"], 0),
            ("Workplace Relations", ["5.0 hrs", "4.0 hrs"], 0),
        ],
        first_col_ratio=0.50,
    ))
    story.append(sp(4))
    story.append(source_note(
        "Note: Values show average weekly hours saved from valid Q17 Copilot time-saved responses."))
    story.append(sp(12))

    # Department usage and value
    story.append(KeepTogether([
        Paragraph("1.3 Copilot Usage and Value Across the Department", s1_h3),
        sp(2),
        Paragraph(
            "While M365 Copilot users reported substantially higher time savings, current M365 licence "
            "coverage was limited across the trial workforce. M365 licences covered <b>4.5%</b> of APS "
            "level staff and <b>9.9%</b> of EL level staff.",
            s1_body),
        sp(6),
        Paragraph(
            "Across organisational groups, coverage ranged from <b>5.7%</b> in Skills and Training "
            "to <b>10.6%</b> in Workplace Relations. This means the strongest reported productivity "
            "gains were concentrated among a relatively small licensed cohort.",
            s1_body),
        visual_spacer(),
    ]))
    story.append(KeepTogether([
        M365LicenceCoveragePanel(width),
        sp(4),
        source_note(
            "Note: Licence coverage uses current M365 licence counts as a share of all staff in each group. "
            "Classification level and organisational group are separate cuts of the workforce and should not be summed."),
    ]))
    story.append(sp(12))

    # Task types
    story.append(KeepTogether([
        Paragraph("1.4 M365 Copilot users reported a broader task footprint", s1_h3),
        sp(2),
        Paragraph(
            "All versions of Copilot were used most often for summarising, editing and revision, "
            "and drafting, but M365 Copilot users reported greater use across more task types on "
            "average than Copilot Chat users.", s1_body),
        sp(6),
        evidence_bullet(
            "M365 Copilot users were more likely to use it for research, problem solving and "
            "ideation, and for planning or meeting preparation."),
        evidence_bullet(
            "These tasks are typically more complex than drafting or summarising alone, suggesting "
            "M365 Copilot version may be associated with broader use in higher-value knowledge-work "
            "activities."),
        visual_spacer(),
        TaskFootprintExhibit(width),
    ]))
    story.append(sp(14))

    # Section 2: Public Gen AI
    story.append(PageBreak())
    story.append(Paragraph("2. Public Gen AI uptake and use", h2))
    story.append(Paragraph(
        "A total of 61 survey respondents indicated that they used one of the Public Generative AI "
        "tools during the trial and answered questions about how they used it, how often, and how "
        "much time they believed it saved them.", section_intro))
    story.append(sp(4))
    story.append(callout(
        "Public Gen AI tools created clear value for many trial users, but benefits were uneven: "
        "strongest for experienced users, staff with Copilot Chat, and tasks where "
        "public tools offered capability or quality beyond Copilot."))
    story.append(ValueSignalsPanel(width, [
        ("80%", "Rated at least one public tool useful"),
        ("72%", "Said public tools add value beyond Copilot"),
        ("72%", "Wanted continued access"),
        ("53%", "Used public tools at least weekly"),
    ], primary_count=1))
    story.append(sp(12))

    # 2.1 Tool comparison
    story.append(Paragraph("2.1 ChatGPT had the widest reach; Claude had the strongest value signals", h3))
    story.append(Paragraph(
        "ChatGPT was the access point for most trial users, while Claude showed the strongest "
        "high-usefulness signal: 46.3% of Claude users rated it very or extremely useful, "
        "compared with 29.7% for Gemini and 28.6% for ChatGPT. This suggests the public-tool choice was not simply about "
        "uptake; different tools played different roles.", body))
    story.append(visual_spacer())
    story.append(EvidenceMatrixPanel(
        width,
        "MEASURE",
        ["ChatGPT", "Claude", "Gemini"],
        [
            ("Used tool during trial", ["92%", "67%", "61%"], 0),
            ("Rated at least moderately useful", ["62.5%", "70.7%", "64.9%"], 1),
            ("Rated very/extremely useful", ["28.6%", "46.3%", "29.7%"], 1),
            ("Wanted continued access", ["54%", "63%", "43%"], 1),
        ],
        first_col_ratio=0.43,
    ))
    story.append(sp(8))

    # 2.2 Task types
    story.append(Paragraph("2.2 Public tools were mainly used for broad knowledge work", h3))
    story.append(Paragraph(
        "Use clustered around general knowledge-work tasks rather than specialised or "
        "administrative workflows. Research, summarising, editing and drafting were the "
        "dominant use cases across the trial.", body))
    story.append(Paragraph(
        "Tool use profiles varied by task. Claude had the strongest research profile, with "
        "73.2% of Claude users using it for research, problem solving or generating ideas.", body))
    story.append(Paragraph(
        "Claude was also notably higher for coding or data work at 26.8%, compared with 13.5% "
        "for Gemini and 10.7% for ChatGPT. Gemini was strongest for editing and revision, at "
        "56.8%, while ChatGPT showed a relatively balanced profile across summarising, drafting, "
        "editing and research.", body))
    story.append(visual_spacer())
    story.append(PublicToolTaskProfilePanel(width))
    story.append(source_note(
        "Note: Percentages are based on users of each respective tool: ChatGPT n=56; Gemini n=37; Claude n=41. "
        "Labelled values indicate the highest tool-specific share for each task. Source: DEWR Public Generative AI Trial survey, 2026."))
    story.append(sp(10))

    # 2.3 Productivity from Public Gen AI
    story.append(Paragraph("2.3 Productivity from Public Gen AI", h3))
    story.append(Paragraph(
        "Survey results suggest that public AI tools were valued differently depending on respondents' "
        "existing Copilot version. Among Copilot Chat/basic users, <b>81.8%</b> rated public AI tools useful, "
        "compared with <b>69.7%</b> who rated Copilot at least moderately useful. Among M365 Copilot users, the pattern was "
        "reversed: <b>92.9%</b> rated Copilot at least moderately useful, compared with <b>78.6%</b> who rated public AI "
        "tools useful.", body))
    story.append(visual_spacer())
    story.append(access_evidence_table())
    story.append(source_note(
        "Note: Results are based on respondents with known Copilot version who used at least one public AI tool and "
        "provided valid responses for the relevant measures. Copilot Chat/basic n=33 and M365 Copilot n=28 unless noted; "
        "the added-value row uses Copilot Chat/basic n=32. Useful means moderately, very or extremely useful."))
    story.append(sp(8))
    story.append(Paragraph(
        "Weekly use points to the same relative pattern. Public AI weekly use was similar across access "
        "groups (<b>54.5%</b> for Copilot Chat/basic users and <b>50.0%</b> for M365 Copilot users). However, "
        "for Copilot Chat/basic users, public AI weekly use sat close to their Copilot weekly use "
        "(<b>57.6%</b>), while for M365 Copilot users it sat well below their Copilot weekly use "
        "(<b>85.7%</b>). Public AI added value beyond Copilot for "
        "<b>75.0%</b> of Copilot Chat/basic users and "
        "<b>82.1%</b> of M365 Copilot users.", body))

    story.append(sp(8))
    story.append(Paragraph("Public Gen AI usage by cohort", h2))
    story.append(sp(4))

    # 2.4 Prior experience variation
    story.append(KeepTogether([
        Paragraph("2.4 Prior Gen AI experience was associated with stronger reported value", h3),
        Paragraph(
            "Prior Gen AI experience was also associated with stronger reported outcomes. Experienced "
            "and highly experienced respondents were more likely to report significant added value from "
            "public tools than respondents with lower levels of prior Gen AI experience.", body),
        visual_spacer(),
        PriorExperienceComparisonPanel(width),
        source_note("Note: Results should be read directionally given the smaller no/basic segment."),
        sp(3),
        Paragraph(
            "Higher-experience users also reported deeper usefulness: <b>73%</b> rated at least one public tool "
            "very or extremely useful, compared with <b>46%</b> some prior Gen AI experience and "
            "<b>39%</b> no/basic prior Gen AI experience.", body),
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
                ("Strongly wanted continued access", ["55%", "31%", "15%"], 0),
            ],
            first_col_ratio=0.33,
        ),
        sp(6),
        Paragraph(
            "They were also more likely to rate at least one public tool better than Copilot on at least "
            "one comparison dimension (<b>86%</b> vs <b>71%</b> for lower-experience users) and to strongly "
            "want continued access (<b>55%</b> vs <b>26%</b> for lower-experience users).", body),
    ]))

    # 2.5 Other segment variation
    story.append(Paragraph("2.5 Reported value varied by classification and organisational group", h3))
    story.append(sp(4))
    story.append(Paragraph("Classification level", mini_heading))
    story.append(sp(4))
    story.append(Paragraph(
        "Classification-level patterns differed by measure. EL level users were slightly more likely to use "
        "public tools weekly or more (<b>53.6% vs 51.5%</b>), while APS level users were more likely to rate "
        "both public tools (<b>87.9% vs 71.4%</b>) and Copilot (<b>84.8% vs 75.0%</b>) as at least moderately useful.", body))
    story.append(sp(5))
    story.append(key_finding(
        "EL level users were more likely to report that public tools added value beyond Copilot "
        "(<b>78.6%</b> vs <b>66.7%</b> for APS level users)."))
    story.append(visual_spacer())
    story.append(EvidenceMatrixPanel(
        width,
        "MEASURE",
        ["APS level", "EL level"],
        [
            ("Public tools", None, None),
            ("Used weekly or more", ["51.5%", "53.6%"], 1),
            ("Rated at least moderately useful", ["87.9%", "71.4%"], 0),
            ("Copilot", None, None),
            ("Used weekly or more", ["72.7%", "67.9%"], 0),
            ("Rated at least moderately useful", ["84.8%", "75.0%"], 0),
        ],
        first_col_ratio=0.56,
    ))
    story.append(sp(8))
    story.append(Paragraph("Organisational group", mini_heading))
    story.append(sp(4))
    story.append(Paragraph(
        "Reported value also varied across groups. Workplace Relations recorded the strongest added-value "
        "result (<b>85.7%</b>), while Employment and Workforce and Corporate and Enabling recorded high "
        "usefulness results (<b>84.2%</b> and <b>83.3%</b> respectively). Skills and Training recorded "
        "comparatively weaker results across both measures.", body))
    story.append(visual_spacer())
    story.append(EvidenceMatrixPanel(
        width,
        "GROUP",
        ["Added value beyond Copilot", "Rated at least moderately useful"],
        [
            ("Corporate and Enabling", ["66.7%", "83.3%"], 1),
            ("Employment and Workforce", ["73.7%", "84.2%"], 1),
            ("Skills and Training", ["53.8%", "69.2%"], None),
            ("Workplace Relations", ["85.7%", "78.6%"], 0),
        ],
        first_col_ratio=0.32,
    ))
    story.append(source_note(
        "Note: Jobs and Skills Australia was excluded because of low sample size (n=3)."))
    story.append(sp(4))

    # 2.6 Barriers
    story.append(PageBreak())
    story.append(Paragraph("2.6 Limitations were common, led by lack of integration with internal systems and request limits", h3))
    story.append(sp(4))
    story.append(HorizontalEvidenceCallout(
        width,
        "Limitations reported",
        "92%",
        "of respondents reported at least one limitation with at least one public AI tool",
        "",
    ))
    story.append(sp(11))
    story.append(Paragraph("Limitations clustered around three signals:", body_bold))
    story.append(sp(2))
    story.append(limitation_bullet(
        "<b>Integration was the universal workflow barrier:</b> <b>49%</b> of survey respondents reported "
        "lack of integration, with tool-level rates around half of users across ChatGPT, Gemini and Claude."))
    story.append(limitation_bullet(
        "<b>Request limits were the main access constraint:</b> <b>41%</b> of survey respondents reported "
        "free prompt/request limits."))
    story.append(limitation_bullet(
        "<b>Limits were most acute for experienced users:</b> <b>59.1%</b> of experienced/highly "
        "experienced users reported request limits, compared with <b>30.8%</b> of both lower-experience groups."))
    story.append(visual_spacer())
    story.append(HorizontalBarPanel(width, "LIMITATIONS REPORTED BY RESPONDENTS", [
        ("Lack of integration with internal systems or Microsoft 365 products", 49),
        ("Free prompt/request limits", 41),
        ("Misinterpreted prompts", 34),
        ("Difficulty with specialised topics", 34),
        ("Slow responses", 28),
        ("Fabricated content or hallucinations", 15),
    ], max_value=100, primary_count=2, row_h=CHART_LAYOUT.row_height_dense))
    story.append(sp(8))
    story.append(Paragraph(
        "The limitation profile also varied by tool. Lack of integration was common across all three "
        "tools, affecting <b>48%</b> of ChatGPT users, <b>49%</b> of Gemini users and <b>51%</b> of "
        "Claude users. Free prompt or request limits were more concentrated in ChatGPT, reported by "
        "<b>36%</b> of ChatGPT users, compared with <b>20%</b> of Claude users and <b>5%</b> of Gemini "
        "users. Gemini had the highest share of users reporting difficulty with specialised topics, "
        "at <b>38%</b>.", body))

    # Section 3: Concerns
    story.append(PageBreak())
    story.append(Paragraph("3. Concerns, risks and safeguards", h2))
    story.append(Paragraph(
        "All survey respondents were asked about concerns, comfort using public Gen AI tools, "
        "data-handling behaviour and the effectiveness of trial safety communications.",
        section_intro))
    story.append(sp(4))
    story.append(callout(
        "Most survey respondents were comfortable and reported security concerns were rare. Survey "
        "results suggest safety communications and splash screens supported cautious use, while "
        "data-handling risks were mainly visible through copy/paste behaviour and user judgement.",
        DEWR_DARK_GREEN))
    story.append(ValueSignalsPanel(width, [
        ("75%", "Comfortable or very comfortable using public tools"),
        ("25%", "Uncomfortable using public tools"),
        ("12%", "Ethical concerns encountered"),
        ("3%", "Reported specific security concerns"),
    ], primary_count=1))
    story.append(sp(12))

    story.append(Paragraph("3.1 Most respondents were comfortable; security concerns were present but rare", h3))
    story.append(Paragraph(
        "Survey results showed relatively high comfort using public tools. Three-quarters of "
        "respondents were comfortable or very comfortable using public tools, while one-quarter "
        "were uncomfortable. Reported concern signals were lower: "
        "<b>12%</b> reported ethical "
        "concerns and <b>3%</b> reported specific security concerns.", body))
    story.append(Paragraph(
        "Comfort was also higher among respondents who rated both the introductory email and splash "
        "screens effective: <b>82.5%</b> of this group were comfortable or very comfortable using "
        "public tools, compared with <b>60.0%</b> among respondents who did not rate both channels "
        "effective.", body))
    story.append(sp(8))

    story.append(Paragraph("3.2 Open-text responses showed uncertainty at practical boundaries", h3))
    story.append(Paragraph(
        "Open-text responses still showed uncertainty at practical boundaries, particularly where "
        "information was technically allowed but still sensitive, commercially confidential, difficult "
        "to classify, or required output validation.", body))
    story.append(visual_spacer())
    story.append(UncertaintyAreasPanel(width))
    story.append(PageBreak())

    story.append(Paragraph("3.3 Respondents were more likely to copy/paste information than upload documents", h3))
    story.append(Paragraph(
        "Reported data-handling behaviour varied by activity. Copying and pasting information "
        "into public tools was more common than uploading documents. Among survey respondents, "
        "<b>70.5%</b> copied and pasted information, while <b>42.6%</b> uploaded documents.", body))
    story.append(visual_spacer())
    story.append(HorizontalBarPanel(width, "MEASURE", [
        ("Copied and pasted information", 70.5),
        ("Uploaded documents", 42.6),
    ], max_value=100, primary_count=1))
    story.append(sp(6))
    story.append(Paragraph(
        "Comfort level appeared to shape the type of data-handling behaviour. Respondents who were "
        "comfortable or very comfortable using public tools were much more likely to upload documents "
        "(<b>47.8%</b> vs <b>26.7%</b>), while copy/paste behaviour was more similar across comfort "
        "groups (<b>71.7%</b> vs <b>66.7%</b>). This suggests lower comfort may have shifted users "
        "toward more cautious forms of information sharing, such as copy/paste, rather than full "
        "document upload.", body))
    story.append(visual_spacer())
    story.append(ComfortDataHandlingPanel(width))
    story.append(sp(8))

    story.append(Paragraph("3.4 Safety communications were rated effective by most survey respondents", h3))
    story.append(ValueSignalsPanel(width, [
        ("74%", "Introductory email moderately or highly effective"),
        ("72%", "Splash screens moderately or highly effective"),
        ("67%", "Rated both email and splash screens effective"),
    ], primary_count=0))
    story.append(sp(10))
    story.append(Paragraph(
        "Most respondents rated the safety communications positively: the introductory email was rated "
        "moderately or highly effective by <b>74%</b> of respondents, while splash screens were rated "
        "moderately or highly effective by <b>72%</b>. Two-thirds of respondents rated both the email "
        "and splash screens as effective.", body))
    story.append(Paragraph(
        "Upload blockers were less visible in the survey results: <b>16.7%</b> of respondents "
        "noticed or rated upload blockers as effective, and no respondent rated upload blockers "
        "ineffective.", body))
    story.append(sp(8))

    # Appendix
    story.append(PageBreak())
    story.append(Paragraph("Appendix A. All-tool task footprint", h2))
    story.append(Paragraph("Share of respondents per tool reporting each task, including Copilot", h3))
    story.append(Paragraph(
        "This option extends the section 2 task-profile visual by adding M365 Copilot and "
        "Copilot Chat to the public-tool comparison. Values are shown on a common percentage "
        "scale to compare task footprints across all five tools.", body))
    story.append(visual_spacer())
    story.append(AllToolTaskProfilePanel(width))
    story.append(sp(4))
    story.append(source_note(
        "Note: Public-tool percentages are based on users of each respective tool: ChatGPT n=56; "
        "Gemini n=37; Claude n=41. Copilot percentages are based on respondents with known "
        "Copilot access and valid Q14 responses: M365 Copilot n=31; Copilot Chat/basic n=39. "
        "Sources: DEWR Public Generative AI Trial survey, 2026; section 1 and section 2 analysis tables."))

    # Build
    doc.build(story, onFirstPage=cover_page, onLaterPages=header_footer)
    print(f"Report generated: {OUTPUT_PATH}")


if __name__ == "__main__":
    build_report()
