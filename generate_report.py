from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm, cm
from reportlab.lib.colors import HexColor, white, black
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, KeepTogether, HRFlowable, ListFlowable, ListItem
)
from reportlab.platypus.flowables import Flowable
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import os

# DEWR Colors
DEWR_GREEN = HexColor("#719F4C")
DEWR_DARK_GREEN = HexColor("#5D7A38")
DEWR_DARK_GREY = HexColor("#404246")
DEWR_NAVY = DEWR_DARK_GREY
DEWR_BLUE = DEWR_DARK_GREY
DEWR_DARK_BLUE = DEWR_DARK_GREY
DEWR_TEAL = HexColor("#009B9F")
DEWR_GREY = HexColor("#A4A7A9")
DEWR_LIGHT_GREY = HexColor("#D7D8D8")
DEWR_LIME = HexColor("#B5C427")
DEWR_RED = HexColor("#91040D")
DEWR_OFF_WHITE = HexColor("#F7F8FA")
DEWR_SOFT_LINE = HexColor("#E1E3DF")
DEWR_TEXT_GREY = HexColor("#6B6E70")
DEWR_MUTED_GREY = HexColor("#B8BBBD")

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "Outputs")
OUTPUT_PATH = os.path.join(OUTPUT_DIR, "DEWR_Public_AI_B.pdf")
COVER_LOCKUP_PATH = os.path.join(os.path.dirname(__file__), "assets", "dewr_cover_lockup_white.png")
os.makedirs(OUTPUT_DIR, exist_ok=True)


