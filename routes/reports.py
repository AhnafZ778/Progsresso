"""
Report generation API endpoints
"""

from flask import Blueprint, request, jsonify, send_file
from services.pdf_service import PDFService
from services.progress_service import ProgressService
import io

reports_bp = Blueprint("reports", __name__, url_prefix="/api/reports")


@reports_bp.route("/pdf", methods=["GET"])
def generate_pdf():
    """Generate PDF progress report"""
    try:
        start_date = request.args.get("start")
        end_date = request.args.get("end")
        weeks = int(request.args.get("weeks", 4))

        pdf_buffer = PDFService.generate_report(start_date, end_date, weeks)

        return send_file(
            pdf_buffer,
            mimetype="application/pdf",
            as_attachment=True,
            download_name="progresso_report.pdf",
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@reports_bp.route("/summary", methods=["GET"])
def get_summary():
    """Get summary data for reports"""
    try:
        weeks = int(request.args.get("weeks", 4))
        summary = ProgressService.get_summary(weeks)
        return jsonify({"summary": summary})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
