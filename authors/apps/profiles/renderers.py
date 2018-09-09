import json

from rest_framework.renderers import JSONRenderer


class ProfileJSONRenderer(JSONRenderer):
    charset = 'utf-8'
    object_label = 'profile'

    def render(self, data, media_type=None, renderer_context=None):

        errors = data.get('errors', None)

        if errors is not None:
            return super(ProfileJSONRenderer, self).render(data)

        return json.dumps({
            self.object_label: data
        })
