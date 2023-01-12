from scrapers.scraper import Scraper, ScrapeData
from constants.urls import SFU_COURSE_OUTLINES


class DataNotFoundError(Exception):
    """Raised when a parameter is invalid or doesn't exist."""
    def __init__(self) -> None:
        super().__init__("The data could not be found.")


class CalendarScraper(Scraper):
    def __init__(self) -> None:
        super().__init__(parser="json")

        # The current selected year and term.
        self.year = "current"
        self.term = "current"

    @staticmethod
    def get_course_outlines_url(year: str, term: str,
                                parameters: tuple[str, ...]) -> str:
        return f"{SFU_COURSE_OUTLINES}?{'/'.join((year, term) + parameters)}"

    async def scrape_calendar(self, url: str) -> ScrapeData:
        result = await self.scrape(url)

        if result['response'] is None or result['response'].status == 404 or \
                result['data'] is None or len(result['data']) == 0:
            raise DataNotFoundError

        return result['data']

    async def scrape_course(self, program: str, number: int | str,
                            section: str, year: int | str | None = None,
                            term: str | None = None):
        if year is None:
            year = self.year
        if term is None:
            term = self.term

        # The parameters for the API.
        parameters = (program.lower(), str(number), section.lower())

        url = self.get_course_outlines_url(str(year), term, parameters)

        return await self.scrape_calendar(url)
