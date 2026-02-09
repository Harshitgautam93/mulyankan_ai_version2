from fpdf import FPDF
import io

class PDFReport(FPDF):
    def __init__(self, roll_number=None):
        super().__init__()
        self.set_margins(12, 15, 12)
        self.set_auto_page_break(auto=True, margin=15)
        self.roll_number = roll_number
    
    def header(self):
        # Title with roll number
        self.set_font('Arial', 'B', 16)
        self.set_text_color(78, 137, 174)
        self.cell(0, 10, 'Mulyankan AI - Evaluation Report', 0, 1, 'C')
        
        # Roll number line
        if self.roll_number:
            self.set_font('Arial', '', 11)
            self.set_text_color(100, 100, 100)
            self.cell(0, 8, f'Student ID: {self.roll_number}', 0, 1, 'C')
        self.ln(3)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.set_text_color(150, 150, 150)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')
    
    def section_header(self, title):
        self.set_font('Arial', 'B', 12)
        self.set_text_color(78, 137, 174)
        self.multi_cell(0, 7, title, align='L')
        self.set_text_color(0, 0, 0)
        
        # Blue line under header
        current_y = self.get_y()
        self.set_draw_color(78, 137, 174)
        self.set_line_width(0.5)
        self.line(12, current_y - 1, self.w - 12, current_y - 1)
        self.ln(0.5)
    
    def subsection_header(self, title):
        self.set_font('Arial', 'B', 10)
        self.set_text_color(50, 50, 50)
        self.multi_cell(0, 6, f"• {title}", align='L')
        self.ln(0.3)

def generate_pdf_bytes(question, student_ans, evaluation_dict, roll_number=None):
    pdf = PDFReport(roll_number=roll_number)
    pdf.add_page()
    
    eff_width = pdf.w - 2 * pdf.l_margin

    def sanitize_text(text, max_length=None):
        text = str(text) if text else ""
        chars = {
            '\u2013': '-', '\u2014': '-', '\u2019': "'", 
            '\u201d': '"', '\u201c': '"', '\u2717': 'x', 
            '\u2713': 'v', '\u2022': '*'
        }
        for k, v in chars.items():
            text = text.replace(k, v)
        text = text.encode('latin-1', 'ignore').decode('latin-1')
        if max_length and len(text) > max_length:
            text = text[:max_length] + "..."
        return text
    
    try:
        # ==================== SECTION 1: TOPIC ====================
        pdf.section_header("Assignment Topic")
        pdf.set_font("Arial", size=10)
        pdf.multi_cell(eff_width, 5, sanitize_text(question))
        pdf.ln(2)
        
        # ==================== SECTION 2: EXECUTIVE SUMMARY ====================
        pdf.section_header("Evaluation Summary")
        
        # Score and Grade boxes
        pdf.set_font('Arial', 'B', 11)
        pdf.set_text_color(78, 137, 174)
        score = sanitize_text(evaluation_dict.get('score', '0'))
        grade = sanitize_text(evaluation_dict.get('grade', 'F'))
        pdf.cell(50, 8, f"Score: {score}/10")
        pdf.cell(eff_width - 50, 8, f"Grade: {grade}", align='L')
        pdf.ln(8)
        
        # Feedback paragraph
        pdf.set_font("Arial", size=9)
        pdf.set_text_color(0, 0, 0)
        feedback = sanitize_text(evaluation_dict.get('feedback', 'No feedback.'), max_length=500)
        pdf.multi_cell(eff_width, 4, feedback)
        pdf.ln(1)
        
        # ==================== SECTION 3: RUBRIC BREAKDOWN ====================
        rubric = evaluation_dict.get('rubric_breakdown', [])
        if rubric:
            pdf.section_header("Scoring Breakdown")
            for item in rubric:
                pdf.subsection_header(sanitize_text(item.get('criteria'), max_length=80))
                pdf.set_font("Arial", 'B', 9)
                pdf.set_text_color(78, 137, 174)
                score_str = f"{item.get('score')}/{item.get('max_score')}"
                pdf.cell(eff_width, 5, f"Score: {score_str}")
                pdf.ln(5)
                pdf.set_font("Arial", size=8)
                pdf.set_text_color(0, 0, 0)
                feedback_text = sanitize_text(item.get('feedback'), max_length=250)
                pdf.multi_cell(eff_width, 4, feedback_text)
                pdf.ln(1)
        
        # ==================== SECTION 4: GAP ANALYSIS ====================
        missing = evaluation_dict.get('missing_concepts', [])
        if missing:
            pdf.section_header("Concepts Needing Improvement")
            for concept in missing:
                pdf.set_font("Arial", 'B', 9)
                pdf.set_text_color(200, 80, 80)
                name = sanitize_text(concept.get('concept'), max_length=60)
                imp = sanitize_text(concept.get('importance'), max_length=20)
                pdf.multi_cell(eff_width, 5, f"[{imp}] {name}")
                pdf.set_font("Arial", size=8)
                pdf.set_text_color(0, 0, 0)
                explanation = sanitize_text(concept.get('explanation'), max_length=200)
                pdf.multi_cell(eff_width, 4, explanation)
                pdf.ln(0.5)
        
        # ==================== SECTION 5: BRIDGE GUIDANCE ====================
        bridge = evaluation_dict.get('bridge_guidance', None)
        if bridge:
            pdf.section_header("How to Improve")
            pdf.set_font("Arial", size=9)
            bridge_text = sanitize_text(bridge, max_length=500)
            pdf.multi_cell(eff_width, 4, bridge_text)
            pdf.ln(1)
        
        # ==================== SECTION 6: RESOURCES ====================
        resources = evaluation_dict.get('suggested_resources', [])
        if resources:
            pdf.section_header("Recommended Resources")
            for i, resource in enumerate(resources[:3]):
                pdf.set_font("Arial", 'B', 9)
                pdf.set_text_color(78, 137, 174)
                title = sanitize_text(resource.get('title'), max_length=70)
                pdf.multi_cell(eff_width, 5, f"{i+1}. {title}")
                pdf.set_font("Arial", size=8)
                pdf.set_text_color(0, 0, 0)
                description = sanitize_text(resource.get('description'), max_length=150)
                pdf.multi_cell(eff_width, 4, f"   Learn: {description}")
                action = sanitize_text(resource.get('action_item'), max_length=150)
                pdf.multi_cell(eff_width, 4, f"   Action: {action}")
                pdf.ln(0.5)
        
        # ==================== SECTION 7: METADATA ====================
        metadata = evaluation_dict.get('metadata', {})
        if metadata:
            pdf.section_header("Assessment Details")
            pdf.set_font("Arial", size=8)
            complexity = sanitize_text(metadata.get('complexity_level', 'N/A'))
            confidence = sanitize_text(metadata.get('ai_confidence', 'N/A'))
            plagiarism = sanitize_text(metadata.get('plagiarism_similarity', 'N/A'))
            
            pdf.multi_cell(eff_width, 4, f"Difficulty Level: {complexity}")
            pdf.multi_cell(eff_width, 4, f"Evaluation Confidence: {confidence}%")
            pdf.multi_cell(eff_width, 4, f"Content Uniqueness: {plagiarism}%")

        # Finalize
        pdf_output = pdf.output(dest='S')
        if isinstance(pdf_output, str):
            return pdf_output.encode('latin-1')
        return bytes(pdf_output)
        
    except Exception as e:
        raise RuntimeError(f"PDF Generation Error: {str(e)}")