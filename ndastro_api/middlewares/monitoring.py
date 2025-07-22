"""Middleware for monitoring and logging HTTP request processing times.

This module provides MonitoringMiddleware, which measures the duration of each HTTP request,
adds an X-Process-Time header to responses, and logs warnings for slow requests.
"""

import time
from collections.abc import Awaitable, Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from ndastro_api.core.logger import logging


class MonitoringMiddleware(BaseHTTPMiddleware):
    """Middleware that measures and logs the processing time of each HTTP request.

    This middleware adds an `X-Process-Time` header to the response, indicating the time taken to process the request.
    If the processing time exceeds 1 second, it logs a warning with the request method, URL, and duration.

    Attributes:
        None
    Methods:
        dispatch(request, call_next):
            Handles incoming requests, measures processing time, adds header, and logs slow requests.

    """

    async def dispatch(self, request: Request, call_next: Callable[[Request], Awaitable[Response]]) -> Response:
        """Handle incoming requests, measure processing time, add header, and log slow requests.

        Parameters
        ----------
        request : Request
            The incoming HTTP request.
        call_next : Callable
            The next middleware or route handler to call.

        Returns
        -------
        Response
            The HTTP response with an added X-Process-Time header.

        """
        start_time = time.time()

        response = await call_next(request)

        process_time = time.time() - start_time
        response.headers["X-Process-Time"] = str(process_time)

        # Log slow requests
        if process_time > 1.0:
            logging.warning(f"Slow request: {request.method} {request.url} - {process_time:.2f}s")

        return response
