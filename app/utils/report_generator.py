from fpdf import FPDF
import os
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
import tempfile
import sys
from pathlib import Path
from functools import lru_cache
from typing import List, Dict, Optional


class UTF8PDF(FPDF):
    def __init__(self):
        super().__init__()
        self.set_auto_page_break(auto=True, margin=15)
        self._setup_fonts()

    def _setup_fonts(self):
        self.windows_font_map = {
            "normal": {"font": "Arial", "style": ""},
            "bold": {"font": "Arial", "style": "B"},
            "italic": {"font": "Arial", "style": "I"},
        }
        self.add_font("DejaVu", "", "DejaVuSansCondensed.ttf", uni=True)
        self.set_font("DejaVu", "", 12)

    def set_windows_fonts(self):
        try:
            windows_font_path = os.path.join(os.environ["WINDIR"], "Fonts")
            for style, filename in [
                ("", "arial.ttf"),
                ("B", "arialbd.ttf"),
                ("I", "ariali.ttf"),
            ]:
                self.add_font(
                    "Arial", style, os.path.join(windows_font_path, filename), uni=True
                )
            self.set_font("Arial", "", 12)
            return True
        except:  # noqa: E722
            try:
                self.add_font("DejaVu", "", "DejaVuSansCondensed.ttf", uni=True)
                self.set_font("DejaVu", "", 12)
                return True
            except:  # noqa: E722
                return False

    def cell(self, w, h=0, txt="", border=0, ln=0, align="", fill=False, link=""):
        try:
            super().cell(
                w,
                h,
                txt.encode("latin-1", "ignore").decode("latin-1"),
                border,
                ln,
                align,
                fill,
                link,
            )
        except UnicodeEncodeError:
            current_font = self.font_family
            if current_font not in ["Arial", "DejaVu"]:
                self.set_font("DejaVu", "", self.font_size_pt)
            super().cell(w, h, txt, border, ln, align, fill, link)
            if current_font not in ["Arial", "DejaVu"]:
                self.set_font(current_font, self.font_style, self.font_size_pt)

    def multi_cell(self, w, h, txt="", border=0, align="J", fill=False):
        try:
            super().multi_cell(
                w,
                h,
                txt.encode("latin-1", "ignore").decode("latin-1"),
                border,
                align,
                fill,
            )
        except UnicodeEncodeError:
            current_font = self.font_family
            if current_font not in ["Arial", "DejaVu"]:
                self.set_font("DejaVu", "", self.font_size_pt)
            super().multi_cell(w, h, txt, border, align, fill)
            if current_font not in ["Arial", "DejaVu"]:
                self.set_font(current_font, self.font_style, self.font_size_pt)


@lru_cache(maxsize=1)
def get_system_font():
    try:
        if sys.platform == "win32":
            return ImageFont.truetype(
                os.path.join(os.environ["WINDIR"], "Fonts", "arial.ttf"), 36
            )
    except:  # noqa: E722
        return ImageFont.load_default()


LATEX_TO_ASCII = {
    "\\rightarrow": "->",
    "\\leftarrow": "<-",
    "\\leq": "<=",
    "\\geq": ">=",
    "\\neq": "!=",
    "\\approx": "~",
    "\\cdot": "*",
    "\\alpha": "alpha",
    "\\beta": "beta",
    "\\gamma": "gamma",
    "\\delta": "delta",
    "\\epsilon": "epsilon",
    "\\theta": "theta",
    "\\lambda": "lambda",
    "\\mu": "mu",
    "\\pi": "pi",
    "\\sigma": "sigma",
    "\\tau": "tau",
    "\\phi": "phi",
    "\\omega": "omega",
}


def format_mathematical_text(text: str) -> str:
    if not isinstance(text, str):
        return str(text)
    text = (
        text.replace("\\(", "(")
        .replace("\\)", ")")
        .replace("\\textbackslash", "\\")
        .replace("\\newline", "\n")
    )
    for latex, ascii_rep in LATEX_TO_ASCII.items():
        text = text.replace(latex, ascii_rep)
    import re

    text = re.sub(r"_\{([^}]*)\}", r"_\1", text)
    text = re.sub(r"\^\{([^}]*)\}", r"^\1", text)
    return text


