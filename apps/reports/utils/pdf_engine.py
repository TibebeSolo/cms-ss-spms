from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from django.conf import settings
import os

class EOTCPDFBuilder:
    # Localization Dictionary
    TEXT = {
        'am': {
            'church_name': "የኢትዮጵያ ኦርቶዶክስ ተዋሕዶ ቤተ ክርስቲያን",
            'prepared_by': "ያዘጋጀው፡ ________________",
            'verified_by': "ያረጋገጠው፡ ________________",
            'stamp': "(የሰንበት ትምህርት ቤቱ ማኅተም)",
        },
        'en': {
            'church_name': "Ethiopian Orthodox Tewahedo Church",
            'prepared_by': "Prepared by: ________________",
            'verified_by': "Verified by: ________________",
            'stamp': "(Official Stamp)",
        }
    }

    def __init__(self, buffer, lang='am'):
        self.canvas = canvas.Canvas(buffer, pagesize=A4)
        self.width, self.height = A4
        self.lang = lang if lang in ['am', 'en'] else 'am'
        self._register_fonts()

    def _register_fonts(self):
        """Registers fonts per Requirement 7.2"""
        # Paths to your font files (ensure these exist in static/fonts)
        font_dir = os.path.join(settings.BASE_DIR, 'static', 'fonts')
        
        # Register Amharic (Nyala/PowerGeez)
        try:
            pdfmetrics.registerFont(TTFont('Nyala', os.path.join(font_dir, 'nyala.ttf')))
            self.amharic_font = "Nyala"
        except:
            self.amharic_font = "Helvetica" # Fallback (won't render Ethiopic correctly)

        # Register English (Garamond/Palatino)
        self.english_font = "Helvetica-Bold" 

    def get_font(self, is_bold=False):
        if self.lang == 'am':
            return self.amharic_font
        return "Helvetica-Bold" if is_bold else "Helvetica"

    def draw_header(self, title, subtitle=""):
        """Bilingual Header with optional subtitle"""
        # Church Name
        self.canvas.setFont(self.get_font(is_bold=True), 14)
        self.canvas.drawCentredString(self.width/2, self.height - 50, self.TEXT[self.lang]['church_name'])
        
        # Report Title
        self.canvas.setFont(self.get_font(), 12)
        self.canvas.drawCentredString(self.width/2, self.height - 70, title)
        
        if subtitle:
            self.canvas.setFont(self.get_font(), 10)
            self.canvas.drawCentredString(self.width/2, self.height - 85, subtitle)
            
        self.canvas.line(50, self.height - 95, self.width - 50, self.height - 95)
        
    def draw_footer(self):
        """Standardized Footer with Signature Blocks"""
        self.canvas.line(50, 100, self.width - 50, 100)
        self.canvas.setFont(self.get_font(), 8)
        
        labels = self.TEXT[self.lang]
        self.canvas.drawString(50, 80, labels['prepared_by'])
        self.canvas.drawCentredString(self.width/2, 80, labels['verified_by'])
        self.canvas.drawRightString(self.width - 50, 80, labels['stamp'])