import os
import csv
import json
from datetime import datetime
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.graphics.shapes import Drawing
from reportlab.graphics.charts.linecharts import HorizontalLineChart

import database


class ExportManager:
    """Manages export operations for the animal tracking app."""

    def __init__(self):
        """Initialize the export manager."""
        self.export_dir = "exports"

        # Create exports directory if it doesn't exist
        if not os.path.exists(self.export_dir):
            os.makedirs(self.export_dir)

        # Set up PDF styles
        self.styles = getSampleStyleSheet()
        self.styles.add(ParagraphStyle(
            name='Heading1Center',
            parent=self.styles['Heading1'],
            alignment=1
        ))
        self.styles.add(ParagraphStyle(
            name='Normal_CENTER',
            parent=self.styles['Normal'],
            alignment=1
        ))

    def export_animal_to_pdf(self, animal_id):
        """
        Export a single animal's data to PDF.

        Args:
            animal_id: The ID of the animal to export

        Returns:
            str: Path to the generated PDF file
        """
        # Get animal details
        animal = database.execute_query(
            """
            SELECT name, species, breed, birthday, sex, castrated, current_weight, 
                   target_weight, target_date 
            FROM animals 
            WHERE id = ?
            """,
            (animal_id,),
            fetch_mode='one'
        )

        if not animal:
            return None

        # Get weight history
        weight_history = database.execute_query(
            """
            SELECT date, weight FROM weight_history
            WHERE animal_id = ? ORDER BY date ASC
            """,
            (animal_id,),
            fetch_mode='all'
        ) or []

        # Get assessments
        assessments = database.execute_query(
            """
            SELECT id, date, scale_used, result FROM assessments
            WHERE animal_id = ? ORDER BY date DESC
            """,
            (animal_id,),
            fetch_mode='all'
        ) or []

        # Create filename with timestamp and animal details
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        animal_name = animal[0].replace(" ", "_")
        filename = f"{self.export_dir}/{timestamp}_{animal_name}_ID{animal_id}.pdf"

        # Create the PDF
        doc = SimpleDocTemplate(filename, pagesize=A4)
        story = []

        # Add title
        title = f"{animal[0]} ({animal[1]})"
        story.append(Paragraph(title, self.styles['Heading1Center']))
        story.append(Spacer(1, 12))

        # Add animal details table
        animal_data = [
            ["Breed:", animal[2] or "Not specified"],
            ["Birthday:", animal[3] or "Not specified"],
            ["Sex:", animal[4] or "Not specified"],
            ["Castrated:", animal[5] or "No"],
            ["Current Weight:", f"{animal[6]} kg"]
        ]

        if animal[7] and animal[8]:  # If target weight exists
            animal_data.append(["Target Weight:", f"{animal[7]} kg"])
            animal_data.append(["Target Date:", animal[8]])

        animal_table = Table(animal_data, colWidths=[100, 400])
        animal_table.setStyle(TableStyle([
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (-1, -1), 6),
            ('RIGHTPADDING', (0, 0), (-1, -1), 6),
        ]))
        story.append(animal_table)
        story.append(Spacer(1, 20))

        # Add weight history section if available
        if weight_history:
            story.append(Paragraph("Weight History", self.styles['Heading2']))
            story.append(Spacer(1, 12))

            # Add weight history table
            weight_data = [["Date", "Weight (kg)"]]
            weights_values = []
            dates = []

            for date, weight in weight_history:
                weight_data.append([date, f"{weight} kg"])
                dates.append(date)
                weights_values.append(weight)

            weight_table = Table(weight_data, colWidths=[250, 250])
            weight_table.setStyle(TableStyle([
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ]))
            story.append(weight_table)
            story.append(Spacer(1, 12))

            # Add weight graph if more than one data point
            if len(weight_history) > 1:
                # Create a line chart
                story.append(Paragraph("Weight Trend", self.styles['Heading3']))
                story.append(Spacer(1, 12))

                drawing = Drawing(400, 200)
                chart = HorizontalLineChart()
                chart.x = 50
                chart.y = 50
                chart.width = 300
                chart.height = 150

                # Format data for the chart
                chart.data = [weights_values]

                # Show every 5th label to avoid crowding for large datasets
                step = max(1, len(dates) // 5)
                chart.categoryAxis.categoryNames = dates[::step]
                chart.categoryAxis.labels.boxAnchor = 'ne'
                chart.categoryAxis.labels.angle = 30

                chart.valueAxis.valueMin = min(weights_values) * 0.9
                chart.valueAxis.valueMax = max(weights_values) * 1.1

                drawing.add(chart)
                story.append(drawing)
                story.append(Spacer(1, 12))

        # Add assessments overview section
        if assessments:
            story.append(Paragraph("Assessments Overview", self.styles['Heading2']))
            story.append(Spacer(1, 12))

            # Create assessments table
            assessment_data = [["Date", "Scale", "Result"]]

            for assessment_id, date, scale, result in assessments:
                # Try to parse result JSON
                try:
                    result_data = json.loads(result)
                    if "score" in result_data and "interpretation" in result_data:
                        result_text = f"{result_data['score']} - {result_data['interpretation']}"
                    else:
                        result_text = str(result)
                except (json.JSONDecodeError, TypeError):
                    result_text = str(result)

                assessment_data.append([date, scale, result_text])

            assessment_table = Table(assessment_data, colWidths=[100, 200, 200])
            assessment_table.setStyle(TableStyle([
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ]))
            story.append(assessment_table)
            story.append(Spacer(1, 20))

            # Add detailed assessment pages
            for assessment_id, date, scale, result in assessments:
                story.append(Paragraph("Assessment Details", self.styles['Heading1Center']))
                story.append(Spacer(1, 12))

                story.append(Paragraph(f"Scale: {scale}", self.styles['Heading2']))
                story.append(Paragraph(f"Date: {date}", self.styles['Normal']))
                story.append(Spacer(1, 12))

                # Try to parse result JSON
                try:
                    result_data = json.loads(result)

                    if "score" in result_data and "interpretation" in result_data:
                        story.append(Paragraph(f"Score: {result_data['score']}", self.styles['Heading3']))
                        story.append(
                            Paragraph(f"Interpretation: {result_data['interpretation']}", self.styles['Normal']))
                        story.append(Spacer(1, 12))

                    if "details" in result_data and isinstance(result_data["details"], list):
                        detail_data = [["Question", "Answer", "Score"]]

                        for detail in result_data["details"]:
                            if isinstance(detail, dict) and "question" in detail and "answer" in detail:
                                detail_data.append([
                                    detail["question"],
                                    detail["answer"],
                                    str(detail.get("score", ""))
                                ])

                        if len(detail_data) > 1:  # If we have details beyond the header
                            detail_table = Table(detail_data, colWidths=[200, 200, 100])
                            detail_table.setStyle(TableStyle([
                                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                                ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
                                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                            ]))
                            story.append(detail_table)
                    else:
                        story.append(Paragraph(f"Result: {result}", self.styles['Normal']))

                except (json.JSONDecodeError, TypeError):
                    story.append(Paragraph(f"Result: {result}", self.styles['Normal']))

                # Add page break between assessments
                story.append(Spacer(1, 20))
                story.append(Paragraph("", self.styles['Normal']))
                story.append(Paragraph("", self.styles['Normal']))

        # Build the PDF
        doc.build(story)
        return filename

    def export_animal_to_csv(self, animal_id):
        """
        Export a single animal's data to CSV files.

        Args:
            animal_id: The ID of the animal to export

        Returns:
            list: Paths to the generated CSV files
        """
        # Get animal details
        animal = database.execute_query(
            """
            SELECT name, species, breed, birthday, sex, castrated, current_weight, 
                   target_weight, target_date 
            FROM animals 
            WHERE id = ?
            """,
            (animal_id,),
            fetch_mode='one'
        )

        if not animal:
            return None

        # Create timestamp for filenames
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        animal_name = animal[0].replace(" ", "_")

        # Create base filename
        base_filename = f"{timestamp}_{animal_name}_ID{animal_id}"

        # Export animal details
        details_filename = f"{self.export_dir}/{base_filename}_details.csv"
        with open(details_filename, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["Field", "Value"])
            writer.writerow(["Name", animal[0]])
            writer.writerow(["Species", animal[1]])
            writer.writerow(["Breed", animal[2] or "Not specified"])
            writer.writerow(["Birthday", animal[3] or "Not specified"])
            writer.writerow(["Sex", animal[4] or "Not specified"])
            writer.writerow(["Castrated", animal[5] or "No"])
            writer.writerow(["Current Weight", f"{animal[6]} kg"])

            if animal[7] and animal[8]:  # If target weight exists
                writer.writerow(["Target Weight", f"{animal[7]} kg"])
                writer.writerow(["Target Date", animal[8]])

        # Export weight history if available
        weight_history = database.execute_query(
            """
            SELECT date, weight FROM weight_history
            WHERE animal_id = ? ORDER BY date ASC
            """,
            (animal_id,),
            fetch_mode='all'
        )

        filenames = [details_filename]

        if weight_history:
            weights_filename = f"{self.export_dir}/{base_filename}_weights.csv"
            with open(weights_filename, 'w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(["Date", "Weight (kg)"])
                for date, weight in weight_history:
                    writer.writerow([date, weight])
            filenames.append(weights_filename)

        # Export assessments if available
        assessments = database.execute_query(
            """
            SELECT id, date, scale_used, result FROM assessments
            WHERE animal_id = ? ORDER BY date DESC
            """,
            (animal_id,),
            fetch_mode='all'
        )

        if assessments:
            assessments_filename = f"{self.export_dir}/{base_filename}_assessments.csv"
            with open(assessments_filename, 'w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(["ID", "Date", "Scale", "Score", "Interpretation", "Details"])

                for assessment_id, date, scale, result in assessments:
                    # Try to parse result JSON
                    score = ""
                    interpretation = ""
                    details = ""

                    try:
                        result_data = json.loads(result)
                        if "score" in result_data:
                            score = result_data["score"]
                        if "interpretation" in result_data:
                            interpretation = result_data["interpretation"]
                        if "details" in result_data:
                            details = json.dumps(result_data["details"])
                    except (json.JSONDecodeError, TypeError):
                        details = result

                    writer.writerow([assessment_id, date, scale, score, interpretation, details])
            filenames.append(assessments_filename)

        return filenames

    def export_multiple_animals_to_pdf(self, animal_ids):
        """
        Export multiple animals to PDF files.

        Args:
            animal_ids: List of animal IDs to export

        Returns:
            list: Paths to the generated PDF files
        """
        filenames = []
        for animal_id in animal_ids:
            filename = self.export_animal_to_pdf(animal_id)
            if filename:
                filenames.append(filename)
        return filenames

    def export_multiple_animals_to_csv(self, animal_ids):
        """
        Export multiple animals to CSV files.

        Args:
            animal_ids: List of animal IDs to export

        Returns:
            list: Paths to the generated CSV files
        """
        all_filenames = []
        for animal_id in animal_ids:
            filenames = self.export_animal_to_csv(animal_id)
            if filenames:
                all_filenames.extend(filenames)
        return all_filenames