def safe_box_coordinates(box: Dict) -> Optional[Dict]:
    if not box or not all(k in box for k in ["left", "top", "width", "height"]):
        return None
    try:
        return {k: float(box[k]) for k in ["left", "top", "width", "height"]}
    except:  # noqa: E722
        return None


def draw_highlights_on_image(
    image: Image,
    features: List,
    text_similarities: Optional[List] = None,
    handwriting_similarities: Optional[List] = None,
) -> Image:
    if not image:
        raise ValueError("No image provided")

    image = image.convert("RGBA")
    overlay = Image.new("RGBA", image.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    font = get_system_font()

    similarity_map = {}

    if features:
        for feature in features:
            box = safe_box_coordinates(feature.get("boundingBox"))
            if box:
                draw.rectangle(
                    [
                        box["left"],
                        box["top"],
                        box["left"] + box["width"],
                        box["top"] + box["height"],
                    ],
                    outline=(255, 255, 0, 128),
                    width=2,
                )

    if text_similarities:
        similarity_map.update(
            {
                str(safe_box_coordinates(sim.get("boundingBox"))): {
                    "box": safe_box_coordinates(sim.get("boundingBox")),
                    "text_sim": sim["score"],
                }
                for sim in text_similarities
                if isinstance(sim, dict)
                and sim.get("score", 0) >= 0.90
                and safe_box_coordinates(sim.get("boundingBox"))
            }
        )

    if handwriting_similarities:
        for sim in handwriting_similarities:
            if isinstance(sim, dict) and sim.get("score", 0) >= 0.80:
                box = safe_box_coordinates(sim.get("boundingBox"))
                if box:
                    box_key = str(box)
                    if box_key in similarity_map:
                        similarity_map[box_key]["hw_sim"] = sim["score"]
                    else:
                        similarity_map[box_key] = {"box": box, "hw_sim": sim["score"]}

    for box_data in similarity_map.values():
        box = box_data["box"]
        if not box:
            continue

        try:
            if "text_sim" in box_data:
                draw.rectangle(
                    [
                        box["left"],
                        box["top"],
                        box["left"] + box["width"],
                        box["top"] + box["height"],
                    ],
                    outline=(255, 0, 0, 255),
                    width=4,
                )

            if "hw_sim" in box_data:
                offset = 4 if "text_sim" in box_data else 0
                draw.rectangle(
                    [
                        box["left"] + offset,
                        box["top"] + offset,
                        box["left"] + box["width"] + offset,
                        box["top"] + box["height"] + offset,
                    ],
                    outline=(0, 0, 255, 255),
                    width=4,
                )

            y_offset = max(0, box["top"] - 45)
            label_parts = []
            if "text_sim" in box_data:
                label_parts.append(f"Text: {box_data['text_sim']*100:.0f}%")
            if "hw_sim" in box_data:
                label_parts.append(f"HW: {box_data['hw_sim']*100:.0f}%")

            if label_parts:
                label = " | ".join(label_parts)
                text_bbox = draw.textbbox((box["left"], y_offset), label, font=font)
                draw.rectangle(
                    (
                        text_bbox[0] - 8,
                        text_bbox[1] - 8,
                        text_bbox[2] + 8,
                        text_bbox[3] + 8,
                    ),
                    fill=(255, 255, 255, 240),
                )
                draw.text(
                    (box["left"], y_offset), label, font=font, fill=(0, 0, 0, 255)
                )

        except:  # noqa: E722
            continue

    return Image.alpha_composite(image, overlay)


def write_text_sample(text: str, doc_num: int, pdf: UTF8PDF):
    pdf.set_font("Arial", "B", 12)
    pdf.cell(pdf.w - pdf.l_margin - pdf.r_margin, 8, f"Document {doc_num}:", 0, 1)
    pdf.ln(2)
    formatted_text = format_mathematical_text(text[:1000]) + (
        "..." if len(text) > 1000 else ""
    )
    pdf.set_font("Arial", "", 10)
    for paragraph in formatted_text.split("\n\n"):
        if paragraph.strip():
            pdf.multi_cell(pdf.w - pdf.l_margin - pdf.r_margin, 5, paragraph.strip())
            pdf.ln(3)
    pdf.ln(5)


def write_document_analysis(
    pdf: UTF8PDF,
    images: List[Image.Image],
    features: List,
    doc_num: int,
    text_similarities: Optional[List] = None,
    handwriting_similarities: Optional[List] = None,
):
    temp_dir = Path(tempfile.gettempdir())
    temp_files = []

    try:
        for i, (image, page_features) in enumerate(zip(images, features)):
            pdf.add_page()
            pdf.set_font("Arial", "B", 14)
            pdf.cell(
                pdf.w - pdf.l_margin - pdf.r_margin,
                10,
                f"Document {doc_num} - Page {i+1} Analysis:",
                0,
                1,
            )
            pdf.ln(5)

            highlighted_image = draw_highlights_on_image(
                image,
                page_features,
                text_similarities[i] if text_similarities else None,
                handwriting_similarities[i] if handwriting_similarities else None,
            )

            temp_path = (
                temp_dir / f"temp_highlighted_{datetime.now().timestamp()}_{i}.png"
            )
            highlighted_image.save(temp_path)
            temp_files.append(temp_path)

            img_width = pdf.w - pdf.l_margin - pdf.r_margin
            pdf.image(str(temp_path), x=pdf.l_margin, w=img_width)

    finally:
        for temp_file in temp_files:
            try:
                temp_file.unlink()
            except:  # noqa: E722
                pass


def generate_report(
    text_similarity: float,
    handwriting_similarity: float,
    similarity_index: float,
    text1: str,
    text2: str,
    feature_scores: Optional[Dict] = None,
    anomalies1: Optional[List] = None,
    anomalies2: Optional[List] = None,
    variations1: Optional[List] = None,
    variations2: Optional[List] = None,
    images1: Optional[List] = None,
    images2: Optional[List] = None,
    features1: Optional[List] = None,
    features2: Optional[List] = None,
    text_similarities: Optional[List] = None,
    handwriting_similarities: Optional[List] = None,
) -> str:
    try:
        pdf = UTF8PDF()
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.add_page()
        pdf.set_windows_fonts()
        pdf.set_margins(15, 15, 15)
        effective_width = pdf.w - pdf.l_margin - pdf.r_margin

        pdf.set_font("Arial", "B", 16)
        pdf.cell(effective_width, 10, "PDF Similarity Analysis Report", 0, 1, "C")
        pdf.ln(10)

        pdf.set_font("Arial", "", 12)
        pdf.cell(
            effective_width,
            10,
            f'Generated on: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}',
            0,
            1,
        )
        pdf.ln(10)

        pdf.set_font("Arial", "B", 14)
        pdf.cell(effective_width, 10, "Similarity Scores:", 0, 1)
        pdf.ln(5)

        pdf.set_font("Arial", "", 12)
        pdf.cell(effective_width, 10, f"Text Similarity: {text_similarity:.2%}", 0, 1)
        pdf.cell(
            effective_width,
            10,
            f"Handwriting Similarity: {handwriting_similarity:.2%}",
            0,
            1,
        )
        pdf.cell(
            effective_width,
            10,
            f"Overall Similarity Index: {similarity_index:.2%}",
            0,
            1,
        )
        pdf.ln(5)

        if feature_scores:
            pdf.set_font("Arial", "B", 14)
            pdf.cell(effective_width, 10, "Handwriting Feature Scores:", 0, 1)
            pdf.ln(5)

            pdf.set_font("Arial", "", 12)
            for key, value in feature_scores.items():
                formatted_key = key.replace("_", " ").title()
                pdf.multi_cell(effective_width, 8, f"{formatted_key}: {value:.2%}")
                pdf.ln(3)
            pdf.ln(10)

        if images1 and features1:
            write_document_analysis(
                pdf, images1, features1, 1, text_similarities, handwriting_similarities
            )

        if images2 and features2:
            write_document_analysis(pdf, images2, features2, 2)

        pdf.add_page()
        pdf.set_font("Arial", "B", 14)
        pdf.cell(effective_width, 10, "Extracted Text Samples:", 0, 1)
        pdf.ln(5)

        write_text_sample(text1, 1, pdf)
        write_text_sample(text2, 2, pdf)

        report_dir = "reports"
        os.makedirs(report_dir, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_path = os.path.join(report_dir, f"similarity_report_{timestamp}.pdf")
        pdf.output(report_path, "F")
        return str(report_path)

    except Exception as e:
        raise Exception(f"Error generating report: {str(e)}")
