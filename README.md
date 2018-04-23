# Crime datamaker
This is a collection of the scrapers and parsers powering the South Florida Sun Sentinel's police incident maps. It runs on Lambda using the [Serverless](https://serverless.com) framework. The scripts currently grab Fort Lauderdale and Delray Beach's incident data, but more departments may be added in the future.

### Prerequisites
- Python 3.6
- [Serverless CLI](https://serverless.com/)
- [Amazon Web Services CLI](https://aws.amazon.com/cli/)
- Node (We used v8.9)
- The Sun Sentinel's AWS credentials

### Installing
TKTKTK

### The script
Right now, handler.py is the main function. Other scrapers/parsers can be added to this file, but we may break it up into separate files if it gets more complex in the future.

### Configuring
Configuration for the Lambda function for deployment and scheduling is done in the  [serverless.yml](https://github.com/SunSentinel/crime-datamaker/blob/master/serverless.yml) file. A list of all available properties can be found [here](https://serverless.com/framework/docs/providers/aws/guide/serverless.yml/).

### Deploying
After you build your scripts, run
```
serverless deploy
```
...and that's it!

### Running the function remotely
Run
```
serverless invoke -f makedata --log
```
