# src/map_generator.py

import folium

class MapGenerator:
    def __init__(self, map_path='map.html'):
        self.map_path = map_path
        self.locations = set() # Use a set to avoid duplicate markers
        self.map = folium.Map(location=[20, 0], zoom_start=2, tiles='CartoDB dark_matter')

    def add_location(self, lat, lon, popup_text):
        """Adds a marker to the map if it doesn't already exist."""
        if (lat, lon) not in self.locations:
            folium.Marker([lat, lon], popup=popup_text).add_to(self.map)
            self.locations.add((lat, lon))

    def save_map(self):
        """Saves the map to an HTML file."""
        self.map.get_root().html.add_child(folium.Element("<script>var map = {};</script>".format(self.map.get_name())))
        self.map.save(self.map_path)
