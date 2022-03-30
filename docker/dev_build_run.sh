docker build . -f Dockerfile.dev -t impatientdev:latest
docker run --rm -it --name impatientdev -p 5000:5000 -v $(pwd):/home/impatient/  impatientdev:latest
