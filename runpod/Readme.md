Install the cli with `wget -qO- cli.runpod.net | sudo bash`


`runpodctl project create` Create files for a project
`runpodctl config --apiKey API_KEY` to authenticate with the cli


Install `pip install runpod` and run the function file with python `python src/handler.py`

Must use test input to run the function. Make a `test_input.json` in your cwd or run the function with `python src/handler.py --test_input '{"input": {"x": 4}}'`

In order to run anything using the cli, you need to set up a storage volumne in Runpod. This costs minimum 0.70$ per month.
Using the cli with e.g. `runpodctl project dev` spins up a server in the cloud you need to pay for.

`runpodctl project build` generate a docker file for your project

`docker build . --tag vikfand/runpod-hello-gpu` build your function as a docker image

`docker run vikfand/runpod-hello-gpu` test that your image can be run

`docker push vikfand/runpod-hello-gpu` you need to push your container to a registry, runpod does not do this for you. Dockerhub is ok for public images
Log in to Dockerhub with `docker login -u vikfand` and change to your username on Dockerhub

Remember to make the image public on Dockerhub if you want to use it without setting up credentials on Runpod

Go to runpod.io/console and create a template with the url of your image in the docker registry

Then go to serverless in the console and make a new endpoint with that template

You now have a url that can be used to invoke your function serverlessly
