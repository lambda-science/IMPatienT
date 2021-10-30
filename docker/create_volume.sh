docker volume create --name datamyoxia

docker run -v datamyoxia:/data --name helper busybox true
docker cp data helper:/
docker rm helper