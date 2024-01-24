from django.shortcuts import render
from django.http import HttpResponse

def index(request):
    return HttpResponse("""
<html>
<h1>Rango says hey there partner!</h1>
<body>
<p>click <a href='http://127.0.0.1:8000/rango/about/'>here</a> to visit the about page.</p>
</body></html>
""")

def about(request):
    return HttpResponse("""
<html>
<body>
<h1>About!</h1>
<p>click <a href='http://127.0.0.1:8000/'>here</a> to visit the index page.</p>
</body></html>
""")