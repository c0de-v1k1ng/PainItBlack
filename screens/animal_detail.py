from kivy.uix.screenmanager import Screen
from kivymd.uix.screen import MDScreen
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDButton, MDButtonText
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.dialog import MDDialog, MDDialogHeadlineText, MDDialogContentContainer, MDDialogButtonContainer
from kivymd.uix.fitimage import FitImage

import database
import os
from datetime import datetime


class AnimalDetailScreen(MDScreen):
    """Screen for displaying detailed information about a specific animal."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.animal_id = None
        self.dialog = None

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

        conn = database.get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT date, weight FROM weight_history
            WHERE animal_id = ? ORDER BY date DESC
        """, (self.animal_id,))

        weights = cursor.fetchall()
        conn.close()

        if not weights:
            self.ids.weight_history_container.add_widget(
                MDLabel(text="No weight records found", halign="center")
            )
            return

        # Add weight history entries
        for date, weight in weights:
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
                text="Delete",
                on_release=lambda x, d=date: self.delete_weight(d)
            )

            entry.add_widget(date_label)
            entry.add_widget(weight_label)
            entry.add_widget(delete_btn)

            self.ids.weight_history_container.add_widget(entry)

    def load_assessments(self):
        """Load and display assessments."""
        self.ids.assessments_container.clear_widgets()

        conn = database.get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT date, scale_used, result FROM assessments
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
        for date, scale, result in assessments:
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
        self.dialog = MDDialog(
            MDDialogHeadlineText(text="Add Weight Record"),
            MDDialogContentContainer(
                MDBoxLayout(
                    orientation="vertical",
                    spacing="10dp",
                    padding=["20dp", "20dp", "20dp", "20dp"],
                    adaptive_height=True,
                    id="weight_dialog_content"
                )
            ),
            MDDialogButtonContainer(
                MDButton(
                    MDButtonText(text="Cancel"),
                    style="text",
                    on_release=lambda x: self.dialog.dismiss()
                ),
                MDButton(
                    MDButtonText(text="Save"),
                    style="elevated",
                    on_release=lambda x: self.save_weight()
                ),
                spacing="8dp"
            ),
            auto_dismiss=False
        )
        self.dialog.open()

    def save_weight(self):
        """Save new weight record to database."""
        # Implementation will go here
        self.dialog.dismiss()
        self.load_weight_history()

    def delete_weight(self, date):
        """Delete a weight record."""
        # Show confirmation dialog
        confirm_dialog = MDDialog(
            MDDialogHeadlineText(text="Confirm Deletion"),
            MDDialogContentContainer(
                MDLabel(text=f"Are you sure you want to delete the weight record from {date}?")
            ),
            MDDialogButtonContainer(
                MDButton(
                    MDButtonText(text="Cancel"),
                    style="text",
                    on_release=lambda x: confirm_dialog.dismiss()
                ),
                MDButton(
                    MDButtonText(text="Delete"),
                    style="elevated",
                    on_release=lambda x: self.confirm_delete_weight(date, confirm_dialog)
                ),
                spacing="8dp"
            ),
            auto_dismiss=False
        )
        confirm_dialog.open()

    def confirm_delete_weight(self, date, dialog):
        """Confirm and perform weight record deletion."""
        conn = database.get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            DELETE FROM weight_history
            WHERE animal_id = ? AND date = ?
        """, (self.animal_id, date))

        conn.commit()
        conn.close()
        dialog.dismiss()
        self.load_weight_history()