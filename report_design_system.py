"""Reusable DEWR/OCE design system primitives for the ReportLab report."""

from dataclasses import dataclass
import os

from reportlab.lib.colors import HexColor
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import KeepTogether, Paragraph, Table, TableStyle


# Official OCE/DEWR palette.
OCE_GRAPHITE = HexColor("#404246")
OCE_MID_GREY = HexColor("#D7D8D8")
OCE_EUCALYPTUS = HexColor("#719F4C")
OCE_DARK_EUCALYPTUS = HexColor("#5D7A38")
OCE_GREY = HexColor("#A4A7A9")
OCE_PLUM = HexColor("#62165C")
OCE_LIME = HexColor("#B5C427")
OCE_TEAL = HexColor("#009B9F")
OCE_NAVY = HexColor("#0D2C6C")
OCE_BLUE = HexColor("#287DB2")
OCE_YELLOW = HexColor("#E9A913")
OCE_RED = HexColor("#91040D")
OCE_PINK = HexColor("#D37190")
OCE_COBALT = HexColor("#004F9D")
OCE_MINT = HexColor("#47BFAF")
OCE_PURPLE = HexColor("#573393")
OCE_ORANGE = HexColor("#F26322")

# Semantic aliases.
TEXT = OCE_GRAPHITE
TEXT_MUTED = HexColor("#6B6E70")
TEXT_SECONDARY = TEXT_MUTED
PANEL_BACKGROUND = HexColor("#F7F8FA")
SOFT_LINE = HexColor("#E1E3DF")
CHART_GRID = OCE_MID_GREY
BAR_TRACK = HexColor("#E3E5E6")
BAR_TRACK_MUTED_GREEN = HexColor("#E1E5E2")
KEY_FINDING_BACKGROUND = HexColor("#EFF4E8")
COMPARISON_NEUTRAL = HexColor("#D7D5CC")
COVER_MUTED_GREEN = HexColor("#9AAB64")
FOGGED_EUCALYPTUS = HexColor("#B2BFA3")
FOGGED_GRAPHITE = HexColor("#A5A6A9")
SUCCESS = OCE_DARK_EUCALYPTUS
ACCENT = OCE_TEAL
CAUTION = OCE_YELLOW

# Compatibility names used by the current generate_report.py.
DEWR_GREEN = OCE_EUCALYPTUS
DEWR_DARK_GREEN = OCE_DARK_EUCALYPTUS
DEWR_DARK_GREY = OCE_GRAPHITE
DEWR_NAVY = OCE_GRAPHITE
DEWR_BLUE = OCE_GRAPHITE
DEWR_DARK_BLUE = OCE_GRAPHITE
DEWR_TEAL = OCE_TEAL
DEWR_GREY = OCE_GREY
DEWR_LIGHT_GREY = OCE_MID_GREY
DEWR_LIME = OCE_LIME
DEWR_RED = OCE_RED
DEWR_OFF_WHITE = PANEL_BACKGROUND
DEWR_SOFT_LINE = SOFT_LINE
DEWR_TEXT_GREY = TEXT_MUTED
DEWR_MUTED_GREY = HexColor("#B8BBBD")
DEWR_NAVY_OFFICIAL = OCE_NAVY
DEWR_BLUE_OFFICIAL = OCE_BLUE


@dataclass(frozen=True)
class Space:
    # Numeric scale (generic tiers)
    xs: float = 2
    sm: float = 4
    md: float = 8
    lg: float = 12
    xl: float = 20

    # Semantic story-rhythm tokens
    # (Some of these map to the tiers above; some are bespoke for now
    # and will be normalized in a later step.)
    heading_gap: float = 2     # == xs
    paragraph_gap: float = 8   # == md
    tight_gap: float = 4       # == sm
    note_gap: float = 5        # bespoke (to normalize)
    after_note_gap: float = 10 # bespoke (to normalize)
    section_gap: float = 14    # bespoke (to normalize)
    visual_gap: float = 30     # bespoke (to normalize)


# Legacy aliases — kept so existing call sites continue working.
# Both `Spacing()` and `StoryRhythmSpec()` now return the same unified Space.
Spacing = Space
StoryRhythmSpec = Space


