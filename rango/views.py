from django.template import RequestContext
from django.shortcuts import render_to_response
from rango.models import Category, Page

# Create your views here.
from django.http import HttpResponse # Not currently used

# helper functions
def name_to_url(name):
    return name.replace(' ', '_')

def url_to_name(url):
    return url.replace('_', ' ')

def index(request):
    # Obtain the context from the HTTP request.
    context = RequestContext(request)
    
    # Query the database - add the list to our context dictionary.
    category_list = Category.objects.order_by('-likes')[:5]
    context_dict = {'categories': category_list}
    
    # Add top 5 Pages to context
    page_list = Page.objects.order_by('-views')[:5]
    context_dict['pages'] = page_list
    
    
    # We loop through each category returned, and create a URL attribute.
    # This attribute stores an encoded URL (e.g. spaces replaced with underscores)
    for category in category_list:
        #category.url = category.name.replace(' ', '_')
        category.url = name_to_url(category.name)
    
    # Render the response and send it back!
    return render_to_response('rango/index.html', context_dict, context)

def about(request):
    context = RequestContext(request)
    return render_to_response('rango/about.html', {}, context)

def category(request, category_name_url):
    # Request our context from the request passed to us.
    context = RequestContext(request)

    # Change underscores in the category name to spaces.
    # URLs don't handle spaces well, soe we encode them as underscores.
    # We can then simply replace the underscores with spaces again to get the name.
    #category_name = category_name_url.replace('_', ' ')
    category_name = url_to_name(category_name_url)

    # Create a context dictionary which we can pass to the themplate rendering engine.
    # We start by containing the name of the category passed by the user.
    context_dict = {'category_name': category_name}
    
    try:
        # Can we find a category with the given name?
        # if we can't the .get() method raises a DoesNotExist exception.
        # So the .get() method returns one model instance or raise an exception.
        category = Category.objects.get(name=category_name)
        
        # Retrieve all of the associated pages.
        # Note that filter return >= 1 model instance. [filter may return empty list -cf]
        pages = Page.objects.filter(category=category)
        
        # Add our results list to the template context under name pages.
        context_dict['pages'] = pages
        # We also add the category object from the database to the context dictionary.
        # We'll use this in the template to verify that the category exists.
        context_dict['category'] = category

    except Category.DoesNotExist:
        # We get here if we didn't find the specified category.
        # Don't do anything - the template displays the "no category" message for us.
        pass

    # Go render the resonse and return it to thee client.
    return render_to_response('rango/category.html', context_dict, context)
