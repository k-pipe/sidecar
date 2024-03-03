IMAGE=kpipe/sidecar:0.0.3
echo "Building docker image $IMAGE"
docker build . -t $IMAGE --platform=linux/amd64
echo "Pushing docker image $IMAGE"
docker push $IMAGE
