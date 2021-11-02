docker build . -f Dockerfile.dev -t myoxiadev:latest
docker run --rm --name myoxiadev -p 5000:5000 -v $(pwd):/home/myoxia/code  myoxiadev:latest