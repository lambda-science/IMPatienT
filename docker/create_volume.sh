docker volume create --name dataimpatient

docker run -v dataimpatient:/data --name helper busybox true
docker cp data helper:/
docker rm helper
