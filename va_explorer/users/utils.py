#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Apr 12 14:33:57 2021

@author: babraham
"""

from django.contrib.auth.models import Group
from django.db.models import F
from django.contrib.auth.models import Permission
from django.utils.crypto import get_random_string
from django.forms import BooleanField
from django.forms.models import ModelMultipleChoiceField as mmc_field
from django.db.models.query import QuerySet


from va_explorer.users.models import User
from va_explorer.va_data_management.models import Location
from va_explorer.users.forms import ExtendedUserCreationForm
from va_explorer.va_data_management.utils.location_assignment import fuzzy_match



import pandas as pd
from pandas.core.frame import DataFrame
from email.utils import parseaddr
import re
import os


def create_users_from_file(user_list_file, email_confirmation=False, debug=False):
    user_df = pd.read_csv(user_list_file).fillna("")
    user_ct = error_ct = 0
    new_users = []

    # fill out user forms one-by-one
    for i, user_data in user_df.iterrows():
        if debug:
            print(i, user_data["name"])
        user_form = fill_user_form_data(user_data, debug=debug)

        if user_form.is_valid():
            user_form.save(email_confirmation=email_confirmation)
            new_users.append(User.objects.get(email=user_data["email"]))
            user_ct +=1
        else:
            error_ct +=1
            print(f"WARNING: user fm for {user_data.get('email', 'Unknown email')} had following errors: {user_form.errors}")

    if user_ct > 0:
        print(f"Successfully created {user_ct} users ({error_ct} issues)")
    else:
        print("WARNING: Failed to create any users.")

    return {'user_ct': user_ct, 'error_ct': error_ct, 'users': new_users}


def fill_user_form_data(user_data, debug=False):
    
    form = ExtendedUserCreationForm()
    
    # if dataframe provided, convert to dict
    if type(user_data) is DataFrame:
        user_data_tmp = user_data.T.to_dict()
        user_data = list(user_data_tmp.values())[0]
        
    # preprocess raw data before parsing for form
    user_data = prep_form_data(user_data)
    
    # initialize all form data values to their defaults
    form_data = {name: [field.initial] if type(field) is mmc_field else field.initial for name, field in form.fields.items()}

    # figure out common fields between form and csv
    common_fields = set(form.fields.keys()).intersection(set(user_data.keys()))

    # iterate over these fields and add to form data
    for field_name in common_fields:
        # raw value to be parsed
        value = user_data[field_name]
        # pointer to form field object
        form_field = form.fields.get(field_name)
        # initialize form_value to form_field's default value. If match found below, will be overridden
        form_value = form_field.initial
        # multiple choice field
        if hasattr(form_field, 'choices'):
            if hasattr(form_field.choices, 'queryset'):
                # query the options for submitted value
                # NOTE: this assumes queryset objects have 'name' field and are indexed as such.
                # If not the case, need to use new field in query below
                qs = form_field.choices.queryset
                # first, try (case insensive) exact matching. If no match, then try consevative fuzzy matching
                try:
                    match = qs.filter(name__iexact=value)
                    if not match.exists():
                        match_name = fuzzy_match(value, qs.values_list('name', flat=True), threshold=.95)
                        if match_name:
                            match = qs.filter(name__iexact=match_name)
                except:
                    match = qs.none()
                
                if debug:
                    print(f"{field_name}: searching for {value} against {qs.values_list('name', flat=True)}")
                    print(f"match: {match}")

                # if matching option, set form value to its primary key. Otherwise, use form field's default value
                if match.exists():
                    form_value = match
                # if group field, try adding s if any groups are plural and rerun query
                elif field_name == "group":

                    plural_names = any(map(lambda x: x.endswith("s"), qs.values_list("name", flat=True)))
                    if plural_names and not value.endswith("s"):
                        value += "s"
                        match = qs.filter(name__iexact=value)
                        if debug:
                            print('trying new group logic...')
                            print(f"searched for {value} against {qs.values_list('name', flat=True)}")
                            print(f"match: {match}")
                        
                        if match.exists():
                            form_value = match
            else:
                # find closest match against list of choices manually
                for _, choice in form_field.choices:
                    # First, assume field is string. If not, fall back to non-string matching
                    try:
                        value, choice = value.lower(), choice.lower()
                    except:
                        pass
                    if choice == value:
                        form_value = choice
                        break
        # boolean field
        elif type(form_field) is BooleanField:
            if type(value) in [int, bool, float]:
                form_value = bool(value)
            else:
                form_value = (str(value).lower() in {'true', '1', '1.0', 'yes', 'y'})

        # catch-all for other field types - likely freeform/text entry
        else:
            form_value = value

        # add parsed value to form's data
        form_data[field_name] = form_value
    # final preprocessing for form
    final_data = prep_form_data(form_data)

    return ExtendedUserCreationForm(final_data)

# assign geographic access based on group and location restrictions. Also some logic to handle 
# facility restrictions for field workers. If new groups are added to the system, need
# to update this logic.
def prep_form_data(user_data):
    # if geographic_access missing, assign it based on group and/or location_restrictions
    if "group" not in user_data:
        raise(ValueError("Must provide group to determine geographic access."))
    # if location_restriction key exists but value is None, convert to empty string
    elif not user_data.get("location_restrictions", None):
        user_data["location_restrictions"] = ""

    # Parse and clean group name. If group object provided, parse name field.
    if type(user_data["group"]) is QuerySet:
        group = user_data["group"].first().name
    else:
        group = user_data["group"]
    try:
        group = re.sub("s$", "", group.lower())
    except:
        # defaulting to data viewer when group is unknown***
        group = "Data Viewer"

    # field worker logic
    if group == "field worker":
        geo_access = "location-specific"
        # if no facility restriction, check for group restriction. Otherwise, drop location restriction
        if user_data.get("facility_restrictions", None) in [None, [], "", [""]]:
            user_data["facility_restrictions"] = user_data["location_restrictions"]
        _ = user_data.pop("location_restrictions")
    # catch-all logic for groups in ["data viewer", "data manager", "dashboard viewer"]
    else:
        geo_access = "national"
        if len(user_data["location_restrictions"]) > 0:
            if user_data["location_restrictions"][0] is not None:
                geo_access = "location-specific"
        if geo_access == "national":
            _ = user_data.pop("location_restrictions")
        # remove facility restriction data if it exists (only field workers should have this key)
        if "facility_restrictions" in user_data:
            _ = user_data.pop("facility_restrictions")

    user_data["geographic_access"] = geo_access

    # convert all queryset objects to primary keys of first match
    for field, data in user_data.items():
        if type(data) is QuerySet and len(data) > 0:
            user_data[field] = data.first().pk if field == "group" else [data.first().pk]

    return user_data


# get schema information of a django form including field types, descriptions, whether they're required, and deafult values
def get_form_fields(form_type=ExtendedUserCreationForm, orient="v"):
    form = form_type()
    field_dict = {name: {"type": str(type(field)).split('.')[-1].replace("'>", ""),
                        "description": field.help_text,
                        "required": field.required, 
                        "default_value": field.initial} for name, field in form.fields.items()}
    field_df = pd.DataFrame(field_dict)
    return field_df if orient.startswith("v") else field_df.T



# get an anonymized table with basic info for all users in system (by defeault) or for a subset of users. 
# users can either be specified as a list of emails, or a txt with one email per line.  No PII included in result
def get_anonymized_user_info(user_list=None, user_list_file=None, debug=False):
    user_objects = User.objects
    # if user list provided, filter User objects to just those with emails in list
    if user_list or user_list_file:
        if not user_list and os.path.exists(user_list_file):
            try:
                user_list = [l.strip() for l in open(user_list_file, 'r').read().splitlines()]
            except:
                print(f"Failed to parse users from {user_list_file}.")
                return

        # filter out entries that aren't proper emails
        bad_emails = list(filter(lambda email: not re.match('[^@]+@[^@]+\.[^@]+', email), user_list))
        if len(bad_emails) > 0:
            print(f'Invalid email address(es) found for: {bad_emails}')
            user_list = list(set(user_list).difference(set(bad_emails)))

        # filter user objects to match known emails
        user_objects = user_objects.filter(email__in=user_list)
        
        # print emails that didn't match to console
        found_emails = set(user_objects.values_list('email', flat=True))
        missing_emails = set(user_list).difference(found_emails)
        if len(missing_emails) > 0:
            print(f"WARNING: failed to find users with following emails: {missing_emails}")

    # get user form fields
    form_fields = get_form_fields(orient="h")
    # figure out which fields are permissions. Assumes that all boolean fields are permissions
    permissions = form_fields.query("type=='BooleanField'").index.tolist()
    if debug:
        print(f"permissions: {permissions}")
    user_data = user_objects\
    .select_related('location_restrictions')\
    .select_related('groups')\
    .select_related('user_permissions')\
    .values(
            'uuid',
            'is_active',
            'is_staff',
            role = F('groups__name'),
            locations = F('location_restrictions__name'), 
            permissions = F('user_permissions__codename')         
    )
    user_df = pd.DataFrame.from_records(user_data).rename(columns={'locations': 'location_restrictions'})

    if not user_df.empty:
        # try creating user permissions pivot based on all observed user permissions. If none, make a blank table
        user_perms = (user_df[['uuid', 'permissions']]
            .pivot_table(index='uuid', columns='permissions', values='uuid', aggfunc=lambda x: len(x) > 0)
            .fillna(False)
            .reset_index()
            )
        if user_perms.empty:
            user_perms = pd.DataFrame({p: ["NA/Unassigned"]*user_df.shape[0] for p in permissions})
            user_perms["uuid"] = user_df["uuid"]
        
        user_df = user_df.drop(columns="permissions").drop_duplicates().merge(user_perms, how="left")
    else:
        print("WARNING: failed to find any users matching provided emails")

    return user_df

def make_field_workers_for_facilities(facilities=None, num_per_facility=2):
    if not facilities:
        facilities = Location.objects.filter(location_type='facility').exclude(name='Unknown')
    
    for i, facility in enumerate(facilities):
        for j in range(num_per_facility):
            worker_id = (i * num_per_facility) + j + 1
            create_demo_field_worker(worker_id, facility)
        

def create_demo_field_worker(worker_id, facility=None):

    username = f"field_worker_{worker_id}"

    user, created = User.objects.get_or_create(
        email=f"{username}@example.com",
        defaults={"name": f"Demo Field Worker {worker_id}", "is_active": True, "has_valid_password": True},
    )

    if created:
        # assign password and save user
        user.set_password("Password1")
        user.save()
        
        # set their username
        user.set_va_username(*[username])
        
        # assign new user to field worker group
        user_group = Group.objects.get(name="Field Workers")
        user_group.user_set.add(user)
        # save user group changes
        user_group.save()
        
        # if facility name provided, assign field worker. Otherwise, randomly assign one
        if not facility:
            facility = Location.objects.filter(location_type='facility').order_by('?').first()
        
        user.location_restrictions.add(*[facility])
        
        # save/export final user
        user.save()
        
        print(f"Successfully created field worker with username {username} for facility {facility.name}")
        