# Create a new file: utils/long_press.py

from kivy.clock import Clock


class LongPressDetector:
    """Utility for detecting long press gestures on widgets."""

    def __init__(self, widget, callback, duration=0.7):
        """
        Initialize a long press detector.

        Args:
            widget: The widget to detect long presses on
            callback: Function to call when a long press is detected.
                      Should accept the widget and touch event as parameters.
            duration: Duration in seconds to consider as a "long" press
        """
        self.widget = widget
        self.callback = callback
        self.duration = duration
        self.long_press_event = None

        # Bind to touch events
        self.widget.bind(on_touch_down=self.on_touch_down)
        self.widget.bind(on_touch_up=self.on_touch_up)
        self.widget.bind(on_touch_move=self.on_touch_move)

    def on_touch_down(self, widget, touch):
        """Handle touch down event."""
        if widget.collide_point(*touch.pos) and not touch.is_double_tap:
            # Cancel any existing long press detection
            self.cancel_long_press()

            # Store touch state
            touch.ud['long_press'] = {'widget': widget, 'pos': touch.pos}

            # Schedule long press detection
            self.long_press_event = Clock.schedule_once(
                lambda dt: self.on_long_press(touch),
                self.duration
            )
            return True
        return False

    def on_touch_up(self, widget, touch):
        """Handle touch up event."""
        if 'long_press' in touch.ud and touch.ud['long_press']['widget'] == widget:
            self.cancel_long_press()
            return True
        return False

    def on_touch_move(self, widget, touch):
        """Handle touch move event - cancel long press if moved too far."""
        if 'long_press' in touch.ud and touch.ud['long_press']['widget'] == widget:
            # Calculate distance moved
            start_pos = touch.ud['long_press']['pos']
            current_pos = touch.pos

            dx = abs(current_pos[0] - start_pos[0])
            dy = abs(current_pos[1] - start_pos[1])

            # If moved more than a small threshold, cancel long press
            if dx > 10 or dy > 10:  # 10 pixels threshold
                self.cancel_long_press()
            return True
        return False

    def on_long_press(self, touch):
        """Triggered when a long press is detected."""
        if 'long_press' in touch.ud:
            widget = touch.ud['long_press']['widget']
            self.callback(widget, touch)
            self.long_press_event = None

    def cancel_long_press(self):
        """Cancel any pending long press detection."""
        if self.long_press_event:
            self.long_press_event.cancel()
            self.long_press_event = None