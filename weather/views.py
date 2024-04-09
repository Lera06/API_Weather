import json
import requests
import os
from django.shortcuts import render, redirect
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .models import City
from .forms import CityForm
from dotenv import load_dotenv

load_dotenv()


def index(request):
    api_key = os.getenv('API_KEY')

    url = 'http://api.openweathermap.org/data/2.5/weather?q={}&units=metric&lang=ru&appid={}'

    cities = City.objects.all()

    # Постраничная разбивка с 2 городами на страницу:
    paginator = Paginator(cities, 2)
    page_number = request.GET.get('page', 1)
    try:
        page_obj = paginator.get_page(page_number)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)

    # Messages for users:
    error_message = ''
    message = ''
    message_class = ''   # css class, represents color of the message

    if request.method == 'POST':
        form = CityForm(request.POST)

        # How to get rid of the duplicates:
        if form.is_valid():
            # If form is valid, the entered city will be in a cleaned_data:
            new_city = form.cleaned_data['name']
            # Check the duplicates in db:
            existing_city_count = City.objects.filter(name=new_city).count()

            if existing_city_count == 0:
                # In addition, we need to check it a city exists in general (the correctness city name):
                data = requests.get(url.format(new_city, api_key)).json()
                # We check if data has a status = 200 OK:
                # print(data)
                if data['cod'] == 200:
                    form.save()
                    paginator = Paginator(cities, 2)
                    page_number = request.GET.get('page')
                    page_obj = paginator.get_page(page_number)
                else:
                    error_message = 'Неверный город. Попробуйте еще раз.'
            else:
                error_message = f'{new_city} уже существует в базе данных!'

        if error_message:
            message = error_message
            message_class = 'is-danger'
        else:
            message = f'{new_city} был успешно добавлен!'
            message_class = 'is-success'

    print(error_message)

    # Every time we submit the form, it restarts again (it becomes blank)
    form = CityForm()

    # cities = City.objects.all()

    # Create a weather data list:
    weather_data = []

    for city in page_obj:  # We iterate over page_obj!!!
        # We request the API data and convert the JSON to Python dict:
        data = requests.get(url.format(city, api_key)).json()

        # We create a dictionary with data that will be rendered in HTML:
        city_weather = {
            'city': city.name,
            'temperature': round(data['main']['temp']),
            'wind': round(data['wind']['speed']),
            'description': data['weather'][0]['description'],
            'icon': data['weather'][0]['icon'],
        }
        # We add the data for the current city into our list: list of the dicts
        weather_data.append(city_weather)

    # Let's pass all of that information over to template:
    context = {'weather_data': weather_data,
               'form': form,
               'message': message,
               'message_class': message_class,
               'page_obj': page_obj,
               }

    return render(request, 'weather/index.html', context)


def delete_city(request, city_name):
    City.objects.get(name=city_name).delete()

    return redirect('index')