class FlowableSpacingMixin:
    def getSpaceBefore(self):
        return getattr(self, "space_before", 0)

    def getSpaceAfter(self):
        return getattr(self, "space_after", 0)


@dataclass(frozen=True)
class TypeScale:
    title: float = 26
    subtitle: float = 14
    h1: float = 18
    h2: float = 14
    h3: float = 11.5
    h4: float = 10
    body: float = 10
    note: float = 7.0
    chart_title: float = 10.5


@dataclass(frozen=True)
class Lines:
    hairline: float = 0.35
    fine: float = 0.5
    regular: float = 0.6


@dataclass(frozen=True)
class Radii:
    sm: float = 4
    md: float = 8
    lg: float = 16


@dataclass(frozen=True)
class PageSpec:
    left_margin: float = 25 * mm
    right_margin: float = 25 * mm
    top_margin: float = 28 * mm
    bottom_margin: float = 25 * mm


@dataclass(frozen=True)
class ChartSpec:
    grid_color = CHART_GRID
    axis_color = SOFT_LINE
    label_color = TEXT_MUTED
    title_color = TEXT
    grid_width: float = 0.35
    axis_width: float = 0.5


@dataclass(frozen=True)
class VisualTextSpec:
    visual_title: float = 10.5
    visual_title_leading: float = 13.0
    panel_header: float = 7.5
    panel_header_small: float = 7.2
    card_title: float = 8.5
    card_body: float = 8.0
    card_body_leading: float = 9.5
    micro_label: float = 7.8
    micro_value: float = 15.0
    theme_title: float = 8.2
    theme_title_leading: float = 9.4
    theme_body: float = 7.7
    theme_body_leading: float = 9.0
    safeguard_title: float = 8.6
    safeguard_title_leading: float = 10.2
    safeguard_body: float = 8.0
    safeguard_body_leading: float = 10.0
    model_body: float = 7.6
    model_body_leading: float = 9.2
    usefulness_title: float = 8.3
    usefulness_title_leading: float = 9.5
    usefulness_value: float = 6.4
    chart_label: float = 7.5
    chart_label_leading: float = 8.6
    chart_tick: float = 7.0
    chart_legend: float = 7.2
    chart_legend_compact: float = 6.6
    chart_value_label: float = 7.0
    chart_value_label_compact: float = 6.8
    stacked_row_label: float = 7.8
    stacked_row_label_leading: float = 8.8
    stacked_segment_label: float = 6.4
    stacked_callout_value: float = 17.0
    stacked_callout_label: float = 7.4
    stacked_callout_label_leading: float = 8.6
    table_header: float = 6.5
    table_header_leading: float = 7.5
    column_header: float = 6.5
    column_header_leading: float = 7.5
    table_label: float = 7.6
    table_label_leading: float = 8.6
    table_value: float = 9.0
    table_value_leading: float = 10.5
    value_reach_section: float = 8.0
    value_reach_label: float = 7.6
    value_reach_label_leading: float = 8.6
    value_reach_value: float = 9.0
    kpi_value: float = 24.0
    kpi_value_medium: float = 22.0
    kpi_value_compact: float = 17.0
    kpi_caption: float = 7.4
    kpi_caption_leading: float = 8.4
    stat_value: float = 20.0
    stat_value_min: float = 14.0
    stat_label: float = 9.0
    callout_text: float = 11.0
    callout_text_leading: float = 15.0
    horizontal_callout_text: float = 9.3
    horizontal_callout_text_leading: float = 10.8
    key_finding: float = 10.5
    key_finding_leading: float = 14.0
    time_savings_label: float = 8.4
    time_savings_value: float = 13.0
    time_savings_context: float = 7.5
    cover_fallback_agency: float = 11.0
    cover_fallback_department: float = 10.0
    note: float = 8.5


