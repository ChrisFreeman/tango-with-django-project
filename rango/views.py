from django.template import RequestContext
from django.shortcuts import render_to_response
from rango.models import Category, Page
from rango.forms import CategoryForm, PageForm

#from django.http import HttpResponse # Not currently used

# Create your views here.

# helper functions
def name_to_url(name):
    return name.replace(' ', '_')

def decode_url(url):
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
    category_name = decode_url(category_name_url)

    # Create a context dictionary which we can pass to the themplate rendering engine.
    # We start by containing the name of the category passed by the user.
    context_dict = {'category_name': category_name}
    
    # Add category_name_url to context for use in add_page links
    context_dict['category_name_url'] = category_name_url
    
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

def add_category(request):
    # Get the context from the request.
    context = RequestContext(request)

    # A HTTP POST?
    if request.method == 'POST':
        form = CategoryForm(request.POST)

        # Have we been provided with a valid form?
        if form.is_valid():
            # Save the new category to the database.
            form.save(commit=True)

            # Now call the index() view.
            # The user will be shown the homepage.
            return index(request)
        else:
            # The supplied form contained errors - just print them to the terminal.
            print form.errors
    else:
        # If the request was not a POST, display the form to enter details.
        form = CategoryForm()

    # Bad form (or form details), no form supplied...
    # Render the form with error messages (if any).
    return render_to_response('rango/add_category.html', {'form': form}, context)

def add_page(request, category_name_url):
    context = RequestContext(request)

    category_name = decode_url(category_name_url)
    if request.method == 'POST':
        form = PageForm(request.POST)

        if form.is_valid():
            # This time we cannot commit straight away.
            # Not all fields are automatically populated!
            page = form.save(commit=False)

            # Retrieve the associated Category object so we can add it.
            # Wrap the code in a try block - check if the category actually exists!
            try:
                cat = Category.objects.get(name=category_name)
                page.category = cat
            except Category.DoesNotExist:
                # If we get here, the category does not exist.
                # Go back and render the add category form as a way of saying the category does not exist.
                return render_to_response('rango/add_category.html', {}, context)

            # Also, create a default value for the number of views.
            page.views = 0

            # With this, we can then save our new model instance.
            page.save()

            # Now that the page is saved, display the category instead.
            return category(request, category_name_url)
        else:
            print form.errors
    else:
        form = PageForm()

    return render_to_response( 'rango/add_page.html',
            {'category_name_url': category_name_url,
             'category_name': category_name, 'form': form},
             context)