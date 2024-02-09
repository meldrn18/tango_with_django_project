from django.shortcuts import render
from django.http import HttpResponse
from rango.models import Category, Page
from rango.forms import CategoryForm, PageForm, UserForm, UserProfileForm
from django.shortcuts import redirect
from django.urls import reverse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from datetime import datetime


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

   visitor_cookie_handler(request)
   #obtain response obj. early so we can add cookie info
   return render(request, 'rango/index.html', context=context_dict)

def get_server_side_cookie(request, cookie, default_val=None):
   val = request.session.get(cookie)
   if not val:
      val = default_val
   return val

def visitor_cookie_handler(request):
   #get no. of visits to site
   #use COOOKIES.get() to obtain visits cookies
   #if cookie exists, val casted to an int, if not default val 1 used
   visits = int(request.COOKIES.get('visits', '1'))
   last_visit_cookie =request.COOKIES.get('last_visit', str(datetime.now()))
   last_visit_time = datetime.strptime(last_visit_cookie, '%Y-%m-%d %H:%M:%S.%f')

   #if its been more than a day since last visit
   if (datetime.now() - last_visit_time).days >0:
      visits = visits+1
      #update last visit cookie now we have updated count
      request.session['last_visit'] = str(datetime.now())
   else:
      #set last visit cookie
      request.session['last_visit'] = last_visit_cookie
   #update/set visits cookie
   request.session['visits'] = visits

def about(request):
    #create dict to pass to template engine as context.
    context_dict = {}
    visitor_cookie_handler(request)
    context_dict['visits'] = request.session['visits']

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

@login_required
def add_category(request):
   form=CategoryForm()

   #A HTTP POST?
   if request.method== 'POST':
      form=CategoryForm(request.POST)

      #Have we been provided with a valid form?
      if form.is_valid():
         #save the new category to the db
         form.save(commit=True)
         #Now that the category is saved, we could confirm this
         #for now just redirect the user back to index view
         return redirect('/rango/')
      else:
         #supplied form contains errors, print them to terminal
         print(form.errors)
   #will handle the bad form, new form, or no for, supplied cases
   #render form with error messages if any
   return render(request, 'rango/add_category.html', {'form':form})

@login_required
def add_page(request, category_name_slug):
   try:
      category=Category.objects.get(slug=category_name_slug)
   except Category.DoesNotExist:
      category = None
   
   #you cannot add a page to a category that doesnt exist
   if category is None:
      return redirect('/rango/')



   form = PageForm()

   if request.method == 'POST':
      form = PageForm(request.POST)

      if form.is_valid():
         if category:
            page = form.save(commit=False)
            page.category = category
            page.views = 0
            page.save()

            return redirect(reverse('rango:show_category', kwargs={'category_name_slug':category_name_slug}))
      else:
         print(form.errors)
   context_dict={'form':form, 'category':category}
   return render(request, 'rango/add_page.html', context=context_dict)

def register(request):
   #bool val. for telling template whether reg. was successful
   #initially false, change to true when reg. succeeds
   registered=False

   #if its a HTTP POST we're interested in processing form data
   if request.method == 'POST':
      #try to grab info  from raw form info
      user_form = UserForm(request.POST)
      profile_form = UserProfileForm(request.POST)

      #if both forms are valid
      if user_form.is_valid() and profile_form.is_valid():
         #save form data to db
         user = user_form.save()

         # hash password and update user object
         user.set_password(user.password)
         user.save()

         #sorting UserProfile instance, set commit=false to delay saving model until its ready
         profile = profile_form.save(commit=False)
         profile.user = user

         #if user provided profile pic, get from form and put in model
         if 'picture' in request.FILES:
            profile.picture = request.FILES['picture']

         #now save UserProfile instance
         profile.save()

         #update variable to indicate reg. was success
         registered = True
      else:
         #invalid form(s) or mistakes, print problems to terminal
         print(user_form.errors, profile_form.errors)
   else:
      #not a HTTP POST, sp render form using 2 ModelForm instances
      #these will be blank and ready for user input
      user_form = UserForm()
      profile_form = UserProfileForm()

   #render template depending on context
   return render(request, 'rango/register.html', context={'user_form':user_form, 'profile_form':profile_form, 'registered':registered})

def user_login(request):
   #if request is HTTP POST, try get relevant info
   if request.method=='POST':
      #retrieve username and password, obtained from login form
      #using request.POST.get('<var>') instead of request.POST['<var>']
      #as first returns None is val doesnt exist, while latter will raise KeyError excep.
      username = request.POST.get('username')
      password = request.POST.get('password')

      #use djangos machinery to see if combo is valid, a user object
      #will be returned if it is
      user = authenticate(username=username, password=password)

      #if we have a user object, details correct, if None no user match
      if user:
         #is account active or has it been disabled
         if user.is_active:
            #if account valid and active log in, go back to homepage
            login(request, user)
            return redirect(reverse('rango:index'))
         else:
            #account inactive, dont log in
            return HttpResponse("Your Rango account is diabled.")
      else:
         #incorrect login details, dont login
         print(f"Invalid login details: {username}, {password}")
         return HttpResponse("Invalid login details supplied.")
   #request is not a HTTP POST, so display login form - most likely a HTTP GET
   else:
      #no context  variables to pass the template system, hence blank dic. obj.
      return render(request, 'rango/login.html')

@login_required
def restricted(request):
   return render(request, 'rango/restricted.html')

#login_required() decorator ensures only those logged in can access this view
@login_required
def user_logout(request):
   logout(request)
   #return to homepage
   return redirect(reverse('rango:index'))