@dataclass(frozen=True)
class Panel:
    """Canonical panel / card / table vocabulary.

    Single source of truth for panel inset, table cell padding, column-header
    heights, gutters and divider weights.
    """

    # ---- Inset: padding between a panel/card border and its content ----
    inset_sm: float = 12
    inset_md: float = 16
    inset_lg: float = 18
    inset_xl: float = 20
    inset_xxl: float = 28

    # ---- Table cells ----
    cell_pad_x: float = 14
    cell_pad_x_tight: float = 6
    cell_pad_y: float = 11
    cell_pad_y_tight: float = 4

    # ---- Column header row heights ----
    header_h_compact: float = 28
    header_h_default: float = 34
    header_h_tall: float = 48

    # ---- Table body row height ----
    row_h_matrix: float = 26

    # ---- Gutter: space between adjacent panel elements ----
    gutter: float = 10

    # ---- Dividers ----
    divider_inset: float = 16
    divider_width: float = 0.5
    hairline_width: float = 0.35


@dataclass(frozen=True)
class KpiSpec:
    panel_height: float = 74.0
    strip_height: float = 96.0
    value_y_without_title: float = 52.0
    value_y_with_title: float = 42.0
    label_gap: float = 16.0
    divider_top_inset: float = 12.0
    divider_bottom_inset: float = 12.0
    stat_box_height: float = 55.0
    stat_box_radius: float = 4.0


@dataclass(frozen=True)
class ChartLayoutSpec:
    row_height: float = 23.0
    row_height_compact: float = 19.0
    row_height_dense: float = 13.0
    bar_height: float = 7.0
    bar_height_compact: float = 6.0
    bar_height_medium: float = 11.0
    bar_height_large: float = 14.0
    dot_radius: float = 3.0
    dot_radius_small: float = 2.6
    dot_radius_compact: float = 2.4
    dot_radius_highlight: float = 3.8
    legend_marker_radius: float = 2.6
    legend_marker_radius_compact: float = 2.4
    axis_top_gap: float = 42.0
    label_width_ratio: float = 0.35
    dumbbell_label_width_ratio: float = 0.39
    dumbbell_line_width: float = 0.7
    dumbbell_line_width_highlight: float = 1.2


@dataclass(frozen=True)
class PageChromeSpec:
    header_line_y: float = 20 * mm
    header_text_y: float = 18 * mm
    footer_line_y: float = 18 * mm
    footer_text_y: float = 13 * mm
    header_text_size: float = 8.0
    footer_text_size: float = 8.0
    header_line_width: float = 2.0
    footer_line_width: float = 0.5


@dataclass(frozen=True)
class CoverSpec:
    left: float = 64.0
    logo_width: float = 196.0
    logo_height: float = 61.0
    title_size: float = 26.0
    title_leading: float = 34.0
    subtitle_size: float = 17.0
    subtitle_leading: float = 25.0
    date_size: float = 16.0
    bottom_bar_height: float = 10 * mm
    logo_y_offset: float = 154.0
    fallback_agency_y_offset: float = 112.0
    fallback_rule_y_offset: float = 118.0
    fallback_department_y_offset: float = 135.0
    fallback_department_second_line_y_offset: float = 148.0
    fallback_rule_width: float = 180.0
    fallback_rule_width_line: float = 0.6
    title_y_offset: float = 285.0
    subtitle_y_offset: float = 326.0
    date_y_offset: float = 354.0
    text_right_margin: float = 64.0


@dataclass(frozen=True)
class FontSpec:
    regular: str = "Helvetica"
    bold: str = "Helvetica-Bold"
    italic: str = "Helvetica-Oblique"
    bold_italic: str = "Helvetica-BoldOblique"


def _font_lookup():
    roots = [
        "/Library/Fonts",
        "/System/Library/Fonts",
        os.path.expanduser("~/Library/Fonts"),
        os.path.expanduser("~/Library/Fonts/Microsoft"),
    ]
    filenames = {
        "regular": ["Aptos.ttf", "Aptos-Regular.ttf"],
        "bold": ["Aptos Bold.ttf", "Aptos-Bold.ttf"],
        "italic": ["Aptos Italic.ttf", "Aptos-Italic.ttf"],
        "bold_italic": ["Aptos Bold Italic.ttf", "Aptos-BoldItalic.ttf"],
    }
    found = {}
    for key, names in filenames.items():
        for root in roots:
            for name in names:
                path = os.path.join(root, name)
                if os.path.exists(path):
                    found[key] = path
                    break
            if key in found:
                break
    return found


