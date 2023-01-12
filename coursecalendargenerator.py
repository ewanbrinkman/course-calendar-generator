from constants.urls import ROOM_FINDER
from constants.filenames import COURSES_INPUT_FILENAME, \
    CALENDAR_OUTPUT_FILENAME
from scrapers.sfu.calendarscraper import CalendarScraper
import asyncio
import datetime
import typing
import ics  # type: ignore


class CourseCalendarGenerator:
    def __init__(self, courses_input_filename: str = COURSES_INPUT_FILENAME,
                 calendar_output_filename: str = CALENDAR_OUTPUT_FILENAME) \
            -> None:
        self.courses_input_filename = courses_input_filename
        self.calendar_output_filename = calendar_output_filename

        self.scraper = CalendarScraper()

    @staticmethod
    def get_date(schedule: dict, key: str) -> datetime.date:
        # Used for getting the date a course starts or ends at. Key will either
        # be "startDate" or "endDate".
        data = schedule[key].split(" ")

        year = int(data[-1])
        month = datetime.datetime.strptime(data[1], '%b').month
        day = int(data[2])

        return datetime.date(year, month, day)

    @staticmethod
    def get_interval(start_date: datetime.date, end_date: datetime.date,
                     weekday: str) -> typing.Generator:
        # Generate days of the week that a course will be on. This will have
        # to be called for each day of the week the course is on.
        delta = end_date - start_date
        for i in range(delta.days + 1):
            day = start_date + datetime.timedelta(days=i)
            if day.strftime("%a")[:2] == weekday:
                yield day

    @staticmethod
    def calendar_serialize_iter_fix_timezone(
            calendar: ics.Calendar) -> typing.Generator:
        # Remove the "Z" so that the time is interpreted as local time instead
        # of GMT+0. Make sure on GMT-8 when adding to calendar, as that is
        # SFU's time zone.
        for text in calendar.serialize_iter():
            if "DTEND" in text or "DTSTART" in text:
                text = text.replace("Z", "")
            yield text

    async def get_courses_data(
            self, courses: tuple[tuple[str, ...], ...]) -> tuple:
        # Get all course data.
        course_coroutines = tuple(self.scraper.scrape_course(*course)
                                  for course in courses)
        return tuple(await asyncio.gather(*course_coroutines))

    async def generate_calendar_file(self) -> None:
        calendar = ics.Calendar()

        # Get the courses to create the calendar file with.
        with open(self.courses_input_filename) as f:
            courses = tuple(tuple(line.split(","))
                            for line in f.read().splitlines())

        # Add each course's schedule to the calendar.
        for course, data in zip(courses, await self.get_courses_data(courses)):
            for schedule in data['courseSchedule']:
                for weekday in schedule['days'].split(", "):
                    for date in self.get_interval(
                            self.get_date(schedule, "startDate"),
                            self.get_date(schedule, "endDate"), weekday):
                        e = ics.Event()
                        e.name = f"{data['info']['name']} " \
                                 f"{schedule['sectionCode']}"

                        # Get the course start and end time during the day.
                        start_time = schedule['startTime']
                        if start_time[1] == ":":
                            start_time = f"0{start_time}"
                        end_time = schedule['endTime']
                        if end_time[1] == ":":
                            end_time = f"0{end_time}"
                        e.begin = f"{date} {start_time}:00"
                        e.end = f"{date} {end_time}:00"

                        # Add the room number and instructor to the event
                        # description.
                        room_number = schedule['buildingCode'] + schedule[
                            'roomNumber']
                        url = ROOM_FINDER + room_number
                        room = f"Room: <a href=\"{url}\">{room_number}</a>"
                        try:
                            plural = "" if len(
                                data['instructor']) == 1 else "s"
                            instructor_list = ', '.join(
                                (person['name'] for person
                                 in data['instructor']))
                        except KeyError:
                            # No instructor.
                            plural = ""
                            instructor_list = "None Specified"
                        instructor = f"Instructor{plural}: {instructor_list}"
                        e.description = room + "\n" + instructor

                        calendar.events.add(e)

        with open(CALENDAR_OUTPUT_FILENAME, 'w') as my_file:
            my_file.writelines(self.calendar_serialize_iter_fix_timezone(
                calendar))
