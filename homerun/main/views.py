import logging

from twilio import twiml

from django.http import HttpResponse
from django.core.urlresolvers import reverse
from django.views.generic.base import View

from django.contrib.auth.models import User


class IVRView(View):
    logger = logging.getLogger('django.request')

    def dispatch(self, request, username, **kwargs):
        response = twiml.Response()
        try:
            request.user = User.objects.get(username=username)
            super(IVRView, self).dispatch(request, response, **kwargs)
        except Exception:
            self.logger.error('ERROR', exc_info=True)
            # Clear out any TwiML built so far.
            response.verbs = []
            # Return error message.
            response.say("Unable to handle your call, please try again later.")
            response.hangup()
        return HttpResponse(response.toxml(), content_type='text/xml')


class IVRMenuView(IVRView):
    options = None

    def get(self, request, response):
        if self.options is None:
            raise NotImplemented('You must define the options attribute')
        with response.gather(numDigits=1, method='POST') as r:
            menu = ['Press %s to %s.' % (k, v) for k, v in self.options.items()]
            r.say(' '.join(menu), loop=3)
        # If the user does not make a selection, say goodbye, then hang-up
        response.say("Goodbye")
        response.hangup()

    def post(self, request, response):
        digits = request.POST.get('digits')
        if digits not in self.options:
            response.say('You have chosen an invalid option.')
            response.redirect(request.build_absolute_uri())
            return
        try:
            handler = getattr(self, 'handle_%s' % digits)
        except AttributeError:
            raise NotImplemented('You must implement a handler for each option')
        handler(request, response)


class IVRMainMenuView(IVRMenuView):
    options = {
        '1': 'hear a list of available homes',
        '2': 'reach a customer service representative',
    }

    def handle_1(self, request, response):
        response.say("Listing now.")

    def handle_2(self, request, response):
        response.say('Forwarding to agent.')