def register_fonts():
    """Register Aptos where available, otherwise return Helvetica names."""
    fallback = FontSpec()
    paths = _font_lookup()
    names = {
        "regular": "Aptos",
        "bold": "Aptos-Bold",
        "italic": "Aptos-Italic",
        "bold_italic": "Aptos-BoldItalic",
    }
    registered = {}
    for key, font_name in names.items():
        path = paths.get(key)
        if not path:
            continue
        try:
            pdfmetrics.registerFont(TTFont(font_name, path))
            registered[key] = font_name
        except Exception:
            continue

    return FontSpec(
        regular=registered.get("regular", fallback.regular),
        bold=registered.get("bold", fallback.bold),
        italic=registered.get("italic", fallback.italic),
        bold_italic=registered.get("bold_italic", fallback.bold_italic),
    )


def _font(fonts, attr):
    if fonts is None:
        fonts = register_fonts()
    if isinstance(fonts, dict):
        return fonts.get(attr, getattr(FontSpec(), attr))
    return getattr(fonts, attr)


_VISUAL_STYLE_ROLES = {
    "visual_title": ("visual_title", "visual_title_leading", TEXT),
    "panel_header": ("panel_header", None, TEXT),
    "panel_header_small": ("panel_header_small", None, TEXT),
    "card_title": ("card_title", None, TEXT),
    "card_body": ("card_body", "card_body_leading", TEXT),
    "kpi_caption": ("kpi_caption", "kpi_caption_leading", TEXT_MUTED),
    "chart_label": ("chart_label", "chart_label_leading", TEXT_MUTED),
    "table_header": ("table_header", "table_header_leading", TEXT),
    "column_header": ("column_header", "column_header_leading", TEXT),
    "table_label": ("table_label", "table_label_leading", TEXT),
    "table_value": ("table_value", "table_value_leading", TEXT),
    "stacked_row_label": ("stacked_row_label", "stacked_row_label_leading", TEXT),
    "theme_title": ("theme_title", "theme_title_leading", TEXT),
    "theme_body": ("theme_body", "theme_body_leading", TEXT),
    "safeguard_title": ("safeguard_title", "safeguard_title_leading", TEXT),
    "safeguard_body": ("safeguard_body", "safeguard_body_leading", TEXT),
    "model_body": ("model_body", "model_body_leading", TEXT),
    "note": ("note", None, TEXT_SECONDARY),
}


def visual_paragraph_style(
    name,
    fonts,
    role,
    alignment=TA_LEFT,
    bold=False,
    italic=False,
    text_color=None,
):
    """Build a reusable ParagraphStyle for visual Flowables."""
    if role not in _VISUAL_STYLE_ROLES:
        raise ValueError(f"Unknown visual paragraph role: {role}")

    size_attr, leading_attr, default_color = _VISUAL_STYLE_ROLES[role]
    visual_text = VisualTextSpec()
    font_attr = "regular"
    if bold and italic:
        font_attr = "bold_italic"
    elif bold:
        font_attr = "bold"
    elif italic:
        font_attr = "italic"

    font_size = getattr(visual_text, size_attr)
    leading = getattr(visual_text, leading_attr) if leading_attr else font_size + 2

    return ParagraphStyle(
        name,
        fontName=_font(fonts, font_attr),
        fontSize=font_size,
        leading=leading,
        alignment=alignment,
        textColor=default_color if text_color is None else text_color,
        spaceBefore=0,
        spaceAfter=0,
    )


