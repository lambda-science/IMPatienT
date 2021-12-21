docker build . -f Dockerfile.dev -t ehroesdev:latest
docker run --rm -it --name ehroesdev -p 5000:5000 -v $(pwd):/home/ehroes/  ehroesdev:latest
