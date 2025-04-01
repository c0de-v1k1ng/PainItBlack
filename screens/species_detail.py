from kivy.uix.screenmanager import Screen
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDButton, MDButtonText
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.screen import MDScreen
from kivymd.uix.card import MDCard
from kivy.metrics import dp
from kivy.uix.video import Video
from kivymd.uix.dialog import MDDialog, MDDialogHeadlineText, MDDialogContentContainer, MDDialogButtonContainer
from kivymd.uix.list import MDListItem, MDListItemHeadlineText, MDListItemSupportingText


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
                {"title": "Proper Rat Handling", "url": "https://youtu.be/7w-YnH7GRm8"},
                {"title": "Rat Grimace Scale Guide", "url": "https://youtu.be/LvTWnBo62Sk"}
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

        # Set species image
        try:
            self.ids.species_image.source = data.get("image", "assets/images/animal_placeholder.png")
        except:
            # Fallback if image loading fails
            self.ids.species_image.source = "assets/images/animal_placeholder.png"

        # Clear existing widgets before adding new ones
        self.ids.assessment_list.clear_widgets()
        self.ids.manual_list.clear_widgets()
        self.ids.video_list.clear_widgets()

        # Add assessment scales with better content containment
        for scale in data["assessment_scales"]:
            scale_item = MDCard(
                orientation="vertical",
                padding=[dp(16), dp(12), dp(16), dp(12)],  # Adjusted padding
                size_hint_y=None,
                height=dp(100),  # Increased height to accommodate content
                size_hint_x=1.0,  # Ensure full width
                radius=[8, 8, 8, 8],
                elevation=1,
                md_bg_color=self.theme_cls.secondaryContainerColor
            )

            # Title with proper containment
            title_label = MDLabel(
                text=scale["name"],
                font_style="Title",
                role="small",
                bold=True,
                halign="center",
                valign="middle",  # Vertical alignment
                size_hint_y=None,
                height=dp(36),  # Fixed height for title
                adaptive_height=False  # Disable adaptive height to maintain fixed size
            )
            scale_item.add_widget(title_label)

            # Description with proper containment
            desc_label = MDLabel(
                text=scale["description"],
                font_style="Body",
                role="small",
                halign="center",
                valign="top",  # Align to top
                size_hint_y=None,
                height=dp(64),  # Fixed height for description
                adaptive_height=False  # Disable adaptive height
            )
            scale_item.add_widget(desc_label)

            self.ids.assessment_list.add_widget(scale_item)

        # If no scales are available
        if not data["assessment_scales"]:
            self.ids.assessment_list.add_widget(MDLabel(
                text="No assessment scales available for this species",
                halign="center",
                size_hint_y=None,
                height=dp(40)
            ))

        # Add manuals with better content containment
        for manual in data["manuals"]:
            manual_item = MDCard(
                orientation="vertical",
                padding=[dp(16), dp(12), dp(16), dp(12)],
                size_hint_y=None,
                height=dp(100),  # Fixed height
                size_hint_x=1.0,  # Full width
                radius=[8, 8, 8, 8],
                elevation=1,
                md_bg_color=self.theme_cls.secondaryContainerColor
            )

            # Title with fixed height
            manual_item.add_widget(MDLabel(
                text=manual["title"],
                halign="center",
                font_style="Title",
                role="small",
                bold=True,
                size_hint_y=None,
                height=dp(36),
                adaptive_height=False
            ))

            # Button container with fixed height
            button_container = MDBoxLayout(
                orientation="horizontal",
                size_hint_y=None,
                height=dp(48),
                padding=[0, dp(6), 0, dp(6)]
            )

            # Button centered in container
            button = MDButton(
                style="elevated",
                on_release=lambda x, link=manual["link"]: self.open_url(link),
                size_hint=(None, None),
                size=(dp(200), dp(36)),
                pos_hint={"center_x": 0.5, "center_y": 0.5}
            )
            button.add_widget(MDButtonText(text="Open Manual"))

            # Add button to a centered box
            centered_box = MDBoxLayout(
                orientation="horizontal",
                size_hint_x=1.0
            )
            centered_box.add_widget(MDBoxLayout(size_hint_x=0.5))
            centered_box.add_widget(button)
            centered_box.add_widget(MDBoxLayout(size_hint_x=0.5))

            button_container.add_widget(centered_box)
            manual_item.add_widget(button_container)

            self.ids.manual_list.add_widget(manual_item)

        # If no manuals are available
        if not data["manuals"]:
            self.ids.manual_list.add_widget(MDLabel(
                text="No manuals available for this species",
                halign="center",
                size_hint_y=None,
                height=dp(40)
            ))

        # Videos with better content containment
        for video in data["videos"]:
            video_item = MDCard(
                orientation="vertical",
                padding=[dp(16), dp(12), dp(16), dp(12)],
                size_hint_y=None,
                height=dp(100),  # Fixed height
                size_hint_x=1.0,  # Full width
                radius=[8, 8, 8, 8],
                elevation=1,
                md_bg_color=self.theme_cls.secondaryContainerColor
            )

            # Title with fixed height
            video_item.add_widget(MDLabel(
                text=video["title"],
                halign="center",
                font_style="Title",
                role="small",
                bold=True,
                size_hint_y=None,
                height=dp(36),
                adaptive_height=False
            ))

            # Button container with fixed height
            button_container = MDBoxLayout(
                orientation="horizontal",
                size_hint_y=None,
                height=dp(48),
                padding=[0, dp(6), 0, dp(6)]
            )

            # Button centered in container
            button = MDButton(
                style="elevated",
                on_release=lambda x, v=video["url"]: self.open_url(v),
                size_hint=(None, None),
                size=(dp(200), dp(36)),
                pos_hint={"center_x": 0.5, "center_y": 0.5}
            )
            button.add_widget(MDButtonText(text="Watch Video"))

            # Add button to a centered box
            centered_box = MDBoxLayout(
                orientation="horizontal",
                size_hint_x=1.0
            )
            centered_box.add_widget(MDBoxLayout(size_hint_x=0.5))
            centered_box.add_widget(button)
            centered_box.add_widget(MDBoxLayout(size_hint_x=0.5))

            button_container.add_widget(centered_box)
            video_item.add_widget(button_container)

            self.ids.video_list.add_widget(video_item)

        # If no videos are available
        if not data["videos"]:
            self.ids.video_list.add_widget(MDLabel(
                text="No videos available for this species",
                halign="center",
                size_hint_y=None,
                height=dp(40)
            ))

    def open_url(self, url):
        """Open URL in a web browser."""
        import webbrowser
        webbrowser.open(url)