def make_visual_styles(fonts):
    """Return reusable ParagraphStyles for custom visual components."""
    return {
        "panel_header": visual_paragraph_style(
            "VisualPanelHeader", fonts, "panel_header", bold=True
        ),
        "panel_header_small": visual_paragraph_style(
            "VisualPanelHeaderSmall", fonts, "panel_header_small", bold=True
        ),
        "visual_title": visual_paragraph_style(
            "VisualTitle", fonts, "visual_title", bold=True
        ),
        "card_title": visual_paragraph_style(
            "VisualCardTitle", fonts, "card_title", bold=True
        ),
        "card_body": visual_paragraph_style("VisualCardBody", fonts, "card_body"),
        "kpi_caption": visual_paragraph_style("VisualKpiCaption", fonts, "kpi_caption"),
        "chart_label": visual_paragraph_style("VisualChartLabel", fonts, "chart_label"),
        "table_header": visual_paragraph_style(
            "VisualTableHeader", fonts, "table_header", bold=True
        ),
        # Canonical column-header style. Same attributes as table_header for
        # now (so no reflow); table_header retires in a later step.
        "column_header": visual_paragraph_style(
            "VisualColumnHeader", fonts, "column_header", bold=True
        ),
        "table_label": visual_paragraph_style("VisualTableLabel", fonts, "table_label"),
        "table_value": visual_paragraph_style(
            "VisualTableValue", fonts, "table_value", bold=True
        ),
        "stacked_row_label": visual_paragraph_style(
            "VisualStackedRowLabel", fonts, "stacked_row_label"
        ),
        "theme_title": visual_paragraph_style(
            "VisualThemeTitle", fonts, "theme_title", bold=True
        ),
        "theme_body": visual_paragraph_style("VisualThemeBody", fonts, "theme_body"),
        "safeguard_title": visual_paragraph_style(
            "VisualSafeguardTitle", fonts, "safeguard_title", bold=True
        ),
        "safeguard_body": visual_paragraph_style(
            "VisualSafeguardBody", fonts, "safeguard_body"
        ),
        "model_body": visual_paragraph_style("VisualModelBody", fonts, "model_body"),
        "note": visual_paragraph_style("VisualNote", fonts, "note"),
    }


def draw_wrapped_text(canvas, text, style, x, y_top, width, max_height):
    """Draw text with ReportLab Paragraph wrapping from a top-left anchor."""
    paragraph = Paragraph("" if text is None else text, style)
    _, height = paragraph.wrap(width, max_height)
    paragraph.drawOn(canvas, x, y_top - height)
    return height


def access_evidence_table_style():
    panel = Panel()
    lines = Lines()
    return TableStyle(
        [
            ("BACKGROUND", (0, 0), (-1, -1), DEWR_OFF_WHITE),
            ("LINEBELOW", (0, 0), (-1, 0), lines.fine, DEWR_LIGHT_GREY),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("ALIGN", (0, 0), (0, 0), "LEFT"),
            ("ALIGN", (1, 1), (-1, -1), "CENTER"),
            ("ALIGN", (0, 0), (0, -1), "LEFT"),
            ("LEFTPADDING", (0, 0), (-1, -1), panel.cell_pad_x),
            ("RIGHTPADDING", (0, 0), (-1, -1), panel.cell_pad_x),
            ("TOPPADDING", (0, 0), (-1, -1), panel.cell_pad_y_tight),
            ("BOTTOMPADDING", (0, 0), (-1, -1), panel.cell_pad_y_tight),
            ("BOTTOMPADDING", (0, 0), (-1, 0), panel.cell_pad_y_tight),
        ]
    )


