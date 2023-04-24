# An API wrapper for Poe.
#### An reverse-engineered asynchronous API wrapper for Quora Poe.

----
## Setup
### Clone the repository
```bash
$ git clone https://github.com/cattodotpy/aiopoe.git
$ cd aiopoe
```
### Install dependencies
```bash
$ pip install -r requirements.txt
```

### Obtain secrets
You need to obtain the following secrets in order to use the API wrapper:
- `Quora-Formkey`
- `Cookie`

Login to [Quora](https://www.quora.com), view the source of the page and search for `formkey`. That's your `Quora-Formkey`.

For the `Cookie`, you need to login to [Quora](https://www.quora.com) and then inspect the website. Go to the `Storage` tab and then `Cookies`. You need to copy the `m-b` value from `https://www.quora.com`.

### Examples
Go to the `examples` folder, open `.env.example` and fill in the secrets you obtained earlier. Then, rename the file to `.env`.

Now, you can run the examples:
```bash
$ python3 examples/example.py
```

### Disclaimer
This repository is intended for educational and research purposes only. The owner of this repository does not endorse any illegal or unethical actions taken by users of this repository. The information provided in this repository is for informational purposes only and should not be construed as legal advice. The owner of this repository is not responsible for any harm or damages that may result from the use of this repository. Users are solely responsible for their own actions and use this repository at their own risk. By accessing this repository, you agree to these terms and conditions.

