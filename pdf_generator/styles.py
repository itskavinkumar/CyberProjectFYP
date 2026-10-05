import os
from reportlab.lib.colors import HexColor
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    Paragraph, Spacer, Table, TableStyle, Image, KeepTogether, HRFlowable
)
from reportlab.pdfgen import canvas

# --- Color Palette ---
PRIMARY = HexColor("#0f172a")       # Dark Slate 900
SECONDARY = HexColor("#1e293b")     # Navy Slate 800
ACCENT_BLUE = HexColor("#0369a1")   # Sky 700
ACCENT_CYAN = HexColor("#0891b2")   # Cyan 600
ACCENT_PURPLE = HexColor("#6d28d9") # Purple 700
ACCENT_GREEN = HexColor("#047857")  # Emerald 700
ACCENT_AMBER = HexColor("#b45309")  # Amber 700
ACCENT_ROSE = HexColor("#be123c")   # Rose 700

TEXT_DARK = HexColor("#0f172a")
TEXT_BODY = HexColor("#334155")     # Slate 700
TEXT_MUTED = HexColor("#64748b")    # Slate 500
BG_LIGHT = HexColor("#f8fafc")      # Slate 50
BG_PANEL = HexColor("#f1f5f9")      # Slate 100
BORDER_COLOR = HexColor("#cbd5e1")  # Slate 300
CODE_BG = HexColor("#0f172a")       # Dark code box
CODE_TEXT = HexColor("#38bdf8")     # Sky cyan code font

# --- Numbered Canvas for Running Headers and Footers ---
class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        print(f"[*] Total PDF Pages Compiled: {num_pages}")
        for state in self._saved_page_states:
            self.__dict__.update(state)
            if self._pageNumber > 1:
                self.saveState()
                self.setFont("Helvetica-Bold", 7.5)
                self.setFillColor(HexColor("#64748b"))
                
                # Running Top Header
                self.drawString(36, 762, "CYBER THREAT FORECASTING SYSTEM")
                self.setFont("Helvetica", 7.5)
                self.drawString(185, 762, "|   Technical & Functional Comprehensive Project Guide")
                self.drawRightString(576, 762, "Academic FYP 2026")
                
                self.setStrokeColor(HexColor("#cbd5e1"))
                self.setLineWidth(0.6)
                self.line(36, 756, 576, 756)
                
                # Running Bottom Footer
                self.line(36, 42, 576, 42)
                self.setFont("Helvetica", 8)
                self.drawString(36, 30, "Confidential — Academic Final Year Project Documentation")
                self.setFont("Helvetica-Bold", 8)
                self.setFillColor(HexColor("#0f172a"))
                self.drawRightString(576, 30, f"Page {self._pageNumber} of {num_pages}")
                self.restoreState()
            super().showPage()
        super().save()

# --- Typography & Styles ---
styles = getSampleStyleSheet()

TitleStyle = ParagraphStyle(
    'DocTitle',
    parent=styles['Normal'],
    fontName='Helvetica-Bold',
    fontSize=22,
    leading=27,
    textColor=PRIMARY,
    alignment=1, # Center
    spaceAfter=8
)

SubtitleStyle = ParagraphStyle(
    'DocSubtitle',
    parent=styles['Normal'],
    fontName='Helvetica',
    fontSize=11,
    leading=15,
    textColor=TEXT_MUTED,
    alignment=1,
    spaceAfter=15
)

Heading1Style = ParagraphStyle(
    'SectionHeading1',
    parent=styles['Normal'],
    fontName='Helvetica-Bold',
    fontSize=14,
    leading=18,
    textColor=PRIMARY,
    spaceBefore=14,
    spaceAfter=6,
    keepWithNext=True
)

Heading2Style = ParagraphStyle(
    'SectionHeading2',
    parent=styles['Normal'],
    fontName='Helvetica-Bold',
    fontSize=11.5,
    leading=15,
    textColor=ACCENT_BLUE,
    spaceBefore=10,
    spaceAfter=4,
    keepWithNext=True
)

Heading3Style = ParagraphStyle(
    'SectionHeading3',
    parent=styles['Normal'],
    fontName='Helvetica-Bold',
    fontSize=9.5,
    leading=13,
    textColor=SECONDARY,
    spaceBefore=8,
    spaceAfter=3,
    keepWithNext=True
)

BodyStyle = ParagraphStyle(
    'DocBody',
    parent=styles['Normal'],
    fontName='Helvetica',
    fontSize=8.5,
    leading=12.5,
    textColor=TEXT_BODY,
    spaceAfter=6
)

BodyBold = ParagraphStyle(
    'DocBodyBold',
    parent=styles['Normal'],
    fontName='Helvetica-Bold',
    fontSize=8.5,
    leading=12.5,
    textColor=TEXT_DARK,
    spaceAfter=6
)

BulletStyle = ParagraphStyle(
    'DocBullet',
    parent=styles['Normal'],
    fontName='Helvetica',
    fontSize=8.5,
    leading=12,
    textColor=TEXT_BODY,
    leftIndent=12,
    firstLineIndent=-8,
    spaceAfter=3
)

CodeTextStyle = ParagraphStyle(
    'DocCode',
    parent=styles['Normal'],
    fontName='Courier',
    fontSize=7.2,
    leading=9.5,
    textColor=HexColor("#0f172a"),
    spaceAfter=0
)

