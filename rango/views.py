from django.shortcuts import render
from django.http import HttpResponse

def index(request):
   #create dict to pass to template engine as context.
   context_dict = {'boldmessage': 'Crunchy, creamy, cookie, candy, cupcake!'}
   #make use of shortcut func. to return rendered response to client.
   #first parameter is the template.
   return render(request, 'rango/index.html', context=context_dict)

def about(request):
    #create dict to pass to template engine as context.
    context_dict = {'boldmessage': 'This tutorial has been put together by mel'}
    #make use of shortcut func. to return rendered response to client.
    #first parameter is the template.
    return render(request, 'rango/about.html', context=context_dict)
