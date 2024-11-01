import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
import aiohttp

# Set up logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# OpenWeatherMap API key
OWM_API_KEY = 'd3ace83101963ae6042e0506d0e66429'

# Data with countries and cities
data = {
    "Africa": {
        "Nigeria": ["Lagos", "Abuja", "Kano", "Ibadan", "Benin City"],
        "Egypt": ["Cairo", "Alexandria", "Giza", "Shubra El Kheima", "Port Said"],
        "South Africa": ["Johannesburg", "Cape Town", "Durban", "Pretoria", "Port Elizabeth"],
        "Kenya": ["Nairobi", "Mombasa", "Kisumu", "Nakuru", "Eldoret"],
        "Morocco": ["Casablanca", "Rabat", "Fes", "Marrakech", "Agadir"],
        # Add more African countries...
    },
    "Asia": {
        "China": ["Beijing", "Shanghai", "Guangzhou", "Shenzhen", "Chengdu"],
        "India": ["Mumbai", "Delhi", "Bangalore", "Hyderabad", "Chennai"],
        "Japan": ["Tokyo", "Osaka", "Nagoya", "Sapporo", "Fukuoka"],
        "South Korea": ["Seoul", "Busan", "Incheon", "Daegu", "Daejeon"],
        "Indonesia": ["Jakarta", "Surabaya", "Bandung", "Medan", "Bekasi"],
        # Add more Asian countries...
    },
    "Europe": {
        "UK": ["London", "Manchester", "Birmingham", "Leeds", "Glasgow"],
        "Germany": ["Berlin", "Munich", "Frankfurt", "Hamburg", "Cologne"],
        "France": ["Paris", "Marseille", "Lyon", "Toulouse", "Nice"],
        "Italy": ["Rome", "Milan", "Naples", "Turin", "Palermo"],
        "Spain": ["Madrid", "Barcelona", "Valencia", "Seville", "Zaragoza"],
        # Add more European countries...
    },
    "North America": {
        "USA": ["New York", "Los Angeles", "Chicago", "Houston", "Phoenix"],
        "Canada": ["Toronto", "Vancouver", "Montreal", "Calgary", "Edmonton"],
        "Mexico": ["Mexico City", "Guadalajara", "Monterrey", "Puebla", "Cancun"],
        # Add more North American countries...
    },
    "South America": {
        "Brazil": ["São Paulo", "Rio de Janeiro", "Brasília", "Salvador", "Fortaleza"],
        "Argentina": ["Buenos Aires", "Córdoba", "Rosario", "Mendoza", "La Plata"],
        "Chile": ["Santiago", "Valparaíso", "Concepción", "La Serena", "Antofagasta"],
        # Add more South American countries...
    },
    "Australia/Oceania": {
        "Australia": ["Sydney", "Melbourne", "Brisbane", "Perth", "Adelaide"],
        "New Zealand": ["Auckland", "Wellington", "Christchurch", "Hamilton", "Dunedin"],
        # Add more countries from Oceania...
    }
}

# Function to get weather data by city name
async def get_weather(city: str):
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={OWM_API_KEY}&units=metric"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return await response.json()

# Function to get weather data by coordinates
async def get_weather_by_coordinates(lat: float, lon: float):
    url = f"http://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={OWM_API_KEY}&units=metric"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return await response.json()

# Start command handler
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    keyboard = [
        [InlineKeyboardButton(continent, callback_data=continent) for continent in data.keys()]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text('Select a continent:', reply_markup=reply_markup)

# Button callback handler
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    data_key = query.data
    if data_key in data:  # It's a continent
        countries = data[data_key]
        keyboard = [[InlineKeyboardButton(country, callback_data=country)] for country in countries]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(f'Select a country in {data_key}:', reply_markup=reply_markup)
    elif any(data_key in countries for countries in data.values()):  # It's a country
        continent = next(cont for cont, countries in data.items() if data_key in countries)
        cities = data[continent][data_key]
        keyboard = [[InlineKeyboardButton(city, callback_data=city)] for city in cities]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(f'Select a city in {data_key}:', reply_markup=reply_markup)
    else:  # It's a city
        await city_weather(update, context)

# Weather response handler
async def city_weather(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    city = query.data
    weather_data = await get_weather(city)
    if weather_data:
        description = weather_data['weather'][0]['description']
        temperature = weather_data['main']['temp']
        await query.edit_message_text(f"Weather in {city}:\nDescription: {description}\nTemperature: {temperature}°C")
    else:
        await query.edit_message_text(f"Could not retrieve weather for {city}.")

# Location message handler
async def location(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_location = update.message.location
    weather_data = await get_weather_by_coordinates(user_location.latitude, user_location.longitude)
    if weather_data:
        description = weather_data['weather'][0]['description']
        temperature = weather_data['main']['temp']
        await update.message.reply_text(f"Weather at your location:\nDescription: {description}\nTemperature: {temperature}°C")
    else:
        await update.message.reply_text("Could not retrieve weather data for your location.")

def main():
    application = Application.builder().token("7174357689:AAHGaDLBJcuIWQ0NOEYlNGiivXBvUL4N_Jk").build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button))
    application.add_handler(MessageHandler(filters.LOCATION, location))

    application.run_polling()

if __name__ == '__main__':
    main()
