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
import json

import database
from assessment_scales import ASSESSMENT_SCALES


class AssessmentsScreen(MDScreen):
    """Screen for displaying and managing assessments."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.dialog = None
        self.menu = None
        self.animal_menu = None
        self.scale_menu = None
        self.selected_scale = None
        self.selected_animal_id = None
        self.selected_animal_species = None
        self.selected_animal_name = None
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
            result_text = assessment[3]

            # Try to parse JSON result for richer display
            try:
                result_data = json.loads(result_text)
                if isinstance(result_data, dict) and "score" in result_data and "interpretation" in result_data:
                    result_display = f"{assessment[2]}: {result_data['score']} - {result_data['interpretation']}"
                else:
                    result_display = f"{assessment[2]}: {result_text}"
            except (json.JSONDecodeError, TypeError):
                # Not JSON or parsing failed, use raw text
                result_display = f"{assessment[2]}: {result_text}"

            item = MDListItem(
                on_release=partial(self.on_assessment_item_click, a_id, animal_id)
            )
            # Add headline text (date)
            item.add_widget(MDListItemHeadlineText(text=assessment[1]))  # Date

            # Add animal info
            item.add_widget(
                MDListItemHeadlineText(text=f"{assessment[4]} ({assessment[5]})"))  # Animal name and species

            # Add result info
            item.add_widget(MDListItemSupportingText(text=result_display))

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
                "on_release": partial(self.select_animal_for_assessment, animal_id, animal_name, animal_species)
            })

        self.animal_menu = MDDropdownMenu(
            caller=field_widget,
            items=menu_items,
            width_mult=4,
            position="bottom"
        )
        self.animal_menu.open()

    def select_animal_for_assessment(self, animal_id, animal_name, species, *args):
        """Select an animal for the assessment."""
        self.selected_animal_id = animal_id
        self.selected_animal_name = animal_name
        self.selected_animal_species = species
        self.animal_field.text = f"{animal_name} ({species})"
        if self.animal_menu:
            self.animal_menu.dismiss()

    def continue_assessment(self):
        """Continue with assessment after animal selection."""
        if not self.selected_animal_id:
            return

        self.dialog.dismiss()

        # Get assessment scales for the selected species
        if self.selected_animal_species in ASSESSMENT_SCALES:
            scales = list(ASSESSMENT_SCALES[self.selected_animal_species].keys())
        else:
            scales = ["General Assessment"]

        # Create dialog for scale selection
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

        # Create the dialog
        self.assessment_dialog = MDDialog(
            MDDialogHeadlineText(text="Select Assessment Scale"),
            MDDialogContentContainer(content),
            MDDialogButtonContainer(
                MDButton(
                    MDButtonText(text="Cancel"),
                    style="text",
                    on_release=lambda x: self.assessment_dialog.dismiss()
                ),
                MDButton(
                    MDButtonText(text="Start Assessment"),
                    style="elevated",
                    on_release=lambda x: self.start_detailed_assessment()
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

    def start_detailed_assessment(self):
        """Start a detailed assessment using the selected scale."""
        if not self.selected_scale or not self.selected_animal_id:
            return

        # Dismiss the dialog
        self.assessment_dialog.dismiss()

        # Get app instance to access the screen manager
        from kivymd.app import MDApp
        app = MDApp.get_running_app()

        # Get the detailed assessment screen
        detailed_screen = app.screen_manager.get_screen('detailed_assessment')

        # Set up the assessment parameters
        detailed_screen.set_assessment_params(
            self.selected_animal_id,
            self.selected_animal_name,
            self.selected_animal_species,
            self.selected_scale
        )

        # Switch to the detailed assessment screen
        app.screen_manager.current = 'detailed_assessment'

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

        # Try to parse JSON result
        result_text = assessment[2]
        try:
            result_data = json.loads(result_text)
            if isinstance(result_data, dict):
                # Format JSON content for display
                content = self.format_assessment_result(result_data, assessment[0], assessment[1], assessment[3],
                                                        assessment[4])
            else:
                # Fall back to simple display
                content = self.create_simple_assessment_content(assessment)
        except (json.JSONDecodeError, TypeError):
            # Not JSON or parsing failed, use simple display
            content = self.create_simple_assessment_content(assessment)

        # Show dialog
        self.detail_dialog = MDDialog(
            MDDialogHeadlineText(text="Assessment Details"),
            MDDialogContentContainer(content),
            MDDialogButtonContainer(
                MDButton(
                    MDButtonText(text="View Animal"),
                    style="outlined",
                    on_release=lambda x: self.view_animal(animal_id)
                ),
                MDButton(
                    MDButtonText(text="Delete", text_color="red"),
                    style="text",
                    on_release=lambda x: self.confirm_delete_assessment(assessment_id),

                ),
                MDButton(
                    MDButtonText(text="Close"),
                    style="text",
                    on_release=lambda x: self.detail_dialog.dismiss()
                ),
                spacing="8dp"
            )
        )
        self.detail_dialog.open()

    def format_assessment_result(self, result_data, date, scale, animal_name, animal_species):
        """Format JSON assessment result for display."""
        content = MDBoxLayout(
            orientation="vertical",
            spacing="8dp",
            padding=["16dp", "16dp", "16dp", "16dp"],
            adaptive_height=True
        )

        # Add animal and scale info
        content.add_widget(MDLabel(text=f"Animal: {animal_name} ({animal_species})"))
        content.add_widget(MDLabel(text=f"Date: {date}"))
        content.add_widget(MDLabel(text=f"Assessment Scale: {scale}"))

        # Add score and interpretation if available
        if "score" in result_data:
            score_label = MDLabel(text=f"Score: {result_data['score']}")
            content.add_widget(score_label)

        if "interpretation" in result_data:
            interp_label = MDLabel(text=f"Result: {result_data['interpretation']}")
            content.add_widget(interp_label)

        # Add details if available
        if "details" in result_data and isinstance(result_data["details"], list):
            content.add_widget(MDLabel(text="Assessment Details:", font_style="Title", role="small"))

            for detail in result_data["details"]:
                if isinstance(detail, dict):
                    detail_box = MDBoxLayout(
                        orientation="vertical",
                        adaptive_height=True,
                        padding=("8dp", "4dp")
                    )

                    if "question" in detail:
                        detail_box.add_widget(MDLabel(text=detail["question"], font_style="Body", role="medium"))

                    if "answer" in detail:
                        answer_text = f"Answer: {detail['answer']}"
                        if "score" in detail:
                            answer_text += f" (Score: {detail['score']})"
                        detail_box.add_widget(MDLabel(text=answer_text, font_style="Body", role="small"))

                    content.add_widget(detail_box)

        return content

    def create_simple_assessment_content(self, assessment):
        """Create simple content display for non-JSON assessment result."""
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

        return content