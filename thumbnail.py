import base64
import boto3
import calendar
import io
import uuid
from datetime import datetime, timedelta
from flask import Flask, request, render_template
from PIL import Image

import sys
from urllib.parse import unquote_plus
import PIL.Image

app = Flask(__name__)

s3 = boto3.resource('s3')  # zappa example 2017
s3_client = boto3.client('s3')

BUCKET_NAME = "zappa-microservice-bucket-gebbles"  # clean things up


# a helper function to generate uuid
def createUniqueFileName():
    myuuid = uuid.uuid4()
    return str(myuuid)

# another helper function
def resize_image(image_path, resized_path):
	with Image.open(image_path) as image:
		image.thumbail(100,100)
		image.save(resized_path)


@app.route('/s3upload', methods=['GET'])
def lambda_handler(event, context):
    try:
        s3Client = boto3.client("s3")
    except Exception as e:
        return {
            "status_code": 400,
            "error": e
        }
    bucketName = "uploadimagev1"
    fileKey = createUniqueFileName()
    fileKey = fileKey+".png"
    expiryTime = 120
    
    try:
        response = s3Client.generate_presigned_url('put_object', 
                                Params={'Bucket': bucketName, 'Key': fileKey}, 
                                ExpiresIn=expiryTime)
 
        return {
            'statusCode': 200,
            'key': fileKey,
            'body': json.dumps(response, default=str)
        }
        
    except Exception as e:
        return {
            "statusCode" : 400,
            "error": e
        }




@app.route("/")
def hello_world():
	return "<p>Hello world!</p>"


@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
	if request.method == 'POST':
		new_file_b64 = request.form['b64file']
		if new_file_b64:
		
			# decode the image
			new_file = base64.b64decode(new_file_b64)
			
			# crop the image
			img = Image.open(io.BytesIO(new_file))
			img.thumbnail((200, 200))

			# Tag this filename with an expiry time
			future = datetime.utcnow() + timedelta(days=10)
			timestamp = str(calendar.timegm(future.timetuple()))
			filename = "thumb.%s.jpg" % timestamp

			# send the bytes to s3
			img_bytes = io.BytesIO()
			img.save(img_bytes, format='JPEG')
			s3_object = s3.Object(BUCKET_NAME, filename)
			resp = s3_object.put(
				Body = img_bytes.getvalue(),
				ContentType = 'image/jpeg'
				)
			if resp['ResponseMetadata']['HTTPStatusCode'] == 200:
				
				# make the result public
				object_acl = s3_object.Acl()
				response = object_acl.put(ACL='public-read')
				object_url = "https://{0}.s3.amazonaws.com/{1}".format(BUCKET_NAME,filename)
				return object_url, 200
			else:
				return "Something went wrong :(", 400
	return render_template('upload.html')


@app.route('/makethumbnail', methods=['GET', 'POST'])
def make_thumbnail():
	# extraxt the ket from the trigger event
	# thumbnail
	# use a consistent naming pattern for the thumbnail objects
	# store it somewhere - s3
	
	for record in event['Records']:
		bucket = record['s3']['bucket']['name']
		key = unquote_plus(['s3']['object']['key'])
		tmpkey = key.replace('/', '')
		download_path = '/tmp/{}{}'.format(uuid.uuid4(), tmpkey)
		upload_path = '/tmp/resized-{}'.format(tmpkey)
		s3_client.download_file(bucket, key, download_path)
		resize_image(download_path, upload_path)

		destination_bucket = "minithumbnails"
		s3_client.upload_file(upload_path, destination_bucket, key)


# we need this for local development
if __name__ == '__main__':
	app.run()
