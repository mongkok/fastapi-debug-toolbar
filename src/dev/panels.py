from debug_toolbar.panels import Panel


class ExamplePanel(Panel):
    title = "Example Panel"
    template = "example.html"

    async def process_request(self, request):
        response = await super().process_request(request)
        return response

    async def generate_stats(self, request, response):
        return {"example": "value"}
