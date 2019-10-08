from sanic.request import Request
from sanic.response import text
from sanic.views import HTTPMethodView


class DefaultEndpoint(HTTPMethodView):
    """
    Default view for the / endpoint.
    """
    async def get(self, request: Request):
        """
        Shows basic information about the Bot.
        """
        return text(f"Hello from Chomusuke! ({request.app.bot.user.id})")