TableHeaderStyle = ParagraphStyle(
    'TableHeader',
    parent=styles['Normal'],
    fontName='Helvetica-Bold',
    fontSize=7.5,
    leading=9.5,
    textColor=HexColor("#ffffff"),
    alignment=0
)

TableCellStyle = ParagraphStyle(
    'TableCell',
    parent=styles['Normal'],
    fontName='Helvetica',
    fontSize=7.2,
    leading=9.5,
    textColor=TEXT_BODY
)

TableCellBold = ParagraphStyle(
    'TableCellB',
    parent=styles['Normal'],
    fontName='Helvetica-Bold',
    fontSize=7.2,
    leading=9.5,
    textColor=TEXT_DARK
)

TableCellCode = ParagraphStyle(
    'TableCellC',
    parent=styles['Normal'],
    fontName='Courier',
    fontSize=6.8,
    leading=8.5,
    textColor=ACCENT_BLUE
)

# --- Helper Builder Functions ---

def create_callout(text, title="NOTE / ARCHITECTURAL VERIFICATION", color=ACCENT_BLUE):
    content = [
        Paragraph(f"<b>{title}</b>", ParagraphStyle('CalloutT', fontName='Helvetica-Bold', fontSize=8, leading=10, textColor=color)),
        Spacer(1, 2),
        Paragraph(text, ParagraphStyle('CalloutB', fontName='Helvetica', fontSize=7.8, leading=11, textColor=TEXT_BODY))
    ]
    t = Table([[content]], colWidths=[536])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), BG_PANEL),
        ('BOX', (0,0), (-1,-1), 0.5, BORDER_COLOR),
        ('LINELEFT', (0,0), (-1,-1), 3.5, color),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
    ]))
    return t

def create_code_block(code_str, caption=None):
    flowables = []
    if caption:
        flowables.append(Paragraph(f"<b>Snippet:</b> {caption}", ParagraphStyle('CodeCap', fontName='Helvetica-Bold', fontSize=7.5, leading=9.5, textColor=TEXT_MUTED, spaceAfter=2)))
    
    # Escape xml entities
    escaped_code = code_str.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    p = Paragraph(f"<font face='Courier' color='#0f172a'>{escaped_code}</font>", CodeTextStyle)
    
    t = Table([[p]], colWidths=[536])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), HexColor("#f8fafc")),
        ('BOX', (0,0), (-1,-1), 0.75, HexColor("#cbd5e1")),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
    ]))
    flowables.append(t)
    flowables.append(Spacer(1, 4))
    return KeepTogether(flowables)

def create_table(headers, rows, col_widths=None, custom_header_bg=PRIMARY):
    table_data = []
    
    header_row = [Paragraph(f"<b>{h}</b>", TableHeaderStyle) for h in headers]
    table_data.append(header_row)
    
    for r in rows:
        row_cells = []
        for cell in r:
            if isinstance(cell, Paragraph):
                row_cells.append(cell)
            elif isinstance(cell, str) and (cell.startswith("code:") or cell.startswith("`")):
                clean = cell.replace("code:", "").strip("`")
                row_cells.append(Paragraph(clean, TableCellCode))
            else:
                row_cells.append(Paragraph(str(cell), TableCellStyle))
        table_data.append(row_cells)
        
    t = Table(table_data, colWidths=col_widths)
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), custom_header_bg),
        ('TEXTCOLOR', (0, 0), (-1, 0), HexColor("#ffffff")),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('GRID', (0, 0), (-1, -1), 0.4, HexColor("#e2e8f0")),
        ('TOPPADDING', (0, 0), (-1, -1), 3.5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3.5),
        ('LEFTPADDING', (0, 0), (-1, -1), 4.5),
        ('RIGHTPADDING', (0, 0), (-1, -1), 4.5),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [HexColor("#ffffff"), HexColor("#f8fafc")]),
    ]))
    return t

def create_diagram(img_filename, caption, width=520, height=270):
    flowables = []
    path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "doc_assets", img_filename)
    if os.path.exists(path):
        img = Image(path, width=width, height=height)
        flowables.append(img)
        flowables.append(Spacer(1, 3))
        cap_p = Paragraph(f"<b>Figure:</b> {caption}", ParagraphStyle('FigCap', fontName='Helvetica-Oblique', fontSize=7.5, leading=9.5, textColor=TEXT_MUTED, alignment=1))
        flowables.append(cap_p)
        flowables.append(Spacer(1, 8))
    else:
        flowables.append(Paragraph(f"[Diagram not found: {img_filename}]", BodyStyle))
    return KeepTogether(flowables)

def create_qa(q_num, category, question, answer):
    content = [
        Paragraph(f"<b>Q{q_num} [{category}]: {question}</b>", ParagraphStyle('QTitle', fontName='Helvetica-Bold', fontSize=8.5, leading=11.5, textColor=PRIMARY)),
        Spacer(1, 2),
        Paragraph(f"<b>Technically Rigorous Answer:</b> {answer}", ParagraphStyle('QAns', fontName='Helvetica', fontSize=8, leading=11, textColor=TEXT_BODY))
    ]
    t = Table([[content]], colWidths=[536])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), HexColor("#ffffff")),
        ('BOX', (0,0), (-1,-1), 0.5, HexColor("#cbd5e1")),
        ('LINELEFT', (0,0), (-1,-1), 3, ACCENT_BLUE),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING', (0,0), (-1,-1), 7),
        ('RIGHTPADDING', (0,0), (-1,-1), 7),
    ]))
    return KeepTogether([t, Spacer(1, 4)])
