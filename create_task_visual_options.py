from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.colors import HexColor, black
from reportlab.lib.enums import TA_JUSTIFY, TA_CENTER
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable, PageBreak
from reportlab.platypus.flowables import Flowable


DEWR_GREEN = HexColor("#719F4C")
DEWR_DARK_GREEN = HexColor("#5D7A38")
DEWR_DARK_GREY = HexColor("#404246")
DEWR_GREY = HexColor("#A4A7A9")
DEWR_LIGHT_GREY = HexColor("#D7D8D8")
PANEL_GREY = HexColor("#F7F8FA")
TRACK_GREY = HexColor("#E3E5E6")
TEXT = DEWR_DARK_GREY

BASE_DIR = "/Users/python/Documents/Public AI Trial /Outputs"


def header_footer(canvas, doc):
    canvas.saveState()
    canvas.setStrokeColor(black)
    canvas.setLineWidth(2)
    canvas.line(doc.leftMargin, A4[1] - 20 * mm, A4[0] - doc.rightMargin, A4[1] - 20 * mm)
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(DEWR_DARK_GREY)
    canvas.drawString(doc.leftMargin, A4[1] - 18 * mm, "Task footprint visual options")
    canvas.setStrokeColor(DEWR_LIGHT_GREY)
    canvas.setLineWidth(0.5)
    canvas.line(doc.leftMargin, 18 * mm, A4[0] - doc.rightMargin, 18 * mm)
    canvas.setFont("Helvetica", 8)
    canvas.drawString(doc.leftMargin, 13 * mm, "DEWR Public AI Trial report")
    canvas.drawRightString(A4[0] - doc.rightMargin, 13 * mm, f"Page {doc.page}")
    canvas.restoreState()


class GapBarPanel(Flowable):
    def __init__(self, width):
        super().__init__()
        self.box_width = width
        self._height = 132
        self.rows = [
            ("Research, problem solving or generating ideas", 67, 44),
            ("Planning or meeting preparation", 33, 15),
        ]

    def wrap(self, availWidth, availHeight):
        self.box_width = availWidth
        return self.box_width, self._height

    def draw(self):
        c = self.canv
        w = self.box_width
        h = self._height
        pad = 16
        label_w = w * 0.42
        bar_x = pad + label_w
        bar_w = w - bar_x - 62
        bar_h = 8

        c.setFillColor(PANEL_GREY)
        c.rect(0, 0, w, h, fill=1, stroke=0)
        c.setFillColor(DEWR_DARK_GREY)
        c.setFont("Helvetica-Bold", 7.5)
        c.drawString(pad, h - 22, "LARGEST TASK-TYPE GAPS")
        c.drawString(bar_x, h - 22, "M365")
        c.drawString(bar_x + 58, h - 22, "CHAT")
        c.setStrokeColor(DEWR_LIGHT_GREY)
        c.line(pad, h - 36, w - pad, h - 36)

        for i, (label, m365, chat) in enumerate(self.rows):
            y = h - 62 - i * 43
            p = Paragraph(label, ParagraphStyle(
                "gap_label",
                fontName="Helvetica-Bold",
                fontSize=8.0,
                leading=9.5,
                textColor=TEXT,
            ))
            p.wrap(label_w - 8, 24)
            p.drawOn(c, pad, y - 8)

            c.setFillColor(TRACK_GREY)
            c.rect(bar_x, y + 8, bar_w, bar_h, fill=1, stroke=0)
            c.rect(bar_x, y - 8, bar_w, bar_h, fill=1, stroke=0)

            c.setFillColor(DEWR_DARK_GREEN)
            c.rect(bar_x, y + 8, bar_w * (m365 / 100), bar_h, fill=1, stroke=0)
            c.setFillColor(DEWR_DARK_GREY)
            c.rect(bar_x, y - 8, bar_w * (chat / 100), bar_h, fill=1, stroke=0)

            c.setFont("Helvetica-Bold", 8.2)
            c.setFillColor(DEWR_DARK_GREEN)
            c.drawString(bar_x + bar_w + 8, y + 6, f"{m365}%")
            c.setFillColor(DEWR_DARK_GREY)
            c.drawString(bar_x + bar_w + 8, y - 10, f"{chat}%")