def build_paragraph_styles(fonts=None):
    """Build the ParagraphStyle set consumed by generate_report.py."""
    regular = _font(fonts, "regular")
    bold = _font(fonts, "bold")
    italic = _font(fonts, "italic")

    body = ParagraphStyle(
        "Body",
        fontName=regular,
        fontSize=10,
        leading=14,
        textColor=TEXT,
        spaceAfter=8,
        alignment=TA_LEFT,
    )
    bullet = ParagraphStyle(
        "Bullet",
        fontName=regular,
        fontSize=10,
        leading=14,
        textColor=TEXT,
        leftIndent=18,
        spaceAfter=4,
        bulletIndent=6,
        bulletFontName=regular,
        bulletFontSize=10,
    )
    h1 = ParagraphStyle(
        "H1",
        fontName=bold,
        fontSize=18,
        leading=24,
        textColor=TEXT,
        spaceBefore=16,
        spaceAfter=20,
    )
    h2 = ParagraphStyle(
        "H2",
        fontName=bold,
        fontSize=14,
        leading=18,
        textColor=TEXT,
        spaceBefore=14,
        spaceAfter=8,
    )
    h3 = ParagraphStyle(
        "H3",
        fontName=bold,
        fontSize=11.5,
        leading=15,
        textColor=TEXT,
        spaceBefore=18,
        spaceAfter=6,
    )

    return {
        "title": ParagraphStyle(
            "Title",
            fontName=bold,
            fontSize=26,
            leading=32,
            textColor=TEXT,
            spaceAfter=6,
        ),
        "subtitle": ParagraphStyle(
            "Subtitle",
            fontName=regular,
            fontSize=14,
            leading=18,
            textColor=TEXT,
            spaceAfter=20,
        ),
        "h1": h1,
        "evaluation_h1": ParagraphStyle(
            "EvaluationH1",
            parent=h1,
            textColor=DEWR_DARK_GREEN,
        ),
        "h2": h2,
        "h3": h3,
        "h4": ParagraphStyle(
            "H4",
            fontName=bold,
            fontSize=10,
            leading=13,
            textColor=TEXT,
            spaceBefore=8,
            spaceAfter=4,
        ),
        "mini_heading": ParagraphStyle(
            "MiniHeading",
            fontName=bold,
            fontSize=8.8,
            leading=11,
            textColor=TEXT,
            spaceBefore=16,
            spaceAfter=4,
        ),
        "metric_context": ParagraphStyle(
            "MetricContext",
            fontName=bold,
            fontSize=8.3,
            leading=10,
            textColor=TEXT,
            spaceBefore=0,
            spaceAfter=5,
        ),
        "body": body,
        "section_intro": ParagraphStyle("SectionIntro", parent=body, spaceAfter=0),
        "body_bold": ParagraphStyle(
            "BodyBold",
            fontName=bold,
            fontSize=10,
            leading=14,
            textColor=TEXT,
            spaceAfter=8,
        ),
        "bullet": bullet,
        "evidence_bullet": ParagraphStyle(
            "EvidenceBullet",
            parent=bullet,
            fontSize=9.6,
            leading=13.5,
            spaceAfter=5,
        ),
        "limitation_bullet": ParagraphStyle(
            "LimitationBullet",
            parent=bullet,
            leading=15,
            spaceAfter=7,
        ),
        "quote": ParagraphStyle(
            "Quote",
            fontName=italic,
            fontSize=9.5,
            leading=13,
            textColor=TEXT_SECONDARY,
            leftIndent=20,
            rightIndent=20,
            spaceAfter=8,
            borderPadding=6,
        ),
        "note": ParagraphStyle(
            "Note",
            fontName=regular,
            fontSize=7,
            leading=9,
            textColor=TEXT_SECONDARY,
            spaceBefore=4,
            spaceAfter=6,
        ),
        "chart_title": ParagraphStyle(
            "ChartTitle",
            fontName=bold,
            fontSize=10.5,
            leading=13,
            textColor=TEXT,
            spaceBefore=4,
            spaceAfter=4,
        ),
    }


def draw_panel_background(
    canvas,
    x,
    y,
    w,
    h,
    fill=None,
    stroke=None,
    radius=None,
    stroke_width=None,
):
    fill = PANEL_BACKGROUND if fill is None else fill
    stroke = SOFT_LINE if stroke is None else stroke
    radius = Radii().md if radius is None else radius
    stroke_width = Lines().hairline if stroke_width is None else stroke_width

    canvas.saveState()
    canvas.setFillColor(fill)
    should_stroke = bool(stroke and stroke_width)
    if should_stroke:
        canvas.setStrokeColor(stroke)
        canvas.setLineWidth(stroke_width)
    if radius:
        canvas.roundRect(x, y, w, h, radius, fill=1, stroke=1 if should_stroke else 0)
    else:
        canvas.rect(x, y, w, h, fill=1, stroke=1 if should_stroke else 0)
    canvas.restoreState()


def draw_hairline(canvas, x1, y1, x2, y2, color=None, width=None):
    canvas.saveState()
    canvas.setStrokeColor(SOFT_LINE if color is None else color)
    canvas.setLineWidth(Lines().hairline if width is None else width)
    canvas.line(x1, y1, x2, y2)
    canvas.restoreState()


def fit_text_size(canvas, text, font_name, start_size, max_width, min_size=6.0):
    size = float(start_size)
    while size > min_size and canvas.stringWidth(text, font_name, size) > max_width:
        size -= 0.5
    return max(size, min_size)
