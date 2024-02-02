from django.shortcuts import render
from django.http import HttpResponse
from rango.models import Category, Page


def index(request):
   #query db for a list of * categories stored
   #order by no. of likes in desc order
   #retrieve only top 5/ all if <5
   #place list in context_dict which will be passed to template engine
   category_list = Category.objects.order_by('-likes')[:5]
   page_list = Page.objects.order_by('-views')[:5]
   context_dict={}
   context_dict['boldmessage']= 'Crunchy, creamy, cookie, candy, cupcake!'
   context_dict['categories'] = category_list
   context_dict['pages'] = page_list
   #make use of shortcut func. to return rendered response to client.
   #first parameter is the template.
   return render(request, 'rango/index.html', context=context_dict)

def about(request):
    #create dict to pass to template engine as context.
    context_dict = {'boldmessage': 'This tutorial has been put together by mel'}
    #make use of shortcut func. to return rendered response to client.
    #first parameter is the template.
    return render(request, 'rango/about.html', context=context_dict)

def show_category(request, category_name_slug):
   #context dict to pass to rendering enging
   context_dict={}
   try:
      #can we find a category name slug with the given name?
      #if we cant the .get() method raises a DoesNotExist exception
      #the .get() method returns one model instance or raises an exception
      category = Category.objects.get(slug=category_name_slug)

      #retrieve all associated pages
      #filter() will return a list of  page objects or an empty list
      pages=Page.objects.filter(category=category)

      #adds our results list to template context under names page
      context_dict['pages']=pages
      #also add category obj. from db to context dict.
      context_dict['category']=category
   except Category.DoesNotExist:
      #enter here if specified category not found
      #template displays no category message
      context_dict['category']=None
      context_dict['pages']=None 
   return render(request, 'rango/category.html', context=context_dict)
