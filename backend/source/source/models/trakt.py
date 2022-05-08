import logging
from typing import Tuple, List

from trakt import Trakt
from django.db import models, transaction
from django.forms.models import model_to_dict

from source.models.source import OAuthSource
from timeline.models import Entry

class TraktPin(object):
    """
    Handles Trakt OAuth and obtaining data from Trakt site
    """
    def __init__(self):
        self.authorization = None

        # Bind trakt events
        Trakt.on('oauth.token_refreshed', self.on_token_refreshed)

    def watched(self) -> Tuple:
        """
        Get user's watched shows and movies
        returns: tuple of (movies, shows)
        """
        self.authenticate()

        if not self.authorization:
            print('ERROR: Authentication required')
            return 1

        with Trakt.configuration.oauth.from_response(self.authorization):

            watched_movies = Trakt['sync/history'].get(media='movies', pagination=True, per_page=100)
            watched_shows = Trakt['sync/history'].get(media='shows', pagination=True, per_page=100)
            return (watched_movies, watched_shows)

    def status(self) -> bool:
        """
        Check the authentication credentials
        """
        if not self.has_auth():
            print('ERROR: Authentication required')
            return False

        with Trakt.configuration.oauth.from_response(self.authorization):
            # grab a small data that requires authenticing. Returns 'None' for failure
            watched_movies_test = Trakt['sync/history'].get(media='movies', per_page=10)
            return (watched_movies_test != None)

    def authenticate(self) -> bool:
        if self.has_auth():
            return True

        # Request authentication
        print('Navigate to %s' % Trakt['oauth/pin'].url())
        pin = input('Pin: ')

        # Exchange `code` for `access_token`
        self.authorization = Trakt['oauth'].token_exchange(pin, 'urn:ietf:wg:oauth:2.0:oob')

        if not self.authorization:
            return False

        print('Token exchanged - authorization: %r' % self.authorization)
        return True

    def get_url_pin(self) -> str:
        return Trakt['oauth/pin'].url()

    def set_pin(self, pin):
        # Exchange `code` for `access_token`
        auth_resp = Trakt['oauth'].token_exchange(pin, 'urn:ietf:wg:oauth:2.0:oob')
        if not auth_resp:
            return False
        self.save_auth(auth_resp)
        return True


    def on_token_refreshed(self, response):
        # OAuth token refreshed, save token for future calls
        self.authorization = response
        self.save_auth(response)

        print('Token refreshed - authorization: %r' % self.authorization)

    def has_auth(self) -> bool:
        # Check if have authentication information
        return bool(self.authorization['access_token'])

    def save_auth(self, authorization):
        """
        Save authentication info to database
        """
        a = TraktSource.objects.get(pk=self.source["key"])
        a.access_token = authorization["access_token"]
        a.refresh_token = authorization["refresh_token"]
        a.access_token_expires_in = authorization["expires_in"]
        a.access_token_created = authorization["created_at"]
        a.save(update_fields=["access_token", "refresh_token", "access_token_expires_in", "access_token_created"])
        self.authorization = authorization

    def load_auth(self, source):
        """
        load authentication into a format usable by trakt library
        """
        self.source = source
        self.authorization = {
            "access_token": source["access_token"],
            "created_at": source["access_token_created"],
            "expires_in": source["access_token_expires_in"],
            "refresh_token": source["refresh_token"],
        }

class TraktSource(OAuthSource):
    """
    Source to handle obtained trakt data for use on timeline
    """
    client_id = models.IntegerField()

    traktApp = TraktPin()

    def app_init(self):
        """
        configure Trakt
        """

        Trakt.configuration.defaults.app(
            id=self.client_id
        )

        Trakt.configuration.defaults.client(
            id=self.consumer_key,
            secret=self.consumer_secret
        )
        self.traktApp.load_auth(model_to_dict(self))

    
    def app(self) -> Tuple:
        """
        Grab Trakt user info
        """
        self.traktApp.load_auth(model_to_dict(self))

        Trakt.configuration.defaults.client(
            id=self.consumer_key,
            secret=self.consumer_secret
        )
        return self.traktApp.watched()

    def process(self, force=False) -> Tuple[int, int]:
        self.app_init()
        (movies,shows) = self.app()

        updated_shows = []
        created_shows = []
        updated_movies = []
        created_movies = []
        with transaction.atomic():
            for movie in movies:
                entry_values = {
                    'title': movie.title,
                    'date_on_timeline': movie.watched_at,
                    'extra_attributes': {
                        'year': movie.year,
                        'ids': {}
                    }
                }

                for k in movie.keys:
                    entry_values['extra_attributes']['ids'][k[0]] = k[1]


                entry, created = Entry.objects.update_or_create(
                    schema='activity.watching.movie',
                    source=self.entry_source,
                    description=movie.id,
                    defaults=entry_values
                )

                if created:
                    created_movies.append(entry)
                else:
                    updated_movies.append(entry)


            for show in shows:
                entry_values = {
                    'title': show.show.title + ' - ' + show.title + '- S' +str(show.pk[0]) + 'E' + str(show.pk[1]),
                    'date_on_timeline': show.watched_at,
                    'extra_attributes': {
                        # specific episode info
                        'episode': {
                            'name': show.title,
                            'season': show.pk[0],
                            'number': show.pk[1],
                            'episode_ids': {}
                        },
                        # overall show info
                        'show': {
                            'name': show.show.title,
                            'year': show.show.year,
                            'show_ids': {},
                        }
                    }
                }
                # The first key is the season-episode pair, unneeded here
                for k in show.keys[1:]:
                    entry_values['extra_attributes']['episode']['episode_ids'][k[0]] = k[1]
                for k in show.show.keys:
                    entry_values['extra_attributes']['show']['show_ids'][k[0]] = k[1]

                entry, created = Entry.objects.update_or_create(
                    schema='activity.watching.show',
                    source=self.entry_source,
                    description=show.id,
                    defaults=entry_values
                )

                if created:
                    created_shows.append(entry)
                else:
                    updated_shows.append(entry)

        return len(created_shows + created_movies), len(updated_shows + updated_movies)

