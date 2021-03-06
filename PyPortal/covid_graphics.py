import time
import json
import displayio
from adafruit_display_text.label import Label
from adafruit_bitmap_font import bitmap_font

cwd = ("/"+__file__).rsplit('/', 1)[0] # the current working directory (where this file is)

small_font = cwd+"/fonts/Arial-12.bdf"
medium_font = cwd+"/fonts/Arial-16.bdf"
large_font = cwd+"/fonts/Arial-Bold-24.bdf"

class Covid_Graphics(displayio.Group):
    def __init__(self, root_group, *, am_pm=True):
        super().__init__(max_size=2)
        self.am_pm = am_pm
        root_group.append(self)
        self._icon_group = displayio.Group(max_size=1)
        self.append(self._icon_group)
        self._text_group = displayio.Group(max_size=9)
        self.append(self._text_group)

        self._icon_sprite = None
        self._icon_file = None
        self.set_icon(cwd+"/icons/sarscov2.bmp")

        self.small_font = bitmap_font.load_font(small_font)
        self.medium_font = bitmap_font.load_font(medium_font)
        self.large_font = bitmap_font.load_font(large_font)
        glyphs = b'0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ-,.: '
        self.small_font.load_glyphs(glyphs)
        self.medium_font.load_glyphs(glyphs)
        self.large_font.load_glyphs(glyphs)
        self.large_font.load_glyphs(('°',))  # a non-ascii character we need for sure
        self.country_text = None

        self.time_text = Label(self.medium_font, max_glyphs=8)
        self.time_text.x = 220
        self.time_text.y = 12
        self.time_text.color = 0xFFFFFF
        self._text_group.append(self.time_text)

        self.date_text = Label(self.medium_font, max_glyphs=10)
        self.date_text.x = 200
        self.date_text.y = 220
        self.date_text.color = 0xFFFFFF
        self._text_group.append(self.date_text)

        self.country_text = Label(self.medium_font, max_glyphs=60)
        self.country_text.x = 10
        self.country_text.y = 12
        self.country_text.color = 0xFFFFFF
        self._text_group.append(self.country_text)

        self.deaths_text = Label(self.medium_font, max_glyphs=18)
        self.deaths_text.x = 10
        self.deaths_text.y = 105
        self.deaths_text.color = 0xFFFFFF
        self._text_group.append(self.deaths_text)

        self.recovered_text = Label(self.medium_font, max_glyphs=18)
        self.recovered_text.x = 10
        self.recovered_text.y = 135
        self.recovered_text.color = 0xFFFFFF
        self._text_group.append(self.recovered_text)

        self.today_cases_text = Label(self.medium_font, max_glyphs=18)
        self.today_cases_text.x = 10
        self.today_cases_text.y = 165
        self.today_cases_text.color = 0xFFFFFF
        self._text_group.append(self.today_cases_text)

        self.cases_text = Label(self.large_font, max_glyphs=20)
        self.cases_text.x = 10
        self.cases_text.y = 195
        self.cases_text.color = 0xFFFFFF
        self._text_group.append(self.cases_text)

        self.fatality_text = Label(self.small_font, max_glyphs=60)
        self.fatality_text.x = 10
        self.fatality_text.y = 225
        self.fatality_text.color = 0xFFFFFF
        self._text_group.append(self.fatality_text)

    def display_cases(self, covid_data):
        covid = json.loads(covid_data)

        self.update_time()
        print(covid["data"][0])
        self.country_text.text =  str(covid["data"][0]["region"]["name"])
        self.deaths_text.text = "Deaths: " + str(covid["data"][0]["deaths"])
        self.recovered_text.text = "Recovered: " + str(covid["data"][0]["recovered"])
        self.today_cases_text.text = "Today Cases: " + str(covid["data"][0]["confirmed_diff"])
        self.cases_text.text = "Cases: " + str(covid["data"][0]["confirmed"])
        self.fatality_text.text = "Fatality rate: " + str(covid["data"][0]["fatality_rate"])

    def update_time(self):
        """Fetch the time.localtime(), parse it out and update the display text"""
        now = time.localtime()
        hour = now[3]
        minute = now[4]
        year = now[0]
        month = now[1]
        day = now[2]
        time_format_str = "%d:%02d"
        date_format_str = "%d-%02d-%02d"
        if self.am_pm:
            if hour >= 12:
                hour -= 12
                time_format_str = time_format_str+" PM"
            else:
                time_format_str = time_format_str+" AM"
            if hour == 0:
                hour = 12
        time_str = time_format_str % (hour, minute)
        print(time_str)
        date_str = date_format_str % (year, month, day)
        self.date_text.text = date_str
        self.time_text.text = time_str

    def set_icon(self, filename):
        """The background image to a bitmap file.

        :param filename: The filename of the chosen icon

        """
        print("Set icon to ", filename)
        if self._icon_group:
            self._icon_group.pop()

        if not filename:
            return  # we're done, no icon desired
        if self._icon_file:
            self._icon_file.close()
        self._icon_file = open(filename, "rb")
        icon = displayio.OnDiskBitmap(self._icon_file)
        try:
            self._icon_sprite = displayio.TileGrid(icon,
                                                   pixel_shader=displayio.ColorConverter())
        except TypeError:
            self._icon_sprite = displayio.TileGrid(icon,
                                                   pixel_shader=displayio.ColorConverter(),
                                                   position=(0,0))
        self._icon_group.append(self._icon_sprite)