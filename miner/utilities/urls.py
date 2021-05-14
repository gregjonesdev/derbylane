trackinfo_mobile_base = "http://m.trackinfo.com/"
trackinfo_desktop_base = "https://www.trackinfo.com/"

results_extension = "/index.jsp?next=resultsrace&raceid="
entries_extension = "/index.jsp?next=entriesrace&raceid="

results_url = "{}{}".format(trackinfo_mobile_base, results_extension)
entries_url = "{}{}".format(trackinfo_mobile_base, entries_extension)

almanac_root = "https://www.almanac.com/weather/history/zipcode/"
dog_root = "{}dog.jsp?runnername=".format(trackinfo_desktop_base)

all_race_results = "{}dog-racelines.jsp?page=1&runnername=".format(trackinfo_desktop_base)
all_race_suffix = "&TotalRowCount=20000"


australia_attempt = "https://old.thedogs.com.au/Racing/RacingFormFields.aspx?meetid=260281"

json_suffix = "&language=en-US&units=e&format=json"
base_url = "https://api.weather.com/v3/wx/forecast/daily/7day?apiKey="
api_key = "6532d6454b8aa370768e63d6ba5a832e"


def build_entries_url(venue_code, year, month, day, time, race_number):
    return "{}G{}${}{}{}{}{}".format(
        entries_url,
        venue_code,
        year,
        str(month).zfill(2),
        str(day).zfill(2),
        time,
        str(race_number).zfill(2))

def build_race_results_url(venue_code, year, month, day, time, race_number):
    return "{}G{}${}{}{}{}{}".format(
        results_url,
        venue_code,
        year,
        str(month).zfill(2),
        str(day).zfill(2),
        time,
        str(race_number).zfill(2))

def build_dog_results_url(dog_name):
    return "{}{}{}".format(all_race_results, dog_name, all_race_suffix)

def build_forecast_url(program):
    return "{}{}&geocode={}{}".format(
        base_url,
        api_key,
        program.venue.weatherlookup.geocode,
        json_suffix)

def build_almanac_url(program):
    if program.venue.code == 'CA':
        zip_code = '92154' # closest US zip code to caliente
    else:
        zip_code = program.venue.zip_code
    return "{}{}/{}".format(almanac_root, zip_code, program.date)

def build_dog_profile_url(dog_name):
    return "{}{}".format(dog_root, dog_name.replace(" ", "+"))    
