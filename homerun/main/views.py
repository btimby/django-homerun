import logging

from twilio import twiml

from django.http import HttpResponse
from django.core.urlresolvers import reverse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views.generic.base import View

from django.contrib.auth.models import User


VOICE = 'woman'


class IVRView(View):
    logger = logging.getLogger('django.request')

    @method_decorator(csrf_exempt)
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
            response.say("Unable to handle your call, please try again later.", voice=VOICE)
            response.hangup()
        return HttpResponse(response.toxml(), content_type='text/xml')


class IVRMenuView(IVRView):
    menu = None

    def get(self, request, response):
        if not self.menu:
            raise NotImplemented('You must define the menu attribute')
        response.say('Please make a selection from the following menu.', voice=VOICE)
        with response.gather(numDigits=1, method='POST') as r:
            menu = ['Press %s to %s.' % (k, v) for k, v in self.menu.items()]
            # Do our own loop, since a pause is not easy to inject between repeats.
            for i in range(3):
                r.say(' '.join(menu), voice=VOICE)
                r.pause(length=3)
        # If the user does not make a selection, say goodbye, then hang-up
        response.say("Goodbye")
        response.hangup()

    def post(self, request, response):
        digits = request.POST.get('Digits')
        if digits not in self.menu:
            response.say('You have chosen an invalid option.', voice=VOICE)
            response.redirect(request.build_absolute_uri(), method='GET')
            return
        try:
            handler = getattr(self, 'handle_%s' % digits)
        except AttributeError:
            raise NotImplemented('You must implement a handler for each menu option')
        handler(request, response)


class IVRMainMenuView(IVRMenuView):
    menu = {
        '1': 'hear a list of available homes',
        '2': 'reach a customer service representative',
    }

    def get(self, request, response):
        response.say('Thank you for calling.', voice=VOICE)
        return super(IVRMainMenuView, self).get(request, response)

    def handle_1(self, request, response):
        response.say("Listing now.", voice=VOICE)

    def handle_2(self, request, response):
        response.say('Forwarding to agent.', voice=VOICE)
