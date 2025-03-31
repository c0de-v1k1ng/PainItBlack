from kivy.uix.screenmanager import Screen
from kivymd.uix.screen import MDScreen
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDButton, MDButtonText
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.dialog import MDDialog, MDDialogHeadlineText, MDDialogContentContainer, MDDialogButtonContainer
from kivymd.uix.fitimage import FitImage
from kivymd.uix.textfield import MDTextField
from kivy_garden.graph import Graph, MeshLinePlot
from kivy.metrics import dp
from kivy.utils import get_color_from_hex

import database
import os
from datetime import datetime


class AnimalDetailScreen(MDScreen):
    """Screen for displaying detailed information about a specific animal."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.animal_id = None
        self.dialog = None
        self.weight_data = []
        self.graph = None
        self.plot = None

    def on_enter(self):
        """Refresh data when entering the screen."""
        if self.animal_id:
            self.load_animal_data()

    def set_animal_id(self, animal_id):
        """Set the animal ID and load its data."""
        self.animal_id = animal_id
        if self.animal_id:
            self.load_animal_data()

    def load_animal_data(self):
        """Load animal details from the database."""
        conn = database.get_db_connection()
        cursor = conn.cursor()

        # Get animal details
        cursor.execute("""
            SELECT name, species, breed, birthday, sex, castrated, current_weight, image_path
            FROM animals WHERE id = ?
        """, (self.animal_id,))

        animal = cursor.fetchone()
        if not animal:
            conn.close()
            return

        # Update the UI with animal details
        self.ids.animal_name.text = animal[0]
        self.ids.animal_species.text = f"Species: {animal[1]}"
        self.ids.animal_breed.text = f"Breed: {animal[2] or 'Not specified'}"

        # Format birthday if it exists
        birthday = animal[3]
        if birthday:
            self.ids.animal_birthday.text = f"Birthday: {birthday}"
        else:
            self.ids.animal_birthday.text = "Birthday: Not specified"

        self.ids.animal_sex.text = f"Sex: {animal[4] or 'Not specified'}"
        self.ids.animal_castrated.text = f"Castrated: {animal[5] or 'No'}"
        self.ids.animal_weight.text = f"Current Weight: {animal[6]} kg"

        # Set image if available
        if animal[7] and os.path.exists(animal[7]):
            self.ids.animal_image.source = animal[7]
        else:
            # Set a default image
            self.ids.animal_image.source = "assets/images/animal_placeholder.png"

        # Load weight history
        self.load_weight_history()

        # Load assessments
        self.load_assessments()

        conn.close()

    def load_weight_history(self):
        """Load and display weight history."""
        self.ids.weight_history_container.clear_widgets()

        # Clear any existing weight data
        self.weight_data = []

        conn = database.get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT id, date, weight FROM weight_history
            WHERE animal_id = ? ORDER BY date ASC
        """, (self.animal_id,))

        weights = cursor.fetchall()
        conn.close()

        if not weights:
            self.ids.weight_history_container.add_widget(
                MDLabel(text="No weight records found", halign="center")
            )
            return

        # Process weight data for the graph
        dates = []
        weights_values = []

        # Add weight history entries
        for weight_id, date, weight in weights:
            # Add to the graph data
            self.weight_data.append((date, weight))
            dates.append(date)
            weights_values.append(weight)

            # Create UI entry
            entry = MDBoxLayout(
                orientation="horizontal",
                adaptive_height=True,
                padding=("8dp", "8dp", "8dp", "8dp"),
                spacing="8dp"
            )

            date_label = MDLabel(text=date, size_hint_x=0.4)
            weight_label = MDLabel(text=f"{weight} kg", size_hint_x=0.4)
            delete_btn = MDButton(
                style="text",
                on_release=lambda x, wid=weight_id: self.delete_weight(wid)
            )
            delete_btn.add_widget(MDButtonText(text="Delete"))

            entry.add_widget(date_label)
            entry.add_widget(weight_label)
            entry.add_widget(delete_btn)

            self.ids.weight_history_container.add_widget(entry)

        # Add weight graph if we have at least 2 data points
        if len(self.weight_data) >= 2:
            # Clear any existing graph container
            if hasattr(self.ids, 'weight_graph_container'):
                self.ids.weight_graph_container.clear_widgets()

            # Create a graph
            self.create_weight_graph(dates, weights_values)

    def format_date_for_display(self, date_str):
        """Convert YYYY-MM-DD to DD.MM for display on graph axis."""
        try:
            date_obj = datetime.strptime(date_str, "%Y-%m-%d")
            return date_obj.strftime("%d.%m.%y")
        except ValueError:
            # Try other date formats
            try:
                date_obj = datetime.strptime(date_str, "%d.%m.%Y")
                return date_obj.strftime("%d.%m")
            except ValueError:
                return date_str  # Return original if parsing fails

    def create_weight_graph(self, dates, weights):
        """Create a line graph showing weight over time with dates on x-axis."""
        # Calculate min/max values for better scaling
        min_weight = min(weights)
        max_weight = max(weights)
        weight_range = max_weight - min_weight

        # Add some padding (10% of range)
        padding = weight_range * 0.1 if weight_range > 0 else 0.5
        y_min = max(0, min_weight - padding)  # Ensure not below 0
        y_max = max_weight + padding

        # Create the graph widget
        graph = Graph(
            xlabel='Date',
            ylabel='Weight (kg)',
            x_ticks_major=1,
            y_ticks_major=(y_max - y_min) / 5,
            y_grid_label=True,
            x_grid_label=True,  # Keep default labels for now
            padding=5,
            x_grid=True,
            y_grid=True,
            xmin=0,
            xmax=len(dates) - 1,
            ymin=y_min,
            ymax=y_max,
            size_hint_y=None,
            height=dp(200)
        )

        # Create the plot
        plot = MeshLinePlot(color=get_color_from_hex('#4f46e5'))
        plot.points = [(i, weights[i]) for i in range(len(weights))]
        graph.add_plot(plot)

        # Create graph container
        graph_container = MDBoxLayout(
            orientation="vertical",
            adaptive_height=True,
            padding=("8dp", "16dp", "8dp", "16dp"),
            spacing="8dp",
            size_hint_y=None,
            height=dp(280)  # Increased height for date labels
        )

        # Add a title
        graph_title = MDLabel(
            text="Weight History Graph",
            halign="center",
            size_hint_y=None,
            height=dp(30),
            font_style="Title",
            role="medium"
        )
        graph_container.add_widget(graph_title)

        # Add the graph
        graph_container.add_widget(graph)

        # Create a container for date labels
        date_labels_container = MDBoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=dp(30),
            padding=("0dp", "0dp", "0dp", "0dp")
        )

        # Format dates for display
        formatted_dates = [self.format_date_for_display(date) for date in dates]

        # Select which dates to display based on total number
        displayed_dates = []
        if len(formatted_dates) <= 5:
            # If 5 or fewer dates, show all
            displayed_dates = formatted_dates
        else:
            # Show first, last, and some in between
            step = max(1, len(formatted_dates) // 5)
            indices = list(range(0, len(formatted_dates), step))
            if len(formatted_dates) - 1 not in indices:
                indices.append(len(formatted_dates) - 1)  # Always add the last index

            # Create a list of empty strings with the correct length
            displayed_dates = [""] * len(formatted_dates)

            # Fill in only the selected indices
            for idx in indices:
                displayed_dates[idx] = formatted_dates[idx]

        # Add date labels
        for date_text in displayed_dates:
            date_label = MDLabel(
                text=date_text,
                halign="center",
                size_hint_x=1.0 / len(displayed_dates),
                font_style="Body",
                role="small"
            )
            date_labels_container.add_widget(date_label)

        # Add date labels container
        graph_container.add_widget(date_labels_container)

        # Add the graph container to the layout
        self.ids.weight_graph_container.add_widget(graph_container)

        # Save references for later updates
        self.graph = graph
        self.plot = plot

    def load_assessments(self):
        """Load and display assessments."""
        self.ids.assessments_container.clear_widgets()

        conn = database.get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT id, date, scale_used, result FROM assessments
            WHERE animal_id = ? ORDER BY date DESC
        """, (self.animal_id,))

        assessments = cursor.fetchall()
        conn.close()

        if not assessments:
            self.ids.assessments_container.add_widget(
                MDLabel(text="No assessments found", halign="center")
            )
            return

        # Add assessment entries
        for assessment_id, date, scale, result in assessments:
            entry = MDBoxLayout(
                orientation="vertical",
                adaptive_height=True,
                padding=("8dp", "8dp", "8dp", "8dp"),
                spacing="4dp"
            )

            header = MDBoxLayout(
                orientation="horizontal",
                adaptive_height=True
            )

            date_label = MDLabel(text=f"Date: {date}", size_hint_x=0.6)
            scale_label = MDLabel(text=f"Scale: {scale}", size_hint_x=0.4)

            header.add_widget(date_label)
            header.add_widget(scale_label)

            result_label = MDLabel(text=f"Result: {result}")

            entry.add_widget(header)
            entry.add_widget(result_label)

            self.ids.assessments_container.add_widget(entry)

    def show_add_weight_dialog(self):
        """Show dialog to add new weight record."""
        content = MDBoxLayout(
            orientation="vertical",
            spacing="16dp",
            adaptive_height=True,
            padding=["16dp", "16dp", "16dp", "0dp"]
        )

        # Create date field with today's date
        today = datetime.now().strftime("%Y-%m-%d")
        date_field = MDTextField(
            hint_text="Date (YYYY-MM-DD)",
            mode="outlined",
            text=today
        )
        content.add_widget(date_field)

        # Create weight field
        weight_field = MDTextField(
            hint_text="Weight (kg)",
            mode="outlined",
            input_filter="float"
        )
        content.add_widget(weight_field)

        self.dialog = MDDialog(
            MDDialogHeadlineText(text="Add Weight Record"),
            MDDialogContentContainer(content),
            MDDialogButtonContainer(
                MDButton(
                    MDButtonText(text="Cancel"),
                    style="text",
                    on_release=lambda x: self.dialog.dismiss()
                ),
                MDButton(
                    MDButtonText(text="Save"),
                    style="text",
                    on_release=lambda x: self.save_weight(date_field.text, weight_field.text)
                ),
                spacing="8dp"
            ),
            auto_dismiss=False
        )
        self.dialog.open()

    def save_weight(self, date, weight_text):
        """Save new weight record to database."""
        try:
            weight = float(weight_text)
            if weight <= 0:
                self.show_error_dialog("Weight must be a positive number.")
                return

            success = database.add_weight_record(self.animal_id, date, weight)
            if success:
                # Update current weight in animals table
                conn = database.get_db_connection()
                cursor = conn.cursor()
                cursor.execute(
                    "UPDATE animals SET current_weight = ? WHERE id = ?",
                    (weight, self.animal_id)
                )
                conn.commit()
                conn.close()

                self.dialog.dismiss()
                self.load_animal_data()  # Refresh all data
                self.show_success_dialog("Weight record added successfully!")
            else:
                self.show_error_dialog("Failed to add weight record.")
        except ValueError:
            self.show_error_dialog("Please enter a valid weight.")

    def delete_weight(self, weight_id):
        """Delete a weight record."""
        # Show confirmation dialog
        confirm_dialog = MDDialog(
            MDDialogHeadlineText(text="Confirm Deletion"),
            MDDialogContentContainer(
                MDLabel(text="Are you sure you want to delete this weight record?")
            ),
            MDDialogButtonContainer(
                MDButton(
                    MDButtonText(text="Cancel"),
                    style="text",
                    on_release=lambda x: confirm_dialog.dismiss()
                ),
                MDButton(
                    MDButtonText(text="Delete"),
                    style="text",
                    on_release=lambda x: self.confirm_delete_weight(weight_id, confirm_dialog)
                ),
                spacing="8dp"
            ),
            auto_dismiss=False
        )
        confirm_dialog.open()

    def confirm_delete_weight(self, weight_id, dialog):
        """Confirm and perform weight record deletion."""
        success = database.delete_weight_record(weight_id)
        dialog.dismiss()

        if success:
            # Check if this was the most recent weight and update animal's current weight
            conn = database.get_db_connection()
            cursor = conn.cursor()
            cursor.execute(
                """SELECT weight FROM weight_history 
                   WHERE animal_id = ? ORDER BY date DESC LIMIT 1""",
                (self.animal_id,)
            )
            latest = cursor.fetchone()

            if latest:
                # Update to the most recent weight
                cursor.execute(
                    "UPDATE animals SET current_weight = ? WHERE id = ?",
                    (latest[0], self.animal_id)
                )
            conn.commit()
            conn.close()

            self.load_animal_data()  # Refresh all data
            self.show_success_dialog("Weight record deleted successfully!")
        else:
            self.show_error_dialog("Failed to delete weight record.")

    def show_success_dialog(self, message):
        """Show a success dialog."""
        success_dialog = MDDialog(
            MDDialogHeadlineText(text="Success"),
            MDDialogContentContainer(
                MDLabel(text=message)
            ),
            MDDialogButtonContainer(
                MDButton(
                    MDButtonText(text="OK"),
                    style="text",
                    on_release=lambda x: success_dialog.dismiss()
                )
            )
        )
        success_dialog.open()

    def show_error_dialog(self, message):
        """Show an error dialog."""
        error_dialog = MDDialog(
            MDDialogHeadlineText(text="Error"),
            MDDialogContentContainer(
                MDLabel(text=message)
            ),
            MDDialogButtonContainer(
                MDButton(
                    MDButtonText(text="OK"),
                    style="text",
                    on_release=lambda x: error_dialog.dismiss()
                )
            )
        )
        error_dialog.open()