from datetime import datetime
import pytz


def date_time(location):
    location = location

    # Specify the timezone of the desired location
    location_timezone = pytz.timezone(location)  # Replace with your desired timezone

    # Get the current date and time in the specified timezone
    current_datetime = datetime.now(location_timezone)
    current_timezone = pytz.timezone(location)

    # Format the date as year:month:day
    formatted_date = current_datetime.strftime('%Y:%m:%d')
    formatted_time = current_datetime.strftime('%H:%M:%S')

    return formatted_date, formatted_time

print(date_time("Africa/Lagos"))
