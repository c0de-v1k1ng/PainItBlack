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

class MainApp(MDApp):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def build(self):
        self.theme_cls.theme_style = "Light"  # ✅ Default theme
        self.theme_cls.primary_palette = "Gray"

        # Load all kv files dynamically
        for kv_file in ['home.kv', 'species_detail.kv', 'my_animals.kv', 'assessments.kv', 'add_animal.kv']:
            Builder.load_file(f'kv/{kv_file}')
            print(f"✅ Loaded kv: {kv_file}")

        # Initialize ScreenManager
        sm = ScreenManager()
        sm.add_widget(HomeScreen(name='home'))
        sm.add_widget(SpeciesDetailScreen(name='species_detail'))
        sm.add_widget(MyAnimalsScreen(name='my_animals'))
        sm.add_widget(AssessmentsScreen(name='assessments'))
        sm.add_widget(AddAnimalScreen(name='add_animal'))
        return sm


    def toggle_theme(self):
        """Toggle between Light and Dark mode dynamically."""
        self.theme_cls.theme_style = ("Dark" if self.theme_cls.theme_style == "Light" else "Light")

if __name__ == '__main__':
    MainApp().run()
