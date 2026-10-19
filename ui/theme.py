"""Modern Theme and Styling System for Word Identity Changer.

Provides polished, cohesive styling using Qt Style Sheets (QSS)
with modern typography, harmonious colors, and crisp component states.
"""

# Color Palette (Tailored Slate & Indigo/Blue)
PRIMARY = "#2563eb"
PRIMARY_HOVER = "#1d4ed8"
PRIMARY_ACTIVE = "#1e40af"
PRIMARY_LIGHT = "#eff6ff"

BACKGROUND = "#f8fafc"
SURFACE = "#ffffff"
SURFACE_BORDER = "#e2e8f0"
SURFACE_BORDER_HOVER = "#cbd5e1"

TEXT_PRIMARY = "#0f172a"
TEXT_SECONDARY = "#475569"
TEXT_MUTED = "#94a3b8"

SUCCESS_BG = "#dcfce7"
SUCCESS_TEXT = "#15803d"
SUCCESS_BORDER = "#86efac"

WARNING_BG = "#fef3c7"
WARNING_TEXT = "#b45309"
WARNING_BORDER = "#fcd34d"

DANGER_BG = "#fee2e2"
DANGER_TEXT = "#b91c1c"
DANGER_BORDER = "#fca5a5"

INFO_BG = "#e0f2fe"
INFO_TEXT = "#0369a1"
INFO_BORDER = "#7dd3fc"


