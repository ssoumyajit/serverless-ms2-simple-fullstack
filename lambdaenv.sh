docker run -ti -p 5000:5000 -e AWS_PROFILE=zappa1 -v "$(pwd):/var/task" -v ~/.aws/:/root/.aws --rm dockerriver/gebbles-microservices
