from fpdf import FPDF
import os
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
import numpy as np
import subprocess
import tempfile
from pathlib import Path

def draw_highlights_on_image(image, features, text_similarities=None, handwriting_similarities=None):
    """Draw highlights on detected regions with similarity indicators"""
    # Convert to RGBA if not already
    image = image.convert('RGBA')
    # Create a transparent overlay
    overlay = Image.new('RGBA', image.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    
    # Different colors for different types of highlights
    detection_color = (255, 255, 0, 128)    # Yellow for detected regions
    text_sim_color = (255, 0, 0, 255)       # Red for text similarity
    hw_sim_color = (0, 0, 255, 255)         # Blue for handwriting similarity
    
    # Create a larger font for text
    try:
        font = ImageFont.truetype("arial.ttf", 36)  # Increased from 24 to 36
    except:
        font = ImageFont.load_default()
    
    # First, draw detection regions
    for feature in features:
        if 'boundingBox' in feature:
            box = feature['boundingBox']
            draw.rectangle(
                [box['left'], box['top'], box['left'] + box['width'], box['top'] + box['height']],
                outline=detection_color,
                width=2
            )
    
    # Create a mapping of bounding boxes to their similarities
    similarity_map = {}
    
    # Add text similarities to the map
    if text_similarities:
        for sim in text_similarities:
            if sim['score'] >= 0.90 and 'boundingBox' in sim:
                box_key = str(sim['boundingBox'])
                if box_key not in similarity_map:
                    similarity_map[box_key] = {'box': sim['boundingBox']}
                similarity_map[box_key]['text_sim'] = sim['score']
    
    # Add handwriting similarities to the map
    if handwriting_similarities:
        for sim in handwriting_similarities:
            if sim['score'] >= 0.80 and 'boundingBox' in sim:
                box_key = str(sim['boundingBox'])
                if box_key not in similarity_map:
                    similarity_map[box_key] = {'box': sim['boundingBox']}
                similarity_map[box_key]['hw_sim'] = sim['score']
    
    # Draw the highlights and labels
    for box_data in similarity_map.values():
        box = box_data['box']
        has_text_sim = 'text_sim' in box_data
        has_hw_sim = 'hw_sim' in box_data
        
        # Draw rectangles for each type of similarity
        if has_text_sim:
            # Draw red rectangle for text similarity
            draw.rectangle(
                [box['left'], box['top'], box['left'] + box['width'], box['top'] + box['height']],
                outline=text_sim_color,
                width=4
            )
        
        if has_hw_sim:
            # Draw blue rectangle slightly offset for handwriting similarity
            offset = 4 if has_text_sim else 0
            draw.rectangle(
                [box['left'] + offset, box['top'] + offset, 
                 box['left'] + box['width'] + offset, box['top'] + box['height'] + offset],
                outline=hw_sim_color,
                width=4
            )
        
        # Add similarity labels with increased spacing
        y_offset = box['top'] - 45  # Increased from 30 to 45 to accommodate larger text
        label_parts = []
        
        if has_text_sim:
            label_parts.append(f"Text: {box_data['text_sim']*100:.0f}%")
        
        if has_hw_sim:
            label_parts.append(f"HW: {box_data['hw_sim']*100:.0f}%")
        
        # Draw combined label
        if label_parts:
            label = " | ".join(label_parts)
            # Add white background to text for better readability
            text_bbox = draw.textbbox((box['left'], y_offset), label, font=font)
            # Add more padding around text
            padding = 8  # Increased from 4 to 8
            padded_bbox = (
                text_bbox[0] - padding,
                text_bbox[1] - padding,
                text_bbox[2] + padding,
                text_bbox[3] + padding
            )
            draw.rectangle(padded_bbox, fill=(255, 255, 255, 240))  # Increased opacity from 230 to 240
            draw.text((box['left'], y_offset), label, font=font, fill=(0, 0, 0, 255))
    
    # Combine the original image with the overlay
    return Image.alpha_composite(image, overlay)

def format_mathematical_text(text):
    """Format text with ASCII-safe alternatives for mathematical symbols"""
    # Basic formatting for mathematical expressions
    text = text.replace('\\(', '(')
    text = text.replace('\\)', ')')
    text = text.replace('\\textbackslash', '\\')
    text = text.replace('\\newline', '\n')
    
    # Replace LaTeX symbols with ASCII alternatives
    replacements = {
        '\\rightarrow': '->',
        '\\leftarrow': '<-',
        '\\leq': '<=',
        '\\geq': '>=',
        '\\neq': '!=',
        '\\approx': '~',
        '\\cdot': '*',
        '\\alpha': 'alpha',
        '\\beta': 'beta',
        '\\gamma': 'gamma',
        '\\delta': 'delta',
        '\\epsilon': 'epsilon',
        '\\theta': 'theta',
        '\\lambda': 'lambda',
        '\\mu': 'mu',
        '\\pi': 'pi',
        '\\sigma': 'sigma',
        '\\tau': 'tau',
        '\\phi': 'phi',
        '\\omega': 'omega'
    }
    
    for latex, ascii_rep in replacements.items():
        text = text.replace(latex, ascii_rep)
    
    # Handle subscripts and superscripts with ASCII
    import re
    text = re.sub(r'_\{([^}]*)\}', r'_\1', text)  # subscripts
    text = re.sub(r'\^\{([^}]*)\}', r'^\1', text)  # superscripts
    
    return text

def write_text_sample(text, doc_num, pdf):
    """Write text sample with basic formatting"""
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(pdf.w - pdf.l_margin - pdf.r_margin, 8, f'Document {doc_num}:', 0, 1)
    pdf.ln(2)
    
    # Format the text
    formatted_text = format_mathematical_text(text[:1000])
    if len(text) > 1000:
        formatted_text += '...'
    
    # Split into paragraphs
    paragraphs = formatted_text.split('\n\n')
    
    # Write paragraphs with proper formatting
    pdf.set_font('Arial', '', 10)
    for paragraph in paragraphs:
        if paragraph.strip():
            pdf.multi_cell(pdf.w - pdf.l_margin - pdf.r_margin, 5, paragraph.strip())
            pdf.ln(3)
    
    pdf.ln(5)

def write_document_analysis(pdf, images, features, doc_num, text_similarities=None, handwriting_similarities=None):
    """Write document analysis with images and detected regions on the same page"""
    temp_files = []
    try:
        for i, (image, page_features) in enumerate(zip(images, features)):
            pdf.add_page()
            pdf.set_font('Arial', 'B', 14)
            pdf.cell(pdf.w - pdf.l_margin - pdf.r_margin, 10, f'Document {doc_num} - Page {i+1} Analysis:', 0, 1)
            pdf.ln(5)
            
            # Get similarities for this page
            page_text_sims = text_similarities[i] if text_similarities else None
            page_hw_sims = handwriting_similarities[i] if handwriting_similarities else None
            
            # Draw highlights on the image
            highlighted_image = draw_highlights_on_image(
                image,
                page_features,
                page_text_sims,
                page_hw_sims
            )
            
            # Save and add the image
            temp_image_path = os.path.join(tempfile.gettempdir(), f'temp_highlighted_{i}.png')
            temp_files.append(temp_image_path)
            highlighted_image.save(temp_image_path)
            
            # Calculate image dimensions to fit on page
            img_width = pdf.w - pdf.l_margin - pdf.r_margin
            img_height = img_width * (highlighted_image.height / highlighted_image.width)
            
            # Add image
            pdf.image(temp_image_path, x=pdf.l_margin, w=img_width)
    finally:
        # Clean up temp files
        for temp_file in temp_files:
            try:
                if os.path.exists(temp_file):
                    os.remove(temp_file)
            except Exception as e:
                print(f"Warning: Could not remove temporary file {temp_file}: {str(e)}")

def generate_report(text_similarity, handwriting_similarity, similarity_index, text1, text2, 
                   feature_scores=None, anomalies1=None, anomalies2=None, variations1=None, variations2=None,
                   images1=None, images2=None, features1=None, features2=None,
                   text_similarities=None, handwriting_similarities=None):
    """
    Generate a PDF report with similarity analysis results
    """
    try:
        # Create PDF with proper encoding
        pdf = FPDF()
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.add_page()
        
        # Set margins
        pdf.set_margins(15, 15, 15)
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
        pdf.ln(5)
        
        # Add explanation of similarity scores
        pdf.set_font('Arial', 'B', 12)
        pdf.cell(effective_width, 10, 'Understanding the Scores:', 0, 1)
        pdf.ln(3)
        
        pdf.set_font('Arial', '', 10)
        explanations = [
            "Text Similarity: Measures how closely the actual content matches between documents. This includes:",
            "* Word choice and phrasing",
            "* Sentence structure",
            "* Mathematical notation and symbols",
            "* Overall text organization",
            "",
            "Handwriting Similarity: Analyzes writing style characteristics including:",
            "* Character formation and consistency",
            "* Spacing between words and lines",
            "* Writing pressure and stroke patterns",
            "* Overall writing style consistency",
            "",
            "Overall Similarity Index: A weighted combination that considers both text and handwriting patterns.",
            "",
            "Score Interpretation:",
            "* 90-100%: Nearly identical",
            "* 70-89%: Very similar, likely related",
            "* 50-69%: Moderately similar, may share common elements",
            "* 30-49%: Some similarities, but largely different",
            "* 0-29%: Minimal similarity"
        ]
        
        for explanation in explanations:
            pdf.multi_cell(effective_width, 5, explanation)
        pdf.ln(10)
        
        # Add handwriting feature scores
        if feature_scores:
            pdf.set_font('Arial', 'B', 14)
            pdf.cell(effective_width, 10, 'Handwriting Feature Scores:', 0, 1)
            pdf.ln(5)
            
            # Add explanation of feature scores
            pdf.set_font('Arial', '', 10)
            pdf.multi_cell(effective_width, 5, "Feature scores measure specific aspects of handwriting similarity:")
            pdf.ln(3)
            
            feature_explanations = {
                'confidence': "Measures the consistency and clarity of handwriting strokes between documents",
                'symbol_density': "Compares the spacing and distribution of characters and symbols",
                'line_break': "Analyzes the pattern and consistency of line breaks and paragraph formatting",
                'average_confidence': "Overall measure of handwriting consistency across all features"
            }
            
            # Write scores with explanations
            pdf.set_font('Arial', '', 12)
            for key, value in feature_scores.items():
                formatted_key = key.replace('_', ' ').title()
                pdf.multi_cell(effective_width, 8, f'{formatted_key}: {value:.2%}', 0)
                # Add explanation in smaller font
                pdf.set_font('Arial', 'I', 10)  # Italic for explanation
                pdf.multi_cell(effective_width, 5, f"({feature_explanations.get(key.lower(), '')})")
                pdf.set_font('Arial', '', 12)  # Reset font
                pdf.ln(3)
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
            write_document_analysis(pdf, images1, features1, 1, text_similarities, handwriting_similarities)

        # Repeat for second document
        if images2 and features2:
            write_document_analysis(pdf, images2, features2, 2)

        # Add extracted text samples
        pdf.add_page()
        pdf.set_font('Arial', 'B', 14)
        pdf.cell(effective_width, 10, 'Extracted Text Samples:', 0, 1)
        pdf.ln(5)
        
        write_text_sample(text1, 1, pdf)
        write_text_sample(text2, 2, pdf)
        
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