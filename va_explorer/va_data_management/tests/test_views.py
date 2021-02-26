import pytest
from django.test import Client
from django.contrib.auth.models import Permission
from va_explorer.users.models import User
from va_explorer.va_data_management.models import VerbalAutopsy
from va_explorer.tests.factories import GroupFactory, VerbalAutopsyFactory, UserFactory

pytestmark = pytest.mark.django_db

# Get the index and make sure the VA in the system is listed
def test_index(user: User):
    client = Client()
    client.force_login(user=user)
    va = VerbalAutopsyFactory.create()
    response = client.get("/va_data_management/")
    assert response.status_code == 200
    assert bytes(va.Id10007, "utf-8") in response.content

# Show a VA and make sure the data is as expected
def test_show(user: User):
    client = Client()
    client.force_login(user=user)
    va = VerbalAutopsyFactory.create()
    response = client.get(f"/va_data_management/show/{va.id}")
    assert response.status_code == 200
    assert bytes(va.Id10007, "utf-8") in response.content

# Request the edit form of a VA and make sure the data is as expected
def test_edit_with_valid_permissions(user: User):
    can_edit_record = Permission.objects.filter(codename="change_verbalautopsy").first()
    can_edit_record_group = GroupFactory.create(permissions=[can_edit_record])
    user = UserFactory.create(groups=[can_edit_record_group])

    client = Client()
    client.force_login(user=user)

    va = VerbalAutopsyFactory.create()
    response = client.get(f"/va_data_management/edit/{va.id}")
    assert response.status_code == 200
    assert bytes(va.Id10007, "utf-8") in response.content

# Request the edit form of a VA without permissions and make sure its forbidden
def test_edit_without_valid_permissions(user: User):
    client = Client()
    client.force_login(user=user)

    va = VerbalAutopsyFactory.create()
    response = client.get(f"/va_data_management/edit/{va.id}")
    assert response.status_code == 403

# Update a VA and make sure 1) the data is changed and 2) the history is tracked
def test_save_with_valid_permissions(user: User):
    can_edit_record = Permission.objects.filter(codename="change_verbalautopsy").first()
    can_edit_record_group = GroupFactory.create(permissions=[can_edit_record])
    user = UserFactory.create(groups=[can_edit_record_group])

    client = Client()
    client.force_login(user=user)
    va = VerbalAutopsyFactory.create()
    assert va.history.count() == 1
    new_name = "Updated Example Name"
    response = client.post(f"/va_data_management/edit/{va.id}", { "Id10007": new_name })
    assert response.status_code == 302
    assert response["Location"] == f"/va_data_management/show/{va.id}"
    va = VerbalAutopsy.objects.get(id=va.id)
    assert va.Id10007 == new_name
    assert va.history.count() == 2
    assert va.history.first().history_user == user
    response = client.get(f"/va_data_management/show/{va.id}")
    # TODO: We need to handle timezones correctly
    assert bytes(va.history.first().history_date.strftime('%Y-%m-%d %H:%M'), "utf-8") in response.content
    assert bytes(va.history.first().history_user.name, "utf-8") in response.content

# Update a VA and make sure 1) the data is changed and 2) the history is tracked
def test_save_without_valid_permissions(user: User):
    client = Client()
    client.force_login(user=user)
    va = VerbalAutopsyFactory.create()
    assert va.history.count() == 1
    new_name = "Updated Example Name"
    response = client.post(f"/va_data_management/edit/{va.id}", { "Id10007": new_name })
    assert response.status_code == 403

# Reset an updated VA and make sure 1) the data is reset to original values and 2) the history is tracked
def test_reset_with_valid_permissions(user: User):
    can_edit_record = Permission.objects.filter(codename="change_verbalautopsy").first()
    can_edit_record_group = GroupFactory.create(permissions=[can_edit_record])
    user = UserFactory.create(groups=[can_edit_record_group])

    client = Client()
    client.force_login(user=user)
    va = VerbalAutopsyFactory.create()
    original_name = va.Id10007
    new_name = "Updated Name"
    client.post(f"/va_data_management/edit/{va.id}", { "Id10007": new_name })
    va = VerbalAutopsy.objects.get(id=va.id)
    assert va.Id10007 == new_name
    assert va.history.count() == 2
    # TODO: Switch the buttons to forms in show.html and make this a POST.
    response = client.get(f"/va_data_management/reset/{va.id}")
    assert response.status_code == 302
    assert response["Location"] == f"/va_data_management/show/{va.id}"
    va = VerbalAutopsy.objects.get(id=va.id)
    assert va.Id10007 == original_name
    assert va.history.count() == 3
    assert va.history.first().history_user == user

# Reset an updated VA and make sure 1) the data is reset to original values and 2) the history is tracked
def test_reset_without_valid_permissions(user: User):
    client = Client()
    client.force_login(user=user)
    va = VerbalAutopsyFactory.create()
    response = client.get(f"/va_data_management/reset/{va.id}")

# Revert an updated VA and make sure 1) the data is reset to previous version and 2) the history is tracked
def test_revert_latest_with_valid_permissions(user: User):
    can_edit_record = Permission.objects.filter(codename="change_verbalautopsy").first()
    can_edit_record_group = GroupFactory.create(permissions=[can_edit_record])
    user = UserFactory.create(groups=[can_edit_record_group])

    client = Client()
    client.force_login(user=user)
    va = VerbalAutopsyFactory.create()
    original_name = va.Id10007
    second_name = "Second Name"
    third_name = "Third Name"
    client.post(f"/va_data_management/edit/{va.id}", { "Id10007": second_name })
    va = VerbalAutopsy.objects.get(id=va.id)
    assert va.Id10007 == second_name
    assert va.history.count() == 2
    client.post(f"/va_data_management/edit/{va.id}", { "Id10007": third_name })
    va = VerbalAutopsy.objects.get(id=va.id)
    assert va.Id10007 == third_name
    assert va.history.count() == 3
    # TODO: Switch the buttons to forms in show.html and make this a POST.
    response = client.get(f"/va_data_management/revert_latest/{va.id}")
    assert response.status_code == 302
    assert response["Location"] == f"/va_data_management/show/{va.id}"
    va = VerbalAutopsy.objects.get(id=va.id)
    assert va.Id10007 == second_name
    assert va.history.count() == 4
    assert va.history.first().history_user == user

def test_revert_latest_without_valid_permissions(user: User):
    client = Client()
    client.force_login(user=user)
    va = VerbalAutopsyFactory.create()
    response = client.get(f"/va_data_management/revert_latest/{va.id}")
    assert response.status_code == 403
