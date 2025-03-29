from kivy.uix.screenmanager import Screen
from kivymd.app import MDApp
from kivymd.uix.list import MDList, MDListItem, MDListItemHeadlineText, MDListItemSupportingText
from kivymd.uix.screen import MDScreen
from kivymd.uix.dialog import MDDialog, MDDialogHeadlineText, MDDialogContentContainer, MDDialogButtonContainer
from kivymd.uix.button import MDButton, MDButtonText
from kivymd.uix.label import MDLabel

import database


class MyAnimalsScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.dialog = None

    def on_enter(self):
        self.load_animals()

    def load_animals(self):
        """Load all animals from the database into the list."""
        self.ids.animals_list.clear_widgets()
        conn = database.get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, species, breed FROM animals ORDER BY name")
        animals = cursor.fetchall()
        conn.close()

        if not animals:
            # Show empty state
            item = MDListItem()
            item.add_widget(MDListItemHeadlineText(text="No animals added yet"))
            self.ids.animals_list.add_widget(item)
            return

        for animal in animals:
            item = MDListItem(
                on_release=lambda x, a_id=animal[0]: self.view_animal(a_id)
            )
            # Add headline text (name and species)
            item.add_widget(MDListItemHeadlineText(text=f"{animal[1]} ({animal[2]})"))

            # Add supporting text (breed if available)
            if animal[3]:
                item.add_widget(MDListItemSupportingText(text=f"Breed: {animal[3]}"))

            self.ids.animals_list.add_widget(item)

    def view_animal(self, animal_id):
        """Navigate to the animal detail screen."""
        animal_detail_screen = self.manager.get_screen('animal_detail')
        animal_detail_screen.set_animal_id(animal_id)
        self.manager.current = 'animal_detail'

    def show_add_animal(self):
        """Navigate to the add animal screen."""
        self.manager.current = 'add_animal'

    def show_delete_confirm(self, animal_id, animal_name):
        """Show confirmation dialog before deleting an animal."""
        self.dialog = MDDialog(
            MDDialogHeadlineText(text="Confirm Deletion"),
            MDDialogContentContainer(
                MDLabel(text=f"Are you sure you want to delete {animal_name}?")
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
                    on_release=lambda x: self.delete_animal(animal_id)
                ),
                spacing="8dp"
            ),
            auto_dismiss=False
        )
        self.dialog.open()

    def delete_animal(self, animal_id):
        """Delete an animal from the database."""
        success = database.delete_animal(animal_id)
        self.dialog.dismiss()

        if success:
            self.load_animals()
            self.show_success_dialog("Animal deleted successfully!")
        else:
            self.show_error_dialog("Failed to delete animal.")

    def show_success_dialog(self, message):
        """Show a success dialog."""
        self.dialog = MDDialog(
            MDDialogHeadlineText(text="Success"),
            MDDialogContentContainer(
                MDLabel(text=message)
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

    def show_error_dialog(self, message):
        """Show an error dialog."""
        self.dialog = MDDialog(
            MDDialogHeadlineText(text="Error"),
            MDDialogContentContainer(
                MDLabel(text=message)
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