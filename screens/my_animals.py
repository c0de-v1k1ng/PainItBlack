import os

from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDButton, MDButtonText
from kivymd.uix.dialog import MDDialog, MDDialogHeadlineText, MDDialogContentContainer, MDDialogButtonContainer
from kivymd.uix.label import MDLabel
from kivymd.uix.list import MDListItem, MDListItemHeadlineText, MDListItemSupportingText
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.screen import MDScreen
from kivymd.uix.selectioncontrol import MDCheckbox

from managers.export_manager import ExportManager
import database
from utils.long_press import LongPressDetector

class MyAnimalsScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.dialog = None
        self.selected_animals = []
        self.is_selection_mode = False
        self.export_dialog = None
        self.loading_dialog = None

    def on_enter(self):
        self.load_species_list()
        self.load_animals()

    def load_animals(self):
        """Load all animals from the database into the list."""
        # Reset filters when reloading all animals
        if hasattr(self.ids, 'search_field'):
            self.ids.search_field.text = ""
        if hasattr(self.ids, 'species_filter'):
            self.ids.species_filter.text = ""

        # Use the database query execution function with 'all' fetch mode
        animals = database.execute_query(
            "SELECT id, name, species, breed FROM animals ORDER BY name",
            fetch_mode='all'
        )

        # Let update_animals_list handle everything else
        self.update_animals_list(animals)

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

    def toggle_selection_mode(self):
        """Toggle between normal and selection mode."""
        self.is_selection_mode = not self.is_selection_mode
        self.load_animals()  # Reload the list with checkboxes if in selection mode

        # Update the FAB based on selection mode
        if self.is_selection_mode:
            self.ids.fab_add.icon = "close"  # Change FAB icon to exit selection mode

            # Show the export FAB if it doesn't exist
            if not hasattr(self.ids, 'fab_export'):
                from kivymd.uix.button import MDFabButton

                export_fab = MDFabButton(
                    id="fab_export",
                    icon="export",
                    style="standard",
                    pos_hint={"center_x": 0.9, "center_y": 0.2},
                    on_release=lambda x: self.show_export_options()
                )
                self.add_widget(export_fab)
                self.ids.fab_export = export_fab
        else:
            self.ids.fab_add.icon = "plus"  # Restore FAB icon for adding animals
            self.selected_animals = []  # Clear selections

            # Remove the export FAB if it exists
            if hasattr(self.ids, 'fab_export'):
                self.remove_widget(self.ids.fab_export)
                if hasattr(self, 'fab_export'):
                    delattr(self.ids, 'fab_export')

                    # Also check ids dictionary
                    if hasattr(self.ids, 'fab_export'):
                        # Try to remove from widget
                        if hasattr(self, 'ids.fab_export'):
                            self.remove_widget(self.ids.fab_export)
                        # Then try to remove the attribute
                        try:
                            delattr(self.ids, 'fab_export')
                        except (AttributeError, KeyError):
                            # Ignore errors if it doesn't exist
                            pass

    def on_animal_select(self, animal_id, is_active):
        """Handle animal selection/deselection."""
        if is_active:
            if animal_id not in self.selected_animals:
                self.selected_animals.append(animal_id)
        else:
            if animal_id in self.selected_animals:
                self.selected_animals.remove(animal_id)

    def show_export_options(self):
        """Show export options dialog for selected animals."""
        if not self.selected_animals:
            self.show_error_dialog("No animals selected.")
            return

        self.export_dialog = MDDialog(
            MDDialogHeadlineText(text="Export Options"),
            MDDialogContentContainer(
                MDLabel(text=f"Export {len(self.selected_animals)} selected animal(s):")
            ),
            MDDialogButtonContainer(
                MDButton(
                    MDButtonText(text="PDF"),
                    style="text",
                    on_release=lambda x: self.export_animals("pdf")
                ),
                MDButton(
                    MDButtonText(text="CSV"),
                    style="text",
                    on_release=lambda x: self.export_animals("csv")
                ),
                MDButton(
                    MDButtonText(text="Cancel"),
                    style="text",
                    on_release=lambda x: self.export_dialog.dismiss()
                ),
                spacing="8dp"
            ),
            auto_dismiss=True
        )
        self.export_dialog.open()

    def export_animals(self, format_type):
        """Export selected animals data in the selected format."""
        self.export_dialog.dismiss()

        # Show loading indicator
        self.show_loading_dialog(f"Exporting {len(self.selected_animals)} animals...")

        # Run export in a separate thread to keep UI responsive
        def export_thread():
            export_manager = ExportManager()

            try:
                from kivy.clock import Clock
                if format_type == "pdf":
                    filenames = export_manager.export_multiple_animals_to_pdf(self.selected_animals)
                    if filenames:
                        # Limit the displayed filenames to 5 if there are more
                        if len(filenames) > 5:
                            displayed_files = [os.path.basename(f) for f in filenames[:5]]
                            displayed_files.append(f"... and {len(filenames) - 5} more")
                        else:
                            displayed_files = [os.path.basename(f) for f in filenames]

                        Clock.schedule_once(
                            lambda dt: self.show_success_dialog(
                                f"Exported {len(filenames)} animals to PDF:\n{', '.join(displayed_files)}"), 0
                        )
                    else:
                        Clock.schedule_once(
                            lambda dt: self.show_error_dialog("Failed to export animal data"), 0
                        )
                elif format_type == "csv":
                    filenames = export_manager.export_multiple_animals_to_csv(self.selected_animals)
                    if filenames:
                        # Limit the displayed filenames to 5 if there are more
                        if len(filenames) > 5:
                            displayed_files = [os.path.basename(f) for f in filenames[:5]]
                            displayed_files.append(f"... and {len(filenames) - 5} more")
                        else:
                            displayed_files = [os.path.basename(f) for f in filenames]

                        Clock.schedule_once(
                            lambda dt: self.show_success_dialog(
                                f"Exported to {len(filenames)} CSV files:\n{', '.join(displayed_files)}"), 0
                        )
                    else:
                        Clock.schedule_once(
                            lambda dt: self.show_error_dialog("Failed to export animal data"), 0
                        )

                # Exit selection mode after export - must also be scheduled
                Clock.schedule_once(lambda dt: self.toggle_selection_mode(), 0.6)
            finally:
                # Dismiss loading dialog
                Clock.schedule_once(lambda dt: self.loading_dialog.dismiss(), 0.5)

        # Start the export thread
        from threading import Thread
        thread = Thread(target=export_thread)
        thread.daemon = True
        thread.start()

    def show_loading_dialog(self, message):
        """Show a loading dialog."""
        from kivymd.uix.progressindicator import MDCircularProgressIndicator
        from kivymd.uix.dialog import MDDialog, MDDialogHeadlineText, MDDialogContentContainer

        # Create a container for the spinner and message
        content = MDBoxLayout(
            orientation="vertical",
            spacing="16dp",
            adaptive_height=True,
            padding=["20dp", "20dp", "20dp", "20dp"]
        )

        # Add spinner
        spinner = MDCircularProgressIndicator()
        spinner_box = MDBoxLayout(
            adaptive_size=True,
            pos_hint={"center_x": 0.5}
        )
        spinner_box.add_widget(spinner)
        content.add_widget(spinner_box)

        # Add message
        content.add_widget(MDLabel(
            text=message,
            halign="center",
            adaptive_height=True
        ))

        # Create the dialog with proper structure
        self.loading_dialog = MDDialog(
            MDDialogHeadlineText(text="Please Wait"),
            MDDialogContentContainer(content),
            auto_dismiss=False
        )
        self.loading_dialog.open()

    # Add long-press handling for individual export
    def check_long_press(self, item, touch, animal_id):
        """Check if there's a long press on an animal item."""
        if touch.is_double_tap:
            return False

        touch.ud[item] = True
        touch.grab(item)

        # Schedule long press detection
        def on_long_press(dt):
            if item in touch.ud and touch.grab_current == item:
                touch.ungrab(item)
                self.show_animal_options(animal_id)
                return True

        from kivy.clock import Clock
        Clock.schedule_once(on_long_press, 0.7)  # 700ms long press

        return True

    def on_touch_up(self, touch):
        """Handle touch up events for long press cancellation."""
        for item in list(touch.ud.keys()):
            if isinstance(item, MDListItem) and touch.grab_current == item:
                touch.ungrab(item)
                del touch.ud[item]
        return super().on_touch_up(touch)

    def show_animal_options(self, animal_id):
        """Show options menu for a single animal."""
        # Get animal name for display
        animal = database.execute_query(
            "SELECT name FROM animals WHERE id = ?",
            (animal_id,),
            fetch_mode='one'
        )

        if not animal:
            return

        animal_name = animal[0]

        self.animal_options_dialog = MDDialog(
            MDDialogHeadlineText(text=f"Options for {animal_name}"),
            MDDialogButtonContainer(
                MDButton(
                    MDButtonText(text="Export to PDF"),
                    style="text",
                    on_release=lambda x: self.export_single_animal(animal_id, "pdf")
                ),
                MDButton(
                    MDButtonText(text="Export to CSV"),
                    style="text",
                    on_release=lambda x: self.export_single_animal(animal_id, "csv")
                ),
                MDButton(
                    MDButtonText(text="View Details"),
                    style="text",
                    on_release=lambda x: self.view_animal_from_dialog(animal_id)
                ),
                MDButton(
                    MDButtonText(text="Cancel"),
                    style="text",
                    on_release=lambda x: self.animal_options_dialog.dismiss()
                ),
                spacing="8dp"
            ),
            auto_dismiss=True
        )
        self.animal_options_dialog.open()

    def view_animal_from_dialog(self, animal_id):
        """View animal details from the options dialog."""
        if hasattr(self, 'animal_options_dialog') and self.animal_options_dialog:
            self.animal_options_dialog.dismiss()
        self.view_animal(animal_id)

    def export_single_animal(self, animal_id, format_type):
        """Export a single animal's data."""
        if hasattr(self, 'animal_options_dialog') and self.animal_options_dialog:
            self.animal_options_dialog.dismiss()

        # Show loading indicator
        self.show_loading_dialog("Exporting...")

        # Run export in a separate thread to keep UI responsive
        def export_thread():
            export_manager = ExportManager()

            try:
                from kivy.clock import Clock
                if format_type == "pdf":
                    filename = export_manager.export_animal_to_pdf(animal_id)
                    if filename:
                        # Schedule UI update on main thread
                        Clock.schedule_once(
                            lambda dt: self.show_success_dialog(f"Exported to PDF:\n{os.path.basename(filename)}"), 0
                        )
                    else:
                        Clock.schedule_once(
                            lambda dt: self.show_error_dialog("Failed to export animal data"), 0
                        )
                elif format_type == "csv":
                    filenames = export_manager.export_animal_to_csv(animal_id)
                    if filenames:
                        Clock.schedule_once(
                            lambda dt: self.show_success_dialog(
                                f"Exported to CSV files:\n{', '.join([os.path.basename(f) for f in filenames])}"), 0
                        )
                    else:
                        Clock.schedule_once(
                            lambda dt: self.show_error_dialog("Failed to export animal data"), 0
                        )
            finally:
                # Dismiss loading dialog
                Clock.schedule_once(lambda dt: self.loading_dialog.dismiss(), 0.5)

        # Start the export thread
        from threading import Thread
        thread = Thread(target=export_thread)
        thread.daemon = True
        thread.start()

    def load_species_list(self):
        """Load list of species for filtering."""
        self.species_list = database.execute_query(
            "SELECT DISTINCT species FROM animals ORDER BY species",
            fetch_mode='all'
        ) or []
        self.species_list = [species[0] for species in self.species_list]
        # Add "All" option at the beginning
        self.species_list.insert(0, "All Species")

    def show_species_filter_menu(self):
        """Show dropdown menu for species filtering."""
        menu_items = [
            {"text": species, "on_release": lambda x=species: self.select_species_filter(x)}
            for species in self.species_list
        ]

        self.species_menu = MDDropdownMenu(
            caller=self.ids.species_filter,
            items=menu_items,
            width_mult=4,
            position="bottom"
        )
        self.species_menu.open()

    def select_species_filter(self, species):
        """Apply species filter."""
        if species == "All Species":
            self.ids.species_filter.text = ""
        else:
            self.ids.species_filter.text = species

        if hasattr(self, 'species_menu') and self.species_menu:
            self.species_menu.dismiss()

        self.filter_animals()

    def filter_animals(self, *args):
        """Filter animals based on search text and species."""
        search_text = self.ids.search_field.text.strip().lower()
        species_filter = self.ids.species_filter.text

        # Build query conditions
        query = "SELECT id, name, species, breed FROM animals"
        params = []
        conditions = []

        if search_text:
            conditions.append("(LOWER(name) LIKE ? OR LOWER(id) LIKE ?)")
            params.extend([f"%{search_text}%", f"%{search_text}%"])

        if species_filter and species_filter != "All Species":
            conditions.append("species = ?")
            params.append(species_filter)

        # Add WHERE clause if there are conditions
        if conditions:
            query += " WHERE " + " AND ".join(conditions)

        query += " ORDER BY name"

        # Execute query with parameters
        animals = database.execute_query(query, params, fetch_mode='all') or []

        # Update the UI with filtered results
        self.update_animals_list(animals)

    # In both screens/my_animals.py and screens/assessments.py
    def clear_filters(self):
        """Clear all applied filters."""
        self.ids.search_field.text = ""
        self.ids.species_filter.text = ""
        self.load_animals()  # or self.load_assessments() for the assessments screen

    def update_animals_list(self, animals):
        """Update the list display with filtered animals."""
        self.ids.animals_list.clear_widgets()

        if not animals:
            # Show empty state
            item = MDListItem()
            item.add_widget(MDListItemHeadlineText(text="No animals match the filter criteria"))
            self.ids.animals_list.add_widget(item)
            return

        self.list_items = []

        # Same code as in load_animals but using the filtered animals data
        for animal in animals:
            animal_id = animal[0]
            item = MDListItem(
                on_release=lambda x, a_id=animal_id: self.view_animal(a_id) if not self.is_selection_mode else None
            )

            # Add checkbox for selection mode
            if self.is_selection_mode:
                checkbox = MDCheckbox(
                    size_hint=(None, None),
                    size=("48dp", "48dp"),
                    pos_hint={"center_y": 0.5},
                    active=animal_id in self.selected_animals
                )
                checkbox.bind(active=lambda cb, value, aid=animal_id: self.on_animal_select(aid, value))
                item.add_widget(checkbox)

            # Add headline text (name and species)
            item.add_widget(MDListItemHeadlineText(text=f"{animal[1]} ({animal[2]})"))

            # Add supporting text (breed if available)
            if animal[3]:
                item.add_widget(MDListItemSupportingText(text=f"Breed: {animal[3]}"))

            # Add long press gesture for export menu
            if not self.is_selection_mode:
                detector = LongPressDetector(
                    item,
                    lambda widget, touch, aid=animal_id: self.show_animal_options(aid)
                )
                self.list_items.append((item, detector))

            self.ids.animals_list.add_widget(item)