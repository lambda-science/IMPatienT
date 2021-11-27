docker volume create --name dataehroes

docker run -v dataehroes:/data --name helper busybox true
docker cp data helper:/
docker rm helper