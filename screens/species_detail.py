from kivy.metrics import dp
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDButton, MDButtonText
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel
from kivymd.uix.screen import MDScreen


class SpeciesDetailScreen(MDScreen):
    species_data = {
        "Rat": {
            "image": "assets/images/rat.png",
            "assessment_scales": [
                {
                    "name": "Body Condition Score",
                    "description": "Evaluates body fat and muscle mass on a 1-5 scale"
                },
                {
                    "name": "Grimace Scale",
                    "description": "Assesses pain by evaluating facial expressions"
                },
                {
                    "name": "Activity Score",
                    "description": "Evaluates general activity level and behavior"
                }
            ],
            "manuals": [
                {"title": "Rat Housing and Care Guide", "link": "https://www.nc3rs.org.uk/rat-housing-and-husbandry"},
                {"title": "Rat Grimace Scale Manual", "link": "https://www.nc3rs.org.uk/rat-grimace-scale"}
            ],
            "videos": [
                {"title": "Proper Rat Handling", "url": "https://www.youtube.com/watch?v=jIGKgZPMYxI"},
                {"title": "Rat Grimace Scale Guide", "url": "https://youtu.be/r7-XqOsAROE"}
            ],
        },
        "Mouse": {
            "image": "assets/images/mouse.png",
            "assessment_scales": [
                {
                    "name": "Mouse Grimace Scale",
                    "description": "Assesses pain by facial expressions on a 0-2 scale for each feature"
                },
                {
                    "name": "Body Condition Score",
                    "description": "Evaluates body fat and muscle mass on a 1-5 scale"
                },
                {
                    "name": "Activity Level",
                    "description": "Evaluates general behavior and activity patterns"
                }
            ],
            "manuals": [
                {"title": "Mouse Housing Guide", "link": "https://www.nc3rs.org.uk/mouse-housing-and-husbandry"},
                {"title": "Mouse Grimace Scale Manual", "link": "https://www.nc3rs.org.uk/mouse-grimace-scale"}
            ],
            "videos": [
                {"title": "Mouse Handling Techniques", "url": "https://youtu.be/PIkjMmXE3bg"},
                {"title": "Mouse Grimace Scale Demonstration", "url": "https://youtu.be/LvTWnBo62Sk"}
            ],
        },
        "Rabbit": {
            "image": "assets/images/rabbit.png",
            "assessment_scales": [
                {
                    "name": "Rabbit Grimace Scale",
                    "description": "Assesses pain by facial expressions on a 0-2 scale for each feature"
                },
                {
                    "name": "Body Condition Score",
                    "description": "Evaluates body fat and muscle mass on a 1-5 scale"
                },
                {
                    "name": "Wellness Score",
                    "description": "Evaluates general health and wellness"
                }
            ],
            "manuals": [
                {"title": "Rabbit Housing Guide", "link": "https://www.nc3rs.org.uk/rabbit-housing-and-husbandry"},
                {"title": "Rabbit Grimace Scale Manual", "link": "https://www.nc3rs.org.uk/rabbit-grimace-scale"}
            ],
            "videos": [
                {"title": "Rabbit Handling Techniques", "url": "https://youtu.be/example-rabbit"}
            ],
        },
        "Goat": {
            "image": "assets/images/goat.png",
            "assessment_scales": [
                {
                    "name": "FAMACHA Score",
                    "description": "Evaluates anemia based on lower eyelid membrane color"
                },
                {
                    "name": "Body Condition Score",
                    "description": "Evaluates fat cover and muscle mass on a 1-5 scale"
                },
                {
                    "name": "Pain Scale",
                    "description": "Assesses pain through behavioral indicators"
                }
            ],
            "manuals": [
                {"title": "Goat Care Guide", "link": "https://www.example.com/goat-care"}
            ],
            "videos": [
                {"title": "Goat Health Assessment", "url": "https://youtu.be/example-goat"}
            ],
        },
        "Sheep": {
            "image": "assets/images/sheep.png",
            "assessment_scales": [
                {
                    "name": "FAMACHA Score",
                    "description": "Evaluates anemia based on lower eyelid membrane color"
                },
                {
                    "name": "Body Condition Score",
                    "description": "Evaluates fat cover and muscle mass on a 1-5 scale"
                },
                {
                    "name": "Lameness Score",
                    "description": "Evaluates degree of lameness on a 0-3 scale"
                }
            ],
            "manuals": [
                {"title": "Sheep Care Guide", "link": "https://www.example.com/sheep-care"}
            ],
            "videos": [
                {"title": "Sheep Health Assessment", "url": "https://youtu.be/example-sheep"}
            ],
        },
        "Pig": {
            "image": "assets/images/pig.png",
            "assessment_scales": [
                {
                    "name": "Body Condition Score",
                    "description": "Evaluates fat cover and condition on a 1-5 scale"
                },
                {
                    "name": "Lameness Score",
                    "description": "Evaluates mobility on a 0-5 scale"
                },
                {
                    "name": "Welfare Assessment",
                    "description": "Evaluates overall welfare status"
                }
            ],
            "manuals": [
                {"title": "Pig Care Guide", "link": "https://www.example.com/pig-care"}
            ],
            "videos": [
                {"title": "Pig Health Assessment", "url": "https://youtu.be/example-pig"}
            ],
        },
    }

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.dialog = None
        self.video_dialog = None
        self.video_player = None

    def set_species_info(self, species_name):
        """Update species detail screen with correct data."""
        if not species_name:
            species_name = "Unknown Species"

        self.ids.species_title.text = str(species_name)

        # Provide default empty lists if species is missing
        data = self.species_data.get(species_name, {
            "image": "assets/images/animal_placeholder.png",
            "assessment_scales": [],
            "manuals": [],
            "videos": []
        })

        # Set species image with safe image loading
        try:
            self.ids.species_image.source = data.get("image", "assets/images/animal_placeholder.png")
        except Exception as e:
            # Log the error and fallback to placeholder
            print(f"Error loading image for {species_name}: {e}")
            self.ids.species_image.source = "assets/images/animal_placeholder.png"

        # Clear existing widgets before adding new ones
        self.ids.assessment_list.clear_widgets()
        self.ids.manual_list.clear_widgets()
        self.ids.video_list.clear_widgets()

        # Add assessment scales
        self._add_assessment_scales(data["assessment_scales"])

        # Add manuals
        self._add_manuals(data["manuals"])

        # Add videos
        self._add_videos(data["videos"])

    def _add_assessment_scales(self, scales):
        """Add assessment scales to the UI."""
        if not scales:
            self.ids.assessment_list.add_widget(MDLabel(
                text="No assessment scales available for this species",
                halign="center",
                size_hint_y=None,
                height=dp(40)
            ))
            return

        for scale in scales:
            scale_item = MDCard(
                orientation="vertical",
                padding=[dp(16), dp(12), dp(16), dp(12)],
                size_hint_y=None,
                height=dp(120),
                size_hint_x=1.0,
                radius=[8, 8, 8, 8],
                elevation=1,
                md_bg_color=self.theme_cls.secondaryContainerColor
            )

            # Create a box layout for the title to ensure proper centering
            title_box = MDBoxLayout(
                orientation="vertical",
                size_hint_y=None,
                height=dp(40),
                padding=[0, dp(4), 0, dp(4)]
            )

            title_label = MDLabel(
                text=scale["name"],
                font_style="Title",
                role="small",
                bold=True,
                halign="center",
                valign="center",
                adaptive_height=True
            )
            title_box.add_widget(title_label)
            scale_item.add_widget(title_box)

            # Create a box layout for the description
            desc_box = MDBoxLayout(
                orientation="vertical",
                size_hint_y=None,
                height=dp(80),
                padding=[0, dp(4), 0, dp(4)]
            )

            desc_label = MDLabel(
                text=scale["description"],
                font_style="Body",
                role="small",
                halign="center",
                valign="top",
                adaptive_height=True
            )
            desc_box.add_widget(desc_label)
            scale_item.add_widget(desc_box)

            self.ids.assessment_list.add_widget(scale_item)

    def _add_manuals(self, manuals):
        """Add manuals to the UI."""
        if not manuals:
            self.ids.manual_list.add_widget(MDLabel(
                text="No manuals available for this species",
                halign="center",
                size_hint_y=None,
                height=dp(40)
            ))
            return

        for manual in manuals:
            manual_item = MDCard(
                orientation="vertical",
                padding=[dp(16), dp(12), dp(16), dp(12)],
                size_hint_y=None,
                height=dp(100),
                size_hint_x=1.0,
                radius=[8, 8, 8, 8],
                elevation=1,
                md_bg_color=self.theme_cls.secondaryContainerColor
            )

            # Title
            title_box = MDBoxLayout(
                orientation="vertical",
                size_hint_y=None,
                height=dp(36),
                padding=[0, dp(4), 0, dp(4)]
            )

            title_label = MDLabel(
                text=manual["title"],
                font_style="Title",
                role="small",
                bold=True,
                halign="center",
                adaptive_height=True
            )
            title_box.add_widget(title_label)
            manual_item.add_widget(title_box)

            # Button container
            button_container = MDBoxLayout(
                orientation="horizontal",
                size_hint_y=None,
                height=dp(48),
                padding=[0, dp(6), 0, dp(6)]
            )

            # Create a button with fixed lambda to avoid reference issues
            button = MDButton(
                style="elevated",
                on_release=lambda x, link=manual["link"]: self.open_url(link),
                size_hint=(None, None),
                size=(dp(200), dp(36)),
                pos_hint={"center_x": 0.5, "center_y": 0.5}
            )
            button.add_widget(MDButtonText(text="Open Manual"))

            # Center the button
            button_container.add_widget(MDBoxLayout(size_hint_x=0.5))
            button_container.add_widget(button)
            button_container.add_widget(MDBoxLayout(size_hint_x=0.5))

            manual_item.add_widget(button_container)
            self.ids.manual_list.add_widget(manual_item)

    def _add_videos(self, videos):
        """Add videos to the UI."""
        if not videos:
            self.ids.video_list.add_widget(MDLabel(
                text="No videos available for this species",
                halign="center",
                size_hint_y=None,
                height=dp(40)
            ))
            return

        for video in videos:
            video_item = MDCard(
                orientation="vertical",
                padding=[dp(16), dp(12), dp(16), dp(12)],
                size_hint_y=None,
                height=dp(100),
                size_hint_x=1.0,
                radius=[8, 8, 8, 8],
                elevation=1,
                md_bg_color=self.theme_cls.secondaryContainerColor
            )

            # Title
            title_box = MDBoxLayout(
                orientation="vertical",
                size_hint_y=None,
                height=dp(36),
                padding=[0, dp(4), 0, dp(4)]
            )

            title_label = MDLabel(
                text=video["title"],
                font_style="Title",
                role="small",
                bold=True,
                halign="center",
                adaptive_height=True
            )
            title_box.add_widget(title_label)
            video_item.add_widget(title_box)

            # Button container
            button_container = MDBoxLayout(
                orientation="horizontal",
                size_hint_y=None,
                height=dp(48),
                padding=[0, dp(6), 0, dp(6)]
            )

            # Create a button with fixed lambda to avoid reference issues
            button = MDButton(
                style="elevated",
                on_release=lambda x, url=video["url"]: self.open_url(url),
                size_hint=(None, None),
                size=(dp(200), dp(36)),
                pos_hint={"center_x": 0.5, "center_y": 0.5}
            )
            button.add_widget(MDButtonText(text="Watch Video"))

            # Center the button
            button_container.add_widget(MDBoxLayout(size_hint_x=0.5))
            button_container.add_widget(button)
            button_container.add_widget(MDBoxLayout(size_hint_x=0.5))

            video_item.add_widget(button_container)
            self.ids.video_list.add_widget(video_item)

    def open_url(self, url):
        """Open URL in a web browser."""
        import webbrowser
        webbrowser.open(url)