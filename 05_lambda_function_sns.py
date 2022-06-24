#Stock Check Lambda function
#
# This function is triggered when values are inserted into the Inventory DynamoDB table.
#Inventory counts are checked and if an item is out of stock, a notification is sent to an SNS Topic.
import json, boto3
# This handler is executed every time the Lambda function is triggered
def lambda_handler(event, context): 
  #Show the incoming event in the debug log
  print("Event received by Lambda function: " + json.dumps(event, indent = 2))

  # For each inventory item added, check if the count is zero
  for record in event['Records']:
    newImage = record['dynamodb'].get('NewImage', None)
    if newImage:
      count = int(record['dynamodb']['NewImage']['Count']['N'])
      if count == 0:
        store = record['dynamodb']['NewImage']['Store']['S']
        item = record['dynamodb']['NewImage']['Item']['S']

        # Construct message to be sent
        message = store + ' is out of stock of ' + item
        print(message)

        # Connect to SNS
        sns = boto3.client('sns')
        alertTopic = 'NoStock'
        snsTopicArn = [t['TopicArn'] for t in sns.list_topics()['Topics']
                          if t['TopicArn'].lower().endswith(':' + alertTopic.lower())][0]
        # Send message to SNS
        sns.publish(
          TopicArn = snsTopicArn,
          Message = message,
          Subject = 'Inventory Alert!',
          MessageStructure = 'raw'
        )
  # Finished!
  return 'Successfully processed {} records.'.format(len(event['Records']))