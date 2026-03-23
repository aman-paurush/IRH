"""
Advanced Reporting and Analysis Module.
Generates comprehensive reports on ransomware attack patterns and deception effectiveness.
"""

import json
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any

from config import DB_PATH


class ReportGenerator:
    """Generate comprehensive honeypot analysis reports."""

    def __init__(self):
        self.db_path = DB_PATH

    def generate_full_report(self, exp_id: int) -> Dict[str, Any]:
        """Generate a comprehensive report for an experiment."""
        try:
            conn = sqlite3.connect(self.db_path, check_same_thread=False)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            # Get experiment info
            cursor.execute("SELECT * FROM experiments WHERE id = ?", (exp_id,))
            exp = cursor.fetchone()
            if not exp:
                return {"error": "experiment_not_found"}

            # Get file event statistics
            cursor.execute(
                "SELECT COUNT(*) as total, SUM(CASE WHEN is_encrypted THEN 1 ELSE 0 END) as encrypted_count FROM file_events WHERE experiment_id = ?",
                (exp_id,),
            )
            file_stats = cursor.fetchone()

            # Get deception statistics
            cursor.execute(
                "SELECT COUNT(*) as total, COUNT(DISTINCT layer) as unique_layers, SUM(files_generated) as total_files_generated FROM deception_events WHERE experiment_id = ?",
                (exp_id,),
            )
            deception_stats = cursor.fetchone()

            # Get process events
            cursor.execute(
                "SELECT COUNT(*) as total FROM process_events WHERE experiment_id = ?",
                (exp_id,),
            )
            process_stats = cursor.fetchone()

            # Get file event timeline
            cursor.execute(
                """
                SELECT 
                    DATE(timestamp) as date,
                    COUNT(*) as event_count,
                    SUM(CASE WHEN is_encrypted THEN 1 ELSE 0 END) as encrypted_count
                FROM file_events 
                WHERE experiment_id = ?
                GROUP BY DATE(timestamp)
                ORDER BY date ASC
            """,
                (exp_id,),
            )
            timeline = [dict(row) for row in cursor.fetchall()]

            # Get most targeted file types
            cursor.execute(
                """
                SELECT 
                    CASE 
                        WHEN filepath LIKE '%.pdf' THEN 'PDF'
                        WHEN filepath LIKE '%.xlsx' THEN 'Excel'
                        WHEN filepath LIKE '%.docx' THEN 'Word'
                        WHEN filepath LIKE '%.txt' THEN 'Text'
                        WHEN filepath LIKE '%.log' THEN 'Log'
                        ELSE 'Other'
                    END as file_type,
                    COUNT(*) as count,
                    SUM(CASE WHEN is_encrypted THEN 1 ELSE 0 END) as encrypted_count
                FROM file_events
                WHERE experiment_id = ?
                GROUP BY file_type
                ORDER BY count DESC
            """,
                (exp_id,),
            )
            file_types = [dict(row) for row in cursor.fetchall()]

            # Get deception effectiveness
            cursor.execute(
                """
                SELECT 
                    layer,
                    COUNT(*) as trigger_count,
                    AVG(files_generated) as avg_files_generated,
                    SUM(files_generated) as total_files_generated
                FROM deception_events
                WHERE experiment_id = ?
                GROUP BY layer
                ORDER BY layer ASC
            """,
                (exp_id,),
            )
            deception_by_layer = [dict(row) for row in cursor.fetchall()]

            # Get most frequently accessed directories
            cursor.execute(
                """
                SELECT 
                    SUBSTR(filepath, 1, INSTR(filepath, '/', INSTR(filepath, '/') + 1)) as directory,
                    COUNT(*) as access_count,
                    SUM(CASE WHEN is_encrypted THEN 1 ELSE 0 END) as encrypted_count
                FROM file_events
                WHERE experiment_id = ?
                GROUP BY directory
                ORDER BY access_count DESC
                LIMIT 10
            """,
                (exp_id,),
            )
            top_directories = [dict(row) for row in cursor.fetchall()]

            conn.close()

            # Calculate engagement time
            start_time = datetime.fromisoformat(exp["start_time"])
            end_time = (
                datetime.fromisoformat(exp["end_time"]) if exp["end_time"] else datetime.now()
            )
            engagement_minutes = int((end_time - start_time).total_seconds() / 60)

            # Calculate encryption rate
            total_files = file_stats["total"] or 0
            encrypted_files = file_stats["encrypted_count"] or 0
            encryption_rate = (
                round((encrypted_files / total_files * 100), 2) if total_files > 0 else 0
            )

            # Build comprehensive report
            report = {
                "experiment_info": {
                    "experiment_id": exp_id,
                    "start_time": exp["start_time"],
                    "end_time": exp["end_time"],
                    "status": exp["status"],
                    "engagement_duration_minutes": engagement_minutes,
                    "engagement_duration_hours": round(engagement_minutes / 60, 2),
                },
                "file_statistics": {
                    "total_honeypot_files": exp["total_files"] or 0,
                    "total_file_events": file_stats["total"] or 0,
                    "files_encrypted": encrypted_files,
                    "encryption_rate_percent": encryption_rate,
                    "file_types_targeted": file_types,
                },
                "deception_effectiveness": {
                    "total_deception_triggers": deception_stats["total"] or 0,
                    "layers_deployed": deception_stats["unique_layers"] or 0,
                    "additional_files_generated": deception_stats["total_files_generated"] or 0,
                    "by_layer": deception_by_layer,
                },
                "process_monitoring": {
                    "suspicious_processes_detected": process_stats["total"] or 0,
                },
                "attack_timeline": timeline,
                "most_targeted_directories": top_directories,
                "report_generated": datetime.now().isoformat(),
            }

            return report
        except Exception as e:
            return {"error": str(e)}

    def generate_pdf_report(self, exp_id: int, output_path: Path = None) -> bool:
        """Generate a PDF report (requires reportlab)."""
        try:
            from reportlab.lib.pagesizes import letter, A4
            from reportlab.lib.styles import getSampleStyleSheet
            from reportlab.lib.units import inch
            from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
            from reportlab.lib import colors
        except ImportError:
            return False

        report_data = self.generate_full_report(exp_id)
        if "error" in report_data:
            return False

        output_path = output_path or self.db_path.parent / f"honeypot_report_{exp_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"

        try:
            doc = SimpleDocTemplate(str(output_path), pagesize=letter)
            elements = []
            styles = getSampleStyleSheet()

            # Title
            title_style = styles["Heading1"]
            elements.append(
                Paragraph(
                    f"Ransomware Honeypot Analysis Report - Experiment {exp_id}",
                    title_style,
                )
            )
            elements.append(Spacer(1, 0.5 * inch))

            # Experiment Info
            elements.append(
                Paragraph(
                    "Experiment Information",
                    styles["Heading2"],
                )
            )
            exp_table_data = [
                ["Metric", "Value"],
                ["Start Time", report_data["experiment_info"]["start_time"]],
                ["End Time", report_data["experiment_info"]["end_time"]],
                [
                    "Duration",
                    f"{report_data['experiment_info']['engagement_duration_hours']} hours",
                ],
                ["Status", report_data["experiment_info"]["status"]],
            ]
            exp_table = Table(exp_table_data, colWidths=[2.5 * inch, 3.5 * inch])
            exp_table.setStyle(
                TableStyle(
                    [
                        ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
                        ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                        ("FONTSIZE", (0, 0), (-1, 0), 12),
                        ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
                        ("BACKGROUND", (0, 1), (-1, -1), colors.beige),
                        ("GRID", (0, 0), (-1, -1), 1, colors.black),
                    ]
                )
            )
            elements.append(exp_table)
            elements.append(Spacer(1, 0.3 * inch))

            # File Statistics
            elements.append(Paragraph("File Statistics", styles["Heading2"]))
            file_stats = report_data["file_statistics"]
            file_table_data = [
                ["Metric", "Value"],
                ["Total Honeypot Files", str(file_stats["total_honeypot_files"])],
                ["Total File Access Events", str(file_stats["total_file_events"])],
                ["Files Successfully Encrypted", str(file_stats["files_encrypted"])],
                ["Encryption Rate", f"{file_stats['encryption_rate_percent']}%"],
            ]
            file_table = Table(file_table_data, colWidths=[3 * inch, 3 * inch])
            file_table.setStyle(
                TableStyle(
                    [
                        ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
                        ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                        ("BACKGROUND", (0, 1), (-1, -1), colors.lightblue),
                        ("GRID", (0, 0), (-1, -1), 1, colors.black),
                    ]
                )
            )
            elements.append(file_table)
            elements.append(PageBreak())

            # Deception Effectiveness
            elements.append(Paragraph("Deception Effectiveness", styles["Heading2"]))
            deception_stats = report_data["deception_effectiveness"]
            deception_table_data = [
                ["Metric", "Value"],
                ["Deception Triggers", str(deception_stats["total_deception_triggers"])],
                ["Layers Deployed", str(deception_stats["layers_deployed"])],
                [
                    "Additional Files Generated",
                    str(deception_stats["additional_files_generated"]),
                ],
            ]
            deception_table = Table(deception_table_data, colWidths=[3 * inch, 3 * inch])
            deception_table.setStyle(
                TableStyle(
                    [
                        ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
                        ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                        ("BACKGROUND", (0, 1), (-1, -1), colors.lightgreen),
                        ("GRID", (0, 0), (-1, -1), 1, colors.black),
                    ]
                )
            )
            elements.append(deception_table)
            elements.append(Spacer(1, 0.3 * inch))

            # Build PDF
            doc.build(elements)
            print(f"PDF report saved: {output_path}")
            return True
        except Exception as e:
            print(f"Error generating PDF: {e}")
            return False

    def export_json_report(self, exp_id: int, output_path: Path = None) -> bool:
        """Export report as JSON."""
        report = self.generate_full_report(exp_id)
        if "error" in report:
            return False

        output_path = output_path or self.db_path.parent / f"honeypot_report_{exp_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

        try:
            with open(output_path, "w") as f:
                json.dump(report, f, indent=2)
            print(f"JSON report saved: {output_path}")
            return True
        except Exception as e:
            print(f"Error exporting JSON: {e}")
            return False

    def compare_experiments(self, exp_ids: List[int]) -> Dict[str, Any]:
        """Compare statistics across multiple experiments."""
        reports = {}
        for exp_id in exp_ids:
            reports[exp_id] = self.generate_full_report(exp_id)

        summary = {
            "experiments_compared": len(exp_ids),
            "total_engagement_time": sum(
                r.get("experiment_info", {}).get("engagement_duration_hours", 0) for r in reports.values()
            ),
            "average_encryption_rate": sum(
                r.get("file_statistics", {}).get("encryption_rate_percent", 0) for r in reports.values()
            ) / len(exp_ids) if exp_ids else 0,
            "total_deception_triggers": sum(
                r.get("deception_effectiveness", {}).get("total_deception_triggers", 0) for r in reports.values()
            ),
            "individual_reports": reports,
        }

        return summary


if __name__ == "__main__":
    gen = ReportGenerator()
    import sys

    if len(sys.argv) > 1:
        exp_id = int(sys.argv[1])
        report = gen.generate_full_report(exp_id)
        print(json.dumps(report, indent=2))
