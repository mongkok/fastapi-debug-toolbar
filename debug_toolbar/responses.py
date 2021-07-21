from fastapi.responses import StreamingResponse


class StreamingHTMLResponse(StreamingResponse):
    media_type = "text/html"
