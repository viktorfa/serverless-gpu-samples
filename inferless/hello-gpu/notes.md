`inferless`

`keyring.errors.NoKeyringError: No recommended backend was available. Install a recommended 3rd party backend package; or, install the keyrings.alt package if you want to use the non-recommended backends. See https://pypi.org/project/keyring for details.`

Some environments like Github Codespaces don't have keyrings set up, so you need to configure an alternative keyring for the cli to work.

Install `pip install keyrings.alt` and use `PYTHON_KEYRING_BACKEND=keyrings.alt.file.PlaintextKeyring inferless` if this happens.

Use `inferless login` and create an auth token
Set it with `inferless token set --token-key 'ACCESS_KEY' --token-secret 'SECRET_KEY'`

`inferless init` Creates config for a function

Create a requirements.txt before running `inferless init` if you want to to automatically configure python packages. You can create one later as well, but the cli will crash.

It says input.json and output.json are deprecated, but you need the auto generated empty object json files for it to work. Make `input_schema.py` to configure input.

If you output is variable, (not a dict of strings I think), you need to return the variable output as a stringified dict, e.g. 
```python
return {"result": json.dumps(my_dict)}
```
