from hishel import Controller
from httpcore import Request, Response


class MightstoneController(Controller):
    # See: https://github.com/karpetrosyan/hishel/issues/238
    def _make_request_conditional(self, request: Request, response: Response) -> None:
        super()._make_request_conditional(request, response)

        request.headers = list(dict(request.headers).items())
