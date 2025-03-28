from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from kivymd.app import MDApp
from kivymd.theming import ThemeManager
from kivymd.uix.boxlayout import MDBoxLayout

import database
from screens.home import HomeScreen
from screens.species_detail import SpeciesDetailScreen
from screens.my_animals import MyAnimalsScreen
from screens.add_animal import AddAnimalScreen
from screens.assessments import AssessmentsScreen
from screens.animal_detail import AnimalDetailScreen


class RootLayout(MDBoxLayout):
    """Root layout that contains the navigation rail and screen manager."""
    pass


class MainApp(MDApp):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.theme_cls = ThemeManager()
        # Add backgroundColor property for dark/light mode
        self.theme_cls.backgroundColor = [0.98, 0.98, 0.98, 1]  # Light mode default
        self.nav_drawer = None
        self.active_nav_item = None

    def build(self):
        self.theme_cls.theme_style = "Light"  # ✅ Default theme
        self.theme_cls.primary_palette = "Gray"

        # Load root layout first
        Builder.load_file('kv/root_layout.kv')

        # Load all kv files dynamically
        for kv_file in ['home.kv', 'species_detail.kv', 'my_animals.kv', 'assessments.kv',
                        'add_animal.kv', 'animal_detail.kv']:
            Builder.load_file(f'kv/{kv_file}')
            print(f"✅ Loaded kv: {kv_file}")

        # Create the root layout
        self.root = RootLayout()

        # Get screen manager from root layout
        self.screen_manager = self.root.ids.screen_manager

        # Add screens to the screen manager
        self.screen_manager.add_widget(HomeScreen(name='home'))
        self.screen_manager.add_widget(SpeciesDetailScreen(name='species_detail'))
        self.screen_manager.add_widget(MyAnimalsScreen(name='my_animals'))
        self.screen_manager.add_widget(AssessmentsScreen(name='assessments'))
        self.screen_manager.add_widget(AddAnimalScreen(name='add_animal'))
        self.screen_manager.add_widget(AnimalDetailScreen(name='animal_detail'))

        # Set up active navigation item tracking
        self.active_nav_item = self.root.ids.nav_home

        return self.root

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

    def go_back(self):
        """Navigate back to the previous screen."""
        self.root.ids.screen_manager.current = 'home'
        self.set_active_nav_item(self.root.ids.nav_home)

    def edit_animal(self, animal_id):
        """Navigate to edit animal screen with the specified animal."""
        # This will be implemented when we add animal editing functionality
        print(f"Edit animal {animal_id}")

    def new_assessment(self, animal_id):
        """Navigate to assessment screen for the specified animal."""
        assessment_screen = self.screen_manager.get_screen('assessments')
        assessment_screen.selected_animal_id = animal_id
        self.screen_manager.current = 'assessments'
        self.set_active_nav_item(self.root.ids.nav_assessments)


if __name__ == '__main__':
    MainApp().run()