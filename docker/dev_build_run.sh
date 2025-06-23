docker build . -f Dockerfile.dev -t impatientdev:latest
docker run --rm -it --name impatientdev -p 7860:7860 -v $(pwd):/home/impatient/  impatientdev:latest
