Modelz is in beta. Their CLI and SDK does provide functionality for development and deployment, but it can be used to infer and query their api.

Create a python file `main.py` and put your code there. ModelZ recommend using Mosec as a framework. 
You need to build a docker image of your code, push it to a registry like Dockerhub, and enter the url when creating a deployment in the ModelZ web dashboard.


The example docker image did not work, and their web portal is so buggy that I cannot deploy to ModelZ now.


`docker build . --tag vikfand/modelz-hello-gpu` build the docker image

`docker run vikfand/modelz-hello-gpu` test that your image can be run

`docker push vikfand/modelz-hello-gpu` you need to push your container to a registry, ModelZ does not do this for you. Dockerhub is ok for public images
Log in to Dockerhub with `docker login -u vikfand` and change to your username on Dockerhub

Remember to make the image public on Dockerhub if you want to use it without setting up credentials on ModelZ