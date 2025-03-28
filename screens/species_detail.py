from kivy.uix.screenmanager import Screen
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDButton
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.screen import MDScreen


class SpeciesDetailScreen(MDScreen):
    species_data = {
        "Rat": {
            "assessment_scales": ["Scale A", "Scale B"],
            "manuals": ["Manual 1", "Manual 2"],
            "videos": ["https://youtu.be/example1", "https://youtu.be/example2"],
        },
        "Mouse": {
            "assessment_scales": ["Scale X", "Scale Y"],
            "manuals": ["Manual A", "Manual B"],
            "videos": ["https://youtu.be/example3", "https://youtu.be/example4"],
        },
    }

    def set_species_info(self, species_name):
        """Update species detail screen with correct data."""
        if not species_name:
            species_name = "Unknown Species"

        self.ids.species_title.text = str(species_name)

        # ✅ Provide default empty lists if species is missing
        data = self.species_data.get(species_name, {"assessment_scales": [], "manuals": [], "videos": []})

        # ✅ Clear existing widgets before adding new ones
        self.ids.assessment_list.clear_widgets()
        self.ids.manual_list.clear_widgets()
        self.ids.video_list.clear_widgets()

        # ✅ Add assessment scales
        for scale in data["assessment_scales"]:
            self.ids.assessment_list.add_widget(MDLabel(text=scale, halign="left"))

        # ✅ Add manuals
        for manual in data["manuals"]:
            self.ids.manual_list.add_widget(MDLabel(text=manual, halign="left"))

        # ✅ Add video links as buttons
        for video in data["videos"]:
            video_button = MDButton(style="elevated", text="Watch Video", on_release=lambda x=video: self.open_video(x))
            self.ids.video_list.add_widget(video_button)

    def open_video(self, video_url):
        """Open video in a web browser."""
        import webbrowser
        webbrowser.open(video_url)
