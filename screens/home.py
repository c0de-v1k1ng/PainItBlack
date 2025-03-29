from functools import partial

from kivy.uix.screenmanager import Screen
from kivymd.uix.card import MDCard
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.fitimage import FitImage
from kivymd.uix.label import MDLabel
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

        try:
            img = FitImage(
                source=image,
                size_hint_y=0.7,
                # Update deprecated properties
                fit_mode="contain"  # Instead of allow_stretch and keep_ratio
            )
        except Exception:
            # Use a generic icon if the image file doesn't exist
            img = MDBoxLayout(
                size_hint_y=0.7,
                md_bg_color=(0.8, 0.8, 0.8, 1)
            )
        label = MDLabel(text=name, halign="center", size_hint_y=0.3)

        box.add_widget(img)
        box.add_widget(label)
        card.add_widget(box)

        return card

    def open_species_details(self, species_name, *args):
        """Navigate to species details screen."""
        species_screen = self.manager.get_screen("species_detail")
        species_screen.set_species_info(species_name)

        # Get the app instance and use the switch_screen method
        app = self.manager.get_parent_window().children[0]
        app.screen_manager.current = "species_detail"