trackinfo_mobile_base = "http://m.trackinfo.com"
trackinfo_desktop_base = "https://www.trackinfo.com"

results_extension = "/index.jsp?next=resultsrace&raceid="
entries_extension = "/index.jsp?next=entriesrace&raceid="

results_url = "{}{}".format(trackinfo_mobile_base, results_extension)
entries_url = "{}{}".format(trackinfo_mobile_base, entries_extension)

almanac_root = "https://www.almanac.com/weather/history/zipcode/"
dog_root = "/{}dog.jsp?runnername=".format(trackinfo_desktop_base)

all_race_results = "{}dog-racelines.jsp?page=1&runnername=".format(trackinfo_desktop_base)
all_race_suffix = "&TotalRowCount=20000"


australia_attempt = "https://old.thedogs.com.au/Racing/RacingFormFields.aspx?meetid=260281"

json_suffix = "&language=en-US&units=e&format=json"
base_url = "https://api.weather.com/v3/wx/forecast/daily/7day?apiKey="
api_key = "6532d6454b8aa370768e63d6ba5a832e"
