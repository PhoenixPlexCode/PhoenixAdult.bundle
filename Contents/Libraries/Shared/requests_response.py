from requests.models import Response


def FakeResponse(req, url, status_code, content):
    response = req
    if response is None:
        response = Response()

    response.url = url
    response.status_code = status_code
    response._content = content.encode('UTF-8')

    return response
