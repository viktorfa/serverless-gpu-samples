Install the beam CLI with `curl https://raw.githubusercontent.com/slai-labs/get-beam/main/get-beam.sh -sSfL | sh`

Authenticate with the CLI with `beam configure --clientId=CLIENT_ID --clientSecret=CLIENT_SECRET`

`beam create-app quickstart` make a basic app from the quickstart template in a quickstart folder
or `beam init` to create files for a function in your current directory.


Run a function in the cloud from your cli with `beam run hello_gpu.py:run --payload '{"x": 234, "y": 888}'`. Your functions has an optional parameter **kwargs which is a dict of your json payload (normal named parameters can also be used).
To spin up your function in the cloud, not only run once, use `beam serve hello_gpu.py`. Now you can interact with it over rest api, schedule triggers etc.


The decorator `@app.rest_api(callback_url="http://my-server.io")` can be used for Beam to send you a webhook when a function completes, whether it fails or succeeds. You can also make make it send a webhook when invoking with web api by passing a callback_url string in the request json body.
Callbacks will be urlencoded forms..

`beam deploy hello_gpu.py` deploy your function

Remember to increase the cpu and ram of your functions if you intend to do heavy work, as the default is very low.
