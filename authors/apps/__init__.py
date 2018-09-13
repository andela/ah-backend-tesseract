import json

from rest_framework.renderers import JSONRenderer


class ApplicationJSONRenderer(JSONRenderer):

    charset = 'utf-8'

    def render(self, data, media_type=None, renderer_context=None):
        errors = data.get('errors', None)

        if errors is not None:
            return super(ApplicationJSONRenderer, self).render(data)

        return json.dumps(data)


def update_data_with_user(request):
    data = request.data
    data["rated_by"] = request.user.id
    return data

