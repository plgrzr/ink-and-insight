from flask import Blueprint, render_template, request, jsonify, current_app
import os
import uuid
from app.similarity.text_similarity import compute_text_similarity
from app.similarity.handwriting_similarity import compute_handwriting_similarity
from app.utils.pdf_processor import extract_text_from_pdf, validate_pdf
from app.utils.report_generator import generate_report
from flask import (
    send_from_directory,
)
from werkzeug.exceptions import NotFound

main = Blueprint("main", __name__)

ALLOWED_EXTENSIONS = {"pdf"}


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def generate_secure_filename(original_filename):
    """Generate a secure random filename while preserving extension"""
    ext = (
        original_filename.rsplit(".", 1)[1].lower() if "." in original_filename else ""
    )
    return f"{uuid.uuid4().hex}.{ext}"


@main.route("/")
def index():
    return render_template("index.html")


# @main.route("/report/<report_id>")
# def report(report_id):
#     report = Report.query.get(report_id)
#     if not report:
#         return jsonify({"error": "Report not found"}), 404
#     # Return File from Reports Directory
#     return send_from_directory, report.filename)


@main.route("/compare", methods=["POST"])
def compare_pdfs():
    print("API Key present:", bool(os.environ.get("GOOGLE_CLOUD_API_KEY")))

    if "file1" not in request.files or "file2" not in request.files:
        return jsonify({"error": "Two PDF files are required"}), 400

    file1 = request.files["file1"]
    file2 = request.files["file2"]

    print(f"Received files: {file1.filename} and {file2.filename}")

    if not all(allowed_file(f.filename) for f in [file1, file2]):
        return jsonify(
            {"error": "Invalid file format. Only PDF files are allowed"}
        ), 400

    try:
        if not os.path.exists(current_app.config["UPLOAD_FOLDER"]):
            os.makedirs(current_app.config["UPLOAD_FOLDER"])

        # Generate random filenames
        filename1 = generate_secure_filename(file1.filename)
        filename2 = generate_secure_filename(file2.filename)

        filepath1 = os.path.join(current_app.config["UPLOAD_FOLDER"], filename1)
        filepath2 = os.path.join(current_app.config["UPLOAD_FOLDER"], filename2)

        file1.save(filepath1)
        file2.save(filepath2)
        print(f"Files saved to {filepath1} and {filepath2}")

        if not os.path.exists(filepath1) or not os.path.exists(filepath2):
            return jsonify({"error": "Error saving files"}), 500

        if os.path.getsize(filepath1) == 0 or os.path.getsize(filepath2) == 0:
            return jsonify({"error": "One or both files are empty"}), 400

        if not validate_pdf(filepath1) or not validate_pdf(filepath2):
            return jsonify({"error": "Invalid or corrupted PDF file(s)"}), 400

        text1 = extract_text_from_pdf(filepath1)
        text2 = extract_text_from_pdf(filepath2)

        if not text1 or not text2:
            return jsonify(
                {"error": "Could not extract text from one or both files"}
            ), 400

        text_analysis = compute_text_similarity(text1, text2)
        text_similarity = text_analysis["similarity_score"]
        (
            handwriting_similarity,
            feature_scores,
            anomalies1,
            anomalies2,
            variations1,
            variations2,
            images1,
            images2,
            features1,
            features2,
            text_similarities,
            handwriting_similarities,
        ) = compute_handwriting_similarity(filepath1, filepath2)

        weight_text = float(request.form.get("weight_text", 0.5))
        weight_handwriting = 1 - weight_text

        similarity_index = (
            weight_text * text_similarity + weight_handwriting * handwriting_similarity
        )

        report_path = generate_report(
            text_similarity,
            handwriting_similarity,
            similarity_index,
            text1,
            text2,
            feature_scores,
            anomalies1,
            anomalies2,
            variations1,
            variations2,
            images1,
            images2,
            features1,
            features2,
            text_similarities,
            handwriting_similarities,
        )
        print("Request Completed")
        return jsonify(
            {
                "text_similarity": text_similarity,
                "text_consistency": text_analysis["consistency_analysis"],
                "handwriting_similarity": handwriting_similarity,
                "similarity_index": similarity_index,
                "feature_scores": feature_scores,
                "anomalies": {"document1": anomalies1, "document2": anomalies2},
                "variations": {"document1": variations1, "document2": variations2},
                "report_url": report_path,
            }
        )

    except Exception as e:
        print(f"Error in compare_pdfs: {str(e)}")
        return jsonify({"error": str(e)}), 500
    finally:
        for filepath in [filepath1, filepath2]:
            try:
                if os.path.exists(filepath):
                    os.remove(filepath)
            except Exception as e:
                print(f"Error removing file {filepath}: {str(e)}")


@main.route("/reports/<report_id>")
def report(report_id):
    # hardcoded for now
    report_filename = f"{report_id}"
    reports_dir = "/Users/suryavirkapur/Projekts/ink-and-insight/reports"

    try:
        os.makedirs(reports_dir, exist_ok=True)

        if not os.path.isfile(os.path.join(reports_dir, report_filename)):
            return jsonify(
                {"error": "Report not found", "filename": report_filename}
            ), 404

        return send_from_directory(
            reports_dir, report_filename, as_attachment=True, mimetype="application/pdf"
        )

    except NotFound:
        return jsonify({"error": "Report not found"}), 404
    except Exception as e:
        return jsonify({"error": f"Error retrieving report: {str(e)}"}), 500
