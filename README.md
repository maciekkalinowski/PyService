# PyService
Python Flask service to save and analize daily payments

## Building Docker image:

```
docker build -t <image_name>:<image_tag> .
```
build image named `pyservice` with `v1` tag name:
```
docker build -t pyservice:v1 .
```

## Creating container from docker image:
```
docker run --name <container_name> -e PORT=<port_inside_container> -p <host_port>:<port_inside_container> <image_name>:<image_tag>
```
run container named `PyService_v1` listening on port `5000`:
```
docker run --name PyService_v1 -e PORT=5000 -p 5000:5000 pyservice:v1
```
detached mode (`-d`) and remove container after stop (`--rm`):
```
docker run -d --name PyService_v1 -e PORT=5000 -p 5000:5000 --rm pyservice:v1
```
run (detached mode) container with mounted local folder (C:\DB) to persist sqlite database file (Windows):
```
docker run --name PyService -v /C/DB:/home/PyService/db -e PORT=5000 -p 5000:5000 -d pyservice:latest
```
## Deploy to Google CLoud Run
Run the command using `gcloud` tool from folder containing `Dockerfile`:
```
gcloud run deploy 
```
You have to set project on Cloud Run and configure docker CLI to connect to Google CLoud

## Usage
### Docker container:
Run app in browser on http://localhost:<host_port>/PyService/v1/index

### Cloud Run:
Run app in browser on https://<GCP_HOST>:8080/PyService/v1/index
example:
http://localhost:5000/PyService/v1/index

### API
/tags
  - GET
  - POST

/entries (params: authors, tags, valueMin, valueMax, dateStart, dateEnd)
  - GET
  - POST

/entries/<entry_id>
  - GET
  - POST
