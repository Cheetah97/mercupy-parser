import asyncio
import os
from functools import reduce
from time import perf_counter
from typing import List, Tuple, Union, Optional
from urllib.parse import urljoin as join

import httpx
import validators
from httpx import Response


def urljoin(*terms: str) -> str:
    return reduce(join, terms)


class Mercupy:
    def __init__(self, api_endpoint: Optional[str] = None, verbose: bool = False):
        print("Check")
        api_endpoint = api_endpoint or os.environ.get("API_ENDPOINT", "http://0.0.0.0:4000")
        self.api_endpoint = urljoin(api_endpoint, "parser")
        print(self.api_endpoint)
        self.verbose = verbose

    def parser(self,
               urls: Union[str, List[str]],
               headers: Optional[str] = None,
               content_type: Optional[str] = None) -> Tuple[Response]:
        """ Gathers responses from async requests to mercury parser """
        if not urls:
            raise AttributeError("URLS not provided")

        if isinstance(urls, str):
            urls = [urls]

        responses = asyncio.run(self._parser(urls, headers, content_type))
        return responses

    async def _parser(self,
                     urls: Union[str, List[str]],
                     headers: Optional[str] = None,
                     content_type: Optional[str] = None,
                     timeout: int = 20) -> Tuple[Response]:
        """ Convenience method to parse multiple urls """
        params = {"headers": headers, "contentType": content_type}
        params = {key: value for key, value in params.items() if value}

        start = perf_counter()

        async with httpx.AsyncClient() as client:
            tasks = (client.get(self.api_endpoint,
                                params={**{"url": url}, **params},
                                timeout=timeout)
                     for url in urls)
            responses = await asyncio.gather(*tasks)

        end = perf_counter()
        if self.verbose is True:
            print(f"Response time: {end - start:.2f} sec")

        return responses

