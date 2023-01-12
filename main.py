# This application is not endorsed or supported by Simon Fraser University.

from coursecalendargenerator import CourseCalendarGenerator
import asyncio


async def main() -> None:
    course_calendar_generator = CourseCalendarGenerator()
    await course_calendar_generator.generate_calendar_file()


if __name__ == '__main__':
    asyncio.run(main())
