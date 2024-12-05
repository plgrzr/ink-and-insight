from fpdf import FPDF
import os
from datetime import datetime
from PIL import Image, ImageDraw
import numpy as np

def draw_highlights_on_image(image, features, color=(255, 255, 0, 128)):
    """Draw semi-transparent highlights on detected regions"""
    # Convert to RGBA if not already
    image = image.convert('RGBA')
    # Create a transparent overlay
    overlay = Image.new('RGBA', image.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    
    for feature in features:
        if 'boundingBox' in feature:
            box = feature['boundingBox']
            draw.rectangle(
                [box['left'], box['top'], box['left'] + box['width'], box['top'] + box['height']],
                fill=color
            )
    
    # Combine the original image with the overlay
    return Image.alpha_composite(image, overlay)

def generate_report(text_similarity, handwriting_similarity, similarity_index, text1, text2, 
                   feature_scores=None, anomalies1=None, anomalies2=None, variations1=None, variations2=None,
                   images1=None, images2=None, features1=None, features2=None):
    """
    Generate a PDF report with similarity analysis results
    """
    try:
        pdf = FPDF()
        # Set page margins (left, top, right) in mm
        pdf.set_margins(15, 15, 15)
        pdf.add_page()
        
        # Get effective page width (accounting for margins)
        effective_width = pdf.w - pdf.l_margin - pdf.r_margin
        
        # Add header
        pdf.set_font('Arial', 'B', 16)
        pdf.cell(effective_width, 10, 'PDF Similarity Analysis Report', 0, 1, 'C')
        pdf.ln(10)
        
        # Add date
        pdf.set_font('Arial', '', 12)
        pdf.cell(effective_width, 10, f'Generated on: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}', 0, 1)
        pdf.ln(10)
        
        # Add similarity scores
        pdf.set_font('Arial', 'B', 14)
        pdf.cell(effective_width, 10, 'Similarity Scores:', 0, 1)
        pdf.ln(5)
        
        pdf.set_font('Arial', '', 12)
        pdf.cell(effective_width, 10, f'Text Similarity: {text_similarity:.2%}', 0, 1)
        pdf.cell(effective_width, 10, f'Handwriting Similarity: {handwriting_similarity:.2%}', 0, 1)
        pdf.cell(effective_width, 10, f'Overall Similarity Index: {similarity_index:.2%}', 0, 1)
        pdf.ln(10)
        
        # Add handwriting feature scores
        if feature_scores:
            pdf.set_font('Arial', 'B', 14)
            pdf.cell(effective_width, 10, 'Handwriting Feature Scores:', 0, 1)
            pdf.ln(5)
            
            pdf.set_font('Arial', '', 12)
            for key, value in feature_scores.items():
                # Format key for better readability
                formatted_key = key.replace('_', ' ').title()
                pdf.multi_cell(effective_width, 8, f'{formatted_key}: {value:.2%}', 0)
            pdf.ln(10)
        
        # Add anomaly analysis section
        if anomalies1 or anomalies2:
            pdf.add_page()
            pdf.set_font('Arial', 'B', 14)
            pdf.cell(effective_width, 10, 'Handwriting Anomaly Analysis:', 0, 1)
            pdf.ln(5)
            
            def write_anomalies(anomalies, doc_num):
                pdf.set_font('Arial', 'B', 12)
                pdf.cell(effective_width, 8, f'Document {doc_num} Anomalies:', 0, 1)
                if anomalies:
                    pdf.set_font('Arial', '', 10)
                    for anomaly in anomalies:
                        pdf.multi_cell(effective_width, 5, f"Paragraph {anomaly['paragraph_index'] + 1}:", 0)
                        if 'confidence' in anomaly:
                            pdf.multi_cell(effective_width, 5, 
                                f"- Unusual confidence level: {anomaly['confidence']['value']:.2f} " +
                                f"(Deviation: {anomaly['confidence']['deviation']:.2f} SD)")
                        if 'symbol_density' in anomaly:
                            pdf.multi_cell(effective_width, 5,
                                f"- Unusual symbol density: {anomaly['symbol_density']['value']:.2f} " +
                                f"(Deviation: {anomaly['symbol_density']['deviation']:.2f} SD)")
                        if 'line_breaks' in anomaly:
                            pdf.multi_cell(effective_width, 5,
                                f"- Unusual line spacing: {anomaly['line_breaks']['value']:.2f} " +
                                f"(Deviation: {anomaly['line_breaks']['deviation']:.2f} SD)")
                        pdf.ln(3)
                else:
                    pdf.set_font('Arial', '', 10)
                    pdf.multi_cell(effective_width, 5, "No significant anomalies detected")
                pdf.ln(5)
            
            write_anomalies(anomalies1, 1)
            write_anomalies(anomalies2, 2)
        
        # Add page variation analysis section
        if variations1 or variations2:
            pdf.add_page()
            pdf.set_font('Arial', 'B', 14)
            pdf.cell(effective_width, 10, 'Page-to-Page Handwriting Variations:', 0, 1)
            pdf.ln(5)
            
            def write_variations(variations, doc_num):
                pdf.set_font('Arial', 'B', 12)
                pdf.cell(effective_width, 8, f'Document {doc_num} Variations:', 0, 1)
                if variations:
                    pdf.set_font('Arial', '', 10)
                    for variation in variations:
                        pdf.multi_cell(effective_width, 5, 
                            f"Changes between pages {variation['from_page']} and {variation['to_page']}:", 0)
                        for change in variation['changes']:
                            pdf.multi_cell(effective_width, 5, f"- {change['description']}")
                        pdf.ln(3)
                else:
                    pdf.set_font('Arial', '', 10)
                    pdf.multi_cell(effective_width, 5, "No significant page-to-page variations detected")
                pdf.ln(5)
            
            write_variations(variations1, 1)
            write_variations(variations2, 2)
        
        # Add highlighted page images if available
        if images1 and features1:
            pdf.add_page()
            pdf.set_font('Arial', 'B', 14)
            pdf.cell(effective_width, 10, 'Document 1 - Detected Regions:', 0, 1)
            pdf.ln(5)

            for i, (image, page_features) in enumerate(zip(images1, features1)):
                # Draw highlights on the image
                highlighted_image = draw_highlights_on_image(image, page_features)
                
                # Save temporary image
                temp_image_path = f'temp_highlighted_{i}.png'
                highlighted_image.save(temp_image_path)
                
                # Add to PDF
                pdf.image(temp_image_path, x=15, w=180)
                pdf.ln(5)
                
                # Clean up temporary file
                os.remove(temp_image_path)

        # Repeat for second document
        if images2 and features2:
            pdf.add_page()
            pdf.set_font('Arial', 'B', 14)
            pdf.cell(effective_width, 10, 'Document 2 - Detected Regions:', 0, 1)
            pdf.ln(5)

            for i, (image, page_features) in enumerate(zip(images2, features2)):
                highlighted_image = draw_highlights_on_image(image, page_features)
                temp_image_path = f'temp_highlighted_{i}.png'
                highlighted_image.save(temp_image_path)
                pdf.image(temp_image_path, x=15, w=180)
                pdf.ln(5)
                os.remove(temp_image_path)

        # Add extracted text samples
        pdf.add_page()
        pdf.set_font('Arial', 'B', 14)
        pdf.cell(effective_width, 10, 'Extracted Text Samples:', 0, 1)
        pdf.ln(5)
        
        def write_text_sample(text, doc_num):
            pdf.set_font('Arial', 'B', 12)
            pdf.cell(effective_width, 8, f'Document {doc_num}:', 0, 1)
            pdf.set_font('Arial', '', 10)
            # Split text into smaller chunks and add ellipsis if needed
            text_preview = text[:1000] + ('...' if len(text) > 1000 else '')
            pdf.multi_cell(effective_width, 5, text_preview)
            pdf.ln(5)
        
        write_text_sample(text1, 1)
        write_text_sample(text2, 2)
        
        # Save the report
        report_dir = 'reports'
        os.makedirs(report_dir, exist_ok=True)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_path = os.path.join(report_dir, f'similarity_report_{timestamp}.pdf')
        pdf.output(report_path)
        
        return report_path
        
    except Exception as e:
        print(f"Detailed error in report generation: {str(e)}")
        raise Exception(f"Error generating report: {str(e)}")