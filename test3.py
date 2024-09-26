from sgp4.api import Satrec
from sgp4.api import jday
from datetime import datetime
import pytz
from skyfield.api import EarthSatellite, load
import time



import requests

# Landsat 9 
url = 'https://www.n2yo.com/sat/gettle.php?s=49260'

# Send a GET request
response = requests.get(url)

# Check if the request was successful
if response.status_code == 200:
    # Parse the response (as JSON if it's a JSON API)
    data = response.json()  # Use .text for raw data as a string
    print(data)
else:
    print(f"Error: {response.status_code}")





# TLE Data for Landsat 9
tle_line1 = data[0]
tle_line2 = data[1]


# Create a timescale object
ts = load.timescale()

# Create the EarthSatellite object
satellite = EarthSatellite(tle_line1, tle_line2, "Landsat 9", ts)

# Function to get current satellite coordinates and system time
def get_satellite_position():
    # Get current time in UTC
    utc_now = datetime.utcnow().replace(tzinfo=pytz.UTC)

    # Convert the current time to the Skyfield time format
    time_now = ts.utc(utc_now.year, utc_now.month, utc_now.day, utc_now.hour, utc_now.minute, utc_now.second)

    # Get the satellite's position relative to Earth at the current time
    geocentric = satellite.at(time_now)

    # Convert geocentric coordinates to latitude, longitude, and altitude
    subpoint = geocentric.subpoint()
    latitude = subpoint.latitude.degrees
    longitude = subpoint.longitude.degrees
    altitude = subpoint.elevation.km

    # Get the system time in local format
    system_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # Print the system time along with satellite position
    print(f"System Time: {system_time}")
    print(f"Latitude: {latitude:.6f} degrees")
    print(f"Longitude: {longitude:.6f} degrees")
    print(f"Altitude: {altitude:.2f} km")
    print("-" * 40)

# Continuously update the satellite position every second
try:
    while True:
        get_satellite_position()
        time.sleep(1)  # Pause for 1 second before the next update
except KeyboardInterrupt:
    print("Tracking stopped.")