class MiniCardsPanel(Flowable):
    def __init__(self, width):
        super().__init__()
        self.box_width = width
        self._height = 100
        self.items = [
            ("4.0 vs 3.2", "Average task types selected"),
            ("1.5x", "More likely to use for research / ideas"),
            ("2.2x", "More likely to use for meeting prep"),
        ]

    def wrap(self, availWidth, availHeight):
        self.box_width = availWidth
        return self.box_width, self._height

    def draw(self):
        c = self.canv
        w = self.box_width
        h = self._height
        pad = 16
        col_w = (w - 2 * pad) / len(self.items)
        c.setFillColor(PANEL_GREY)
        c.rect(0, 0, w, h, fill=1, stroke=0)
        for i, (value, label) in enumerate(self.items):
            x = pad + i * col_w
            if i:
                c.setStrokeColor(DEWR_LIGHT_GREY)
                c.line(x, 18, x, h - 18)
            c.setFillColor(DEWR_DARK_GREEN if i == 0 else DEWR_DARK_GREY)
            c.setFont("Helvetica-Bold", 21)
            c.drawCentredString(x + col_w / 2, h - 42, value)
            p = Paragraph(label, ParagraphStyle(
                "mini_label",
                fontName="Helvetica",
                fontSize=7.8,
                leading=8.8,
                alignment=TA_CENTER,
                textColor=TEXT,
            ))
            _, ph = p.wrap(col_w - 22, 28)
            p.drawOn(c, x + 11, h - 58 - ph)


class DumbbellPanel(Flowable):
    def __init__(self, width):
        super().__init__()
        self.box_width = width
        self._height = 128
        self.rows = [
            ("Research, problem solving or generating ideas", 67, 44),
            ("Planning or meeting preparation", 33, 15),
        ]

    def wrap(self, availWidth, availHeight):
        self.box_width = availWidth
        return self.box_width, self._height

    def draw(self):
        c = self.canv
        w = self.box_width
        h = self._height
        pad = 16
        label_w = w * 0.42
        axis_x = pad + label_w
        axis_w = w - axis_x - 40

        c.setFillColor(PANEL_GREY)
        c.rect(0, 0, w, h, fill=1, stroke=0)
        c.setFillColor(DEWR_DARK_GREY)
        c.setFont("Helvetica-Bold", 7.5)
        c.drawString(pad, h - 22, "LARGEST TASK-TYPE GAPS")
        c.setStrokeColor(DEWR_LIGHT_GREY)
        c.line(pad, h - 36, w - pad, h - 36)
        c.setFont("Helvetica", 7.2)
        c.drawString(axis_x, h - 48, "0%")
        c.drawCentredString(axis_x + axis_w * 0.5, h - 48, "50%")
        c.drawRightString(axis_x + axis_w, h - 48, "100%")

        for i, (label, m365, chat) in enumerate(self.rows):
            y = h - 72 - i * 34
            p = Paragraph(label, ParagraphStyle(
                "dumbbell_label",
                fontName="Helvetica-Bold",
                fontSize=8.0,
                leading=9.2,
                textColor=TEXT,
            ))
            p.wrap(label_w - 8, 24)
            p.drawOn(c, pad, y - 8)

            c.setStrokeColor(DEWR_LIGHT_GREY)
            c.line(axis_x, y, axis_x + axis_w, y)
            chat_x = axis_x + axis_w * (chat / 100)
            m365_x = axis_x + axis_w * (m365 / 100)
            c.setStrokeColor(DEWR_GREY)
            c.setLineWidth(1.0)
            c.line(chat_x, y, m365_x, y)
            c.setFillColor(DEWR_DARK_GREY)
            c.circle(chat_x, y, 3.5, fill=1, stroke=0)
            c.setFillColor(DEWR_DARK_GREEN)
            c.circle(m365_x, y, 4.2, fill=1, stroke=0)
            c.setFont("Helvetica-Bold", 8.0)
            c.setFillColor(DEWR_DARK_GREY)
            c.drawCentredString(chat_x, y - 15, f"{chat}%")
            c.setFillColor(DEWR_DARK_GREEN)
            c.drawCentredString(m365_x, y + 8, f"{m365}%")


