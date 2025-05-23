# Code to check registered routes
from fastapi.routing import APIRoute
for route in app.routes:
    if isinstance(route, APIRoute):
        print(route.path, route.methods)
