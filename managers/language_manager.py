"""
Translation module for the Animal Tracking App.
Manages language switching between German and English.
"""


class TranslationManager:
    """Manages translations and language switching for the application."""

    # Available languages
    LANGUAGES = {
        'en': 'English',
        'de': 'Deutsch'
    }

    # Translation dictionaries
    _translations = {
        # Main navigation items
        'navigation': {
            'home': {
                'en': 'Home',
                'de': 'Startseite'
            },
            'animals': {
                'en': 'Animals',
                'de': 'Tiere'
            },
            'assessments': {
                'en': 'Assessments',
                'de': 'Bewertungen'
            },
            'theme': {
                'en': 'Theme',
                'de': 'Design'
            }
        },

        # Screen titles
        'screen_titles': {
            'home': {
                'en': 'Home',
                'de': 'Startseite'
            },
            'species_detail': {
                'en': 'Species Details',
                'de': 'Artendetails'
            },
            'my_animals': {
                'en': 'My Animals',
                'de': 'Meine Tiere'
            },
            'assessments': {
                'en': 'Assessments',
                'de': 'Bewertungen'
            },
            'add_animal': {
                'en': 'Add Animal',
                'de': 'Tier hinzufügen'
            },
            'edit_animal': {
                'en': 'Edit Animal',
                'de': 'Tier bearbeiten'
            },
            'animal_detail': {
                'en': 'Animal Details',
                'de': 'Tierdetails'
            },
            'detailed_assessment': {
                'en': 'Detailed Assessment',
                'de': 'Detaillierte Bewertung'
            }
        },

        # Button labels
        'buttons': {
            'save': {
                'en': 'Save',
                'de': 'Speichern'
            },
            'cancel': {
                'en': 'Cancel',
                'de': 'Abbrechen'
            },
            'delete': {
                'en': 'Delete',
                'de': 'Löschen'
            },
            'edit': {
                'en': 'Edit',
                'de': 'Bearbeiten'
            },
            'add': {
                'en': 'Add',
                'de': 'Hinzufügen'
            },
            'close': {
                'en': 'Close',
                'de': 'Schließen'
            },
            'export': {
                'en': 'Export',
                'de': 'Exportieren'
            },
            'next': {
                'en': 'Next',
                'de': 'Weiter'
            },
            'previous': {
                'en': 'Previous',
                'de': 'Zurück'
            },
            'finish': {
                'en': 'Finish',
                'de': 'Abschließen'
            },
            'set_target': {
                'en': 'Set Target',
                'de': 'Ziel setzen'
            },
            'save_animal': {
                'en': 'Save Animal',
                'de': 'Tier speichern'
            },
            'save_changes': {
                'en': 'Save Changes',
                'de': 'Änderungen speichern'
            },
            'choose_photo': {
                'en': 'Choose Photo',
                'de': 'Foto auswählen'
            }
        },

        # Animal detail fields
        'animal_fields': {
            'name': {
                'en': 'Animal Name',
                'de': 'Tiername'
            },
            'species': {
                'en': 'Species',
                'de': 'Tierart'
            },
            'breed': {
                'en': 'Breed',
                'de': 'Rasse'
            },
            'birthday': {
                'en': 'Birthday',
                'de': 'Geburtsdatum'
            },
            'birthdate': {
                'en': 'Birthdate',
                'de': 'Geburtsdatum'
            },
            'sex': {
                'en': 'Sex',
                'de': 'Geschlecht'
            },
            'castrated': {
                'en': 'Castrated',
                'de': 'Kastriert'
            },
            'weight': {
                'en': 'Weight (kg)',
                'de': 'Gewicht (kg)'
            },
            'current_weight': {
                'en': 'Current Weight',
                'de': 'Aktuelles Gewicht'
            },
            'target_weight': {
                'en': 'Target Weight',
                'de': 'Zielgewicht'
            },
            'target_date': {
                'en': 'Target Date',
                'de': 'Zieldatum'
            }
        },

        # Assessment-related texts
        'assessments': {
            'title': {
                'en': 'Assessment Scale',
                'de': 'Bewertungsskala'
            },
            'question': {
                'en': 'Question',
                'de': 'Frage'
            },
            'of': {
                'en': 'of',
                'de': 'von'
            },
            'result': {
                'en': 'Result',
                'de': 'Ergebnis'
            },
            'score': {
                'en': 'Score',
                'de': 'Punktzahl'
            },
            'interpretation': {
                'en': 'Interpretation',
                'de': 'Interpretation'
            }
        },

        # Dialog texts
        'dialogs': {
            'confirm_deletion': {
                'en': 'Confirm Deletion',
                'de': 'Löschen bestätigen'
            },
            'success': {
                'en': 'Success',
                'de': 'Erfolg'
            },
            'error': {
                'en': 'Error',
                'de': 'Fehler'
            },
            'warning': {
                'en': 'Warning',
                'de': 'Warnung'
            },
            'missing_info': {
                'en': 'Missing Info',
                'de': 'Fehlende Informationen'
            },
            'set_weight_target': {
                'en': 'Set Weight Target',
                'de': 'Gewichtsziel festlegen'
            },
            'choose_photo_method': {
                'en': 'Choose Photo Method',
                'de': 'Fotomethode wählen'
            },
            'take_photo': {
                'en': 'Take Photo',
                'de': 'Foto aufnehmen'
            },
            'please_wait': {
                'en': 'Please Wait',
                'de': 'Bitte warten'
            },
            'exporting': {
                'en': 'Exporting...',
                'de': 'Exportiere...'
            }
        },

        # Weight tracking
        'weight': {
            'history': {
                'en': 'Weight History',
                'de': 'Gewichtsverlauf'
            },
            'add_weight': {
                'en': 'Add Weight',
                'de': 'Gewicht hinzufügen'
            },
            'add_weight_record': {
                'en': 'Add Weight Record',
                'de': 'Gewichtseintrag hinzufügen'
            },
            'date': {
                'en': 'Date',
                'de': 'Datum'
            },
            'weight': {
                'en': 'Weight',
                'de': 'Gewicht'
            },
            'weight_kg': {
                'en': 'Weight (kg)',
                'de': 'Gewicht (kg)'
            },
            'change': {
                'en': 'Change',
                'de': 'Änderung'
            },
            'weight_history_graph': {
                'en': 'Weight History Graph',
                'de': 'Gewichtsverlauf Diagramm'
            },
            'progress': {
                'en': 'Progress',
                'de': 'Fortschritt'
            },
            'remaining': {
                'en': 'Remaining',
                'de': 'Verbleibend'
            }
        },

        # Species details
        'species_details': {
            'assessment_scales': {
                'en': 'Assessment Scales',
                'de': 'Bewertungsskalen'
            },
            'manuals': {
                'en': 'Manuals',
                'de': 'Handbücher'
            },
            'training_videos': {
                'en': 'Training Videos',
                'de': 'Trainingsvideos'
            },
            'open_manual': {
                'en': 'Open Manual',
                'de': 'Handbuch öffnen'
            },
            'watch_video': {
                'en': 'Watch Video',
                'de': 'Video ansehen'
            }
        },

        # Export options
        'export': {
            'export_options': {
                'en': 'Export Options',
                'de': 'Exportoptionen'
            },
            'export_format': {
                'en': 'Select export format:',
                'de': 'Exportformat wählen:'
            },
            'pdf': {
                'en': 'PDF',
                'de': 'PDF'
            },
            'csv': {
                'en': 'CSV',
                'de': 'CSV'
            },
            'exported_to_pdf': {
                'en': 'Exported to PDF:',
                'de': 'Als PDF exportiert:'
            },
            'exported_to_csv': {
                'en': 'Exported to CSV files:',
                'de': 'Als CSV-Dateien exportiert:'
            }
        },

        # Messages
        'messages': {
            'no_animals': {
                'en': 'No animals added yet',
                'de': 'Noch keine Tiere hinzugefügt'
            },
            'animal_saved': {
                'en': 'Animal saved successfully!',
                'de': 'Tier erfolgreich gespeichert!'
            },
            'animal_updated': {
                'en': 'Animal updated successfully!',
                'de': 'Tier erfolgreich aktualisiert!'
            },
            'animal_deleted': {
                'en': 'Animal deleted successfully!',
                'de': 'Tier erfolgreich gelöscht!'
            },
            'weight_added': {
                'en': 'Weight record added successfully.',
                'de': 'Gewichtseintrag erfolgreich hinzugefügt.'
            },
            'weight_deleted': {
                'en': 'Weight record deleted successfully.',
                'de': 'Gewichtseintrag erfolgreich gelöscht.'
            },
            'assessment_saved': {
                'en': 'Assessment saved successfully!',
                'de': 'Bewertung erfolgreich gespeichert!'
            },
            'assessment_deleted': {
                'en': 'Assessment deleted successfully!',
                'de': 'Bewertung erfolgreich gelöscht!'
            },
            'target_set': {
                'en': 'Weight target set successfully!',
                'de': 'Gewichtsziel erfolgreich festgelegt!'
            },
            'target_cleared': {
                'en': 'Weight target cleared successfully!',
                'de': 'Gewichtsziel erfolgreich gelöscht!'
            },
            'no_assessments': {
                'en': 'No assessments found',
                'de': 'Keine Bewertungen gefunden'
            },
            'no_assessments_recorded': {
                'en': 'No assessments recorded',
                'de': 'Keine Bewertungen erfasst'
            },
            'confirm_delete_animal': {
                'en': 'Are you sure you want to delete this animal?',
                'de': 'Sind Sie sicher, dass Sie dieses Tier löschen möchten?'
            },
            'confirm_delete_weight': {
                'en': 'Are you sure you want to delete this weight record?',
                'de': 'Sind Sie sicher, dass Sie diesen Gewichtseintrag löschen möchten?'
            },
            'confirm_delete_assessment': {
                'en': 'Are you sure you want to delete this assessment?',
                'de': 'Sind Sie sicher, dass Sie diese Bewertung löschen möchten?'
            },
            'required_fields': {
                'en': 'Name/ID, Species, and Weight are required!',
                'de': 'Name/ID, Tierart und Gewicht sind erforderlich!'
            }
        },

        # Common terms
        'common': {
            'not_specified': {
                'en': 'Not specified',
                'de': 'Nicht angegeben'
            },
            'yes': {
                'en': 'Yes',
                'de': 'Ja'
            },
            'no': {
                'en': 'No',
                'de': 'Nein'
            },
            'male': {
                'en': 'Male',
                'de': 'Männlich'
            },
            'female': {
                'en': 'Female',
                'de': 'Weiblich'
            },
            'language': {
                'en': 'Language',
                'de': 'Sprache'
            }
        }
    }

    def __init__(self):
        """Initialize the translation manager with English as default."""
        self._current_language = 'en'
        self._observers = []

    @property
    def current_language(self):
        """Get the current language code."""
        return self._current_language

    def set_language(self, language_code):
        """
        Set the current language.

        Args:
            language_code (str): The language code ('en' or 'de')

        Returns:
            bool: True if language was changed, False otherwise
        """
        if language_code not in self.LANGUAGES:
            return False

        if language_code != self._current_language:
            self._current_language = language_code
            # Notify observers about language change
            self._notify_observers()
            return True
        return False

    def translate(self, category, key):
        """
        Get a translated string.

        Args:
            category (str): The translation category
            key (str): The translation key

        Returns:
            str: The translated string or the key itself if not found
        """
        try:
            return self._translations[category][key][self._current_language]
        except KeyError:
            # If translation not found, return the key itself
            return key

    def register_observer(self, observer):
        """
        Register an observer to be notified of language changes.

        Args:
            observer: An object with an update_language method
        """
        if observer not in self._observers:
            self._observers.append(observer)

    def unregister_observer(self, observer):
        """
        Unregister an observer.

        Args:
            observer: The observer to unregister
        """
        if observer in self._observers:
            self._observers.remove(observer)

    def _notify_observers(self):
        """Notify all observers about a language change."""
        for observer in self._observers:
            if hasattr(observer, 'update_language'):
                observer.update_language()


# Create a global instance to be used throughout the app
translator = TranslationManager()