class CalloutBox(Flowable):
    """A colored callout box with text."""
    def __init__(self, text, width, bg_color=DEWR_NAVY, text_color=white, font_size=11, padding=12):
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
        style = ParagraphStyle('callout_measure', fontName='Helvetica-Bold',
                               fontSize=self.font_size, leading=self.font_size + 4,
                               textColor=self.text_color)
        p = Paragraph(self.text, style)
        w, h = p.wrap(self.box_width - 2 * self.padding, availHeight)
        self._height = h + 2 * self.padding
        return self.box_width, self._height

    def draw(self):
        self.canv.setFillColor(self.bg_color)
        self.canv.rect(0, 0, self.box_width, self._height, fill=1, stroke=0)
        style = ParagraphStyle('callout_draw', fontName='Helvetica-Bold',
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
        return self.box_width, 55

    def draw(self):
        self.canv.setFillColor(self.color)
        self.canv.roundRect(0, 0, self.box_width, 55, 4, fill=1, stroke=0)
        self.canv.setFillColor(white)
        stat_size = 20
        max_stat_width = self.box_width - 24
        while stat_size > 14 and self.canv.stringWidth(self.stat, "Helvetica-Bold", stat_size) > max_stat_width:
            stat_size -= 1
        self.canv.setFont("Helvetica-Bold", stat_size)
        self.canv.drawString(12, 28, self.stat)
        self.canv.setFont("Helvetica", 9)
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
        label_font = "Helvetica-Bold"
        label_size = 8.5
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
        c.setLineWidth(0.5)
        line_y = self._height - 43
        c.line(inset, line_y, self.box_width - inset, line_y)

        # Two halves
        half = self.box_width / 2
        # Highlight side (left)
        c.setFillColor(self.h_color)
        c.setFont("Helvetica-Bold", 22)
        c.drawCentredString(half / 2, 34, self.h_value)
        c.setFillColor(DEWR_DARK_GREY)
        c.setFont("Helvetica", 7.5)
        c.drawCentredString(half / 2, 16, self.h_label)

        # Vertical divider
        c.setStrokeColor(DEWR_LIGHT_GREY)
        c.line(half, 14, half, line_y - 5)

        # Compare side (right)
        c.setFillColor(self.c_color)
        c.setFont("Helvetica-Bold", 22)
        c.drawCentredString(half + half / 2, 34, self.c_value)
        c.setFillColor(DEWR_DARK_GREY)
        c.setFont("Helvetica", 7.5)
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
        pad = 16

        c.setFillColor(HexColor("#F7F8FA"))
        c.rect(0, 0, w, h, fill=1, stroke=0)

        top_offset = 20 if self.title else 0
        if self.title:
            c.setFillColor(DEWR_DARK_GREY)
            c.setFont("Helvetica-Bold", 11)
            c.drawString(pad, h - 20, self.title)
            c.setStrokeColor(DEWR_LIGHT_GREY)
            c.setLineWidth(0.4)
            c.line(pad, h - 31, w - pad, h - 31)

        col_w = (w - 2 * pad) / len(self.items)
        value_y = h - (44 if not self.title else 54)
        label_top_y = value_y - 16
        for i, (value, label) in enumerate(self.items):
            x = pad + i * col_w
            cx = x + col_w / 2
            if i:
                c.setStrokeColor(DEWR_LIGHT_GREY)
                c.line(x, 12, x, h - 12 - top_offset)
            c.setFillColor(DEWR_GREEN if i < self.primary_count else DEWR_DARK_GREY)
            value_size = 22 if len(value) <= 8 else 17
            c.setFont("Helvetica-Bold", value_size)
            c.drawCentredString(cx, value_y, value)
            p = Paragraph(label, ParagraphStyle(
                "value_signal_label",
                fontName="Helvetica",
                fontSize=7.4,
                leading=8.2,
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
        self.padding = 12
        self.card_height = 74
        self.gap = 10
        self._height = None
        self._text_height = None

    def wrap(self, availWidth, availHeight):
        self.box_width = availWidth
        style = ParagraphStyle(
            "callout_signals_measure",
            fontName="Helvetica-Bold",
            fontSize=11,
            leading=15,
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
            fontName="Helvetica-Bold",
            fontSize=11,
            leading=15,
            textColor=white,
        )
        p = Paragraph(self.text, style)
        p.wrap(w - 2 * pad, self._text_height)
        p.drawOn(c, pad, h - pad - self._text_height)

        card_x = pad
        card_y = pad
        card_w = w - 2 * pad
        card_h = self.card_height
        c.setFillColor(HexColor("#F7F8FA"))
        c.roundRect(card_x, card_y, card_w, card_h, 3, fill=1, stroke=0)

        inner_pad = 12
        col_w = (card_w - 2 * inner_pad) / len(self.items)
        value_y = card_y + 41
        label_top_y = card_y + 27
        for i, (value, label) in enumerate(self.items):
            x = card_x + inner_pad + i * col_w
            cx = x + col_w / 2
            if i:
                c.setStrokeColor(DEWR_LIGHT_GREY)
                c.setLineWidth(0.5)
                c.line(x, card_y + 11, x, card_y + card_h - 11)
            c.setFillColor(DEWR_GREEN if i < self.primary_count else DEWR_DARK_GREY)
            value_size = 22 if len(value) <= 8 else 17
            c.setFont("Helvetica-Bold", value_size)
            c.drawCentredString(cx, value_y, value)
            label_p = Paragraph(label, ParagraphStyle(
                "callout_signal_label",
                fontName="Helvetica",
                fontSize=7.4,
                leading=8.2,
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
        pad = 16

        c.setFillColor(HexColor("#F7F8FA"))
        c.rect(0, 0, w, h, fill=1, stroke=0)

        label_w = w * 0.28
        bar_x = pad + label_w
        bar_w = w - bar_x - 112
        bar_h = 11
        max_value = 75
        rows = [
            ("M365 Copilot", 68.7, "5.7 hrs/week", DEWR_DARK_GREEN),
            ("Copilot Chat", 33.8, "2.8 hrs/week", DEWR_DARK_GREY),
        ]
        for i, (label, value, weekly, color) in enumerate(rows):
            y = h - 41 - i * 35
            c.setFillColor(DEWR_DARK_GREY)
            c.setFont("Helvetica-Bold", 8.4)
            c.drawString(pad, y + 1, label)

            c.setFillColor(color)
            c.rect(bar_x, y, bar_w * (value / max_value), bar_h, fill=1, stroke=0)
            c.setFillColor(color)
            c.setFont("Helvetica-Bold", 13)
            c.drawRightString(w - pad, y + 5, weekly)
            c.setFillColor(HexColor("#565B5F"))
            c.setFont("Helvetica", 7.5)
            c.drawRightString(w - pad, y - 12, f"{value} min/day")


class CopilotEngagementDeltaPanel(Flowable):
    """Engagement comparison by Copilot access type."""
    def __init__(self, width):
        Flowable.__init__(self)
        self.box_width = width
        self.rows = [
            ("Rated very/extremely useful", "66.7%", "36.6%"),
            ("Used at least weekly", "80.0%", "56.1%"),
            ("Used daily or most of day", "63.3%", "26.8%"),
        ]
        self._height = 122

    def wrap(self, availWidth, availHeight):
        self.box_width = availWidth
        return self.box_width, self._height

    def draw(self):
        c = self.canv
        w = self.box_width
        h = self._height
        pad = 16

        c.setFillColor(HexColor("#F7F8FA"))
        c.rect(0, 0, w, h, fill=1, stroke=0)

        first_w = w * 0.56
        col_w = (w - first_w - pad) / 2
        head_y = h - 22

        c.setFillColor(DEWR_DARK_GREY)
        c.setFont("Helvetica-Bold", 7.2)
        c.drawString(pad, head_y, "MEASURE")
        for i, col in enumerate(["M365", "CHAT"]):
            c.drawCentredString(first_w + i * col_w + col_w / 2, head_y, col)

        c.setStrokeColor(DEWR_LIGHT_GREY)
        c.setLineWidth(0.5)
        c.line(pad, h - 36, w - pad, h - 36)

        row_h = 27
        for r_idx, (label, m365, chat) in enumerate(self.rows):
            y = h - 58 - r_idx * row_h
            if r_idx:
                c.setStrokeColor(DEWR_LIGHT_GREY)
                c.line(pad, y + 16, w - pad, y + 16)

            c.setFillColor(DEWR_NAVY)
            c.setFont("Helvetica-Bold", 8.1)
            c.drawString(pad, y, label)

            values = [m365, chat]
            for i, value in enumerate(values):
                c.setFillColor(DEWR_DARK_GREEN if i == 0 else DEWR_NAVY)
                c.setFont("Helvetica-Bold", 12)
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
        self.row_h = 26
        self._height = 44 + self.row_h * len(rows)

    def wrap(self, availWidth, availHeight):
        self.box_width = availWidth
        return self.box_width, self._height

    def draw(self):
        c = self.canv
        w = self.box_width
        h = self._height
        pad = 16

        c.setFillColor(HexColor("#F7F8FA"))
        c.rect(0, 0, w, h, fill=1, stroke=0)

        first_w = w * self.first_col_ratio
        data_w = w - first_w - pad
        col_w = data_w / len(self.columns)
        head_y = h - 22

        c.setFillColor(DEWR_DARK_GREY)
        c.setFont("Helvetica-Bold", 7.2)
        c.drawString(pad, head_y, self.title)
        for i, col in enumerate(self.columns):
            c.drawCentredString(first_w + i * col_w + col_w / 2, head_y, col.upper())

        c.setStrokeColor(DEWR_LIGHT_GREY)
        c.setLineWidth(0.5)
        c.line(0, h - 36, w, h - 36)

        for r_idx, row in enumerate(self.rows):
            label, values, highlight_idx = row
            y = h - 57 - r_idx * self.row_h
            if r_idx:
                c.setStrokeColor(DEWR_LIGHT_GREY)
                c.line(0, y + 16, w, y + 16)

            p = Paragraph(label, ParagraphStyle(
                "matrix_label",
                fontName="Helvetica-Bold",
                fontSize=8.0,
                leading=9.5,
                textColor=DEWR_NAVY,
            ))
            p.wrap(first_w - pad - 4, 18)
            p.drawOn(c, pad, y - 3)

            c.setFont("Helvetica-Bold", 11.5)
            for i, value in enumerate(values):
                highlighted = (
                    highlight_idx == "all"
                    or (isinstance(highlight_idx, (list, tuple, set)) and i in highlight_idx)
                    or i == highlight_idx
                )
                c.setFillColor(DEWR_DARK_GREEN if highlighted else DEWR_NAVY)
                c.drawCentredString(first_w + i * col_w + col_w / 2, y, value)


class MarginalValuePanel(Flowable):
    """Compact two-part panel for public-tool marginal value signals."""
    def __init__(self, width):
        Flowable.__init__(self)
        self.box_width = width
        self._height = 126

    def wrap(self, availWidth, availHeight):
        self.box_width = availWidth
        return self.box_width, self._height

    def draw(self):
        c = self.canv
        w = self.box_width
        h = self._height
        pad = 16

        c.setFillColor(HexColor("#F7F8FA"))
        c.rect(0, 0, w, h, fill=1, stroke=0)
        c.setStrokeColor(DEWR_LIGHT_GREY)
        c.setLineWidth(0.5)
        c.line(pad, h / 2, w - pad, h / 2)

        c.setFillColor(DEWR_DARK_GREY)
        c.setFont("Helvetica-Bold", 7.5)
        c.drawString(pad, h - 20, "ACCESS EFFECT")
        c.drawString(pad, h / 2 - 17, "TOOL EFFECT")

        metric_x = pad
        chat_x = w * 0.55
        m365_x = w * 0.78

        c.setFont("Helvetica-Bold", 7.0)
        c.drawCentredString(chat_x, h - 20, "COPILOT CHAT")
        c.drawCentredString(m365_x, h - 20, "M365 COPILOT")

        for y, metric, chat_value, m365_value, highlight_idx in [
            (h - 43, "Added value beyond Copilot", "79%", "63%", 0),
            (h - 61, "Used weekly+", "53%", "52%", None),
        ]:
            c.setFillColor(DEWR_DARK_GREY)
            c.setFont("Helvetica", 7.8)
            c.drawString(metric_x, y, metric)
            c.setFont("Helvetica-Bold", 12)
            c.setFillColor(DEWR_DARK_GREEN if highlight_idx == 0 else DEWR_NAVY)
            c.drawCentredString(chat_x, y, chat_value)
            c.setFillColor(DEWR_DARK_GREEN if highlight_idx == 1 else DEWR_NAVY)
            c.drawCentredString(m365_x, y, m365_value)

        c.setFont("Helvetica-Bold", 7.0)
        c.setFillColor(DEWR_DARK_GREY)
        c.drawCentredString(chat_x, h / 2 - 17, "COPILOT CHAT")
        c.drawCentredString(m365_x, h / 2 - 17, "M365 COPILOT")

        c.setFont("Helvetica", 7.8)
        c.drawString(metric_x, h / 2 - 40, "Strongest tool signal")
        c.setFont("Helvetica-Bold", 15)
        c.setFillColor(DEWR_DARK_GREEN)
        c.drawCentredString(chat_x, h / 2 - 41, "47%")
        c.drawCentredString(m365_x, h / 2 - 41, "44%")
        c.setFont("Helvetica", 7.4)
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
        gap = 10
        card_count = len(self.cards)
        card_w = (w - gap * (card_count - 1)) / card_count

        label_style = ParagraphStyle(
            "evidence_card_label",
            fontName="Helvetica",
            fontSize=8.2,
            leading=9.4,
            textColor=DEWR_DARK_GREY,
            alignment=TA_CENTER,
        )
        vs_style = ParagraphStyle(
            "evidence_card_vs",
            fontName="Helvetica-Bold",
            fontSize=8.2,
            leading=9.3,
            textColor=DEWR_DARK_GREY,
            alignment=TA_CENTER,
        )

        for idx, card in enumerate(self.cards):
            x = idx * (card_w + gap)
            c.setFillColor(HexColor("#F7F8FA"))
            c.rect(x, 0, card_w, h, fill=1, stroke=0)

            c.setFillColor(DEWR_DARK_GREY)
            c.setFont("Helvetica-Bold", 7.2)
            c.drawCentredString(x + card_w / 2, h - 21, card["metric"].upper())
            c.setStrokeColor(DEWR_LIGHT_GREY)
            c.setLineWidth(0.5)
            c.line(x + 16, h - 34, x + card_w - 16, h - 34)

            c.setFillColor(DEWR_DARK_GREEN)
            c.setFont("Helvetica-Bold", 24)
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
        pad = 18
        value_w = 92

        c.setFillColor(HexColor("#F7F8FA"))
        c.rect(0, 0, w, h, fill=1, stroke=0)

        c.setFillColor(DEWR_DARK_GREEN)
        c.setFont("Helvetica-Bold", 22)
        c.drawCentredString(value_w / 2 + 4, 22, self.value)

        c.setStrokeColor(DEWR_LIGHT_GREY)
        c.setLineWidth(0.6)
        c.line(value_w + 8, 16, value_w + 8, h - 16)

        text_style = ParagraphStyle(
            "horizontal_callout_text",
            fontName="Helvetica",
            fontSize=9.3,
            leading=10.8,
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
              font="Helvetica", color=DEWR_DARK_GREY, bold=False):
        style = ParagraphStyle(
            "tmp",
            fontName="Helvetica-Bold" if bold else font,
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

        c.setFillColor(DEWR_OFF_WHITE)
        c.rect(0, 0, w, h, fill=1, stroke=0)

        pad = 28
        inner_w = w - 2 * pad
        gap = 28
        col_w = (inner_w - gap) / 2
        left_x = pad
        right_x = pad + col_w + gap
        divider_x = pad + col_w + gap / 2

        # Column divider
        c.setStrokeColor(DEWR_SOFT_LINE)
        c.setLineWidth(0.6)
        c.line(divider_x, 10, divider_x, h - 10)

        def draw_group(x, title, rows):
            title_y = h - 16
            label_w = 50
            bar_x = x + label_w + 10
            value_gap = 6
            bar_w = col_w - label_w - 48
            bar_h = 12
            max_value = 100

            c.setFillColor(DEWR_DARK_GREY)
            c.setFont("Helvetica-Bold", 9.0)
            title_para = Paragraph(title, ParagraphStyle(
                "usefulness_group_title",
                fontName="Helvetica-Bold",
                fontSize=8.3,
                leading=9.5,
                textColor=DEWR_DARK_GREY,
            ))
            title_para.wrap(col_w - 8, 22)
            title_para.drawOn(c, x, title_y - 12)

            for i, (label, value, color) in enumerate(rows):
                y = title_y - 36 - i * 22
                c.setFillColor(DEWR_DARK_GREY)
                c.setFont("Helvetica", 8.0)
                c.drawString(x, y + 2, label)
                c.setFillColor(color)
                c.rect(bar_x, y, bar_w * value / max_value, bar_h, fill=1, stroke=0)
                c.setFillColor(DEWR_DARK_GREY)
                c.setFont("Helvetica-Bold", 7.6)
                c.drawString(bar_x + bar_w * value / max_value + value_gap, y + 2, f"{value:.1f}%")

        comparison_grey = HexColor("#D7D5CC")
        draw_group(
            left_x,
            "Copilot Chat",
            [
                ("Public AI", 82.4, DEWR_DARK_GREEN),
                ("Copilot", 70.6, comparison_grey),
            ],
        )
        draw_group(
            right_x,
            "M365 Copilot",
            [
                ("Copilot", 92.6, DEWR_DARK_GREY),
                ("Public AI", 77.8, comparison_grey),
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
        pad = 16
        inner_top = h - 16
        col_w = (w - 2 * pad) / 3

        c.setFillColor(HexColor("#F7F8FA"))
        c.rect(0, 0, w, h, fill=1, stroke=0)

        c.setStrokeColor(DEWR_LIGHT_GREY)
        c.setLineWidth(0.5)
        for i in (1, 2):
            x = pad + i * col_w
            c.line(x, 16, x, inner_top)

        columns = [
            ("Experienced/highly experienced", "91%", "reported significant added value", DEWR_DARK_GREEN),
            ("Some prior experience", "73%", "reported significant added value", DEWR_DARK_GREY),
            ("No/basic experience", "62%", "reported significant added value", DEWR_DARK_GREY),
        ]
        label_style = ParagraphStyle(
            "prior_experience_comparison_label",
            fontName="Helvetica",
            fontSize=7.4,
            leading=8.4,
            alignment=TA_CENTER,
            textColor=DEWR_DARK_GREY,
        )
        for i, (name, value, label, color) in enumerate(columns):
            x = pad + i * col_w
            cx = x + col_w / 2
            c.setFillColor(DEWR_DARK_GREY)
            c.setFont("Helvetica-Bold", 7.0)
            c.drawCentredString(cx, h - 24, name)
            c.setFillColor(color)
            c.setFont("Helvetica-Bold", 24)
            c.drawCentredString(cx, h - 56, value)
            p = Paragraph(label, label_style)
            _, label_h = p.wrap(col_w - 24, 22)
            p.drawOn(c, x + 12, 27 - label_h / 2)


class HorizontalBarPanel(Flowable):
    """Full-width grey panel with labelled horizontal bars."""
    def __init__(self, width, title, items, max_value=100, primary_count=0, value_suffix="%", row_h=19):
        Flowable.__init__(self)
        self.box_width = width
        self.title = title
        self.items = items
        self.max_value = max_value
        self.primary_count = primary_count
        self.value_suffix = value_suffix
        self.row_h = row_h
        self._height = 46 + self.row_h * len(items)

    def wrap(self, availWidth, availHeight):
        self.box_width = availWidth
        return self.box_width, self._height

    def draw(self):
        c = self.canv
        w = self.box_width
        h = self._height
        pad = 16

        c.setFillColor(HexColor("#F7F8FA"))
        c.rect(0, 0, w, h, fill=1, stroke=0)

        c.setFillColor(DEWR_DARK_GREY)
        c.setFont("Helvetica-Bold", 7.5)
        c.drawString(pad, h - 22, self.title)
        c.setStrokeColor(DEWR_LIGHT_GREY)
        c.setLineWidth(0.5)
        c.line(pad, h - 36, w - pad, h - 36)

        label_w = w * 0.47
        bar_x = pad + label_w
        bar_w = w - bar_x - 44
        bar_h = 6 if self.row_h < 18 else 7

        for i, (label, value) in enumerate(self.items):
            y = h - 55 - i * self.row_h
            c.setFillColor(DEWR_NAVY)
            c.setFont("Helvetica", 7.6)
            p = Paragraph(label, ParagraphStyle(
                "bar_label",
                fontName="Helvetica",
                fontSize=7.6,
                leading=8.5,
                textColor=DEWR_NAVY,
            ))
            p.wrap(label_w - 8, 16)
            p.drawOn(c, pad, y - 3)

            c.setFillColor(HexColor("#E3E5E6"))
            c.rect(bar_x, y, bar_w, bar_h, fill=1, stroke=0)
            c.setFillColor(DEWR_DARK_GREEN if i < self.primary_count else DEWR_DARK_GREY)
            c.rect(bar_x, y, bar_w * (value / self.max_value), bar_h, fill=1, stroke=0)
            c.setFillColor(DEWR_NAVY)
            c.setFont("Helvetica-Bold", 8.0)
            c.drawRightString(w - pad, y - 1, f"{value:g}{self.value_suffix}")


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
            ("ChatGPT", HexColor("#000000")),
            ("Gemini", DEWR_LIME),
            ("Claude", DEWR_DARK_GREEN),
        ]
        self.max_value = 80
        self.row_h = 23
        self._height = 226

    def wrap(self, availWidth, availHeight):
        self.box_width = availWidth
        return self.box_width, self._height

    def draw(self):
        c = self.canv
        w = self.box_width
        h = self._height
        pad = 16

        c.setFillColor(HexColor("#F7F8FA"))
        c.rect(0, 0, w, h, fill=1, stroke=0)

        label_w = w * 0.35
        axis_x = pad + label_w
        axis_w = w - axis_x - 24
        head_y = h - 22
        tick_y = h - 43
        top_y = h - 62
        bottom_y = top_y - self.row_h * (len(self.rows) - 1)

        c.setFillColor(DEWR_DARK_GREY)
        c.setFont("Helvetica-Bold", 7.5)
        c.drawString(pad, head_y, "SHARE OF RESPONDENTS PER TOOL REPORTING EACH TASK")

        c.setFont("Helvetica", 7.2)
        marker_gap = 8
        item_gap = 16
        legend_w = 0
        for name, _ in self.series:
            legend_w += 5 + marker_gap + c.stringWidth(name, "Helvetica", 7.2) + item_gap
        legend_w -= item_gap
        legend_x = w - pad - legend_w
        for name, color in self.series:
            c.setFillColor(color)
            c.circle(legend_x, head_y + 2, 2.6, fill=1, stroke=0)
            c.setFillColor(DEWR_DARK_GREY)
            c.drawString(legend_x + marker_gap, head_y - 1, name)
            legend_x += 5 + marker_gap + c.stringWidth(name, "Helvetica", 7.2) + item_gap

        c.setStrokeColor(DEWR_LIGHT_GREY)
        c.setLineWidth(0.5)
        c.line(pad, h - 36, w - pad, h - 36)

        label_style = ParagraphStyle(
            "public_tool_task_label",
            fontName="Helvetica",
            fontSize=7.5,
            leading=8.5,
            textColor=DEWR_NAVY,
        )
        label_bold_style = ParagraphStyle(
            "public_tool_task_label_bold",
            parent=label_style,
            fontName="Helvetica-Bold",
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
                c.circle(x, y, 3.5 if highlighted else 3.0, fill=1, stroke=0)

                if highlighted:
                    label_text = f"{value:.1f}%"
                    c.setFont("Helvetica-Bold", 7.0)
                    text_w = c.stringWidth(label_text, "Helvetica-Bold", 7.0)
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
        pad = 16

        c.setFillColor(HexColor("#F7F8FA"))
        c.rect(0, 0, w, h, fill=1, stroke=0)

        c.setFillColor(DEWR_DARK_GREY)
        c.setFont("Helvetica-Bold", 7.5)
        c.drawString(pad, h - 22, "PRACTICAL JUDGEMENT BOUNDARIES")
        c.setStrokeColor(DEWR_LIGHT_GREY)
        c.setLineWidth(0.5)
        c.line(pad, h - 36, w - pad, h - 36)

        col_w = (w - 2 * pad) / 3
        for i, (title, text) in enumerate(self.items):
            x = pad + i * col_w
            if i:
                c.setStrokeColor(DEWR_LIGHT_GREY)
                c.line(x, 18, x, h - 46)

            title_p = Paragraph(title, ParagraphStyle(
                "safeguard_title",
                fontName="Helvetica-Bold",
                fontSize=8.6,
                leading=10.2,
                textColor=DEWR_DARK_GREY,
            ))
            title_p.wrap(col_w - 22, 28)
            title_p.drawOn(c, x + 10, h - 72)
            p = Paragraph(text, ParagraphStyle(
                "safeguard_text",
                fontName="Helvetica",
                fontSize=8.0,
                leading=10,
                textColor=DEWR_DARK_GREY,
            ))
            p.wrap(col_w - 22, 42)
            p.drawOn(c, x + 10, h - 116)


class UncertaintyAreasPanel(Flowable):
    """Three-column panel for uncertainty themes in open-text responses."""
    def __init__(self, width):
        Flowable.__init__(self)
        self.box_width = width
        self._height = 126
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
        pad = 16

        c.setFillColor(HexColor("#F7F8FA"))
        c.rect(0, 0, w, h, fill=1, stroke=0)

        c.setFillColor(DEWR_DARK_GREY)
        c.setFont("Helvetica-Bold", 7.5)
        c.drawString(pad, h - 22, "AREAS OF UNCERTAINTY IN OPEN-TEXT RESPONSES")
        c.setStrokeColor(DEWR_LIGHT_GREY)
        c.setLineWidth(0.5)
        c.line(pad, h - 36, w - pad, h - 36)

        col_w = (w - 2 * pad) / 3
        for i, (title, text) in enumerate(self.items):
            x = pad + i * col_w
            if i:
                c.setStrokeColor(DEWR_LIGHT_GREY)
                c.line(x, 18, x, h - 46)

            title_p = Paragraph(title, ParagraphStyle(
                "uncertainty_title",
                fontName="Helvetica-Bold",
                fontSize=8.6,
                leading=10.2,
                textColor=DEWR_DARK_GREY,
            ))
            title_p.wrap(col_w - 22, 28)
            title_p.drawOn(c, x + 10, h - 68)
            p = Paragraph(text, ParagraphStyle(
                "uncertainty_text",
                fontName="Helvetica",
                fontSize=8.0,
                leading=9.6,
                textColor=DEWR_DARK_GREY,
            ))
            p.wrap(col_w - 22, 48)
            p.drawOn(c, x + 10, h - 112)


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
        pad = 16

        c.setFillColor(HexColor("#F7F8FA"))
        c.rect(0, 0, w, h, fill=1, stroke=0)

        c.setFillColor(DEWR_DARK_GREY)
        c.setFont("Helvetica-Bold", 7.5)
        c.drawString(pad, h - 22, "SAFEGUARD OPERATING MODEL")
        c.setStrokeColor(DEWR_LIGHT_GREY)
        c.setLineWidth(0.5)
        c.line(pad, h - 36, w - pad, h - 36)

        col_w = (w - 2 * pad) / 4
        for i, (title, text) in enumerate(self.items):
            x = pad + i * col_w
            if i:
                c.setStrokeColor(DEWR_LIGHT_GREY)
                c.line(x, 18, x, h - 46)

            c.setFillColor(DEWR_DARK_GREEN if i < 2 else DEWR_DARK_GREY)
            c.setFont("Helvetica-Bold", 11)
            c.drawString(x + 9, h - 60, title)
            p = Paragraph(text, ParagraphStyle(
                "safeguard_model_text",
                fontName="Helvetica",
                fontSize=7.6,
                leading=9.2,
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
        pad = 16
        cluster_gap = 20
        cluster_w = (w - 2 * pad - cluster_gap) / 2

        c.setFillColor(HexColor("#F7F8FA"))
        c.rect(0, 0, w, h, fill=1, stroke=0)

        for cluster_idx, (title, rows) in enumerate(self.clusters):
            x = pad + cluster_idx * (cluster_w + cluster_gap)
            if cluster_idx:
                c.setStrokeColor(DEWR_LIGHT_GREY)
                c.setLineWidth(0.5)
                c.line(x - cluster_gap / 2, 18, x - cluster_gap / 2, h - 18)

            c.setFillColor(DEWR_DARK_GREY)
            c.setFont("Helvetica-Bold", 7.2)
            c.drawString(x, h - 24, title)
            c.setStrokeColor(DEWR_LIGHT_GREY)
            c.line(x, h - 38, x + cluster_w, h - 38)

            row_y = h - 62
            for row_idx, (dot_count, label) in enumerate(rows):
                y = row_y - row_idx * 28
                dot_center_y = y + 4
                for dot_idx in range(3):
                    c.setFillColor(DEWR_DARK_GREEN if dot_idx < dot_count and cluster_idx == 0 else
                                   DEWR_DARK_GREY if dot_idx < dot_count else HexColor("#E3E5E6"))
                    c.circle(x + 6 + dot_idx * 10, dot_center_y, 2.7, fill=1, stroke=0)
                p = Paragraph(label, ParagraphStyle(
                    "concern_cluster_label",
                    fontName="Helvetica",
                    fontSize=7.6,
                    leading=9.0,
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

        self.bar_h = 16
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
        c.setFont("Helvetica-Bold", 11.5)
        c.drawString(0, h - 14, self.title)
        # Subtitle
        c.setFont("Helvetica", 9.5)
        c.setFillColor(DEWR_GREY)
        c.drawString(0, h - 32, self.subtitle)

        # Legend (right-aligned, below subtitle)
        leg_y = h - 18 - 16 - 6
        # measure label widths to right-align cleanly
        c.setFont("Helvetica", 9)
        a_text_w = c.stringWidth(self.a_label, "Helvetica", 9)
        b_text_w = c.stringWidth(self.b_label, "Helvetica", 9)
        max_text_w = max(a_text_w, b_text_w)
        leg_block_w = 14 + max_text_w
        leg_x = w - leg_block_w

        c.setFillColor(self.a_color)
        c.rect(leg_x, leg_y, 11, 11, fill=1, stroke=0)
        c.setFillColor(DEWR_DARK_GREY)
        c.setFont("Helvetica", 9)
        c.drawString(leg_x + 16, leg_y + 2, self.a_label)
        leg_y -= 16
        c.setFillColor(self.b_color)
        c.rect(leg_x, leg_y, 11, 11, fill=1, stroke=0)
        c.setFillColor(DEWR_DARK_GREY)
        c.setFont("Helvetica", 9)
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
            c.setLineWidth(0.5)
            c.line(0, cur_y, w, cur_y)
            cur_y -= 4
            c.setFillColor(DEWR_DARK_GREY)
            c.setFont("Helvetica-Bold", 9.5)
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
                c.setFont("Helvetica-Bold", 9)
                c.drawString(bar_area_x + a_w + 6, cur_y - self.bar_h + 4,
                             f"{a_val}%")
                cur_y -= self.bar_h + self.bar_gap

                # Series B bar
                b_w = bar_area_w * (b_val / self.max_value)
                c.setFillColor(self.b_color)
                c.rect(bar_area_x, cur_y - self.bar_h, b_w, self.bar_h,
                       fill=1, stroke=0)
                c.setFillColor(DEWR_DARK_GREY)
                c.setFont("Helvetica-Bold", 9)
                c.drawString(bar_area_x + b_w + 6, cur_y - self.bar_h + 4,
                             f"{b_val}%")

                # Category label (vertically centred between the two bars)
                label_mid_y = bar_top - self.bar_h - (self.bar_gap / 2)
                c.setFillColor(DEWR_DARK_GREY)
                c.setFont("Helvetica", 9.5)
                words = cat.split()
                lines = []
                current_line = ""
                for word in words:
                    test = (current_line + " " + word).strip()
                    if c.stringWidth(test, "Helvetica", 9.5) <= self.label_w - 12:
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
        c.setLineWidth(0.5)
        c.line(bar_area_x, baseline_top - 2, bar_area_x, baseline_bottom_actual + self.section_gap)

        # Source
        if self.source_text:
            c.setFillColor(DEWR_GREY)
            c.setFont("Helvetica-Oblique", 8)
            c.drawString(0, 4, self.source_text)


class TaskFootprintExhibit(Flowable):
    """Full task-footprint dumbbell with the largest access-type gaps highlighted."""
    def __init__(self, width):
        Flowable.__init__(self)
        self.box_width = width
        self._height = 230
        # Corrected task-use values supplied from the validated survey table.
        self.rows = [
            ("Summarising", 83.3, 73.2, False),
            ("Editing and revision", 70.0, 63.4, False),
            ("Drafting", 70.0, 65.9, False),
            ("Research, problem solving or generating ideas", 66.7, 43.9, True),
            ("General administrative tasks", 46.7, 41.5, False),
            ("Planning or meeting preparation", 33.3, 14.6, True),
            ("Coding or data work", 23.3, 19.5, False),
        ]

    def wrap(self, availWidth, availHeight):
        self.box_width = availWidth
        return self.box_width, self._height

    def draw(self):
        c = self.canv
        w = self.box_width
        h = self._height
        pad = 16
        label_w = w * 0.40
        axis_x = pad + label_w
        axis_w = w - axis_x - 58
        top_y = h - 60
        row_gap = 23

        c.setFillColor(HexColor("#F7F8FA"))
        c.rect(0, 0, w, h, fill=1, stroke=0)

        c.setFillColor(DEWR_DARK_GREY)
        c.setFont("Helvetica-Bold", 7.5)
        c.drawString(pad, h - 22, "MEASURE")
        c.setFont("Helvetica", 7.4)
        m365_label = "M365 Copilot"
        chat_label = "Copilot Chat"
        marker_gap = 8
        item_gap = 18
        m365_w = c.stringWidth(m365_label, "Helvetica", 7.4)
        chat_w = c.stringWidth(chat_label, "Helvetica", 7.4)
        legend_w = 6 + marker_gap + m365_w + item_gap + 6 + marker_gap + chat_w
        legend_x = w - pad - legend_w
        c.setFillColor(DEWR_DARK_GREEN)
        c.circle(legend_x, h - 20, 3.0, fill=1, stroke=0)
        c.setFillColor(DEWR_DARK_GREY)
        c.drawString(legend_x + marker_gap, h - 23, m365_label)
        chat_marker_x = legend_x + marker_gap + m365_w + item_gap
        c.setFillColor(DEWR_DARK_GREY)
        c.circle(chat_marker_x, h - 20, 3.0, fill=1, stroke=0)
        c.drawString(chat_marker_x + marker_gap, h - 23, chat_label)
        c.setStrokeColor(DEWR_LIGHT_GREY)
        c.line(pad, h - 36, w - pad, h - 36)

        c.setFont("Helvetica", 7.2)
        c.setFillColor(DEWR_GREY)
        for tick, label in [(0, "0%"), (25, "25%"), (50, "50%"), (75, "75%"), (100, "100%")]:
            x = axis_x + axis_w * (tick / 100)
            c.setStrokeColor(DEWR_LIGHT_GREY)
            c.setLineWidth(0.35)
            c.line(x, top_y + 9, x, top_y - row_gap * (len(self.rows) - 1) - 8)
            c.drawCentredString(x, h - 48, label)

        for i, (label, m365, chat, highlight) in enumerate(self.rows):
            y = top_y - i * row_gap
            p = Paragraph(label, ParagraphStyle(
                "full_task_dumbbell_label",
                fontName="Helvetica-Bold" if highlight else "Helvetica",
                fontSize=7.6,
                leading=8.6,
                textColor=DEWR_DARK_GREY,
            ))
            p.wrap(label_w - 8, 20)
            p.drawOn(c, pad, y - 7)

            chat_x = axis_x + axis_w * (chat / 100)
            m365_x = axis_x + axis_w * (m365 / 100)
            line_color = DEWR_DARK_GREEN if highlight else DEWR_GREY
            m365_color = DEWR_DARK_GREEN if highlight else DEWR_GREY
            chat_color = DEWR_DARK_GREY if highlight else DEWR_GREY

            c.setStrokeColor(line_color)
            c.setLineWidth(1.1 if highlight else 0.7)
            c.line(chat_x, y, m365_x, y)
            c.setFillColor(chat_color)
            c.circle(chat_x, y, 3.1, fill=1, stroke=0)
            c.setFillColor(m365_color)
            c.circle(m365_x, y, 3.6 if highlight else 3.1, fill=1, stroke=0)

            if highlight:
                c.setFont("Helvetica-Bold", 7.4)
                c.setFillColor(DEWR_DARK_GREY)
                c.drawRightString(chat_x - 5, y - 3, f"{chat}%")
                c.setFillColor(DEWR_DARK_GREEN)
                c.drawString(m365_x + 5, y - 3, f"{m365}%")


class KeyFindingBar(Flowable):
    """A left-bordered key finding highlight."""
    def __init__(self, text, width, border_color=DEWR_GREEN, bg_color=None):
        Flowable.__init__(self)
        self.text = text
        self.box_width = width
        self.border_color = border_color
        self.bg_color = bg_color or HexColor("#EFF4E8")
        self._height = None

    def wrap(self, availWidth, availHeight):
        self.box_width = availWidth
        style = ParagraphStyle('kf_measure', fontName='Helvetica-Bold',
                               fontSize=10.5, leading=14,
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
        style = ParagraphStyle('kf_draw', fontName='Helvetica-Bold',
                               fontSize=10.5, leading=14,
                               textColor=DEWR_DARK_GREY)
        p = Paragraph(self.text, style)
        p.wrap(self.box_width - 24, self._height)
        p.drawOn(self.canv, 16, 10)


def header_footer(canvas, doc):
    canvas.saveState()
    # Header line
    canvas.setStrokeColor(DEWR_NAVY)
    canvas.setLineWidth(2)
    canvas.line(doc.leftMargin, A4[1] - 20*mm, A4[0] - doc.rightMargin, A4[1] - 20*mm)

    # Header text
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(DEWR_DARK_GREY)
    canvas.drawString(doc.leftMargin, A4[1] - 18*mm,
                      "Evaluation of the Public Generative AI Trial")

    # Footer
    canvas.setStrokeColor(DEWR_LIGHT_GREY)
    canvas.setLineWidth(0.5)
    canvas.line(doc.leftMargin, 18*mm, A4[0] - doc.rightMargin, 18*mm)
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(DEWR_DARK_GREY)
    canvas.drawString(doc.leftMargin, 13*mm,
                      "Department of Employment and Workplace Relations")
    canvas.drawRightString(A4[0] - doc.rightMargin, 13*mm,
                           f"Page {doc.page}")
    canvas.restoreState()


def cover_page(canvas, doc):
    canvas.saveState()
    page_w, page_h = A4
    left = 64
    cover_green = HexColor("#9AAB64")

    canvas.setFillColor(DEWR_DARK_GREY)
    canvas.rect(0, 0, page_w, page_h, fill=1, stroke=0)

    canvas.setFillColor(DEWR_GREEN)
    canvas.rect(0, 0, page_w, 10*mm, fill=1, stroke=0)

    if os.path.exists(COVER_LOCKUP_PATH):
        canvas.drawImage(
            COVER_LOCKUP_PATH,
            left,
            page_h - 154,
            width=196,
            height=61,
            mask="auto",
        )
    else:
        canvas.setFillColor(white)
        canvas.setFont("Helvetica-Bold", 11)
        canvas.drawString(left, page_h - 112, "Australian Government")
        canvas.setLineWidth(0.6)
        canvas.setStrokeColor(white)
        canvas.line(left, page_h - 118, left + 180, page_h - 118)
        canvas.setFont("Helvetica-Bold", 10)
        canvas.drawString(left, page_h - 135, "Department of Employment")
        canvas.drawString(left, page_h - 148, "and Workplace Relations")

    title_style = ParagraphStyle(
        "CoverPageTitle",
        fontName="Helvetica-Bold",
        fontSize=26,
        leading=34,
        textColor=white,
    )
    title = Paragraph("Evaluation of the Public<br/>Generative AI Trial", title_style)
    title.wrap(page_w - left - 64, 120)
    title.drawOn(canvas, left, page_h - 285)

    subtitle_style = ParagraphStyle(
        "CoverPageSubtitle",
        fontName="Helvetica",
        fontSize=17,
        leading=25,
        textColor=cover_green,
    )
    subtitle = Paragraph("Summary of evaluation findings", subtitle_style)
    subtitle.wrap(page_w - left - 64, 80)
    subtitle.drawOn(canvas, left, page_h - 390)

    canvas.setFillColor(cover_green)
    canvas.setFont("Helvetica", 16)
    canvas.drawString(left, page_h - 520, "May 2026")
    canvas.restoreState()


def build_report():
    doc = SimpleDocTemplate(
        OUTPUT_PATH,
        pagesize=A4,
        leftMargin=25*mm,
        rightMargin=25*mm,
        topMargin=28*mm,
        bottomMargin=25*mm,
    )

    width = A4[0] - doc.leftMargin - doc.rightMargin
    story = []

    # --- Styles ---
    styles = getSampleStyleSheet()

    title_style = ParagraphStyle('Title', fontName='Helvetica-Bold',
                                  fontSize=26, leading=32, textColor=DEWR_NAVY,
                                  spaceAfter=6)
    subtitle_style = ParagraphStyle('Subtitle', fontName='Helvetica',
                                     fontSize=14, leading=18, textColor=DEWR_DARK_GREY,
                                     spaceAfter=20)
    h1 = ParagraphStyle('H1', fontName='Helvetica-Bold', fontSize=18,
                         leading=24, textColor=DEWR_NAVY, spaceBefore=16, spaceAfter=10)
    h2 = ParagraphStyle('H2', fontName='Helvetica-Bold', fontSize=14,
                         leading=18, textColor=DEWR_NAVY, spaceBefore=14, spaceAfter=8)
    h3 = ParagraphStyle('H3', fontName='Helvetica-Bold', fontSize=11.5,
                         leading=15, textColor=DEWR_DARK_GREY, spaceBefore=10, spaceAfter=6)
    h4 = ParagraphStyle('H4', fontName='Helvetica-Bold', fontSize=10,
                         leading=13, textColor=DEWR_DARK_GREY, spaceBefore=8, spaceAfter=4)
    mini_heading = ParagraphStyle('MiniHeading', fontName='Helvetica-Bold', fontSize=8.8,
                                  leading=11, textColor=DEWR_DARK_GREY,
                                  spaceBefore=4, spaceAfter=4)
    metric_context = ParagraphStyle('MetricContext', fontName='Helvetica-Bold', fontSize=8.3,
                                    leading=10, textColor=DEWR_DARK_GREY,
                                    spaceBefore=0, spaceAfter=5)
    body = ParagraphStyle('Body', fontName='Helvetica', fontSize=10,
                           leading=14, textColor=DEWR_DARK_GREY, spaceAfter=8,
                           alignment=TA_JUSTIFY)
    body_bold = ParagraphStyle('BodyBold', fontName='Helvetica-Bold', fontSize=10,
                                leading=14, textColor=DEWR_DARK_GREY, spaceAfter=8)
    bullet_style = ParagraphStyle('Bullet', fontName='Helvetica', fontSize=10,
                                   leading=14, textColor=DEWR_DARK_GREY,
                                   leftIndent=18, spaceAfter=4,
                                   bulletIndent=6, bulletFontName='Helvetica',
                                   bulletFontSize=10)
    quote_style = ParagraphStyle('Quote', fontName='Helvetica-Oblique', fontSize=9.5,
                                  leading=13, textColor=DEWR_GREY,
                                  leftIndent=20, rightIndent=20, spaceAfter=8,
                                  borderPadding=6)
    note_style = ParagraphStyle('Note', fontName='Helvetica-Oblique', fontSize=8.5,
                                 leading=11, textColor=DEWR_GREY, spaceAfter=6)
    chart_title = ParagraphStyle('ChartTitle', fontName='Helvetica-Bold', fontSize=10.5,
                                  leading=13, textColor=DEWR_DARK_GREY,
                                  spaceBefore=4, spaceAfter=4)
    s1_h2 = ParagraphStyle('S1H2', parent=h2, spaceBefore=14, spaceAfter=10)
    s1_h3 = ParagraphStyle('S1H3', parent=h3, spaceBefore=0, spaceAfter=6)
    s1_body = ParagraphStyle('S1Body', parent=body, spaceAfter=0)

    def bullet(text):
        return Paragraph(f"<bullet>&bull;</bullet> {text}", bullet_style)

    limitation_bullet_style = ParagraphStyle(
        'LimitationBullet',
        parent=bullet_style,
        leading=15,
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

    def sp(h=6):
        return Spacer(1, h)

    # ==============================
    # COVER PAGE
    # ==============================
    story.append(PageBreak())

    # ==============================
    # TABLE OF CONTENTS
    # ==============================
    story.append(Paragraph("Contents", h1))
    story.append(sp(4))
    toc_items = [
        ("Executive summary", "3"),
        ("    Preface", "3"),
        ("    Overarching findings", "4"),
        ("    Recommendations", "5"),
        ("Evaluation findings", "6"),
        ("    1. Copilot productivity baseline", "6"),
        ("    2. Public Gen AI uptake, use and productivity", "8"),
        ("    3. Concerns, risks and safeguards", "13"),
        ("Approach and methodology", "15"),
        ("Appendix", "16"),
    ]
    toc_style = ParagraphStyle('TOC', fontName='Helvetica', fontSize=10,
                                leading=18, textColor=DEWR_DARK_GREY)
    toc_bold = ParagraphStyle('TOCBold', fontName='Helvetica-Bold', fontSize=10,
                               leading=18, textColor=DEWR_NAVY)
    for item, pg in toc_items:
        is_main = not item.startswith("    ")
        s = toc_bold if is_main else toc_style
        display = item.strip()
        dots = '.' * max(3, (80 - len(display)))
        story.append(Paragraph(f"{display} {'.' * 3}<spacer length='flexible'/>{pg}", s))
    story.append(PageBreak())

    # ==============================
    # EXECUTIVE SUMMARY
    # ==============================
    story.append(Paragraph("Executive summary", h1))
    story.append(HRFlowable(width="100%", thickness=1, color=DEWR_GREEN))
    story.append(sp(4))

    # Preface
    story.append(Paragraph("Preface", h2))
    story.append(Paragraph(
        "DEWR currently provides all employees with access to Generative AI. All employees can access "
        "the free Microsoft Copilot Chat and just under 10% can access the paid M365 Copilot with "
        "greater integration capability. In March 2026, nearly 80% of all staff used one of these tools, "
        "entering over 250,000 prompts, or about 4 prompts per person every workday.",
        body))
    story.append(Paragraph(
        "In January 2026, DEWR ran a trial in which 5% of employees were provided access to Public "
        "Generative AI tools, in addition to their existing Copilot access. The trial cohort was selected "
        "at random and stratified to ensure representation across Groups, Copilot access types, and "
        "APS levels. The tools were the free versions of OpenAI’s ChatGPT, Google’s Gemini, and "
        "Anthropic’s Claude, accessed via web browsers. Staff were provided with technical and "
        "governance instruction, including on what could be uploaded (unclassified information only). "
        "Technical protections were established to reduce the likelihood of classified material being "
        "uploaded to the tools.",
        body))
    story.append(Paragraph(
        "At the conclusion of the trial period, all participants were invited to complete a voluntary "
        "survey about their experience. A total of 104 staff completed the survey, representing an "
        "approximate 52% response rate. Respondents were evenly split by classification, with 52 APS "
        "staff (50%) and 52 Executive Level staff (50%), drawn from all five departmental groups.",
        body))
    story.append(sp(4))

    # Assessment areas
    story.append(Paragraph("The trial was intended to assess:", body_bold))
    story.append(bullet("The current productivity of Copilot (both versions)"))
    story.append(bullet("Whether Public Gen AI tools provided additional value beyond Copilot"))
    story.append(bullet("The relative utility of each of the selected Public Gen AI tools"))
    story.append(bullet("The potential productivity benefits from the Public Gen AI tools"))
    story.append(bullet("The degree of concern staff have when using the tools"))
    story.append(sp(4))

    # Overarching findings
    story.append(Paragraph("Overarching findings", h2))
    story.append(callout(
        "Public Gen AI tools delivered clear productivity benefits for many users, "
        "but value was not uniform. Copilot already provides meaningful time savings, "
        "and public tools offered additional value, particularly for users with lower Copilot access."))
    story.append(sp(10))

    # Stat boxes row
    stat_data = [
        ("68.7 min/day", "M365 daily saving", DEWR_NAVY),
        ("33.8 min/day", "Copilot Chat daily saving", DEWR_BLUE),
        ("80%", "Rated tool useful", DEWR_GREEN),
        ("72%", "Continued access", DEWR_DARK_GREEN),
    ]
    stat_width = (width - 18) / 4
    stat_boxes = []
    for stat, label, color in stat_data:
        stat_boxes.append(StatBox(stat, label, stat_width, color))

    stat_table = Table([[s for s in stat_boxes]], colWidths=[stat_width]*4)
    stat_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('LEFTPADDING', (0,0), (-1,-1), 2),
        ('RIGHTPADDING', (0,0), (-1,-1), 2),
    ]))
    story.append(visual_title("Copilot already saves time, and most public-tool users saw value"))
    story.append(stat_table)
    story.append(source_note(
        "Source: DEWR Public Generative AI Trial survey, 2026. Public-tool results are based on survey respondents."))
    story.append(sp(12))

    # Key finding bullets
    story.append(key_finding(
        "M365 Copilot users saved nearly double the time of Copilot Chat users: "
        "5.7 hours vs 2.8 hours per week."))
    story.append(sp(4))
    story.append(key_finding(
        "ChatGPT had the broadest uptake (92%), but Claude showed the strongest "
        "usefulness (71%) and continuation intent (63%)."))
    story.append(sp(6))
    story.append(key_finding(
        "Public tools provided clearer marginal value for Copilot Chat users "
        "than for M365 Copilot users."))
    story.append(sp(6))
    story.append(key_finding(
        "The most common barrier was lack of integration with internal systems (49%), "
        "followed by free-tier prompt limits (41%)."))
    story.append(sp(6))
    story.append(key_finding(
        "75% of respondents were comfortable using public tools. 11% reported ethical "
        "concerns and 3% reported specific security concerns."))
    story.append(sp(10))

    # Recommendations
    story.append(Paragraph("Recommendations", h2))
    story.append(Paragraph(
        "The findings reveal several considerations for DEWR in the context of "
        "future adoption of Public Generative AI tools.", body))
    story.append(sp(4))

    # Rec categories
    recs = [
        ("Targeted access expansion", [
            "Consider providing broader access to public Gen AI tools, prioritising user groups that showed "
            "the strongest productivity gains, particularly experienced Gen AI users and Copilot Chat users.",
            "Evaluate whether paid tiers of public tools (especially Claude) would address free-tier "
            "limitations that constrained trial benefits.",
        ]),
        ("Capability building", [
            "Offer specialised training reflecting DEWR-specific use cases, building on the finding that "
            "prior Gen AI experience was the clearest predictor of stronger outcomes.",
            "Identify and promote ‘Gen AI Champions’ to share effective practices and encourage adoption.",
        ]),
        ("Integration and workflow", [
            "Investigate integration pathways to reduce the manual effort of transferring public tool "
            "outputs into internal systems, which was the most commonly reported barrier.",
            "Conduct workflow analysis across Groups and classifications to identify high-value use cases.",
        ]),
        ("Governance and risk management", [
            "Provide clearer guidance on boundary cases for data classification, where staff reported "
            "uncertainty about what was technically allowed but still sensitive.",
            "Proactively monitor the impacts of generative AI on the workforce, including effects on "
            "accuracy, over-reliance, and environmental considerations.",
        ]),
    ]
    for rec_title, rec_items in recs:
        story.append(Paragraph(rec_title, h3))
        for item in rec_items:
            story.append(bullet(item))
        story.append(sp(4))

    story.append(PageBreak())

    # ==============================
    # EVALUATION FINDINGS
    # ==============================
    story.append(Paragraph("Evaluation findings", h1))
    story.append(HRFlowable(width="100%", thickness=1, color=DEWR_GREEN))
    story.append(sp(10))

    # Section 1: Copilot
    story.append(Paragraph("1. Copilot productivity baseline", s1_h2))
    story.append(callout(
        "Copilot already delivers material productivity value, but benefits are tiered by "
        "access: integrated M365 Copilot produces stronger time savings, deeper engagement "
        "and a broader task footprint than Copilot Chat."))
    story.append(ValueSignalsPanel(width, [
        ("2.0x", "M365 Copilot users reported twice as much average weekly time saved as Copilot Chat users"),
        ("1.8x", "M365 Copilot users were 1.8x as likely to rate Copilot very or extremely useful"),
        ("1.4x", "M365 Copilot users were 1.4x as likely to use Copilot weekly or more often"),
    ], primary_count=1))
    story.append(sp(12))

    # Time savings
    story.append(Paragraph("1.1 M365 Copilot access set a higher productivity baseline", s1_h3))
    story.append(Paragraph(
        "M365 Copilot users reported average time savings of 68.7 minutes per day, compared "
        "with 33.8 minutes per day for Copilot Chat users. This means M365 Copilot users reported "
        "roughly twice the daily time savings of Copilot Chat users.", s1_body))
    story.append(sp(8))
    story.append(TimeSavingsPanel(width))
    story.append(sp(12))

    # Usefulness and frequency
    story.append(KeepTogether([
        Paragraph("1.2 Higher time savings were matched by deeper engagement", s1_h3),
        Paragraph(
            "The productivity gap was reinforced by engagement signals. M365 Copilot users were "
            "more likely to rate Copilot as highly useful, use it weekly, and use it daily or most "
            "of the day, suggesting integration is supporting more habitual use.", s1_body),
        sp(8),
        CopilotEngagementDeltaPanel(width),
    ]))
    story.append(sp(12))

    # Task types
    story.append(KeepTogether([
        Paragraph("1.3 M365 Copilot users reported a broader task footprint", s1_h3),
        Paragraph(
            "Across M365 Copilot and Copilot Chat users, Copilot was used most often for summarising, editing and "
            "revision, and drafting. M365 Copilot users reported using Copilot across more task "
            "types on average than Copilot Chat users. While both user groups used Copilot "
            "for the same broad categories of work, M365 Copilot users were more likely to report use for "
            "research, problem solving and idea generation, and for planning or meeting preparation. "
            "These tasks are typically more complex than drafting or summarising alone, suggesting "
            "M365 Copilot access may be associated with broader use in higher-value knowledge-work "
            "activities.", s1_body),
        sp(8),
        TaskFootprintExhibit(width),
    ]))
    story.append(sp(14))

    # Section 2: Public Gen AI
    story.append(PageBreak())
    story.append(Paragraph("2. Public Gen AI uptake, use and productivity", h2))
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
    story.append(sp(6))

    # 2.1 Tool comparison
    story.append(Paragraph("2.1 ChatGPT had the widest reach; Claude had the strongest value signals", h3))
    story.append(Paragraph(
        "ChatGPT was the access point for most trial users, while Claude showed the strongest "
        "high-usefulness signal: 46.3% of Claude users rated it very or extremely useful, "
        "compared with 29.7% for Gemini and 28.6% for ChatGPT. This suggests the public-tool choice was not simply about "
        "uptake; different tools played different roles.", body))
    story.append(sp(8))
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
        "73.2% of Claude users using it for research, problem solving or generating ideas. "
        "Claude was also notably higher for coding or data work at 26.8%, compared with 13.5% "
        "for Gemini and 10.7% for ChatGPT.", body))
    story.append(Paragraph(
        "Gemini was strongest for editing and revision, at 56.8%, while ChatGPT showed a "
        "relatively balanced profile across summarising, drafting, editing and research.", body))
    story.append(sp(8))
    story.append(PublicToolTaskProfilePanel(width))
    story.append(sp(4))
    story.append(source_note(
        "Note: Percentages are based on users of each respective tool: ChatGPT n=56; Gemini n=37; Claude n=41. "
        "Labelled values indicate the highest tool-specific share for each task. Source: DEWR Public Generative AI Trial survey, 2026."))
    story.append(sp(8))

    story.append(PageBreak())

    # 2.3 Access-type variation
    story.append(Paragraph("2.3 Public AI tools provided different value for M365 Copilot and Copilot Chat users", h3))
    story.append(Paragraph(
        "Public-tool value was not evenly distributed by Copilot access type. Copilot Chat users rated "
        "public AI tools more useful than Copilot itself, suggesting public tools helped fill gaps left by "
        "the less integrated Copilot product. M365 Copilot users continued to rate Copilot more highly than "
        "public AI tools, but most still said public tools added value beyond Copilot. This suggests public "
        "AI tools provided additional value for both groups, but the type of value differed by existing "
        "Copilot access.", body))
    story.append(sp(4))
    story.append(Paragraph(
        "Copilot Chat users were more likely to rate Public AI as useful, while M365 Copilot users rated Copilot more useful.",
        body_bold))
    story.append(sp(4))
    story.append(PublicAIUsefulnessVisual(width))
    story.append(source_note(
        "Note: Useful means rated moderately, very or extremely useful. Source: DEWR Public Generative AI Trial survey, 2026."))
    story.append(sp(6))
    story.append(Paragraph(
        "Among Copilot Chat users, <b>82.4%</b> rated at least one public AI tool moderately useful "
        "or better, compared with <b>70.6%</b> who rated Copilot moderately useful or better. Weekly use "
        "was also similar across the two tool types, with <b>52.9%</b> using public AI tools weekly or more "
        "and <b>58.8%</b> using Copilot weekly or more. This suggests public AI tools may have provided "
        "clearer additional value for users without access to the more integrated M365 Copilot product.", body))
    story.append(sp(4))
    story.append(Paragraph(
        "For M365 Copilot users, public AI tools were used less regularly and rated less useful than Copilot, "
        "but still provided additional value. While <b>92.6%</b> rated Copilot useful, <b>77.8%</b> rated at "
        "least one public AI tool useful and <b>81.5%</b> said public AI tools added value beyond Copilot. "
        "This suggests public AI tools were not replacing M365 Copilot, but were still useful for some tasks.", body))
    story.append(Paragraph(
        "Overall, the results suggest public AI tools should be understood as a complement to Copilot rather "
        "than a direct substitute. The additional value appears different by access type: for Copilot Chat "
        "users, public AI tools may help fill capability gaps; for M365 Copilot users, they provide optional "
        "additional functionality for selected tasks.", body))

    # 2.4 Prior experience variation
    story.append(KeepTogether([
        Paragraph("2.4 Prior Gen AI experience was associated with stronger reported value", h3),
        Paragraph(
            "Prior Gen AI experience was also associated with stronger reported outcomes. Experienced "
            "and highly experienced respondents were more likely to report significant added value from "
            "public tools than respondents with lower levels of prior Gen AI experience.", body),
        sp(4),
        PriorExperienceComparisonPanel(width),
        sp(3),
        source_note("Note: Results should be read directionally given the smaller no/basic segment."),
        sp(3),
        Paragraph(
            "Higher-experience users also reported deeper usefulness: <b>73%</b> rated at least one public tool "
            "very or extremely useful, compared with <b>46%</b> some prior Gen AI experience and "
            "<b>39%</b> no/basic prior Gen AI experience.", body),
        Paragraph(
            "They were also more likely to rate at least one public tool better than Copilot on at least "
            "one comparison dimension (<b>86% vs 69%</b> for both lower-experience groups) and to strongly "
            "want continued access (<b>55% vs 31%</b> some prior Gen AI experience and <b>15%</b> no/basic "
            "prior Gen AI experience).", body),
    ]))

    # 2.5 Other segment variation
    story.append(Paragraph("2.5 Reported value varied by classification and organisational group", h3))
    story.append(sp(4))
    story.append(Paragraph("Classification level", mini_heading))
    story.append(Paragraph(
        "EL users were more likely than APS users to report that public tools provided value over and above "
        "Copilot (<b>78.6% vs 66.7%</b>) and were slightly more likely to use public tools weekly or more "
        "(<b>53.6% vs 51.5%</b>). APS users, however, were more likely to rate at least one public tool "
        "as useful (<b>87.9% vs 71.4%</b>).", body))
    story.append(sp(5))
    story.append(EvidenceMatrixPanel(
        width,
        "MEASURE",
        ["APS", "EL"],
        [
            ("Added value beyond Copilot", ["66.7%", "78.6%"], 1),
            ("Used weekly or more", ["51.5%", "53.6%"], 1),
            ("Rated at least moderately useful", ["87.9%", "71.4%"], 0),
        ],
        first_col_ratio=0.50,
    ))
    story.append(sp(8))
    story.append(PageBreak())
    story.append(Paragraph("Organisational group", mini_heading))
    story.append(Paragraph(
        "Reported value also varied across groups. Workplace Relations recorded the strongest added-value "
        "result (<b>85.7%</b>), while Employment and Workforce and Corporate and Enabling recorded high "
        "usefulness results (<b>84.2%</b> and <b>83.3%</b> respectively). Skill and Training recorded "
        "comparatively weaker results across both measures.", body))
    story.append(sp(5))
    story.append(EvidenceMatrixPanel(
        width,
        "GROUP",
        ["Added value beyond Copilot", "Rated at least moderately useful"],
        [
            ("Corporate and Enabling", ["66.7%", "83.3%"], 1),
            ("Employment and Workforce", ["73.7%", "84.2%"], 1),
            ("Skill and Training", ["53.8%", "69.2%"], None),
            ("Workplace Relations", ["85.7%", "78.6%"], 0),
        ],
        first_col_ratio=0.32,
    ))
    story.append(source_note(
        "Note: Jobs and Skills Australia was excluded because of low sample size (n=3)."))
    story.append(sp(4))

    # 2.6 Barriers
    story.append(PageBreak())
    story.append(Paragraph("2.6 Limitations were common, led by lack of integration and request limits", h3))
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
    story.append(sp(11))
    story.append(HorizontalBarPanel(width, "LIMITATIONS REPORTED BY RESPONDENTS", [
        ("Lack of integration with internal systems or Microsoft 365 products", 49),
        ("Free prompt/request limits", 41),
        ("Misinterpreted prompts", 34),
        ("Difficulty with specialised topics", 34),
        ("Slow responses", 28),
        ("Fabricated content or hallucinations", 15),
    ], max_value=100, primary_count=2, row_h=13))

    # Section 3: Concerns
    story.append(PageBreak())
    story.append(Paragraph("3. Concerns, risks and safeguards", h2))
    story.append(callout(
        "Most survey respondents were comfortable and reported security concerns were rare. Survey "
        "results suggest safety communications and splash screens supported cautious use, while "
        "data-handling risks were mainly visible through copy/paste behaviour and user judgement.",
        DEWR_DARK_GREEN))
    story.append(ValueSignalsPanel(width, [
        ("75%", "Comfortable or very comfortable using public tools"),
        ("25%", "Uncomfortable using public tools"),
        ("11%", "Ethical concerns encountered"),
        ("3%", "Reported specific security concerns"),
    ], primary_count=1))
    story.append(sp(12))

    story.append(Paragraph("3.1 Most respondents were comfortable; security concerns were rare", h3))
    story.append(Paragraph(
        "Survey results showed relatively high comfort using public tools. Three-quarters of "
        "respondents were comfortable or very comfortable using public tools, while one-quarter "
        "were uncomfortable. Reported concern signals were lower: <b>11%</b> reported ethical "
        "concerns and <b>3%</b> reported specific security concerns.", body))
    story.append(Paragraph(
        "Comfort was also higher among respondents who rated both the introductory email and splash "
        "screens effective: <b>82.5%</b> of this group were comfortable or very comfortable using "
        "public tools, compared with <b>61.9%</b> among respondents who did not rate both channels "
        "effective.", body))
    story.append(sp(8))

    story.append(Paragraph("3.2 Open-text responses showed uncertainty at practical boundaries", h3))
    story.append(Paragraph(
        "Open-text responses still showed uncertainty at practical boundaries, particularly where "
        "information was technically allowed but still sensitive, commercially confidential, difficult "
        "to classify, or required output validation.", body))
    story.append(sp(6))
    story.append(UncertaintyAreasPanel(width))
    story.append(sp(8))

    story.append(PageBreak())
    story.append(Paragraph("3.3 Respondents were more likely to copy/paste information than upload documents", h3))
    story.append(Paragraph(
        "Reported data-handling behaviour varied by activity. Copying and pasting information "
        "into public tools was more common than uploading documents. Among survey respondents, "
        "<b>70.5%</b> copied and pasted information, while <b>42.6%</b> uploaded documents.", body))
    story.append(sp(8))
    story.append(HorizontalBarPanel(width, "MEASURE", [
        ("Copied and pasted information", 70.5),
        ("Uploaded documents", 42.6),
    ], max_value=100, primary_count=1))
    story.append(sp(8))

    story.append(Paragraph("3.4 Safety communications were rated effective by most survey respondents", h3))
    story.append(ValueSignalsPanel(width, [
        ("74%", "Introductory email moderately or highly effective"),
        ("72%", "Splash screens moderately or highly effective"),
        ("67%", "Rated both email and splash screens effective"),
    ], primary_count=0))
    story.append(sp(10))
    story.append(Paragraph(
        "Survey responses showed two different safeguard signals. Most respondents rated the "
        "safety communications positively: the introductory email was rated moderately or highly "
        "effective by <b>74%</b> of respondents, while splash screens were rated moderately or "
        "highly effective by <b>72%</b>. Two-thirds of respondents rated both the email and splash "
        "screens effective.", body))
    story.append(Paragraph(
        "Upload blockers were less visible in the survey results: <b>16.7%</b> of respondents "
        "noticed or rated upload blockers as effective, and no respondent rated upload blockers "
        "ineffective.", body))
    story.append(sp(8))

    story.append(sp(10))

    # ==============================
    # APPROACH AND METHODOLOGY
    # ==============================
    story.append(PageBreak())
    story.append(Paragraph("Approach and methodology", h1))
    story.append(HRFlowable(width="100%", thickness=1, color=DEWR_GREEN))
    story.append(sp(8))

    story.append(Paragraph("Goal and scope", h3))
    story.append(Paragraph(
        "The trial assessed whether providing DEWR staff with access to publicly available "
        "Generative AI tools would deliver productivity benefits beyond those already provided by "
        "Microsoft Copilot. The trial ran for a defined period in January 2026 with approximately "
        "200 randomly selected and stratified employees.", body))
    story.append(sp(4))

    story.append(Paragraph("Sampling", h3))
    story.append(bullet("5% of DEWR employees were selected for the trial."))
    story.append(bullet("Selection was randomised and stratified across Groups, Copilot access types, and APS levels."))
    story.append(bullet("All trial participants retained their existing Copilot access throughout."))
    story.append(sp(4))

    story.append(Paragraph("Survey design and response", h3))
    story.append(bullet("A voluntary post-trial survey was administered to all trial participants."))
    story.append(bullet("104 staff completed the survey (approximately 52% response rate)."))
    story.append(bullet("Respondents: 52 APS staff (50%) and 52 Executive Level staff (50%)."))
    story.append(bullet("Respondents came from all five departmental groups."))
    story.append(bullet("71 respondents (68.3%) used at least one public Gen AI tool during the trial."))
    story.append(bullet("30 respondents reported having M365 Copilot access."))
    story.append(sp(4))

    story.append(Paragraph("Most respondents had at least some prior Gen AI experience", h3))
    exp_data = [
        ["Experience level", "Count", "Share"],
        ["No prior experience", "7", "6.7%"],
        ["Basic familiarity", "33", "31.7%"],
        ["Some experience", "35", "33.7%"],
        ["Experienced", "24", "23.1%"],
        ["Highly experienced", "5", "4.8%"],
    ]
    exp_w = [width * 0.50, width * 0.25, width * 0.25]
    t3 = Table(exp_data, colWidths=exp_w)
    t3.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), DEWR_NAVY),
        ('TEXTCOLOR', (0, 0), (-1, 0), white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('FONTNAME', (0, 1), (0, -1), 'Helvetica'),
        ('TEXTCOLOR', (0, 1), (-1, -1), DEWR_DARK_GREY),
        ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
        ('GRID', (0, 0), (-1, -1), 0.5, DEWR_LIGHT_GREY),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [HexColor("#F5F5F5"), white]),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(t3)
    story.append(source_note(
        "Note: n=104; shares may not total 100 due to rounding. Source: DEWR Public Generative AI Trial survey, 2026."))
    story.append(sp(10))

    # ==============================
    # APPENDIX
    # ==============================
    story.append(PageBreak())
    story.append(Paragraph("Appendix", h1))
    story.append(HRFlowable(width="100%", thickness=1, color=DEWR_GREEN))
    story.append(sp(8))

    story.append(Paragraph("Additional survey patterns", h3))
    story.append(Paragraph(
        "Public-tool value also varied by APS/EL level and organisational group. EL users were more "
        "likely to report value over Copilot, APS users were more likely to rate at least one public "
        "tool as useful, and Workplace Relations recorded the strongest value-over-Copilot result.",
        body))
    story.append(sp(8))

    story.append(Paragraph("Survey questionnaire", h2))
    story.append(Paragraph(
        "The survey comprised mandatory and optional questions across six sections. "
        "Questions requiring an answer are denoted with an asterisk (*). Skip logic directed "
        "participants to later questions based on their responses.", body))
    story.append(sp(4))

    sections = [
        ("Section 1: General questions (Q1–Q11)", [
            "APS level, Group, Job Family, Job Title",
            "Prior Gen AI experience level",
            "Whether the participant used public Gen AI tools during the trial",
            "Reasons for non-use (if applicable)",
            "Frequency of public tool use, experience improvement, document upload and copy-paste behaviour",
        ]),
        ("Section 2: Copilot (Q12–Q17)", [
            "M365 Copilot access status",
            "Copilot usage frequency, task types, overall usefulness",
            "Time saved by activity area and across the average workday",
        ]),
        ("Section 3: ChatGPT (Q18–Q25)", [
            "Whether ChatGPT was used, frequency, task types, usefulness",
            "Comparison with Copilot across five dimensions",
            "Additional value beyond Copilot by task type",
            "Limitations experienced and continuation intent",
        ]),
        ("Section 4: Gemini (Q26–Q33)", [
            "Same structure as ChatGPT section",
        ]),
        ("Section 5: Claude (Q34–Q41)", [
            "Same structure as ChatGPT section",
        ]),
        ("Section 6: Final questions (Q42–Q48)", [
            "Overall comfort using public Gen AI tools",
            "Value of public tools over and above Copilot",
            "Ethical and security concerns encountered",
            "Open-text feedback on concerns and additional comments",
        ]),
    ]
    for sec_title, items in sections:
        story.append(Paragraph(sec_title, h3))
        for item in items:
            story.append(bullet(item))
        story.append(sp(4))

    # Build
    doc.build(story, onFirstPage=cover_page, onLaterPages=header_footer)
    print(f"Report generated: {OUTPUT_PATH}")


if __name__ == "__main__":
    build_report()
