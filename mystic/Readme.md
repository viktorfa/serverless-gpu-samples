pipeline container init # Creates files for a container
pipeline container build # Makes docker file and builds docker image
pipeline container up # Starts the container with a web UI


pipeline cluster login mystic-api API_TOKEN -u https://www.mystic.ai -a # Login

pipeline container push # Deploy

The pipeline does not show up in the dashboard after deploying. Go to your public profile on Mystic.ai to see it.

The pipeline is named [USERNAME]/[CONTAINER_NAME]:[VERSION]

Configure GPU in pipeline.yaml, e.g.
```yaml
accelerators: ["nvidia_t4"]
accelerator_memory: 16000
```


There is no queue system. If you try to invoke a container that is sleeping, you get a 503 error. 
This can be mitigated with `run_pipeline(pointer, 1, wait_for_resources=True)` which will timeout with a 503 error after waiting 5 minutes.

Output files can be stored in Mystic.ai's cloud, and you can output files that will have an automagic url to the stored files.

There is no support for webhooks from Mystic.ai, so you have to poll Mystic.ai's api to get notified on completion.
