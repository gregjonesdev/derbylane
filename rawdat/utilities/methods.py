

def get_date_from_ymd(year, month, day):
    return "{}-{}-{}".format(
        year,
        str(month).zfill(2),
        str(day).zfill(2))

# def get_chart(program, time):
#     try:
#         chart = Chart.objects.get(
#             time=time,
#             program=program
#         )
#     except ObjectDoesNotExist:
#         new_chart = Chart(
#             time=time,
#             program=program
#         )
#         new_chart.set_fields_to_base()
#         new_chart.save()
#         chart = new_chart
#     return chart
#
# def get_program(venue, year, month, day):
#     formatted_date = "{}-{}-{}".format(
#         year,
#         str(month).zfill(2),
#         str(day).zfill(2))
#     try:
#         program = Program.objects.get(
#             venue=venue,
#             date=formatted_date
#         )
#     except ObjectDoesNotExist:
#         new_program = Program(
#             venue=venue,
#             date=formatted_date
#         )
#         new_program.set_fields_to_base()
#         new_program.save()
#         program = new_program
#     # return program

# def get_race(chart, number):
#
#     try:
#         race = Race.objects.get(
#             chart=chart,
#             number=number
#         )
#     except ObjectDoesNotExist:
#         new_race = Race(
#             chart=chart,
#             number=number,
#         )
#         new_race.set_fields_to_base()
#         new_race.save()
#         race = new_race
#     return race
