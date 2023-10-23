import datetime


class TimeBasedThemeSelector:
    def get_theme(self) -> str:
        """
        Returns the theme to use based on the current time
        """
        now = datetime.datetime.now()
        return "dracula" if now.hour > 18 or now.hour < 6 else "light"
