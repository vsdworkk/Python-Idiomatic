"""Reusable DEWR/OCE design system primitives for the ReportLab report."""

from dataclasses import dataclass
import os

from reportlab.lib.colors import HexColor
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont


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
class Spacing:
    xs: float = 2
    sm: float = 4
    md: float = 8
    lg: float = 12
    xl: float = 20


@dataclass(frozen=True)
class TypeScale:
    title: float = 26
    subtitle: float = 14
    h1: float = 18
    h2: float = 14
    h3: float = 11.5
    h4: float = 10
    body: float = 10
    note: float = 8.5
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
    table_label: float = 7.6
    table_label_leading: float = 8.6
    table_value: float = 11.0
    table_value_leading: float = 12.0
    comparison_column_header: float = 7.8
    comparison_group_label: float = 7.8
    comparison_measure_label: float = 7.4
    comparison_measure_label_leading: float = 8.6
    comparison_value: float = 11.0
    value_reach_section: float = 8.0
    value_reach_column_header: float = 6.6
    value_reach_label: float = 7.6
    value_reach_label_leading: float = 8.6
    value_reach_value: float = 11.0
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
    note: float = 8.0


@dataclass(frozen=True)
class PanelSpec:
    padding: float = 16.0
    padding_medium: float = 18.0
    padding_large: float = 20.0
    padding_xlarge: float = 28.0
    padding_callout: float = 12.0
    inner_padding: float = 12.0
    gutter: float = 10.0
    title_y_offset: float = 20.0
    divider_y_offset: float = 36.0
    divider_inset: float = 16.0
    section_divider_width: float = 0.5
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
class TableSpec:
    matrix_row_height: float = 26.0
    matrix_header_height: float = 44.0
    matrix_header_height_single: float = 50.0
    comparison_header_height: float = 18.0
    comparison_group_header_height: float = 36.0
    comparison_group_gap: float = 14.0
    comparison_group_indent: float = 8.0
    comparison_row_height: float = 24.0
    comparison_block_gap: float = 18.0
    comparison_label_width_ratio: float = 0.56
    comparison_header_y_offset: float = 22.0
    comparison_label_wrap_inset: float = 6.0
    comparison_column_header_inset: float = 4.0
    comparison_value_label_inset: float = 8.0
    comparison_value_y_offset: float = 9.0
    access_header_height: float = 28.0
    access_row_height: float = 31.0
    cell_padding_x: float = 16.0
    cell_padding_y: float = 5.0
    section_row_value: float = 8.0


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
        spaceAfter=10,
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
        spaceBefore=10,
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
            spaceBefore=4,
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
            fontName=italic,
            fontSize=8.5,
            leading=11,
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
        "s1_h2": ParagraphStyle("S1H2", parent=h2, spaceBefore=14, spaceAfter=10),
        "s1_h3": ParagraphStyle("S1H3", parent=h3, spaceBefore=0, spaceAfter=6),
        "s1_body": ParagraphStyle("S1Body", parent=body, spaceAfter=0),
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
