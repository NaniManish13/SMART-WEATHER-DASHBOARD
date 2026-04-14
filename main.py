import sys
import requests
from PyQt5.QtWidgets import (QWidget, QApplication, QVBoxLayout, 
                             QLineEdit, QPushButton, QLabel, QMessageBox)
from PyQt5.QtCore import Qt
import matplotlib.pyplot as plt
from datetime import datetime

# ---------------- WEATHER UTILS ----------------

def kelvin_to_celsius(kelvin):
    return kelvin - 273.15

def celsius_to_fahrenheit(celsius):
    return (celsius * 9/5) + 32

def extract_weather_metrics(data):
    main = data["main"]
    weather = data["weather"][0]
    wind = data["wind"]
    
    temp_c = kelvin_to_celsius(main["temp"])
    temp_f = celsius_to_fahrenheit(temp_c)
    
    return {
        "temp_c": temp_c,
        "temp_f": temp_f,
        "humidity": main["humidity"],
        "weather_id": weather["id"],
        "wind_speed": wind["speed"],
        "pressure": main["pressure"],
        "description": weather["description"].title(),
        "time_now": datetime.now().strftime('%d %b %Y %H:%M')
    }

# ---------------- MAIN APP ----------------

class SmartWeatherDashboard(QWidget):
    def __init__(self):
        super().__init__()
        self.unit = "C"
        self.cache = {}
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Weather Dashboard")
        self.setGeometry(200, 100, 500, 600)

        # UI Elements
        self.city_input = QLineEdit()
        self.city_input.setPlaceholderText("Enter city name")
        
        self.fetch_btn = QPushButton("Get Weather")
        self.toggle_btn = QPushButton("°C/°F")
        self.graph_btn = QPushButton("Show Graphs")
        
        self.temp_label = QLabel()
        self.temp_label.setAlignment(Qt.AlignCenter)
        
        self.emoji_label = QLabel()
        self.emoji_label.setAlignment(Qt.AlignCenter)
        
        self.desc_label = QLabel()
        self.desc_label.setAlignment(Qt.AlignCenter)
        
        self.details_label = QLabel()
        self.details_label.setAlignment(Qt.AlignCenter)

        # Layout
        layout = QVBoxLayout(self)
        layout.addWidget(self.city_input)
        layout.addWidget(self.fetch_btn)
        layout.addWidget(self.toggle_btn)
        layout.addWidget(self.temp_label)
        layout.addWidget(self.emoji_label)
        layout.addWidget(self.desc_label)
        layout.addWidget(self.details_label)
        layout.addWidget(self.graph_btn)

        self.apply_styles()

        # Connections
        self.fetch_btn.clicked.connect(self.fetch_weather)
        self.toggle_btn.clicked.connect(self.toggle_unit)
        self.graph_btn.clicked.connect(self.show_graphs)
        self.city_input.returnPressed.connect(self.fetch_weather)

        # Initial state
        self.toggle_btn.hide()
        self.graph_btn.hide()
        self.temp_label.hide()
        self.emoji_label.hide()
        self.desc_label.hide()
        self.details_label.hide()

    def fetch_weather(self):
        city = self.city_input.text().strip().title()
        if not city:
            return

        api_key = "YOUR_API_KEY"

        try:
            if city in self.cache:
                data = self.cache[city]
            else:
                url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}"
                r = requests.get(url, timeout=5)
                r.raise_for_status()
                data = r.json()
                self.cache[city] = data
            
            self.metrics = extract_weather_metrics(data)
            self.display_weather()
        except:
            QMessageBox.critical(self, "Error", "City not found / Network error")

    def display_weather(self):
        self.temp_c = self.metrics["temp_c"]
        self.temp_f = self.metrics["temp_f"]
        self.weather_id = self.metrics["weather_id"]
        self.humidity = self.metrics["humidity"]
        self.wind_speed = self.metrics["wind_speed"]
        self.pressure = self.metrics["pressure"]
        self.description = self.metrics["description"]
        self.time_now = self.metrics["time_now"]

        self.update_temp()
        
        self.temp_label.show()
        self.emoji_label.show()
        self.desc_label.show()
        self.details_label.show()
        self.toggle_btn.show()
        self.graph_btn.show()

        self.emoji_label.setText(self.get_weather_emoji(self.weather_id))
        self.desc_label.setText(self.description)
        
        self.details_label.setText(
            f"Humidity: {self.humidity}%\n"
            f"Wind: {self.wind_speed} m/s\n"
            f"Pressure: {self.pressure} hPa\n"
            f"Time: {self.time_now}"
        )

    def toggle_unit(self):
        self.unit = "F" if self.unit == "C" else "C"
        self.update_temp()

    def update_temp(self):
        temp = self.temp_c if self.unit == "C" else self.temp_f
        self.temp_label.setText(f"{temp:.1f}°{self.unit}")

    def show_graphs(self):
        plt.figure(figsize=(6, 4))
        plt.bar(["Temp", "Humidity", "Wind"], 
                [self.temp_c, self.humidity, self.wind_speed])
        plt.title("Weather Metrics")
        plt.show()

    @staticmethod
    def get_weather_emoji(wid):
        if 200 <= wid <= 232: return "⛈️"
        if 300 <= wid <= 321: return "🌦️"
        if 500 <= wid <= 531: return "🌧️"
        if 600 <= wid <= 622: return "❄️"
        if wid == 800: return "☀️"
        if 801 <= wid <= 804: return "☁️"
        return "❓"

    def apply_styles(self):
        self.setStyleSheet("""
            QWidget { background: #1e3c72; color: white; }
            QLineEdit { font-size:18px; padding: 8px; border-radius:8px; color: black; }
            QPushButton { font-size:16px; padding:10px; border-radius: 10px; background: #ff9800; }
            QLabel { font-size:15px; }
        """)
        self.temp_label.setStyleSheet("font-size:48px; font-weight:bold;")
        self.emoji_label.setStyleSheet("font-size:40px;")

# ---------------- RUN APP ----------------

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SmartWeatherDashboard()
    window.show()
    sys.exit(app.exec_())