from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from kivymd.app import MDApp
from kivymd.theming import ThemeManager

import database
from screens.home import HomeScreen
from screens.species_detail import SpeciesDetailScreen
from screens.my_animals import MyAnimalsScreen
from screens.add_animal import AddAnimalScreen
from screens.assessments import AssessmentsScreen
from screens.animal_detail import AnimalDetailScreen

class MainApp(MDApp):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.theme_cls = ThemeManager()
        # Add backgroundColor property for dark/light mode
        self.theme_cls.backgroundColor = [0.98, 0.98, 0.98, 1]  # Light mode default

    def build(self):
        self.theme_cls.theme_style = "Light"  # ✅ Default theme
        self.theme_cls.primary_palette = "Gray"

        # Load all kv files dynamically
        for kv_file in ['home.kv', 'species_detail.kv', 'my_animals.kv', 'assessments.kv', 'add_animal.kv', 'animal_detail.kv']:
            Builder.load_file(f'kv/{kv_file}')
            print(f"✅ Loaded kv: {kv_file}")

        # Initialize ScreenManager
        sm = ScreenManager()
        sm.add_widget(HomeScreen(name='home'))
        sm.add_widget(SpeciesDetailScreen(name='species_detail'))
        sm.add_widget(MyAnimalsScreen(name='my_animals'))
        sm.add_widget(AssessmentsScreen(name='assessments'))
        sm.add_widget(AddAnimalScreen(name='add_animal'))
        sm.add_widget(AnimalDetailScreen(name='animal_detail'))
        return sm


    def toggle_theme(self):
        """Toggle between Light and Dark mode dynamically."""
        if self.theme_cls.theme_style == "Light":
            self.theme_cls.theme_style = "Dark"
            self.theme_cls.backgroundColor = [0.1, 0.1, 0.1, 1]  # Dark mode
        else:
            self.theme_cls.theme_style = "Light"
            self.theme_cls.backgroundColor = [0.98, 0.98, 0.98, 1]  # Light mode

    def go_back(self):
        """Navigate back to the previous screen."""
        self.root.current = 'home'

    def edit_animal(self, animal_id):
        """Navigate to edit animal screen with the specified animal."""
        # This will be implemented when we add animal editing functionality
        print(f"Edit animal {animal_id}")

    def new_assessment(self, animal_id):
        """Navigate to assessment screen for the specified animal."""
        assessment_screen = self.root.get_screen('assessments')
        assessment_screen.selected_animal_id = animal_id
        self.root.current = 'assessments'
        # This will trigger the new assessment dialog from the animal details
        # (Implementation will be added)

if __name__ == '__main__':
    MainApp().run()