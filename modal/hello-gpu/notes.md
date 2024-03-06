Create a file like function.py


Make a stub or a class where the code you want to execute lives


`modal setup` to sign in

`modal run function.py` to run your local entrypoint. Can run locally or remote

`modal deploy function.py` deploys your function, making it available over https or with python code


Note that web endpoints don't have any security enabled by default. Anyone can invoke your web endpoints and you pay!

It's better to deploy functions and run them directly in Modal with Python.
Or deploy a web app that does authentication in Modal web app on a CPU, that again invokes other Modal functions with GPUs.
