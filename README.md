# Django Blogapp

## Project setup

Add the following to your `/etc/hosts` file.

    127.0.0.1       api.blogapp.com

Run the following commands:

    make init
    make up


## Code formatting

### Working with Intellij
Install Black Connect: https://plugins.jetbrains.com/plugin/14321-blackconnect

`blackd` is used to run black as a service

Go to `Preferences > Tools > BlackConnect`

Check `Trigger when saving changed files`

Check `Trigger on code format`

Check `Skip string normalization `  **IMPORTANT!**

Connection Settings:

    Hostname: localhost
    Port: 45484


### Working with VSCode

Install black formatter extension: https://marketplace.visualstudio.com/items?itemName=ms-python.black-formatter

**Ensure you set the `--skip-string-normalization` argument, to avoid double quotes!**

Set `black` as the default formatter

Set `black` as formatting provider

Set `Format on save` to true

## Django Admin GUI
[http://api.blogapp.com:8080/admin/](http://api.blogapp.com:8080/admin/)
    
    Username: admin
    Password: admin

## GraphiQL Browser
[http://api.blogapp.com:8080/graphql/](http://api.blogapp.com:8080/graphql/)


## Django bash and python dependencies
Whenever you have to install any python dependency, run the following command:

    make bash
    pip install <your dependency>
    pip freeze > requirements.txt


## GraphQL support
In order to work with `.grapqhl` files and code completion features for our tests, we need to update the api schema json file.
Whenever you change the api, run the following command:

    make codegen


## Tests
    make bash
    pytest


## Update Fixtures

    ./manage.py dumpdata --natural-foreign --indent 4 --exclude admin --exclude auth --exclude contenttypes --exclude sessions --exclude refresh_token.refreshtoken > blog/fixtures/initial_data.json

##
Returning a lot of "fake" posts for testing:

    posts_list = []
    for post in posts:
        for i in range(100):
            posts_list.append(post)
    paginator = Paginator(posts_list, 4)
