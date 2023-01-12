import aiohttp
import json
import typing
import bs4

ParsedData = dict | bs4.BeautifulSoup
ScrapeData = str | ParsedData  # ScrapeData will be a string if not parsed.


class ScrapeResult(typing.TypedDict):
    response: aiohttp.ClientResponse
    data: ScrapeData


class ParserNotFoundError(Exception):
    """Raised when a parser is requested but doesn't exist."""
    def __init__(self, parser: str) -> None:
        super().__init__(f"The requested parser \"{parser}\" does not exist.")


class ParserDecodeError(Exception):
    """Raised when a parser could not successfully decode data."""
    def __init__(self, parser: str) -> None:
        super().__init__(
            f"The data could not be decoded using the parser \"{parser}\".")


class Scraper:
    def __init__(
            self, parser: str = "soup", verify: bool | None = True) -> None:
        # The default parser to use, such as JSON or beautiful soup.
        valid_parsers = (None, "json", "soup")
        if parser not in valid_parsers:
            # If another parser was specified, raise an error since it does
            # not exist.
            raise ParserNotFoundError(parser)
        self.parser = parser
        # If website SSL certificates should be verified or not. This is
        # strongly encouraged.
        self.verify = verify

    def parse(self, data: str, parser: str | None = None) -> ParsedData:
        # Use the default parser if none is specified.
        if parser is None:
            parser = self.parser

        if parser == "json":
            # For a JSON string.
            try:
                return json.loads(data)
            except json.decoder.JSONDecodeError:
                raise ParserDecodeError(parser)
        elif parser == "soup":
            # For HTML.
            return bs4.BeautifulSoup(data, "lxml")
        else:
            raise ParserNotFoundError(parser)

    async def scrape(
            self, url: str, verify: bool | None = None,
            parse: bool | None = None, parser: str | None = None,
            **kwargs) -> ScrapeResult:

        async with aiohttp.ClientSession() as session:
            # If website SSL certificates should be verified or not. This is
            # strongly encouraged.
            if verify is None:
                verify = self.verify

            try:
                async with session.get(url, verify_ssl=verify,
                                       **kwargs) as response:
                    text = await response.text()

                    # Decide whether to parse based on the parser function
                    # argument or use the default parser if none is specified.
                    if parse is None:
                        if parser is not None:
                            parse = True
                        else:
                            parse = bool(self.parser)

                    # Parse the text if required.
                    return {
                        "response": response,
                        "data": self.parse(text, parser) if parse else text
                    }

            except aiohttp.ClientConnectorError:
                raise ConnectionError
