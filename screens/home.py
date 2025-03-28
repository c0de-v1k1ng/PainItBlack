from functools import partial

from kivy.uix.screenmanager import Screen
from kivymd.uix.card import MDCard
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.fitimage import FitImage
from kivymd.uix.label import MDLabel
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.screen import MDScreen


class HomeScreen(MDScreen):
    species_list = [
        {"name": "Rat", "image": "assets/images/rat.png"},
        {"name": "Mouse", "image": "assets/images/mouse.png"},
        {"name": "Rabbit", "image": "assets/images/rabbit.png"},
        {"name": "Goat", "image": "assets/images/goat.png"},
        {"name": "Sheep", "image": "assets/images/sheep.png"},
        {"name": "Pig", "image": "assets/images/pig.png"},
    ]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.menu = None

    def show_menu(self):
        """Opens flyout menu on clicking menu button"""
        if not self.menu:
            menu_items = [
                {"leading_icon": "home", "text": "Home", "on_release": lambda x="home": self.navigate_to(x)},
                {"leading_icon": "paw", "text": "My Animals", "on_release": lambda x="my_animals": self.navigate_to(x)},
                {"leading_icon": "file-document", "text": "Assessments", "on_release": lambda x="assessments": self.navigate_to(x)}
            ]

            self.menu = MDDropdownMenu(
                caller=self.ids.menu_button,
                items=menu_items,
                width_mult=3
            )
        self.menu.open()

    def navigate_to(self, screen_name):
        """Switch to selected screen and close menu"""
        self.menu.dismiss()
        self.manager.current = screen_name

    def on_enter(self):
        """Load species dynamically into the grid."""
        grid = self.ids.species_grid
        grid.clear_widgets()

        for species in self.species_list:
            card = self.create_species_card(species["name"], species["image"])
            grid.add_widget(card)

    def create_species_card(self, name, image):
        """Create a card for each species."""
        card = MDCard(
            size_hint=(None, None),
            size=("150dp", "150dp"),
            orientation="vertical",
            on_release=partial(self.open_species_details, name),
        )

        box = MDBoxLayout(orientation="vertical")
        img = FitImage(source=image, size_hint_y=0.7)
        label = MDLabel(text=name, halign="center", size_hint_y=0.3)

        box.add_widget(img)
        box.add_widget(label)
        card.add_widget(box)

        return card

    def open_species_details(self, species_name, *args):
        """Navigate to species details screen."""
        species_screen = self.manager.get_screen("species_detail")
        species_screen.set_species_info(species_name)
        self.manager.current = "species_detail"