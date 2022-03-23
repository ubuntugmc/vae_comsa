import csv
import json
import os
import re
from io import StringIO

import pandas as pd
import requests
from django.forms import model_to_dict

from va_explorer.va_data_management.models import (
    CauseCodingIssue,
    CauseOfDeath,
    CodingBatch,
    VerbalAutopsy,
)

# NOTE: By default, VA Explorer runs InterVA5 (settings found in .env file)
# To change coding algorithm, will need to update settings below and point
# to that algorithm's service

PYCROSS_HOST = os.environ.get("PYCROSS_HOST", "http://127.0.0.1:5001")
INTERVA_HOST = os.environ.get("INTERVA_HOST", "http://127.0.0.1:5002")

# Param Setting value sets (used for validation)
# TODO: add other algorithms' settings as we add support for them
ALGORITHM_PARAM_OPTIONS = {
    "INTERVA": {
        "HIV": ["h", "l", "v"],
        "Malaria": ["h", "l", "v"],
        "groupcode": ["True", "False"],
        "api": "True",
    }
}

# InterVA5
ALGORITHM_SETTINGS = {
    # describes prevalence of HIV. Should be "h"(high),"l"(low), or "v"(very low).
    "HIV": os.environ.get("INTERVA_HIV", "h"),
    # describes prevalence of Malaria. Should be "h"(high),"l"(low), or "v"(very low).
    "Malaria": os.environ.get("INTERVA_MALARIA", "l"),
    # Whether to include group code in the output causes
    "groupcode": os.environ.get("INTERVA_GROUPCODE", "True"),
    # Required parameter when calling InterVA5 via api - need not get from .env file because it should always be 'True'
    "api": "True",
}


# validates provided algorithm settings against algorithm param value sets. Currently
# only works with interva5 but set up to generalize to other algorithms once supported
def validate_algorithm_settings():
    # TODO: turn algorithm keyname into parameter once we support other algorithms
    param_opts = ALGORITHM_PARAM_OPTIONS["INTERVA"]
    setting_keys = set(ALGORITHM_SETTINGS.keys())
    common_keys = setting_keys.intersection(param_opts.keys())

    if len(common_keys) != len(setting_keys):
        unrecognized = setting_keys.difference(common_keys)
        print(
            f"WARNING: options {unrecognized} not recognized (expected any of {list(param_opts.keys())}). Skipping..."
        )

    # ensure all common settings are valid
    for key in common_keys:
        if ALGORITHM_SETTINGS[key] not in param_opts[key]:
            print(
                f"ERROR: provided {key} value {ALGORITHM_SETTINGS[key]} not \
                 found. Expecting one of {param_opts[key]}"
            )
            return False

    return True


def _run_pycross_and_interva5(verbal_autopsies):
    # Get into CSV format, also prefixing keys with - as expected by
    # pyCrossVA (e.g. Id10424 becomes -Id10424)
    va_data = [model_to_dict(va) for va in verbal_autopsies]
    va_data = [dict([(f"-{k}", v) for k, v in d.items()]) for d in va_data]
    va_data_csv = pd.DataFrame.from_records(va_data).to_csv()

    # Transform to algorithm format using the pyCrossVA web service
    transform_url = f"{PYCROSS_HOST}/transform?input=2016WHOv151&output=InterVA5"
    transform_response = requests.post(transform_url, data=va_data_csv.encode("utf-8"))

    # Convert result to JSON
    transform_response_reader = csv.DictReader(StringIO(transform_response.text))

    # Replace blank key with ID and append to list for later jsonification
    rows = [
        {"ID" if key == "" else key: value for key, value in row.items()}
        for row in transform_response_reader
    ]

    result_json = json.dumps({"Input": rows, **ALGORITHM_SETTINGS})

    # This is to get to the data into required algorithm format for interva5
    result_json = result_json.replace('"0.0"', '"."').replace('"1.0"', '"y"')

    algorithm_url = f"{INTERVA_HOST}/interva5"
    algorithm_response = requests.post(algorithm_url, data=result_json)
    return json.loads(algorithm_response.text)


def run_coding_algorithms():
    # Start a new import batch
    interva_batch = CodingBatch.objects.create()

    # Load all verbal autopsies that don't have a cause coding
    # TODO: This should eventually check to see that there's a cause coding for
    # every supported algorithm
    verbal_autopsies_without_causes = list(
        VerbalAutopsy.objects.filter(causes__isnull=True)
    )

    print(f"ALGORITHM SETTINGS: {ALGORITHM_SETTINGS}")

    causes, issues = run_interva5(verbal_autopsies_without_causes)
    interva_batch.finish_coding(causes, issues)

    return verbal_autopsies_without_causes, causes, issues


def run_interva5(verbal_autopsies_without_causes):
    interva_response_data = _run_pycross_and_interva5(verbal_autopsies_without_causes)

    # The ID that comes back is the index in the data that was passed in.
    # Use that to look up the matching VA in the verbal_autopsies_without_causes list.
    causes = []
    for cause_data in interva_response_data["results"]["VA5"]:
        cause = cause_data["CAUSE1"][0].strip()
        # Account for indeterminate cause of death, which has CAUSE1 == '', LIK1 == '', and INDET == 100
        if (
            cause == ""
            and cause_data["INDET"][0] == 100
            and cause_data["LIK1"][0].strip() == ""
        ):
            cause = "Indeterminate"

        if cause:
            va_offset = int(cause_data["ID"][0].strip())
            va_id = verbal_autopsies_without_causes[va_offset].id
            causes.append(
                CauseOfDeath(
                    verbalautopsy_id=va_id,
                    cause=cause,
                    algorithm="InterVA5",
                    settings=ALGORITHM_SETTINGS,
                )
            )

    CauseOfDeath.objects.bulk_create(causes)

    # The ID that comes back is the index in the data that was passed in.
    # Use that to look up the matching VA in the verbal_autopsies_without_causes list.
    issues = []
    for severity in CauseCodingIssue.SEVERITY_OPTIONS:
        for issue in interva_response_data[severity + "s"]:
            if isinstance(issue, list):
                issue = issue[0]
            va_offset, issue_text = re.split("  +", issue, maxsplit=1)
            va_id = verbal_autopsies_without_causes[int(va_offset)].id
            issues.append(
                CauseCodingIssue(
                    verbalautopsy_id=va_id,
                    text=issue_text,
                    severity=severity,
                    algorithm="InterVA5",
                    settings=ALGORITHM_SETTINGS,
                )
            )

    CauseCodingIssue.objects.bulk_create(issues)

    return causes, issues
