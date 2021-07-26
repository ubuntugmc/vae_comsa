from io import StringIO
from pathlib import Path

import pandas as pd
import pytest
import datetime
from django.core.management import call_command

from va_explorer.va_data_management.models import Location
from va_explorer.va_data_management.models import VerbalAutopsy
from va_explorer.va_data_management.models import VaUsername

from va_explorer.users.models import User

from va_explorer.va_data_management.utils.loading import load_records_from_dataframe
from va_explorer.tests.factories import UserFactory, LocationFactory, VerbalAutopsyFactory
from django.contrib.auth.models import Group
from va_explorer.users.management.commands.initialize_groups import GROUPS_PERMISSIONS
from va_explorer.users.tests.user_test_utils import setup_test_db, get_fake_user_data
from va_explorer.users.utils.field_worker_linking import link_fieldworkers_to_vas, assign_va_usernames

pytestmark = pytest.mark.django_db

def test_link_fieldworkers_to_vas():
    setup_test_db(with_vas=False)
    # Location gets assigned automatically/randomly.
    # If that changes in loading.py we'll need to change that here too.
    # create users before VAs are added to system
    group, created = Group.objects.get_or_create(name="Field Workers")
    u1 = UserFactory(name="Johnny", email="field_worker_1@example.com", groups=[group]).save()
    u2 = UserFactory(name="Apple", email="field_worker_2@example.com", groups=[group]).save()
    u1 = UserFactory(name="Seed", email="field_worker_3@example.com", groups=[group]).save()

    
    worker_emails = list(User.objects.values_list('email', flat=True))
    
    loc1 = Location.objects.filter(name="Facility1").first()
    loc2 = Location.objects.filter(name="Facility2").first()

    # add VA data to system
    va1 = VerbalAutopsyFactory.create(Id10010='unknown_user', location=loc1).save()
    va2 = VerbalAutopsyFactory.create(Id10010='Johnny', location=loc2).save()
    va3 = VerbalAutopsyFactory.create(Id10010='appLe', location=loc1).save()
    va4 = VerbalAutopsyFactory.create(Id10010='SEED', location=loc2).save()
    
    res = link_fieldworkers_to_vas(emails=worker_emails)
    res = set(res)
    assert len(res) == 3
    assert ('johnny', 'johnny') in res
    assert ('apple', 'apple') in res
    assert ('seed', 'seed') in res

    usernames = [u.get_va_username() for u in User.objects.all()]
    assert len(set(usernames).intersection({'johnny', 'apple', 'seed'})) == 3

    va_usernames = VerbalAutopsy.objects.values_list('username', flat=True)
    assert len(set(va_usernames).intersection({'johnny', 'apple', 'seed'})) == 3

    unknown = VerbalAutopsy.objects.filter(Id10010='unknown_user').first()
    assert unknown
    assert len(unknown.username) == 0


def test_assign_va_usernames():
    setup_test_db(with_vas=False)
    # dummy facilities 
    loc1 = Location.objects.filter(name="Facility1").first()
    loc2 = Location.objects.filter(name="Facility2").first()

    # first, create VAs
    va1 = VerbalAutopsyFactory.create(instanceid="instance1", Id10010='johnny', location=loc1).save()
    va2 = VerbalAutopsyFactory.create(instanceid="instance2",Id10010='Johnny', location=loc2).save()
    va3 = VerbalAutopsyFactory.create(instanceid="instance3",Id10010='appLe', location=loc1).save()
    va4 = VerbalAutopsyFactory.create(instanceid="instance4",Id10010='SEED', location=loc2).save()
    va4 = VerbalAutopsyFactory.create(instanceid="instance5", Id10010='JOHNNY', location=loc2).save()

    # then, create a field worker johnny 
    group, created = Group.objects.get_or_create(name="Field Workers")
    u1 = UserFactory(name="Johnny", email="field_worker_1@example.com", groups=[group])
    u1.set_va_username("johnny")
    u1.save()

    # finally, match vas against field workers
    success_ct = assign_va_usernames(usernames="johnny")
    assert success_ct == 3
    assert VerbalAutopsy.objects.get(instanceid='instance1').username == "johnny"
    assert VerbalAutopsy.objects.get(instanceid='instance2').username == "johnny"
    assert VerbalAutopsy.objects.get(instanceid='instance3').username != "johnny"
    assert VerbalAutopsy.objects.get(instanceid='instance4').username != "johnny"
    assert VerbalAutopsy.objects.get(instanceid='instance5').username == "johnny"
    


    

    