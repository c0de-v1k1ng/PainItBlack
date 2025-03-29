from functools import partial

from kivy.uix.screenmanager import Screen
from kivymd.material_resources import dp
from kivymd.uix.label import MDLabel
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.pickers import MDDockedDatePicker, MDModalDatePicker
from kivymd.uix.dialog import MDDialog, MDDialogButtonContainer, MDDialogHeadlineText, MDDialogContentContainer
from kivymd.uix.button import MDButton, MDButtonText
from kivy.uix.filechooser import FileChooserListView
from kivymd.uix.screen import MDScreen

import database
import os
import shutil


class AddAnimalScreen(MDScreen):
    species_list = ["Rat", "Mouse", "Rabbit", "Goat", "Sheep", "Pig"]  # Example species list
    weight_units = ["kg", "g"]
    sex_options = ["Male", "Female"]
    birthday_text = "Select Date"
    selected_image_path = ""

    def __init__(self, **kwargs):
        """Prepares UI when the screen is entered."""
        super().__init__(**kwargs)
        self.file_dialog = None
        self.filechooser_view = None
        self.dialog = None
        self.selected_species = None
        self.selected_sex = None
        self.selected_unit = "kg"
        self.selected_image_path = ""
        self.species_menu = None
        self.sex_menu = None
        self.unit_menu = None
        self.file_chooser_view = None

    def show_species_menu(self):
        """Dropdown for selecting species."""
        menu_items = [
            {"text": species, "on_release": lambda x=species: self.set_species(x)}
            for species in self.species_list
        ]
        MDDropdownMenu(caller=self.ids.species_dropdown, items=menu_items, width_mult=4).open()


    def set_species(self, species):
        self.selected_species = species
        self.ids.species_dropdown.text = species


    def show_sex_menu(self):
        """Dropdown for selecting sex."""
        menu_items = [
            {"text": gender, "on_release": lambda x=gender: self.set_sex(x)}
            for gender in self.sex_options
        ]
        MDDropdownMenu(caller=self.ids.sex_dropdown, items=menu_items, width_mult=3).open()

    def set_sex(self, gender):
        self.selected_sex = gender
        self.ids.sex_dropdown.text = gender

    def show_weight_unit_menu(self):
        """Dropdown for selecting weight unit."""
        menu_items = [
            {"text": unit, "on_release": lambda x=unit: self.set_weight_unit(x)}
            for unit in self.weight_units
        ]
        MDDropdownMenu(caller=self.ids.weight_unit, items=menu_items, width_mult=3).open()

    def set_weight_unit(self, unit):
        self.selected_unit = unit
        self.ids.weight_unit.text = unit

    def show_date_picker(self, field_widget):
        if not field_widget.focus:
            return

        date_dialog = MDModalDatePicker()
        date_dialog.bind(on_ok=self.on_date_ok)

        # Schedule the position update after it's been created but before opening
        def set_pos(*args):
            # Adjust the position so the date picker stays within screen bounds
            x = field_widget.center_x - date_dialog.width / 2
            y = field_widget.y - (date_dialog.height + dp(16))

            # Optional: clamp to screen bounds (for small screens)
            if y < 0:
                y = dp(16)

            date_dialog.pos = [x, y]
            date_dialog.open()
            # Wait for layout before setting position

        from kivy.clock import Clock
        Clock.schedule_once(set_pos, 0.1)

    def on_date_ok(self, instance):
        if instance:
            selected_date_list = instance.get_date()
            selected_date = selected_date_list[0]
            formatted_date = selected_date.strftime("%d.%m.%Y")
            self.birthday_text = formatted_date
            self.ids.animal_birth_date.text = formatted_date
            instance.dismiss()

    def show_file_chooser(self):
        """Show dialog with file chooser to select an image."""
        user_pictures = os.path.expanduser("~/Pictures")

        self.filechooser_view = FileChooserListView(
            path=user_pictures,
            filters=["*.png", "*.jpg", "*.jpeg"],
            size_hint_y=None,
            height="400dp"
        )

        self.file_dialog = MDDialog(
            MDDialogHeadlineText(text="Choose Animal Photo"),
            MDDialogContentContainer(
                self.filechooser_view
            ),
            MDDialogButtonContainer(
                MDButton(
                    MDButtonText(text="Cancel"),
                    style="text",
                    on_release=lambda x: self.file_dialog.dismiss()
                ),
                MDButton(
                    MDButtonText(text="Select"),
                    style="text",
                    on_release=lambda x: self.select_image()
                ),
                spacing="8dp"
            ),
            auto_dismiss=False,
        )
        self.file_dialog.open()

    def select_image(self):
        """Handle image selection."""
        selection = self.filechooser_view.selection
        if selection:
            self.selected_image_path = selection[0]
            # Update photo preview directly instead of using photo_label
            self.ids.photo_preview.source = self.selected_image_path
        self.file_dialog.dismiss()

    def save_animal(self):
        """Save new animal entry to the database."""
        name = self.ids.animal_name.text.strip()
        species = self.selected_species
        breed = self.ids.animal_breed.text.strip()
        birthday = self.birthday_text if self.birthday_text != "Select Date" else None
        sex = self.selected_sex
        castrated = "Yes" if self.ids.animal_castrated.active else "No"
        weight = self.ids.animal_weight.text.strip()
        weight_unit = self.selected_unit

        if not name or not species or not weight:
            self.show_error("Name/ID, Species, and Weight are required!")
            return

        try:
            weight_in_kg = float(weight) if weight_unit == "kg" else float(weight) / 1000  # Convert g to kg
        except ValueError:
            self.show_error("Weight must be a valid number!")
            return

        # Save image in app directory
        image_save_path = ""
        if self.selected_image_path:
            image_dir = "animal_images"
            os.makedirs(image_dir, exist_ok=True)
            image_save_path = os.path.join(image_dir, os.path.basename(self.selected_image_path))
            shutil.copy(self.selected_image_path, image_save_path)

        animal_id = database.add_animal(name, species, breed, birthday, sex, castrated, weight_in_kg, image_save_path)

        self.reset_form()
        self.show_confirmation("Animal saved successfully!")

        # Get the app instance more reliably
        from kivymd.app import MDApp
        app = MDApp.get_running_app()

        # Schedule the navigation after the dialog is dismissed
        def navigate_back(*args):
            app.switch_screen('my_animals')
            # Refresh the animals list
            app.screen_manager.get_screen('my_animals').load_animals()

        # Schedule navigation to happen after dialog is dismissed
        from kivy.clock import Clock
        Clock.schedule_once(navigate_back, 0.5)

    def reset_form(self):
        for field in [
            "animal_name", "species_dropdown", "animal_breed", "animal_birth_date",
            "sex_dropdown", "animal_weight", "weight_unit"
        ]:
            self.ids[field].text = ""
        self.ids.animal_castrated.active = False
        self.ids.photo_preview.source = ""
        self.selected_image_path = ""
        self.selected_species = None
        self.selected_sex = None
        self.selected_unit = "kg"
        self.birthday_text = "Select Date"

    def show_confirmation(self, message):
        self.dialog = MDDialog(
            MDDialogHeadlineText(text="Success"),
            MDDialogContentContainer(MDLabel(text=message)),
            MDDialogButtonContainer(
                MDButton(
                    MDButtonText(text="OK"),
                    style="text",
                    on_release=lambda x: self.dialog.dismiss()
                )
            )
        )
        self.dialog.open()

    def show_error(self, message):
        self.dialog = MDDialog(
            MDDialogHeadlineText(text="Missing Info"),
            MDDialogContentContainer(MDLabel(text=message)),
            MDDialogButtonContainer(
                MDButton(
                    MDButtonText(text="OK"),
                    style="text",
                    on_release=lambda x: self.dialog.dismiss()
                )
            )
        )
        self.dialog.open()