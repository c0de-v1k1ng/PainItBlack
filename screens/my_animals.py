from kivy.uix.screenmanager import Screen
from kivymd.app import MDApp
from kivymd.uix.list import MDList, MDListItem, MDListItemHeadlineText
from kivymd.uix.screen import MDScreen

import database

class MyAnimalsScreen(MDScreen):
    def on_enter(self):
        self.load_animals()

    def load_animals(self):
        self.ids.animals_list.clear_widgets()
        conn = database.get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, species FROM animals")
        for animal in cursor.fetchall():
            item = MDListItem(
                on_release=lambda x, a=animal[0]: self.view_animal(a)
            )
            #add headline text
            text_component = MDListItemHeadlineText(text=f"{animal[1]} ({animal[2]})")
            item.add_widget(text_component)

            self.ids.animals_list.add_widget(item)
        conn.close()

    def view_animal(self, animal_id):
        print(f"Selected Animal ID: {animal_id}")
