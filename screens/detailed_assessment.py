from kivymd.uix.screen import MDScreen
import json
from datetime import datetime

from kivy.metrics import dp
from kivy.properties import StringProperty, NumericProperty, ListProperty
from kivy.utils import get_color_from_hex
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDButton, MDButtonText
from kivymd.uix.dialog import MDDialog, MDDialogHeadlineText, MDDialogContentContainer, MDDialogButtonContainer
from kivymd.uix.label import MDLabel
from kivymd.uix.screen import MDScreen

import database
# Import the assessment scales
from assessment_scales import ASSESSMENT_SCALES


class DetailedAssessmentScreen(MDScreen):
    """Screen for conducting detailed assessment using specific scales."""

    animal_id = NumericProperty(None)
    animal_name = StringProperty("")
    animal_species = StringProperty("")
    selected_scale = StringProperty("")

    current_question_idx = NumericProperty(0)
    total_questions = NumericProperty(0)

    questions = ListProperty([])
    answers = ListProperty([])

    def __init__(self, **kwargs):
        # Initialize properties before super().__init__ to avoid KV binding issues
        self.animal_id = None
        self.animal_name = ""
        self.animal_species = ""
        self.selected_scale = ""
        self.current_question_idx = 0
        self.total_questions = 0
        self.questions = []
        self.answers = [None]  # Initialize with at least one None value

        self.dialog = None
        self.result_dialog = None
        self.scale_data = None

        super().__init__(**kwargs)

    def on_kv_post(self, base_widget):
        """Called after the kv file is processed"""
        # Update the UI after kv processing
        self.update_ui()

    def set_assessment_params(self, animal_id, animal_name, animal_species, scale_name):
        """Set up the assessment parameters and load the scale."""
        self.animal_id = animal_id
        self.animal_name = animal_name
        self.animal_species = animal_species
        self.selected_scale = scale_name

        # Reset assessment state
        self.current_question_idx = 0
        self.answers = []

        # Load the scale data
        if animal_species in ASSESSMENT_SCALES and scale_name in ASSESSMENT_SCALES[animal_species]:
            self.scale_data = ASSESSMENT_SCALES[animal_species][scale_name]
            self.questions = self.scale_data["questions"]
            self.total_questions = len(self.questions)

            # Pre-initialize answers array
            self.answers = [None] * self.total_questions

            # Update the UI
            self.update_ui()
        else:
            self.show_error_dialog(f"Scale '{scale_name}' not found for {animal_species}")

    def on_enter(self):
        """Called when screen is entered."""
        if self.scale_data:
            self.update_ui()

    def update_ui(self):
        """Update the user interface with current question."""
        if not hasattr(self, 'ids') or not self.ids:
            return

        if not self.scale_data or self.current_question_idx >= self.total_questions:
            return

        # Clear previous content
        self.ids.question_container.clear_widgets()
        self.ids.options_container.clear_widgets()

        # Update header and progress information
        self.ids.assessment_title.text = self.scale_data["title"]
        self.ids.animal_info.text = f"{self.animal_name} ({self.animal_species})"
        self.ids.progress_text.text = f"Question {self.current_question_idx + 1} of {self.total_questions}"
        self.ids.progress_bar.value = ((self.current_question_idx + 1) / self.total_questions) * 100

        # Get current question
        question_data = self.questions[self.current_question_idx]

        # Add question text
        question_box = MDBoxLayout(
            orientation="vertical",
            adaptive_height=True,
            padding=dp(16),
            spacing=dp(8)
        )

        question_box.add_widget(MDLabel(
            text=question_data["question"],
            font_style="Title",
            role="medium",
            adaptive_height=True
        ))

        # Add guidance if available
        if "guidance" in question_data:
            guidance_label = MDLabel(
                text=f"Guidance: {question_data['guidance']}",
                theme_text_color="Secondary",
                font_style="Body",
                role="small",
                adaptive_height=True
            )
            question_box.add_widget(guidance_label)

        self.ids.question_container.add_widget(question_box)

        # Add option buttons
        for i, option in enumerate(question_data["options"]):
            option_button = MDButton(
                style="outlined" if self.answers[self.current_question_idx] != i else "elevated",
                on_release=lambda x, idx=i: self.select_answer(idx)
            )
            option_button.add_widget(MDButtonText(
                text=option["text"],
                padding=dp(16)
            ))
            self.ids.options_container.add_widget(option_button)

    def select_answer(self, option_index):
        """Handle selection of an answer option."""
        if self.current_question_idx < self.total_questions:
            # Save the answer (store the option index)
            self.answers[self.current_question_idx] = option_index

            # Update UI to show selected option
            self.update_ui()

            # After a short delay, move to next question or finish
            from kivy.clock import Clock
            Clock.schedule_once(lambda dt: self.next_question(), 0.3)

    def next_question(self):
        """Move to the next question or finish the assessment."""
        if self.current_question_idx < self.total_questions - 1:
            # Move to next question
            self.current_question_idx += 1
            self.update_ui()
        else:
            # All questions answered, calculate and show results
            self.show_results()

    def prev_question(self):
        """Move to the previous question."""
        if self.current_question_idx > 0:
            self.current_question_idx -= 1
            self.update_ui()

    def calculate_score(self):
        """Calculate the total score based on answers."""
        total_score = 0
        score_details = []

        for i, answer_idx in enumerate(self.answers):
            if answer_idx is not None:
                question = self.questions[i]
                score = question["options"][answer_idx]["score"]
                total_score += score
                score_details.append({
                    "question": question["question"],
                    "answer": question["options"][answer_idx]["text"],
                    "score": score
                })

        # Find the interpretation based on score
        interpretation = {"text": "No interpretation available", "color": "blue"}

        for interp in self.scale_data["interpretation"]:
            if interp["range"][0] <= total_score <= interp["range"][1]:
                interpretation = interp
                break

        return {
            "total_score": total_score,
            "details": score_details,
            "interpretation": interpretation
        }

    def show_results(self):
        """Display assessment results and save to database."""
        result = self.calculate_score()

        # Create results display
        content = MDBoxLayout(
            orientation="vertical",
            spacing=dp(16),
            padding=dp(16),
            adaptive_height=True
        )

        # Add total score with interpretation
        score_box = MDBoxLayout(
            orientation="vertical",
            adaptive_height=True,
            spacing=dp(4)
        )

        score_box.add_widget(MDLabel(
            text=f"Total Score: {result['total_score']}",
            font_style="Title",
            role="large",
            halign="center",
            adaptive_height=True
        ))

        # Interpretation with color
        interp_label = MDLabel(
            text=result["interpretation"]["text"],
            font_style="Title",
            role="medium",
            halign="center",
            theme_text_color="Custom",
            text_color=self.get_color_from_name(result["interpretation"]["color"]),
            adaptive_height=True
        )
        score_box.add_widget(interp_label)

        content.add_widget(score_box)

        # Add divider
        content.add_widget(MDBoxLayout(
            orientation="horizontal",
            height=dp(1),
            size_hint_y=None,
            md_bg_color=get_color_from_hex("#CCCCCC")
        ))

        # Add score details
        details_label = MDLabel(
            text="Assessment Details:",
            font_style="Title",
            role="small",
            adaptive_height=True
        )
        content.add_widget(details_label)

        for detail in result["details"]:
            detail_box = MDBoxLayout(
                orientation="vertical",
                adaptive_height=True,
                padding=(dp(8), dp(4))
            )

            question_label = MDLabel(
                text=detail["question"],
                font_style="Body",
                role="medium",
                adaptive_height=True
            )
            detail_box.add_widget(question_label)

            answer_label = MDLabel(
                text=f"Answer: {detail['answer']} (Score: {detail['score']})",
                font_style="Body",
                role="small",
                adaptive_height=True
            )
            detail_box.add_widget(answer_label)

            content.add_widget(detail_box)

        # Save result to database as JSON string
        result_data = {
            "score": result["total_score"],
            "interpretation": result["interpretation"]["text"],
            "details": result["details"]
        }

        result_json = json.dumps(result_data)
        today = datetime.now().strftime("%Y-%m-%d")

        database.add_assessment(
            self.animal_id,
            today,
            self.selected_scale,
            result_json
        )

        # Show results dialog
        self.result_dialog = MDDialog(
            MDDialogHeadlineText(text="Assessment Results"),
            MDDialogContentContainer(content),
            MDDialogButtonContainer(
                MDButton(
                    MDButtonText(text="Done"),
                    style="text",
                    on_release=lambda x: self.finish_assessment()
                )
            )
        )
        self.result_dialog.open()

    def finish_assessment(self):
        """Return to previous screen after completing assessment."""
        if self.result_dialog:
            self.result_dialog.dismiss()

        # Get app instance and go back to assessments screen
        from kivymd.app import MDApp
        app = MDApp.get_running_app()

        # Go back to assessments screen
        app.switch_screen('assessments')

        # Refresh assessments list
        assessments_screen = app.screen_manager.get_screen('assessments')
        assessments_screen.load_assessments()

    def show_error_dialog(self, message):
        """Show error dialog with message."""
        self.dialog = MDDialog(
            MDDialogHeadlineText(text="Error"),
            MDDialogContentContainer(MDLabel(text=message)),
            MDDialogButtonContainer(
                MDButton(
                    MDButtonText(text="OK"),
                    style="text",
                    on_release=lambda x: self.handle_error_dismiss()
                )
            )
        )
        self.dialog.open()

    def handle_error_dismiss(self):
        """Handle dismissal of error dialog."""
        if self.dialog:
            self.dialog.dismiss()

        # Return to assessments screen
        from kivymd.app import MDApp
        app = MDApp.get_running_app()
        app.switch_screen('assessments')

    def get_color_from_name(self, color_name):
        """Convert color name to RGB tuple."""
        color_map = {
            "red": get_color_from_hex("#f44336"),
            "orange": get_color_from_hex("#ff9800"),
            "yellow": get_color_from_hex("#ffeb3b"),
            "green": get_color_from_hex("#4caf50"),
            "blue": get_color_from_hex("#2196f3")
        }

        return color_map.get(color_name.lower(), get_color_from_hex("#2196f3"))  # Default to blue