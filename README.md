# Creating a remote webserver for my electra air conditioner

## Running

### Anaconda

You can run the examples locally by installing anaconda3, grabing the source and creating the environment:
```bash
conda env create -f environment.yml
```

Activate it and run the notebook:
```bash
conda activate ir
jupyter notebook
```

### Virtualenv

Or by using virtualenv on python3:
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Activate it and run the noteboook:
```bash
source venv/bin/activate
jupyter notebook
```

## Chapters

If you are having trouble viewing this notebooks @ github, you can try viewing them on [nbviewer](https://nbviewer.jupyter.org/github/tzickel/electra_remote_ir/tree/master/).

Also the source code provided is very modular and should help you try to figure out your own RC signal and code your own web server.

Chapter 0 - [Setting up a headless Wi-Fi Rasperry Pi](Setting%20up%20a%20headless%20Wi-Fi%20Rasperry%20Pi.ipynb)

Chapter 1 - [Talking IR with the Raspberry Pi](Talking%20IR%20with%20the%20Raspberry%20Pi.ipynb)

Chapter 2 - [Decoding the IR signal](Decoding%20the%20IR%20signal.ipynb)

Chapter 3 - [Writing the IR signal](Writing%20the%20IR%20signal.ipynb)

To be continuted...
