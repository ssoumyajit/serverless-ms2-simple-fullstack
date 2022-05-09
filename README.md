Nice article from zappa blog.

here the lambda function renders the index.html :) as a function response where there is a simple javascript form to upload image (ofcourse 10mb api gateway and 6 mb lambda request size is there). the POST request with the uploaded image will hit the lambda function where it will be resized and then put into an s3 bucket.

- flask is being used as  a wsgi server with the help of zappa.
- pillow is being used
- major dependancies flask, zappa

it is a nice one.
specially the index.html response. total full stack with a single microservice through flask.umm actually there is an html template with a js script inside the simple flask project.
