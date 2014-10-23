"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

import uuid
import time
from datetime import datetime
from collections import Counter

from django.test import TestCase
from django.contrib.auth import get_user_model

from mygpo.podcasts.models import Podcast, Episode
from mygpo.users.models import Client
from mygpo.history.models import EpisodeHistoryEntry
from mygpo.maintenance.merge import PodcastMerger
from mygpo.subscriptions import subscribe, unsubscribe


class SimpleTest(TestCase):

    def test_merge(self):

        p1 = Podcast.objects.get_or_create_for_url('http://example.com/podcast1.rss')
        p2 = Podcast.objects.get_or_create_for_url('http://example.com/podcast2.rss')

        e1 = Episode.objects.get_or_create_for_url(p1, 'http://example.com/podcast1/e1.mp3')
        e1.title = 'Episode 1'
        e1.save()

        e2 = Episode.objects.get_or_create_for_url(p2, 'http://example.com/podcast1/e2.mp3')
        e2.title = 'Episode 2'
        e2.save()

        e3 = Episode.objects.get_or_create_for_url(p2, 'http://example.com/podcast2/e2.mp3')
        e3.title = 'Episode 3'
        e3.save()

        e4 = Episode.objects.get_or_create_for_url(p2, 'http://example.com/podcast2/e3.mp3')
        e4.title = 'Episode 4'
        e4.save()

        User = get_user_model()
        user = User()
        user.username = 'user-test_merge'
        user.email = 'user-test_merge@example.com'
        user.set_password('secret')
        user.save()

        device1 = Client.objects.create(user=user, uid='dev1', id=uuid.uuid1())
        device2 = Client.objects.create(user=user, uid='dev2', id=uuid.uuid1())

        subscribe(p1, user, device1)
        time.sleep(1)
        unsubscribe(p1, user, device1)
        time.sleep(1)
        subscribe(p1, user, device1)
        subscribe(p2, user, device2)

        action1 = EpisodeHistoryEntry.objects.create(
            episode = e1,
            user = user,
            action = EpisodeHistoryEntry.PLAY,
            timestamp = datetime.utcnow(),
            created = datetime.utcnow(),
        )

        action3 = EpisodeHistoryEntry.objects.create(
            episode = e3,
            user = user,
            action = EpisodeHistoryEntry.PLAY,
            timestamp = datetime.utcnow(),
            created = datetime.utcnow(),
        )

        # we need that for later
        e3_id = e3.pk

        actions = Counter()

        # decide which episodes to merge
        groups = [(0, [e1]), (1, [e2, e3]), (2, [e4])]

        # carry out the merge
        pm = PodcastMerger([p1, p2], actions, groups)
        pm.merge()

        e1 = Episode.objects.get(pk=e1.pk)
        history1 = EpisodeHistoryEntry.objects.filter(episode=e1, user=user)
        self.assertEqual(len(history1), 1)

        # check if merged episode's id can still be accessed
        e3 = Episode.objects.filter(podcast=p1).get_by_any_id(e3_id)
        history3 = EpisodeHistoryEntry.objects.filter(episode=e3, user=user)
        self.assertEqual(len(history3), 1)

        p1 = Podcast.objects.get(pk=p1.get_id())
        subscribed_clients = Client.objects.filter(subscription__podcast=p1)
        self.assertEqual(len(subscribed_clients), 2)

        episodes = p1.episode_set.all()
        self.assertEqual(len(episodes), 3)