class FullTaskDumbbellPanel(Flowable):
    def __init__(self, width):
        super().__init__()
        self.box_width = width
        self._height = 230
        # Estimated from the supplied reference chart, with the two text-confirmed
        # largest gaps held fixed at 67/44 and 33/15.
        self.rows = [
            ("Summarising", 86, 76, False),
            ("Editing and revision", 72, 66, False),
            ("Drafting", 71, 61, False),
            ("Research, problem solving or generating ideas", 67, 44, True),
            ("General administrative tasks", 47, 38, False),
            ("Planning or meeting preparation", 33, 15, True),
            ("Coding or data work", 24, 20, False),
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

        c.setFillColor(PANEL_GREY)
        c.rect(0, 0, w, h, fill=1, stroke=0)
        c.setFillColor(DEWR_DARK_GREY)
        c.setFont("Helvetica-Bold", 7.5)
        c.drawString(pad, h - 22, "COPILOT TASK FOOTPRINT BY ACCESS TYPE")
        legend_x = w - pad - 150
        c.setFillColor(DEWR_DARK_GREEN)
        c.circle(legend_x, h - 20, 3.0, fill=1, stroke=0)
        c.setFillColor(DEWR_DARK_GREY)
        c.setFont("Helvetica", 7.4)
        c.drawString(legend_x + 8, h - 23, "M365 Copilot")
        c.setFillColor(DEWR_DARK_GREY)
        c.circle(legend_x + 82, h - 20, 3.0, fill=1, stroke=0)
        c.drawString(legend_x + 90, h - 23, "Copilot Chat")
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
            label_style = ParagraphStyle(
                "full_dumbbell_label",
                fontName="Helvetica-Bold" if highlight else "Helvetica",
                fontSize=7.6,
                leading=8.6,
                textColor=TEXT,
            )
            p = Paragraph(label, label_style)
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


def build_option(filename, option_title, recommendation, visual=None, bullets=None):
    output = f"{BASE_DIR}/{filename}"
    doc = SimpleDocTemplate(
        output,
        pagesize=A4,
        leftMargin=25 * mm,
        rightMargin=25 * mm,
        topMargin=28 * mm,
        bottomMargin=25 * mm,
    )
    width = A4[0] - doc.leftMargin - doc.rightMargin
    title = ParagraphStyle("Title", fontName="Helvetica-Bold", fontSize=20, leading=25, textColor=black, spaceAfter=8)
    h2 = ParagraphStyle("H2", fontName="Helvetica-Bold", fontSize=13, leading=17, textColor=TEXT, spaceBefore=12, spaceAfter=6)
    body = ParagraphStyle("Body", fontName="Helvetica", fontSize=10.5, leading=15, textColor=TEXT, spaceAfter=8, alignment=TA_JUSTIFY)
    note = ParagraphStyle("Note", fontName="Helvetica-Oblique", fontSize=8.5, leading=11, textColor=DEWR_GREY)
    story = [
        Paragraph(option_title, title),
        HRFlowable(width="100%", thickness=1, color=DEWR_GREEN),
        Spacer(1, 10),
        Paragraph(recommendation, body),
    ]
    if bullets:
        story.append(Paragraph("Evidence treatment", h2))
        for bullet in bullets:
            story.append(Paragraph(f"&bull; {bullet}", body))
    if visual:
        story.extend([Spacer(1, 8), visual(width)])
    story.append(Spacer(1, 5))
    story.append(Paragraph(
        "Note: M365 Copilot n=30; Copilot Chat n=41. Source: DEWR Public Generative AI Trial survey, 2026.",
        note,
    ))
    doc.build(story, onFirstPage=header_footer, onLaterPages=header_footer)
    return output


def append_option_page(story, width, styles, option_title, recommendation, visual=None, bullets=None):
    story.extend([
        Paragraph(option_title, styles["title"]),
        HRFlowable(width="100%", thickness=1, color=DEWR_GREEN),
        Spacer(1, 10),
        Paragraph(recommendation, styles["body"]),
    ])
    if bullets:
        story.append(Paragraph("Evidence treatment", styles["h2"]))
        for bullet in bullets:
            story.append(Paragraph(f"&bull; {bullet}", styles["body"]))
    if visual:
        story.extend([Spacer(1, 8), visual(width)])
    story.append(Spacer(1, 5))
    story.append(Paragraph(
        "Note: M365 Copilot n=30; Copilot Chat n=41. Source: DEWR Public Generative AI Trial survey, 2026.",
        styles["note"],
    ))


def build_combined_options():
    output = f"{BASE_DIR}/task_visual_options_all.pdf"
    doc = SimpleDocTemplate(
        output,
        pagesize=A4,
        leftMargin=25 * mm,
        rightMargin=25 * mm,
        topMargin=28 * mm,
        bottomMargin=25 * mm,
    )
    width = A4[0] - doc.leftMargin - doc.rightMargin
    styles = {
        "title": ParagraphStyle("Title", fontName="Helvetica-Bold", fontSize=20, leading=25, textColor=black, spaceAfter=8),
        "h2": ParagraphStyle("H2", fontName="Helvetica-Bold", fontSize=13, leading=17, textColor=TEXT, spaceBefore=12, spaceAfter=6),
        "body": ParagraphStyle("Body", fontName="Helvetica", fontSize=10.5, leading=15, textColor=TEXT, spaceAfter=8, alignment=TA_JUSTIFY),
        "note": ParagraphStyle("Note", fontName="Helvetica-Oblique", fontSize=8.5, leading=11, textColor=DEWR_GREY),
    }
    story = []
    pages = [
        (
            "Option 1: Prose-only treatment",
            "M365 Copilot users reported a broader task footprint, selecting 4.0 task types on average compared with 3.2 for Copilot Chat/basic users. The largest differences were in research, problem solving and idea generation, and in planning or meeting preparation.",
            None,
            [
                "Best when the point is secondary and does not need another visual.",
                "Keeps the section visually quieter after the time savings and engagement panels.",
                "Lowest risk of over-explaining a modest but useful finding.",
            ],
        ),
        (
            "Option 2: Two-row gap bars",
            "M365 Copilot users selected more task types overall, and the largest task-level gaps were concentrated in research/ideation and meeting preparation.",
            GapBarPanel,
            None,
        ),
        (
            "Option 3: Three mini evidence cards",
            "The task-breadth finding can be compressed into three executive signals: broader task range, higher research/ideation use and higher meeting-prep use.",
            MiniCardsPanel,
            None,
        ),
        (
            "Option 4: Dumbbell gap plot",
            "A dumbbell plot makes the access-type distance visible without turning the exhibit into a table.",
            DumbbellPanel,
            None,
        ),
        (
            "Option 5: Full task-footprint dumbbell",
            "All task types are shown to establish the full footprint, while the two largest access-type gaps are highlighted: research/ideation and planning/meeting preparation.",
            FullTaskDumbbellPanel,
            None,
        ),
    ]
    for idx, (title, recommendation, visual, bullets) in enumerate(pages):
        if idx:
            story.append(PageBreak())
        append_option_page(story, width, styles, title, recommendation, visual, bullets)
    doc.build(story, onFirstPage=header_footer, onLaterPages=header_footer)
    return output


def main():
    print(build_combined_options())


if __name__ == "__main__":
    main()
