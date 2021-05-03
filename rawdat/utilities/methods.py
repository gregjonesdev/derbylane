from rawdat.utilities.urls import (
    results_url,
)

def build_results_url(venue_code, year, month, day, time, race_number):
    return "{}G{}${}{}{}{}{}".format(
                results_url,
                venue_code,
                year,
                str(month).zfill(2),
                str(day).zfill(2),
                time,
                str(race_number).zfill(2))
