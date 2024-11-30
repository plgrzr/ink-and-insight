from fpdf import FPDF
import os
from datetime import datetime

def generate_report(text_similarity, handwriting_similarity, similarity_index, text1, text2):
    """
    Generate a PDF report with similarity analysis results
    """
    try:
        pdf = FPDF()
        pdf.add_page()
        
        # Add header
        pdf.set_font('Arial', 'B', 16)
        pdf.cell(0, 10, 'PDF Similarity Analysis Report', 0, 1, 'C')
        pdf.ln(10)
        
        # Add date
        pdf.set_font('Arial', '', 12)
        pdf.cell(0, 10, f'Generated on: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}', 0, 1)
        pdf.ln(10)
        
        # Add similarity scores
        pdf.set_font('Arial', 'B', 14)
        pdf.cell(0, 10, 'Similarity Scores:', 0, 1)
        pdf.ln(5)
        
        pdf.set_font('Arial', '', 12)
        pdf.cell(0, 10, f'Text Similarity: {text_similarity:.2%}', 0, 1)
        pdf.cell(0, 10, f'Handwriting Similarity: {handwriting_similarity:.2%}', 0, 1)
        pdf.cell(0, 10, f'Overall Similarity Index: {similarity_index:.2%}', 0, 1)
        pdf.ln(10)
        
        # Add extracted text samples
        pdf.set_font('Arial', 'B', 14)
        pdf.cell(0, 10, 'Extracted Text Samples:', 0, 1)
        pdf.ln(5)
        
        pdf.set_font('Arial', '', 12)
        pdf.multi_cell(0, 10, f'Document 1:\n{text1[:500]}...')
        pdf.ln(5)
        pdf.multi_cell(0, 10, f'Document 2:\n{text2[:500]}...')
        
        # Save the report
        report_dir = 'reports'
        os.makedirs(report_dir, exist_ok=True)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_path = os.path.join(report_dir, f'similarity_report_{timestamp}.pdf')
        pdf.output(report_path)
        
        return report_path
        
    except Exception as e:
        raise Exception(f"Error generating report: {str(e)}") 