from kivy.uix.screenmanager import Screen
from kivymd.uix.label import MDLabel
from kivymd.uix.screen import MDScreen
from kivymd.uix.list import MDList, MDListItem, MDListItemHeadlineText, MDListItemSupportingText
from kivymd.uix.button import MDButton, MDButtonText
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.dialog import MDDialog, MDDialogHeadlineText, MDDialogContentContainer, MDDialogButtonContainer
from kivymd.uix.textfield import MDTextField
from kivymd.uix.menu import MDDropdownMenu
from datetime import datetime
from functools import partial
from kivy.metrics import dp

import database


class AssessmentsScreen(MDScreen):
    """Screen for displaying and managing assessments."""

    assessment_scales = {
        "Rat": ["Body Condition Score", "Grimace Scale", "Activity Score"],
        "Mouse": ["Mouse Grimace Scale", "BCS Mouse", "Activity Level"],
        "Rabbit": ["Rabbit Grimace Scale", "Body Condition Score", "Wellness Score"],
        "Goat": ["FAMACHA Score", "Body Condition Score", "Pain Scale"],
        "Sheep": ["FAMACHA Score", "Body Condition Score", "Lameness Score"],
        "Pig": ["Body Condition Score", "Lameness Score", "Welfare Assessment"]
    }

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.dialog = None
        self.menu = None
        self.animal_menu = None
        self.scale_menu = None
        self.selected_scale = None
        self.selected_animal_id = None
        self.selected_animal_species = None
        self.assessment_dialog = None
        self.detail_dialog = None
        self.confirm_dialog = None
        self.success_dialog = None
        self.error_dialog = None
        self.animal_field = None
        self.scale_field = None

    def on_enter(self):
        """Refresh assessments when entering the screen."""
        self.load_assessments()

    def load_assessments(self):
        """Load all assessments into the list."""
        self.ids.assessments_list.clear_widgets()

        # Get all assessments with animal names
        conn = database.get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT a.id, a.date, a.scale_used, a.result, n.name, n.species, a.animal_id
            FROM assessments a
            JOIN animals n ON a.animal_id = n.id
            ORDER BY a.date DESC
        """)

        assessments = cursor.fetchall()
        conn.close()

        if not assessments:
            # Show empty state
            empty_item = MDListItem()
            empty_item.add_widget(MDListItemHeadlineText(text="No assessments recorded"))
            self.ids.assessments_list.add_widget(empty_item)
            return

        # Add assessments to the list
        for assessment in assessments:
            a_id = assessment[0]
            animal_id = assessment[6]

            item = MDListItem()
            item.add_widget(MDListItemHeadlineText(text=assessment[1]))  # Date
            item.add_widget(
                MDListItemHeadlineText(text=f"{assessment[4]} ({assessment[5]})"))  # Animal name and species
            item.add_widget(MDListItemSupportingText(text=f"{assessment[2]}: {assessment[3]}"))  # Scale and result

            # Use a separate binding method to avoid lambda issues
            item.bind(on_release=partial(self.on_assessment_item_click, a_id, animal_id))

            self.ids.assessments_list.add_widget(item)

    def on_assessment_item_click(self, assessment_id, animal_id, instance):
        """Handle assessment item click event"""
        self.show_assessment_details(assessment_id, animal_id)

    def show_new_assessment_dialog(self, *args):
        """Show dialog to create a new assessment."""
        # First, get a list of animals
        conn = database.get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, species FROM animals ORDER BY name")
        animals = cursor.fetchall()
        conn.close()

        if not animals:
            # Show error if no animals available
            self.dialog = MDDialog(
                MDDialogHeadlineText(text="No Animals"),
                MDDialogContentContainer(
                    MDLabel(text="You need to add animals before creating assessments.")
                ),
                MDDialogButtonContainer(
                    MDButton(
                        MDButtonText(text="OK"),
                        style="text",
                        on_release=lambda x: self.dialog.dismiss()
                    )
                )
            )
            self.dialog.open()
            return

        # Create dialog for animal selection
        content = MDBoxLayout(
            orientation="vertical",
            spacing="12dp",
            padding=["20dp", "20dp", "20dp", "20dp"],
            adaptive_height=True
        )

        # Create animal selection dropdown
        self.animal_field = MDTextField(
            hint_text="Select Animal",
            mode="outlined",
            id="animal_selector"
        )
        self.animal_field.bind(focus=self.show_animal_menu)
        content.add_widget(self.animal_field)

        # Create the dialog
        self.dialog = MDDialog(
            MDDialogHeadlineText(text="New Assessment"),
            MDDialogContentContainer(content),
            MDDialogButtonContainer(
                MDButton(
                    MDButtonText(text="Cancel"),
                    style="text",
                    on_release=lambda x: self.dialog.dismiss()
                ),
                MDButton(
                    MDButtonText(text="Continue"),
                    style="text",
                    on_release=lambda x: self.continue_assessment()
                ),
                spacing="8dp"
            ),
            auto_dismiss=False
        )
        self.dialog.open()

    def show_animal_menu(self, field_widget, focus):
        """Show dropdown menu for animal selection"""
        if not focus:
            return

        # Get animals from database
        conn = database.get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, species FROM animals ORDER BY name")
        animals = cursor.fetchall()
        conn.close()

        menu_items = []
        for animal in animals:
            animal_id = animal[0]
            animal_name = animal[1]
            animal_species = animal[2]
            menu_items.append({
                "text": f"{animal_name} ({animal_species})",
                "on_release": partial(self.select_animal_for_assessment, animal_id, animal_species)
            })

        self.animal_menu = MDDropdownMenu(
            caller=field_widget,
            items=menu_items,
            width_mult=4,
            position="bottom"
        )
        self.animal_menu.open()

    def select_animal_for_assessment(self, animal_id, species, *args):
        """Select an animal for the assessment."""
        self.selected_animal_id = animal_id
        self.selected_animal_species = species
        self.animal_field.text = f"{species} (ID: {animal_id})"
        if self.animal_menu:
            self.animal_menu.dismiss()

    def continue_assessment(self):
        """Continue with assessment after animal selection."""
        if not self.selected_animal_id:
            return

        self.dialog.dismiss()

        # Get assessment scales for the selected species
        scales = self.assessment_scales.get(self.selected_animal_species, ["General Assessment"])

        # Create dialog for assessment details
        content = MDBoxLayout(
            orientation="vertical",
            spacing="12dp",
            padding=["20dp", "20dp", "20dp", "20dp"],
            adaptive_height=True
        )

        # Create scale selection dropdown
        self.scale_field = MDTextField(
            hint_text="Select Assessment Scale",
            mode="outlined",
            id="scale_selector"
        )
        self.scale_field.bind(focus=partial(self.show_scale_menu, scales))
        content.add_widget(self.scale_field)

        # Add result field
        result_field = MDTextField(
            hint_text="Assessment Result",
            mode="outlined",
            id="result_field"
        )
        content.add_widget(result_field)

        # Create the dialog
        self.assessment_dialog = MDDialog(
            MDDialogHeadlineText(text="Enter Assessment"),
            MDDialogContentContainer(content),
            MDDialogButtonContainer(
                MDButton(
                    MDButtonText(text="Cancel"),
                    style="text",
                    on_release=lambda x: self.assessment_dialog.dismiss()
                ),
                MDButton(
                    MDButtonText(text="Save"),
                    style="elevated",
                    on_release=lambda x: self.save_assessment(self.scale_field.text, result_field.text)
                ),
                spacing="8dp"
            ),
            auto_dismiss=False
        )
        self.assessment_dialog.open()

    def show_scale_menu(self, scales, field_widget, focus):
        """Show dropdown menu for scale selection"""
        if not focus:
            return

        menu_items = []
        for scale in scales:
            menu_items.append({
                "text": scale,
                "on_release": partial(self.select_scale, scale)
            })

        self.scale_menu = MDDropdownMenu(
            caller=field_widget,
            items=menu_items,
            width_mult=4,
            position="bottom"
        )
        self.scale_menu.open()

    def select_scale(self, scale, *args):
        """Select an assessment scale."""
        self.selected_scale = scale
        self.scale_field.text = scale
        if self.scale_menu:
            self.scale_menu.dismiss()

    def save_assessment(self, scale, result):
        """Save the assessment to the database."""
        if not scale or not result:
            return

        today = datetime.now().strftime("%Y-%m-%d")
        success = database.add_assessment(self.selected_animal_id, today, scale, result)

        if success:
            self.assessment_dialog.dismiss()
            self.load_assessments()
            self.show_success_dialog("Assessment saved successfully!")
        else:
            self.show_error_dialog("Failed to save assessment.")

    def show_assessment_details(self, assessment_id, animal_id):
        """Show details of an assessment."""
        conn = database.get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT a.date, a.scale_used, a.result, n.name, n.species
            FROM assessments a
            JOIN animals n ON a.animal_id = n.id
            WHERE a.id = ?
        """, (assessment_id,))

        assessment = cursor.fetchone()
        conn.close()

        if not assessment:
            return

        content = MDBoxLayout(
            orientation="vertical",
            spacing="8dp",
            padding=["16dp", "16dp", "16dp", "16dp"],
            adaptive_height=True
        )

        # Add assessment details
        content.add_widget(MDLabel(text=f"Animal: {assessment[3]} ({assessment[4]})"))
        content.add_widget(MDLabel(text=f"Date: {assessment[0]}"))
        content.add_widget(MDLabel(text=f"Assessment Scale: {assessment[1]}"))
        content.add_widget(MDLabel(text=f"Result: {assessment[2]}"))

        # Create action buttons
        actions = MDBoxLayout(
            orientation="horizontal",
            spacing="8dp",
            adaptive_height=True
        )

        # Add view animal button
        view_button = MDButton(
            style="outlined",
            on_release=lambda x: self.view_animal(animal_id)
        )
        view_button.add_widget(MDButtonText(text="View Animal"))
        actions.add_widget(view_button)

        # Add delete button
        delete_button = MDButton(
            style="outlined",
            on_release=lambda x: self.confirm_delete_assessment(assessment_id)
        )
        delete_button.add_widget(MDButtonText(text="Delete Assessment", text_color="red"))
        actions.add_widget(delete_button)

        content.add_widget(actions)

        # Show dialog
        self.detail_dialog = MDDialog(
            MDDialogHeadlineText(text="Assessment Details"),
            MDDialogContentContainer(content),
            MDDialogButtonContainer(
                MDButton(
                    MDButtonText(text="OK"),
                    style="text",
                    on_release=lambda x: self.detail_dialog.dismiss()
                )
            )
        )
        self.detail_dialog.open()

    def view_animal(self, animal_id):
        """Navigate to animal details screen."""
        self.detail_dialog.dismiss()
        animal_detail_screen = self.manager.get_screen('animal_detail')
        animal_detail_screen.set_animal_id(animal_id)
        self.manager.current = 'animal_detail'

    def confirm_delete_assessment(self, assessment_id):
        """Confirm before deleting an assessment."""
        self.detail_dialog.dismiss()

        # Create confirmation dialog
        self.confirm_dialog = MDDialog(
            MDDialogHeadlineText(text="Confirm Deletion"),
            MDDialogContentContainer(
                MDLabel(text="Are you sure you want to delete this assessment?")
            ),
            MDDialogButtonContainer(
                MDButton(
                    MDButtonText(text="Cancel"),
                    style="text",
                    on_release=lambda x: self.confirm_dialog.dismiss()
                ),
                MDButton(
                    MDButtonText(text="Delete"),
                    style="elevated",
                    on_release=lambda x: self.delete_assessment(assessment_id)
                ),
                spacing="8dp"
            ),
            auto_dismiss=False
        )
        self.confirm_dialog.open()

    def delete_assessment(self, assessment_id):
        """Delete the assessment from the database."""
        success = database.delete_assessment(assessment_id)
        self.confirm_dialog.dismiss()

        if success:
            self.load_assessments()
            self.show_success_dialog("Assessment deleted successfully!")
        else:
            self.show_error_dialog("Failed to delete assessment.")

    def show_success_dialog(self, message):
        """Show a success dialog."""
        self.success_dialog = MDDialog(
            MDDialogHeadlineText(text="Success"),
            MDDialogContentContainer(
                MDLabel(text=message)
            ),
            MDDialogButtonContainer(
                MDButton(
                    MDButtonText(text="OK"),
                    style="text",
                    on_release=lambda x: self.success_dialog.dismiss()
                )
            )
        )
        self.success_dialog.open()

    def show_error_dialog(self, message):
        """Show an error dialog."""
        self.error_dialog = MDDialog(
            MDDialogHeadlineText(text="Error"),
            MDDialogContentContainer(
                MDLabel(text=message)
            ),
            MDDialogButtonContainer(
                MDButton(
                    MDButtonText(text="OK"),
                    style="text",
                    on_release=lambda x: self.error_dialog.dismiss()
                )
            )
        )
        self.error_dialog.open()