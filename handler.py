import requests
import json
import csv
import re
from datetime import datetime, timedelta

import boto3
import botocore

# Store dates for today and two weeks ago for use in queries.
now = datetime.now().replace(microsecond=0)
last_week = now - timedelta(days=14)

# Get Fort Lauderdale police incident records from their API.
def get_FLPD():
    queried_url = "https://fortlauderdale.data.socrata.com/resource/8kzg-hfzf.geojson?$$app_token=cADtqEAvKhAk8xLORatHGxSvm&$where=date_occu between '" + last_week.isoformat() + "' and '" + now.isoformat() + "' and offense not like '%25INFORMATION%25'"
    offense_field = "offense"
    date_field = "date_occu"

    print("Getting FLPD incidents from: " + queried_url)
    prepped_data = get_incidents(queried_url, offense_field, date_field)

    print("Writing FLPD results to S3...")
    save_to_s3(prepped_data, "FLPD_data.geojson")


# Get Delray Beach police incident records from their API.
def get_DelrayPD():

    queried_url = "https://moto.data.socrata.com/resource/ub3s-nu4t.geojson?$where=incident_datetime between '" + last_week.isoformat() + "' and '" + now.isoformat() + "' and starts_with(incident_type_primary, '[INC]')"
    offense_field = "incident_description"
    date_field = "incident_datetime"

    print("Getting Delray PD incidents from: " + queried_url)
    prepped_data = get_incidents(queried_url, offense_field, date_field)

    print("Writing Delray PD results to S3...")
    save_to_s3(prepped_data, "DelrayPD_data.geojson")


# Get incidents by passing in url.
# Each data source has a different name for its offense and incident date fields,
# so pass those in too to standardize.
def get_incidents(url, offense_field, date_field):

    req = requests.get(url)
    incidents_data = req.json()

    # Designate categories of crimes based on offense field keywords.
    cat_violent = ['AGGREVATED', 'ARSON', 'ASSAULT', 'HOMICIDE', 'BATTERY', 'ROBBERY']
    cat_property = ['BURGLARY', 'BURGL', 'VANDALISM', 'THEFT', 'TRESPASS', 'TRESSPASS', 'PROPERTY CRIME', 'BREAKING & ENTERING']
    cat_vehicle = ['ACCIDENT', 'DRIVING', 'DUI', 'TRAFFIC', 'HIT AND RUN', 'HIT/RUN']
    cat_fraud = ['FORGERY', 'FORGE', 'FRAUD', 'IMPERSONAT', 'IMPERSONATION', 'IMPERSONATING']
    cat_drug = ['DRUG', 'DRUGS', 'COCAIN', 'MARIJUANA', 'OVERDOSE', 'CANNABIS', 'CANNIBIS', 'WEED']

    for feature in incidents_data['features']:


        # Standardize incident date fields into new column.
        dateValue = datetime.strptime(feature['properties'][date_field], "%Y-%m-%dT%H:%M:%S.%f")
        feature['properties']['incident_date'] = dateValue.strftime('%m/%d/%Y')

        # Standardize offenses into new column.
        offenseValue = feature['properties'][offense_field].upper().strip()
        feature['properties']['offense_final'] = offenseValue.title()

        # Dissect our offense fields, fuzzy match and categorize crime type.
        offenseSplit = re.split('\W+', offenseValue)

        if set(offenseSplit).intersection(cat_violent):
            feature['properties']['crimecategory'] = 'violent'
        elif set(offenseSplit).intersection(cat_property):
            feature['properties']['crimecategory'] = 'property'
        elif set(offenseSplit).intersection(cat_vehicle):
            feature['properties']['crimecategory'] = 'vehicle'
        elif set(offenseSplit).intersection(cat_fraud):
            feature['properties']['crimecategory'] = 'fraud'
        elif set(offenseSplit).intersection(cat_drug):
            feature['properties']['crimecategory'] = 'drug'
        else:
            feature['properties']['crimecategory'] = 'other'

    return incidents_data


# Push data to the S3 bucket to our S3 bucket.
def save_to_s3(incidents_data, filename):

    AWS_BUCKET_NAME = 'projects.sun-sentinel.com'
    s3 = boto3.resource('s3')
    bucket = s3.Bucket(AWS_BUCKET_NAME)
    path = "crime-map/data/" + filename
    data = json.dumps(incidents_data)

    bucket.put_object(
        ACL='public-read',
        ContentType='application/json',
        Key=path,
        Body=data,
    )

    body = {
        "uploaded": "true",
        "bucket": AWS_BUCKET_NAME,
        "path": path,
    }
    return {
        "statusCode": 200,
        "body": body
    }


def main(event, context):
    get_FLPD()
    get_DelrayPD()
    print("Done!")

if __name__ == '__main__':
    main('', '')
