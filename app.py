# /run.py
import os

from flask import Flask, current_app, render_template
from .src.appinit import create_app


env_name = 'local'
app = create_app(env_name)


if __name__ == '__main__':

  # run app
  app.run(debug=True,host='0.0.0.0',port=5000)