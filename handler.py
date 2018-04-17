import requests
import json
import csv

from datetime import datetime, timedelta
import boto3
import botocore

# Pull and parse Fort Lauderdale police incident records from their API.
def get_FLPD():

    # Designate categories of crimes based on offense keywords.
    cat_violent = ['AGGREVATED', 'ARSON', 'ASSAULT', 'HOMICIDE', 'BATTERY', 'ROBBERY']
    cat_property = ['BURGLARY', 'BURGL', 'VANDALISM', 'THEFT', 'TRESPASS']
    cat_vehicle = ['ACCIDENT', 'DRIVING', 'DUI', 'TRAFFIC', 'HIT AND RUN', 'HIT/RUN']
    cat_fraud = ['FORGERY', 'FRAUD', 'IMPERSONAT']
    cat_drug = ['DRUG', 'COCAIN', 'MARIJUANA', 'OVERDOSE', 'CANNABIS', 'CANNIBIS', 'WEED']

    # Build url with queries to get previous two weeks, omitting 'INFORMATION' entries.
    now = datetime.now().replace(microsecond=0)
    last_week = now - timedelta(days=14)
    queried_url = "https://fortlauderdale.data.socrata.com/resource/8kzg-hfzf.geojson?$$app_token=cADtqEAvKhAk8xLORatHGxSvm&$where=date_occu between '" + last_week.isoformat() + "' and '" + now.isoformat() + "' and offense not like '%25INFORMATION%25'"

    print("Using url: " + queried_url)

    req = requests.get(queried_url)
    incidents_data = req.json()

    print(len(incidents_data['features']))

    # Loop through each offense and categorize them types for our apps.
    for feature in incidents_data['features']:
        offense = feature['properties']['offense']

        if offense in cat_violent:
            feature['properties']['crimecategory'] = 'violent'
        elif offense in cat_property:
            feature['properties']['crimecategory'] = 'property'
        elif offense in cat_vehicle:
            feature['properties']['crimecategory'] = 'vehicle'
        elif offense in cat_fraud:
            feature['properties']['crimecategory'] = 'fraud'
        elif offense in cat_drug:
            feature['properties']['crimecategory'] = 'drug'
        else:
            feature['properties']['crimecategory'] = 'other'

    print("Writing FLPD results to S3...")

    filename = "FLPD_data.geojson"
    save_to_s3(incidents_data, filename)
    print("Done!")



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
    get_FLPD();


if __name__ == '__main__':
    main(None, None)
