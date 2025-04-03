from kivy.base import EventLoop

from managers.language_manager import translator
from kivy.lang import Builder
from kivymd.app import MDApp
from kivymd.theming import ThemeManager
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.textfield import MDTextField
from kivymd.uix.menu import MDDropdownMenu
from kivy.properties import StringProperty, ObjectProperty
from kivy.clock import Clock

import database
from screens.add_animal import AddAnimalScreen
from screens.animal_detail import AnimalDetailScreen
from screens.assessments import AssessmentsScreen
from screens.detailed_assessment import DetailedAssessmentScreen
from screens.edit_animal import EditAnimalScreen
from screens.home import HomeScreen
from screens.my_animals import MyAnimalsScreen
from screens.species_detail import SpeciesDetailScreen

from kivy.properties import BooleanProperty


class RootLayout(MDBoxLayout):
    """Root layout that contains the navigation rail and screen manager."""
    pass


class MainApp(MDApp):
    # Current language property that can be bound to UI elements
    current_language = StringProperty('en')
    # Translator instance as a property for easier access in KV files
    translator = ObjectProperty(translator)
    ui_ready = BooleanProperty(False)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.theme_cls = ThemeManager()
        # Add backgroundColor property for dark/light mode
        self.theme_cls.backgroundColor = [0.98, 0.98, 0.98, 1]  # Light mode default
        self.nav_drawer = None
        self.active_nav_item = None
        self.language_menu = None

        # Register the app as an observer of language changes
        translator.register_observer(self)

    def build(self):
        self.theme_cls.theme_style = "Light"  # ✅ Default theme
        self.theme_cls.primary_palette = "Gray"

        # Load root layout first
        Builder.load_file('kv/root_layout.kv')

        # Load all kv files dynamically
        for kv_file in ['home.kv', 'species_detail.kv', 'my_animals.kv', 'assessments.kv',
                        'add_animal.kv', 'edit_animal.kv', 'animal_detail.kv',
                        'detailed_assessment.kv']:  # Added detailed_assessment.kv
            Builder.load_file(f'kv/{kv_file}')
            print(f"✅ Loaded kv: {kv_file}")

        # Create the root layout
        self.root = RootLayout()
        Clock.schedule_once(self.update_after_mainloop, 0)

        self.bind(ui_ready=self.on_ui_ready)

        # Get screen manager from root layout
        self.screen_manager = self.root.ids.screen_manager

        # Add screens to the screen manager
        self.screen_manager.add_widget(HomeScreen(name='home'))
        self.screen_manager.add_widget(SpeciesDetailScreen(name='species_detail'))
        self.screen_manager.add_widget(MyAnimalsScreen(name='my_animals'))
        self.screen_manager.add_widget(AssessmentsScreen(name='assessments'))
        self.screen_manager.add_widget(AddAnimalScreen(name='add_animal'))
        self.screen_manager.add_widget(EditAnimalScreen(name='edit_animal'))
        self.screen_manager.add_widget(AnimalDetailScreen(name='animal_detail'))
        self.screen_manager.add_widget(
            DetailedAssessmentScreen(name='detailed_assessment'))  # Added detailed assessment

        # Set up active navigation item tracking
        self.active_nav_item = self.root.ids.nav_home

        # Set initial language property
        self.current_language = translator.current_language

        # Schedule an update to ensure UI reflects the correct language
        Clock.schedule_once(self.set_ui_ready,0)

        return self.root

    def set_ui_ready(self, dt):
        self.ui_ready = True

    def on_ui_ready(self, instance, value):
        if value:  # If ui_ready is True
            self.update_language_ui()

    def switch_screen(self, screen_name):
        """Switch to the specified screen and update navigation rail state."""
        # Update screen
        self.screen_manager.current = screen_name

        # Update active navigation item
        if screen_name == 'home':
            self.set_active_nav_item(self.root.ids.nav_home)
        elif screen_name == 'my_animals':
            self.set_active_nav_item(self.root.ids.nav_animals)
        elif screen_name == 'assessments':
            self.set_active_nav_item(self.root.ids.nav_assessments)

    def set_active_nav_item(self, item):
        """Set the active navigation item."""
        if self.active_nav_item:
            self.active_nav_item.active = False
        item.active = True
        self.active_nav_item = item

    def toggle_theme(self):
        """Toggle between Light and Dark mode dynamically."""
        if self.theme_cls.theme_style == "Light":
            self.theme_cls.theme_style = "Dark"
            self.theme_cls.backgroundColor = [0.1, 0.1, 0.1, 1]  # Dark mode
        else:
            self.theme_cls.theme_style = "Light"
            self.theme_cls.backgroundColor = [0.98, 0.98, 0.98, 1]  # Light mode

    def update_after_mainloop(self, dt):
        """Force update after main loop is running."""

        def trigger_update(*args):
            self.update_language_ui()

        if EventLoop.status == 'started':
            trigger_update()
        else:
            Clock.schedule_interval(
                lambda dt: trigger_update() if EventLoop.status == 'started' else None,
                0.1  # Check every 0.1 seconds
            )

    def go_back(self):
        """Navigate back to the previous screen."""
        self.root.ids.screen_manager.current = 'home'
        self.set_active_nav_item(self.root.ids.nav_home)

    def edit_animal(self, animal_id):
        """Navigate to edit animal screen with the specified animal."""
        edit_screen = self.screen_manager.get_screen('edit_animal')
        edit_screen.set_animal_id(animal_id)
        self.screen_manager.current = 'edit_animal'

    def new_assessment(self, animal_id):
        """Navigate to assessment screen for the specified animal."""
        assessment_screen = self.screen_manager.get_screen('assessments')

        animal = database.execute_query("SELECT name, species FROM animals WHERE id = ?",(animal_id,),"all")


        if animal:
            animal_name, animal_species = animal
            assessment_screen.selected_animal_id = animal_id
            assessment_screen.selected_animal_name = animal_name
            assessment_screen.selected_animal_species = animal_species
            self.screen_manager.current = 'assessments'
            self.set_active_nav_item(self.root.ids.nav_assessments)

            # Automatically show the scale selection dialog
            assessment_screen.animal_field = MDTextField(text=f"{animal_name} ({animal_species})")
            assessment_screen.continue_assessment()

    def show_language_menu(self, caller_widget):
        """Show a dropdown menu to select a language."""
        menu_items = [
            {
                "text": "English",
                "on_release": lambda x="en": self.change_language("en")
            },
            {
                "text": "Deutsch",
                "on_release": lambda x="de": self.change_language("de")
            }
        ]

        self.language_menu = MDDropdownMenu(
            caller=caller_widget,
            items=menu_items,
            width_mult=4
        )
        self.language_menu.open()

    def change_language(self, language_code):
        """Change the application language."""
        # Close the menu
        if self.language_menu:
            self.language_menu.dismiss()

        # Set the new language
        translator.set_language(language_code)

        # Update app's language property
        self.current_language = language_code

    def update_language(self):
        """Called when language changes to update UI."""
        # Update app's language property
        self.current_language = translator.current_language

        # This method will be called when language changes
        # Schedule an update for all screens
        Clock.schedule_once(self.update_language_ui, 0)

    def update_language_ui(self, dt=None):
        """Update UI elements with new language strings."""
        # Update navigation item labels
        self.root.ids.home_label.text = translator.translate('navigation', 'home')
        self.root.ids.animals_label.text = translator.translate('navigation', 'animals')
        self.root.ids.assessments_label.text = translator.translate('navigation', 'assessments')
        self.root.ids.theme_toggle_label.text = translator.translate('navigation', 'theme')

        # Update the currently active screen
        current_screen = self.screen_manager.current_screen
        if hasattr(current_screen, 'update_language'):
            current_screen.update_language()


if __name__ == '__main__':
    MainApp().run()