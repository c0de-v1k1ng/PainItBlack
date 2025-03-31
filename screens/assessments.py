from kivy.uix.screenmanager import Screen
from kivy.uix.scrollview import ScrollView
from kivy.utils import get_color_from_hex
from kivymd.uix.card import MDCard
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

    def show_new_assessment_dialog(self, animal_id=None):
        """Show dialog to create a new assessment, optionally preselecting an animal."""

        # Get a list of all animals
        conn = database.get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, species FROM animals ORDER BY name")
        animals = cursor.fetchall()
        conn.close()

        if not animals:
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

        # Create dialog content layout
        content = MDBoxLayout(
            orientation="vertical",
            spacing="12dp",
            padding=["20dp", "20dp", "20dp", "20dp"],
            adaptive_height=True
        )

        # Create the animal selection field
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

        # Preselect the given animal if provided
        if animal_id is not None:
            for a_id, name, species in animals:
                if a_id == animal_id:
                    self.select_animal_for_assessment(a_id, name, species)
                    break

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

        # Create button container with balanced spacing
        buttons = MDDialogButtonContainer(
            #adaptive_width=True,
            spacing=dp(8),
            padding=[dp(8), dp(8), dp(8), dp(8)]
        )

        # Create individual buttons with proper spacing
        view_button = MDButton(
            style="outlined",
            on_release=lambda x: self.view_animal(animal_id)
        )
        view_button.add_widget(MDButtonText(text="View Animal"))

        delete_button = MDButton(
            style="text",
            on_release=lambda x: self.confirm_delete_assessment(assessment_id)
        )
        delete_button.add_widget(MDButtonText(text="Delete", text_color="red"))

        close_button = MDButton(
            style="text",
            on_release=lambda x: self.detail_dialog.dismiss()
        )
        close_button.add_widget(MDButtonText(text="Close"))

        # Add buttons to container
        buttons.add_widget(view_button)
        buttons.add_widget(delete_button)
        buttons.add_widget(close_button)

        # Show dialog with better sizing
        self.detail_dialog = MDDialog(
            MDDialogHeadlineText(
                text="Assessment Details",
                halign="center"
            ),
            MDDialogContentContainer(content),
            buttons,
            size_hint=(0.9, None),  # Allow dialog to be wider
            # Let height be determined automatically
        )
        self.detail_dialog.open()

    def format_assessment_result(self, result_data, date, scale, animal_name, animal_species):
        """Format JSON assessment result for display."""
        content = MDBoxLayout(
            orientation="vertical",
            spacing=dp(12),
            padding=[dp(16), dp(16), dp(16), dp(16)],
            adaptive_height=True,
            size_hint_y=None,
            # Calculate height based on content but ensure minimum height
            height=dp(400)  # Start with a reasonable height
        )

        # Create a scrollable container for all content to handle overflow
        scroll_container = ScrollView(
            size_hint=(1, None),
            height=dp(360)  # Fixed height for scroll area
        )

        scroll_content = MDBoxLayout(
            orientation="vertical",
            spacing=dp(12),
            adaptive_height=True,
            size_hint_y=None
        )

        # Add animal and scale info
        info_box = MDBoxLayout(
            orientation="vertical",
            spacing=dp(4),
            adaptive_height=True,
            size_hint_y=None
        )

        info_box.add_widget(MDLabel(
            text=f"Animal: {animal_name} ({animal_species})",
            adaptive_height=True,
            size_hint_y=None,
            height=dp(24)
        ))

        info_box.add_widget(MDLabel(
            text=f"Date: {date}",
            adaptive_height=True,
            size_hint_y=None,
            height=dp(24)
        ))

        info_box.add_widget(MDLabel(
            text=f"Assessment Scale: {scale}",
            adaptive_height=True,
            size_hint_y=None,
            height=dp(24)
        ))

        scroll_content.add_widget(info_box)

        # Add divider
        divider = MDBoxLayout(
            size_hint_y=None,
            height=dp(1),
            md_bg_color=get_color_from_hex("#CCCCCC")
        )
        scroll_content.add_widget(divider)

        # Add score and interpretation if available
        if "score" in result_data or "interpretation" in result_data:
            result_box = MDBoxLayout(
                orientation="vertical",
                spacing=dp(4),
                adaptive_height=True,
                size_hint_y=None
            )

            if "score" in result_data:
                result_box.add_widget(MDLabel(
                    text=f"Score: {result_data['score']}",
                    font_style="Title",
                    role="medium",
                    adaptive_height=True,
                    size_hint_y=None,
                    height=dp(30)
                ))

            if "interpretation" in result_data:
                # Get appropriate color based on interpretation text
                color = get_color_from_hex("#4CAF50")  # Default green
                if "moderate" in result_data["interpretation"].lower():
                    color = get_color_from_hex("#FF9800")  # Orange
                elif "severe" in result_data["interpretation"].lower() or "urgent" in result_data[
                    "interpretation"].lower():
                    color = get_color_from_hex("#F44336")  # Red

                result_box.add_widget(MDLabel(
                    text=f"Result: {result_data['interpretation']}",
                    font_style="Title",
                    role="small",
                    theme_text_color="Custom",
                    text_color=color,
                    adaptive_height=True,
                    size_hint_y=None,
                    height=dp(30)
                ))

            scroll_content.add_widget(result_box)

            # Add another divider
            scroll_content.add_widget(MDBoxLayout(
                size_hint_y=None,
                height=dp(1),
                md_bg_color=get_color_from_hex("#CCCCCC")
            ))

        # Add details if available
        if "details" in result_data and isinstance(result_data["details"], list):
            details_label = MDLabel(
                text="Assessment Details:",
                font_style="Title",
                role="small",
                adaptive_height=True,
                size_hint_y=None,
                height=dp(40)
            )
            scroll_content.add_widget(details_label)

            for detail in result_data["details"]:
                if isinstance(detail, dict):
                    detail_box = MDCard(
                        orientation="vertical",
                        adaptive_height=True,
                        size_hint_y=None,
                        height=dp(80),
                        padding=[dp(12), dp(8), dp(12), dp(8)],
                        margin=dp(4),
                        elevation=1
                    )

                    if "question" in detail:
                        question_label = MDLabel(
                            text=detail["question"],
                            font_style="Body",
                            role="medium",
                            adaptive_height=True,
                            size_hint_y=None,
                            height=dp(24)
                        )
                        detail_box.add_widget(question_label)

                    if "answer" in detail:
                        answer_text = f"Answer: {detail['answer']}"
                        if "score" in detail:
                            answer_text += f" (Score: {detail['score']})"

                        answer_label = MDLabel(
                            text=answer_text,
                            font_style="Body",
                            role="small",
                            adaptive_height=True,
                            size_hint_y=None,
                            height=dp(24)
                        )
                        detail_box.add_widget(answer_label)

                    scroll_content.add_widget(detail_box)

                    # Add spacing after each detail item
                    scroll_content.add_widget(MDBoxLayout(
                        size_hint_y=None,
                        height=dp(4)
                    ))

        # Add the scroll content to the scroll container
        scroll_container.add_widget(scroll_content)

        # Add the scroll container to the main content box
        content.add_widget(scroll_container)

        return content

    def create_simple_assessment_content(self, assessment):
        """Create simple content display for non-JSON assessment result."""
        content = MDBoxLayout(
            orientation="vertical",
            spacing=dp(12),
            padding=[dp(16), dp(16), dp(16), dp(16)],
            adaptive_height=True,
            size_hint_y=None,
            height=dp(200)  # Fixed height for simple content
        )

        # Add assessment details with better spacing
        content.add_widget(MDLabel(
            text=f"Animal: {assessment[3]} ({assessment[4]})",
            adaptive_height=True,
            size_hint_y=None,
            height=dp(30)
        ))

        content.add_widget(MDLabel(
            text=f"Date: {assessment[0]}",
            adaptive_height=True,
            size_hint_y=None,
            height=dp(30)
        ))

        content.add_widget(MDLabel(
            text=f"Assessment Scale: {assessment[1]}",
            adaptive_height=True,
            size_hint_y=None,
            height=dp(30)
        ))

        content.add_widget(MDLabel(
            text=f"Result: {assessment[2]}",
            adaptive_height=True,
            size_hint_y=None,
            height=dp(60)  # Taller to accommodate longer text
        ))

        return content

    def view_animal(self, animal_id):
        """Navigate to animal details screen."""
        if self.detail_dialog:
            self.detail_dialog.dismiss()

        # Get the app instance
        from kivymd.app import MDApp
        app = MDApp.get_running_app()

        # Access the animal detail screen and set the animal ID
        animal_detail_screen = app.screen_manager.get_screen('animal_detail')
        animal_detail_screen.set_animal_id(animal_id)

        # Switch to the animal detail screen
        app.switch_screen('animal_detail')

    def confirm_delete_assessment(self, assessment_id):
        """Confirm before deleting an assessment."""
        # Dismiss the detail dialog if it's open
        if self.detail_dialog:
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

        if self.confirm_dialog:
            self.confirm_dialog.dismiss()

        if success:
            self.load_assessments()
            self.show_success_dialog("Assessment deleted successfully!")
        else:
            self.show_error_dialog("Failed to delete assessment.")

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
