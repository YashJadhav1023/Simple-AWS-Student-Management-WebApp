import json
import boto3
from botocore.exceptions import ClientError

# Initialize the DynamoDB client
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('StudentData')

def lambda_handler(event, context):
    http_method = event['httpMethod']
    path = event['path']
    body = event.get('body')

    # Define a standard response dictionary with headers
    response_headers = {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*'
    }

    try:
        if http_method == 'GET' and path == '/students':
            # Get all students
            response = table.scan()
            return {
                'statusCode': 200,
                'headers': response_headers,
                'body': json.dumps(response['Items'])
            }
        
        elif http_method == 'GET' and path.startswith('/students/'):
            # Get a single student by studentId
            student_id = path.split('/')[-1]
            response = table.get_item(Key={'studentId': student_id})
            if 'Item' in response:
                return {
                    'statusCode': 200,
                    'headers': response_headers,
                    'body': json.dumps(response['Item'])
                }
            else:
                return {
                    'statusCode': 404,
                    'headers': response_headers,
                    'body': json.dumps({'error': 'Student not found'})
                }
        
        elif http_method == 'POST' and path == '/students':
            # Add a new student
            student_data = json.loads(body)
            table.put_item(Item=student_data)
            return {
                'statusCode': 201,
                'headers': response_headers,
                'body': json.dumps({'message': 'Student added successfully'})
            }
        
        elif http_method == 'PUT' and path.startswith('/students/'):
            # Update a student
            student_id = path.split('/')[-1]
            student_data = json.loads(body)
            if student_data.get('studentId') != student_id:
                return {
                    'statusCode': 400,
                    'headers': response_headers,
                    'body': json.dumps({'error': 'studentId in body does not match path'})
                }
            
            table.put_item(Item=student_data)
            return {
                'statusCode': 200,
                'headers': response_headers,
                'body': json.dumps({'message': 'Student updated successfully'})
            }

        elif http_method == 'DELETE' and path.startswith('/students/'):
            # Delete a student
            student_id = path.split('/')[-1]
            table.delete_item(Key={'studentId': student_id})
            return {
                'statusCode': 200,
                'headers': response_headers,
                'body': json.dumps({'message': 'Student deleted successfully'})
            }
        
        else:
            return {
                'statusCode': 405,
                'headers': response_headers,
                'body': json.dumps({'error': 'Method Not Allowed'})
            }
            
    except ClientError as e:
        print(e.response['Error']['Message'])
        return {
            'statusCode': 500,
            'headers': response_headers,
            'body': json.dumps({'error': 'DynamoDB operation failed'})
        }
    except Exception as e:
        print(e)
        return {
            'statusCode': 500,
            'headers': response_headers,
            'body': json.dumps({'error': 'Internal server error'})
        }