# Crime datamaker

The scraper and parser framework powering the South Florida Sun Sentinel's police incident map.

### Prerequisites
- Python 3.6
- [Serverless CLI](https://serverless.com/)
- [Amazon Web Services CLI](https://aws.amazon.com/cli/)
- Node (We used v8.9)
- The Sun Sentinel's AWS credentials

### Installing


### Configuring
Configuration for the Lambda function like the deployment parameters, the script scheduler and deployment settings are located in [serverless.yml](https://github.com/SunSentinel/crime-datamaker/blob/master/serverless.yml) file. A list of all available properties can be found [here](https://serverless.com/framework/docs/providers/aws/guide/serverless.yml/).

### Deploying
Just run
```
serverless deploy
```
...and that's it!

### Running the function remotely
Run
```
serverless invoke -f makedata --log
```