MAIN_STYLESHEET = f"""
QMainWindow {{
    background-color: {BACKGROUND};
    font-family: 'Segoe UI', 'Inter', -apple-system, sans-serif;
}}

QWidget {{
    font-family: 'Segoe UI', 'Inter', -apple-system, sans-serif;
    color: {TEXT_PRIMARY};
}}

/* Card containers */
QFrame.CardFrame {{
    background-color: {SURFACE};
    border: 1px solid {SURFACE_BORDER};
    border-radius: 12px;
    padding: 16px;
}}

QFrame.SectionFrame {{
    background-color: {SURFACE};
    border: 1px solid {SURFACE_BORDER};
    border-radius: 10px;
    padding: 12px;
}}

/* Typography */
QLabel.HeaderTitle {{
    font-size: 18px;
    font-weight: 700;
    color: {TEXT_PRIMARY};
}}

QLabel.SectionTitle {{
    font-size: 14px;
    font-weight: 600;
    color: {TEXT_PRIMARY};
}}

QLabel.FieldLabel {{
    font-size: 12px;
    font-weight: 600;
    color: {TEXT_SECONDARY};
}}

QLabel.SubText {{
    font-size: 12px;
    color: {TEXT_MUTED};
}}

/* Inputs */
QLineEdit {{
    background-color: {SURFACE};
    border: 1px solid {SURFACE_BORDER};
    border-radius: 8px;
    padding: 8px 12px;
    font-size: 13px;
    color: {TEXT_PRIMARY};
    selection-background-color: {PRIMARY};
}}

QLineEdit:focus {{
    border: 1px solid {PRIMARY};
    background-color: #ffffff;
}}

QLineEdit:disabled {{
    background-color: #f1f5f9;
    color: {TEXT_MUTED};
    border: 1px solid #e2e8f0;
}}

/* Buttons */
QPushButton {{
    background-color: {SURFACE};
    border: 1px solid {SURFACE_BORDER};
    border-radius: 8px;
    padding: 8px 16px;
    font-size: 13px;
    font-weight: 600;
    color: {TEXT_PRIMARY};
}}

QPushButton:hover {{
    background-color: #f1f5f9;
    border-color: {SURFACE_BORDER_HOVER};
}}

QPushButton:pressed {{
    background-color: #e2e8f0;
}}

QPushButton:disabled {{
    background-color: #f1f5f9;
    color: {TEXT_MUTED};
    border-color: #e2e8f0;
}}

QPushButton.PrimaryButton {{
    background-color: {PRIMARY};
    border: 1px solid {PRIMARY};
    color: #ffffff;
    font-weight: 600;
    border-radius: 8px;
    padding: 10px 20px;
}}

QPushButton.PrimaryButton:hover {{
    background-color: {PRIMARY_HOVER};
    border-color: {PRIMARY_HOVER};
}}

QPushButton.PrimaryButton:pressed {{
    background-color: {PRIMARY_ACTIVE};
    border-color: {PRIMARY_ACTIVE};
}}

QPushButton.PrimaryButton:disabled {{
    background-color: #93c5fd;
    border-color: #93c5fd;
    color: #ffffff;
}}

QPushButton.DangerButton {{
    background-color: #ffffff;
    border: 1px solid {DANGER_BORDER};
    color: {DANGER_TEXT};
}}

QPushButton.DangerButton:hover {{
    background-color: {DANGER_BG};
}}

/* Radio Buttons */
QRadioButton {{
    font-size: 13px;
    font-weight: 500;
    color: {TEXT_PRIMARY};
    spacing: 8px;
}}

QRadioButton::indicator {{
    width: 18px;
    height: 18px;
    border: 2px solid {SURFACE_BORDER};
    border-radius: 10px;
    background-color: {SURFACE};
}}

QRadioButton::indicator:hover {{
    border-color: {PRIMARY};
}}

QRadioButton::indicator:checked {{
    border-color: {PRIMARY};
    background-color: {PRIMARY};
}}

/* Tables */
QTableWidget {{
    background-color: {SURFACE};
    border: 1px solid {SURFACE_BORDER};
    border-radius: 8px;
    gridline-color: #f1f5f9;
    font-size: 12px;
}}

QTableWidget::item {{
    padding: 8px 10px;
    border-bottom: 1px solid #f1f5f9;
}}

QTableWidget::item:selected {{
    background-color: {PRIMARY_LIGHT};
    color: {TEXT_PRIMARY};
}}

QHeaderView::section {{
    background-color: #f8fafc;
    color: {TEXT_SECONDARY};
    font-weight: 600;
    font-size: 12px;
    padding: 8px 10px;
    border: none;
    border-bottom: 1px solid {SURFACE_BORDER};
}}

/* Progress Bar */
QProgressBar {{
    border: 1px solid {SURFACE_BORDER};
    border-radius: 6px;
    background-color: #f1f5f9;
    text-align: center;
    font-size: 11px;
    font-weight: 600;
    color: {TEXT_PRIMARY};
    height: 18px;
}}

QProgressBar::chunk {{
    background-color: {PRIMARY};
    border-radius: 5px;
}}

/* Scrollbars */
QScrollBar:vertical {{
    background: #f1f5f9;
    width: 8px;
    border-radius: 4px;
}}

QScrollBar::handle:vertical {{
    background: #cbd5e1;
    min-height: 20px;
    border-radius: 4px;
}}

QScrollBar::handle:vertical:hover {{
    background: #94a3b8;
}}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0px;
}}
"""


def get_status_badge_style(status_type: str) -> str:
    """Returns CSS stylesheet for colored status pill/badge."""
    styles = {
        "success": f"""
            background-color: {SUCCESS_BG};
            color: {SUCCESS_TEXT};
            border: 1px solid {SUCCESS_BORDER};
            border-radius: 12px;
            padding: 3px 10px;
            font-size: 11px;
            font-weight: 600;
        """,
        "warning": f"""
            background-color: {WARNING_BG};
            color: {WARNING_TEXT};
            border: 1px solid {WARNING_BORDER};
            border-radius: 12px;
            padding: 3px 10px;
            font-size: 11px;
            font-weight: 600;
        """,
        "danger": f"""
            background-color: {DANGER_BG};
            color: {DANGER_TEXT};
            border: 1px solid {DANGER_BORDER};
            border-radius: 12px;
            padding: 3px 10px;
            font-size: 11px;
            font-weight: 600;
        """,
        "info": f"""
            background-color: {INFO_BG};
            color: {INFO_TEXT};
            border: 1px solid {INFO_BORDER};
            border-radius: 12px;
            padding: 3px 10px;
            font-size: 11px;
            font-weight: 600;
        """,
    }
    return styles.get(status_type, styles["info"])
