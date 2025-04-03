import json
import os
from datetime import datetime

from kivy.graphics import Color, Ellipse
from kivy.metrics import dp
from kivy.properties import NumericProperty, StringProperty
from kivy.utils import get_color_from_hex
from kivy_garden.graph import Graph, MeshLinePlot
from kivymd.app import MDApp
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDButton, MDButtonText, MDIconButton
from kivymd.uix.dialog import MDDialog, MDDialogHeadlineText, MDDialogContentContainer, MDDialogButtonContainer
from kivymd.uix.label import MDLabel
from kivymd.uix.screen import MDScreen
from kivymd.uix.textfield import MDTextField

import database


class AnimalDetailScreen(MDScreen):
    """Screen for displaying detailed information about a specific animal."""

    animal_id = NumericProperty(None)
    target_weight = NumericProperty(None)
    target_date = StringProperty("")


    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.animal_id = None
        self.dialog = None
        self.weight_data = []
        self.graph = None
        self.plot = None
        self.target_dialog = None
        self.target_weight = None
        self.target_date = ""

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
        # Get animal details using the new execute_query function
        animal = database.execute_query(
            """
            SELECT name, species, breed, birthday, sex, castrated, current_weight, image_path, 
                   target_weight, target_date
            FROM animals WHERE id = ?
            """,
            (self.animal_id,),
            fetch_mode='one'
        )
        if not animal:
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

        # Load target weight if available
        if animal[8] and animal[9]:
            self.target_weight = animal[8]
            self.target_date = animal[9]

        # Load weight history
        self.load_weight_history()

        # Load assessments
        self.load_assessments()

        return

    def load_weight_history(self):
        """Load and display weight history."""
        self.ids.weight_history_container.clear_widgets()

        # always clear graph container!
        if hasattr(self.ids, 'weight_graph_container'):
            self.ids.weight_graph_container.clear_widgets()

        # Clear any existing weight data
        self.weight_data = []

        # Get weight history using the new execute_query function
        weights = database.execute_query(
            """
            SELECT id, date, weight FROM weight_history
            WHERE animal_id = ? ORDER BY date ASC
            """,
            (self.animal_id,),
            fetch_mode='all'
        )

        if not weights:
            self.ids.weight_history_container.add_widget(
                MDLabel(text="No weight records found", halign="center")
            )

            # Add weight target UI if we don't have any data yet
            if not hasattr(self.ids, 'target_container'):
                # Add the target weight container to the animal_detail.kv file first
                pass
            else:
                self.update_target_ui()

            return

        # Process weight data for the graph
        dates = []
        weights_values = []
        prev_weight = None

        # Add title for weight history
        title_box = MDBoxLayout(
            orientation="horizontal",
            adaptive_height=True,
            padding=(dp(8), dp(16), dp(8), dp(8)),
            spacing="8dp"
        )

        date_header = MDLabel(text="Date", size_hint_x=0.3, font_style="Body", role="medium")
        weight_header = MDLabel(text="Weight (kg)", size_hint_x=0.3, font_style="Body", role="medium")
        change_header = MDLabel(text="Change", size_hint_x=0.2, font_style="Body", role="medium")

        title_box.add_widget(date_header)
        title_box.add_widget(weight_header)
        title_box.add_widget(change_header)
        title_box.add_widget(MDLabel(text="", size_hint_x=0.2))  # Placeholder for delete button

        self.ids.weight_history_container.add_widget(title_box)

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
                padding=(dp(8), dp(8), dp(8), dp(8)),
                spacing="8dp"
            )

            date_label = MDLabel(text=date, size_hint_x=0.3)
            weight_label = MDLabel(text=f"{weight} kg", size_hint_x=0.3)

            # Calculate and display weight change
            if prev_weight is not None:
                change = weight - prev_weight
                change_text = f"{change:+.2f} kg"

                # Color code the change (green for gain, red for loss)
                if change > 0:
                    change_color = get_color_from_hex("#4CAF50")  # Green
                elif change < 0:
                    change_color = get_color_from_hex("#F44336")  # Red
                else:
                    change_color = get_color_from_hex("#757575")  # Gray

                change_label = MDLabel(
                    text=change_text,
                    size_hint_x=0.2,
                    theme_text_color="Custom",
                    text_color=change_color
                )
            else:
                change_label = MDLabel(text="", size_hint_x=0.2)

            delete_btn = MDButton(
                style="text",
                size_hint_x=0.2,
                on_release=lambda x, wid=weight_id: self.delete_weight(wid)
            )
            delete_btn.add_widget(MDButtonText(text="Delete"))

            entry.add_widget(date_label)
            entry.add_widget(weight_label)
            entry.add_widget(change_label)
            entry.add_widget(delete_btn)

            self.ids.weight_history_container.add_widget(entry)

            # Update previous weight for next iteration
            prev_weight = weight

        # Add weight graph if we have at least 2 data points
        if len(self.weight_data) >= 2:
            # Clear any existing graph container
            if hasattr(self.ids, 'weight_graph_container'):
                self.ids.weight_graph_container.clear_widgets()

            # Create a graph
            self.create_weight_graph(dates, weights_values)

        # Update target weight UI
        self.update_target_ui()

    def update_target_ui(self):
        """Update the target weight UI based on current data."""
        if not hasattr(self.ids, 'target_container'):
            return

        # Clear the existing content in the container
        self.ids.target_container.clear_widgets()

        # If we have a target weight, display it
        if self.target_weight and self.target_date:
            # Add target weight and date info
            self.ids.target_container.add_widget(MDLabel(
                text=f"Target Weight: {self.target_weight} kg",
                font_style="Body",
                role="medium",
                size_hint_y=None,
                height=dp(24)
            ))

            self.ids.target_container.add_widget(MDLabel(
                text=f"Target Date: {self.target_date}",
                font_style="Body",
                role="medium",
                size_hint_y=None,
                height=dp(24)
            ))

            # Calculate progress if we have current weight
            if self.weight_data:
                current_weight = self.weight_data[-1][1]  # Get the latest weight

                # Calculate percentage towards target
                if current_weight != self.target_weight:
                    initial_weight = self.weight_data[0][1]  # Get the first recorded weight
                    total_change_needed = self.target_weight - initial_weight
                    current_change = current_weight - initial_weight

                    if total_change_needed != 0:  # Avoid division by zero
                        progress_percent = (current_change / total_change_needed) * 100

                        progress_text = f"Progress: {progress_percent:.1f}%"

                        # For animals that need to lose weight, the calculation is different
                        if total_change_needed < 0:
                            if current_change < 0:  # Weight loss is happening
                                progress_percent = (current_change / total_change_needed) * 100
                                progress_text = f"Progress: {progress_percent:.1f}%"
                            else:  # Weight still increasing when should decrease
                                progress_text = "Progress: Moving away from target"
                    else:
                        progress_text = "Progress: Already at target"

                    progress_label = MDLabel(
                        text=progress_text,
                        font_style="Body",
                        role="medium",
                        size_hint_y=None,
                        height=dp(24)
                    )
                    self.ids.target_container.add_widget(progress_label)

                    # Add remaining calculation
                    remaining = self.target_weight - current_weight
                    remaining_label = MDLabel(
                        text=f"Remaining: {remaining:+.2f} kg",
                        font_style="Body",
                        role="medium",
                        theme_text_color="Custom",
                        text_color=get_color_from_hex("#4CAF50") if remaining > 0 else get_color_from_hex("#F44336"),
                        size_hint_y=None,
                        height=dp(24)
                    )
                    self.ids.target_container.add_widget(remaining_label)
        else:
            # No target set
            self.ids.target_container.add_widget(MDLabel(
                text="No weight target set",
                font_style="Body",
                role="medium",
                halign="center",
                size_hint_y=None,
                height=dp(40)  # Fixed height for visibility
            ))

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

        # If we have a target weight, include it in the y-axis range
        if self.target_weight:
            y_min = min(y_min, self.target_weight - padding)
            y_max = max(y_max, self.target_weight + padding)

        # Create the graph widget
        graph = Graph(
            xlabel='Date',
            ylabel='Weight (kg)',
            x_ticks_major=1,
            y_ticks_major=(y_max - y_min) / 5,
            y_grid_label=True,
            x_grid_label=True,
            padding=5,
            x_grid=True,
            y_grid=True,
            xmin=0,
            xmax=len(dates) - 1,
            ymin=y_min,
            ymax=y_max,
            size_hint_y=None,
            height=dp(300)  # Increased for better visibility
        )

        # Create the main weight plot
        plot = MeshLinePlot(color=get_color_from_hex('#4f46e5'))
        plot.points = [(i, weights[i]) for i in range(len(weights))]
        plot.line_width = 4  # Thicker line
        graph.add_plot(plot)

        # Add data points:
        # Add dots for data points
        for i, y in enumerate(weights):
            with graph.canvas.after:
                Color(rgba=get_color_from_hex('#4f46e5'))
                d = dp(6)  # diameter
                x_px = graph.x + graph.width * ((i - graph.xmin) / (graph.xmax - graph.xmin))
                y_px = graph.y + graph.height * ((y - graph.ymin) / (graph.ymax - graph.ymin))
                Ellipse(pos=(x_px - d / 2, y_px - d / 2), size=(d, d))

        # Add target weight line if available
        if self.target_weight:
            target_plot = MeshLinePlot(color=get_color_from_hex('#4CAF50'))
            target_plot.points = [(0, self.target_weight), (len(dates) - 1, self.target_weight)]
            target_plot.line_width = 4  # Thicker line
            graph.add_plot(target_plot)

        # Create graph container
        graph_container = MDBoxLayout(
            orientation="vertical",
            adaptive_height=True,
            padding=("8dp", "16dp", "8dp", "16dp"),
            spacing="8dp",
            size_hint_y=None,
            height=dp(320)
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

        formatted_dates = [self.format_date_for_display(date) for date in dates]

        displayed_dates = []
        if len(formatted_dates) <= 5:
            displayed_dates = formatted_dates
        else:
            step = max(1, len(formatted_dates) // 5)
            indices = list(range(0, len(formatted_dates), step))
            if len(formatted_dates) - 1 not in indices:
                indices.append(len(formatted_dates) - 1)

            displayed_dates = [""] * len(formatted_dates)
            for idx in indices:
                displayed_dates[idx] = formatted_dates[idx]

        for date_text in displayed_dates:
            date_label = MDLabel(
                text=date_text,
                halign="center",
                size_hint_x=1.0 / len(displayed_dates),
                font_style="Body",
                role="small"
            )
            date_labels_container.add_widget(date_label)

        graph_container.add_widget(date_labels_container)

        if self.target_weight:
            legend_container = MDBoxLayout(
                orientation="horizontal",
                size_hint_y=None,
                height=dp(30),
                padding=("8dp", "4dp", "8dp", "4dp")
            )

            history_box = MDBoxLayout(
                orientation="horizontal",
                adaptive_height=True,
                spacing="4dp",
                size_hint_x=0.5
            )

            history_color = MDBoxLayout(
                size_hint=(None, None),
                size=(dp(16), dp(16)),
                md_bg_color=get_color_from_hex('#4f46e5')
            )

            history_label = MDLabel(
                text="Weight History",
                font_style="Body",
                role="small"
            )

            history_box.add_widget(history_color)
            history_box.add_widget(history_label)

            target_box = MDBoxLayout(
                orientation="horizontal",
                adaptive_height=True,
                spacing="4dp",
                size_hint_x=0.5
            )

            target_color = MDBoxLayout(
                size_hint=(None, None),
                size=(dp(16), dp(16)),
                md_bg_color=get_color_from_hex('#4CAF50')
            )

            target_label = MDLabel(
                text=f"Target: {self.target_weight} kg",
                font_style="Body",
                role="small"
            )

            target_box.add_widget(target_color)
            target_box.add_widget(target_label)

            legend_container.add_widget(history_box)
            legend_container.add_widget(target_box)

            graph_container.add_widget(legend_container)

        self.ids.weight_graph_container.add_widget(graph_container)

        self.graph = graph
        self.plot = plot

    def show_target_dialog(self):
        """Show dialog to set weight target."""
        content = MDBoxLayout(
            orientation="vertical",
            spacing="16dp",
            adaptive_height=True,
            padding=["16dp", "16dp", "16dp", "0dp"]
        )

        # Current weight info
        if self.weight_data:
            current_weight = self.weight_data[-1][1]  # Get the latest weight
            current_weight_label = MDLabel(
                text=f"Current Weight: {current_weight} kg",
                adaptive_height=True
            )
            content.add_widget(current_weight_label)

        # Target weight field
        target_weight_field = MDTextField(
            hint_text="Target Weight (kg)",
            mode="outlined",
            input_filter="float",
            text=str(self.target_weight) if self.target_weight else ""
        )
        content.add_widget(target_weight_field)

        # Target date field
        today = datetime.now().strftime("%Y-%m-%d")
        target_date_field = MDTextField(
            hint_text="Target Date (YYYY-MM-DD)",
            mode="outlined",
            text=self.target_date if self.target_date else today
        )
        content.add_widget(target_date_field)

        self.target_dialog = MDDialog(
            MDDialogHeadlineText(text="Set Weight Target"),
            MDDialogContentContainer(content),
            MDDialogButtonContainer(
                MDButton(
                    MDButtonText(text="Cancel"),
                    style="text",
                    on_release=lambda x: self.target_dialog.dismiss()
                ),
                MDButton(
                    MDButtonText(text="Save"),
                    style="text",
                    on_release=lambda x: self.save_target(target_weight_field.text, target_date_field.text)
                ),
                MDButton(
                    MDButtonText(text="Clear Target"),
                    style="text",
                    on_release=lambda x: self.clear_target()
                ),
                spacing="8dp"
            ),
            auto_dismiss=False
        )
        self.target_dialog.open()

    def save_target(self, weight_text, date_text):
        """Save the weight target to the database."""
        try:
            target_weight = float(weight_text)
            if target_weight <= 0:
                self.show_error_dialog("Target weight must be a positive number.")
                return

            # Validate date format
            try:
                datetime.strptime(date_text, "%Y-%m-%d")
            except ValueError:
                self.show_error_dialog("Invalid date format. Use YYYY-MM-DD.")
                return

            # Update animal record with target weight and date
            success = database.execute_query(
                "UPDATE animals SET target_weight = ?, target_date = ? WHERE id = ?",
                (target_weight, date_text, self.animal_id)
            )

            if not success:
                self.show_error_dialog("Failed to update target weight. Please try again.")
                return

            # Update local properties
            self.target_weight = target_weight
            self.target_date = date_text

            # Dismiss dialog and update UI
            self.target_dialog.dismiss()
            self.load_weight_history()  # This will also update the target UI
            self.show_success_dialog("Weight target set successfully!")

        except ValueError:
            self.show_error_dialog("Please enter a valid weight.")

    def clear_target(self):
        """Clear the weight target."""
        # Update animal record to clear target weight and date
        success = database.execute_query(
            "UPDATE animals SET target_weight = NULL, target_date = NULL WHERE id = ?",
            (self.animal_id,)
        )

        if not success:
            self.show_error_dialog("Failed to clear target weight. Please try again.")
            return

        # Update local properties
        self.target_weight = None
        self.target_date = ""

        # Dismiss dialog and update UI
        self.target_dialog.dismiss()
        self.load_weight_history()  # This will also update the target UI
        self.show_success_dialog("Weight target cleared successfully!")

    def load_assessments(self):
        app = MDApp.get_running_app()
        """Load and display assessments."""
        if not hasattr(self, 'ids') or not self.ids or not hasattr(self.ids, 'assessments_container'):
            return

        self.ids.assessments_container.clear_widgets()

        # Get assessments using the new execute_query function
        assessments = database.execute_query(
            """
            SELECT id, date, scale_used, result FROM assessments
            WHERE animal_id = ? ORDER BY date DESC
            """,
            (self.animal_id,),
            fetch_mode='all'
        )


        if not assessments:
            empty_label = MDLabel(
                text="No assessments found",
                halign="center",
                size_hint_y=None,
                height=dp(40)
            )
            self.ids.assessments_container.add_widget(empty_label)
            return

        for index, (assessment_id, date, scale, result) in enumerate(assessments):
            try:
                result_data = json.loads(result)
                if isinstance(result_data, dict) and "score" in result_data and "interpretation" in result_data:
                    result_display = f"{result_data['score']} - {result_data['interpretation']}"
                else:
                    result_display = result
            except (json.JSONDecodeError, TypeError):
                result_display = result

            bg_color = get_color_from_hex("#f0f0f0") if index % 2 == 0 else get_color_from_hex("#ffffff")

            # Entire row
            row = MDBoxLayout(
                orientation="horizontal",
                size_hint_y=None,
                height=dp(48),
                padding=[dp(8), 0, dp(8), 0],
                spacing=dp(8),
                md_bg_color=bg_color
            )

            # Make entire left section clickable
            clickable_box = MDBoxLayout(
                orientation="horizontal",
                size_hint_x=0.9,
                spacing=dp(8)
            )
            clickable_box.add_widget(MDLabel(text=date, size_hint_x=0.25))
            clickable_box.add_widget(MDLabel(text=scale, size_hint_x=0.35))
            clickable_box.add_widget(MDLabel(text=result_display, size_hint_x=0.4))



            clickable_box.bind(
                on_touch_down=lambda inst, touch, aid=assessment_id, anid=self.animal_id: (
                    self.show_assessment_details(aid,anid)
                    if inst.collide_point(*touch.pos) and not touch.is_double_tap else None
                )
            )

            delete_btn = MDIconButton(
                icon="trash-can-outline",
                style="standard",
                pos_hint={"center_y": 0.5},
                on_release=lambda x, aid=assessment_id: app.screen_manager.get_screen("assessments").delete_assessment(
                    aid)
            )

            row.add_widget(clickable_box)
            row.add_widget(delete_btn)

            self.ids.assessments_container.add_widget(row)

    def show_success_dialog(self, message):
        """Display a success dialog with the provided message."""
        if self.dialog:
            self.dialog.dismiss()

        self.dialog = MDDialog(
            MDDialogHeadlineText(text="Success"),
            MDDialogContentContainer(
                MDLabel(text=message, theme_text_color="Custom", text_color=(0, 0.5, 0, 1))
            ),
            MDDialogButtonContainer(
                MDButton(
                    MDButtonText(text="OK"),
                    on_release=lambda x: self.dialog.dismiss()
                )
            ),
        )
        self.dialog.open()

    def show_assessment_details(self,assessment_id, animal_id):
        """Forward to the assessment screen to show details"""
        app = MDApp.get_running_app()
        assessments_screen = app.screen_manager.get_screen("assessments")
        assessments_screen.show_assessment_details(assessment_id, animal_id)

    def show_error_dialog(self, message):
        """Display an error dialog with the provided message."""
        if self.dialog:
            self.dialog.dismiss()

        self.dialog = MDDialog(
            MDDialogHeadlineText(text="Error"),
            MDDialogContentContainer(
                MDLabel(text=message, theme_text_color="Custom", text_color=(1, 0, 0, 1))
            ),
            MDDialogButtonContainer(
                MDButton(
                    MDButtonText(text="Close"),
                    on_release=lambda x: self.dialog.dismiss()
                )
            ),
        )
        self.dialog.open()

    def show_add_weight_dialog(self):
        """Show dialog to add a new weight entry."""
        today = datetime.now().strftime("%Y-%m-%d")

        content = MDBoxLayout(
            orientation="vertical",
            spacing="16dp",
            adaptive_height=True,
            padding=["16dp", "16dp", "16dp", "0dp"]
        )

        # Weight input
        weight_field = MDTextField(
            hint_text="Weight (kg)",
            mode="outlined",
            input_filter="float"
        )
        content.add_widget(weight_field)

        # Date input (default to today)
        date_field = MDTextField(
            hint_text="Date (YYYY-MM-DD)",
            mode="outlined",
            text=today
        )
        content.add_widget(date_field)

        self.weight_dialog = MDDialog(
            MDDialogHeadlineText(text="Add Weight Record"),
            MDDialogContentContainer(content),
            MDDialogButtonContainer(
                MDButton(
                    MDButtonText(text="Cancel"),
                    style="text",
                    on_release=lambda x: self.weight_dialog.dismiss()
                ),
                MDButton(
                    MDButtonText(text="Add"),
                    style="text",
                    on_release=lambda x: self.save_weight_record(weight_field.text, date_field.text)
                ),
                spacing="8dp"
            ),
            auto_dismiss=False
        )
        self.weight_dialog.open()

    def save_weight_record(self, weight_text, date_text):
        """Validate and save new weight entry."""
        try:
            weight = float(weight_text)
            if weight <= 0:
                self.show_error_dialog("Weight must be a positive number.")
                return

            # Validate date
            try:
                datetime.strptime(date_text, "%Y-%m-%d")
            except ValueError:
                self.show_error_dialog("Invalid date format. Use YYYY-MM-DD.")
                return

            success = database.add_weight_record(self.animal_id, date_text, weight)
            if success:
                self.weight_dialog.dismiss()
                self.load_weight_history()
                self.show_success_dialog("Weight record added successfully.")
            else:
                self.show_error_dialog("Failed to save weight. Please try again.")

        except ValueError:
            self.show_error_dialog("Please enter a valid weight.")

    def delete_weight(self, weight_id):
        """Delete a weight record from the database."""
        # Show confirmation dialog
        self.dialog = MDDialog(
            MDDialogHeadlineText(text="Confirm Deletion"),
            MDDialogContentContainer(
                MDLabel(text="Are you sure you want to delete this weight record?")
            ),
            MDDialogButtonContainer(
                MDButton(
                    MDButtonText(text="Cancel"),
                    style="text",
                    on_release=lambda x: self.dialog.dismiss()
                ),
                MDButton(
                    MDButtonText(text="Delete"),
                    style="elevated",
                    on_release=lambda x: self.perform_weight_delete(weight_id)
                ),
                spacing="8dp"
            ),
            auto_dismiss=False
        )
        self.dialog.open()

    def perform_weight_delete(self, weight_id):
        """Actually delete the weight record after confirmation."""
        success = database.delete_weight_record(weight_id)
        self.dialog.dismiss()

        if success:
            self.load_weight_history()
            self.show_success_dialog("Weight record deleted successfully.")
        else:
            self.show_error_dialog("Failed to delete weight record.")