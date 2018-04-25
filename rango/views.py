from rango.models import Category
from rango.models import Page
from django.shortcuts import render, redirect
from django.http import HttpResponse
from rango.forms import CategoryForm
from rango.forms import PageForm
from rango.forms import UserForm, UserProfileForm
from django.contrib.auth import authenticate, login
from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth import logout
from django.contrib.auth.models import User

from registration.backends.simple.views import RegistrationView
from datetime import datetime

from rango.webhose_search import run_query

#How many people view my website

def track_url(request):
    page_id = None
    url = '/rango/'
    if request.method == 'GET':
        if 'page_id' in request.GET:
            page_id = request.GET['page_id']
            try:
                page = Page.objects.get(id=page_id)
                page.views = page.views +1
                page.save()
                url = page.url
            except:
                pass
    return redirect(url)


def get_category_list(max_results=0, starts_with=''):
    cat_list = []
    if starts_with:
        cat_list = Category.objects.filter(name__istartswith=starts_with)
    if max_results > 0:
        if len(cat_list) > max_results:
            cat_list = cat_list[:max_results]
    return cat_list


def suggest_category(request):
    cat_list = []
    starts_with = ''
   
    if request.method == 'GET':
        starts_with = request.GET['suggestion']
    cat_list = get_category_list(5, starts_with)


    return render(request, 'rango/cats.html', {'cats': cat_list})



# search feature

def search(request):
    result_list = []
    context_dict = {}
    if request.method == 'POST':
        query = request.POST['query'].strip()
        if query:
            result_list = run_query(query)
            context_dict['query'] = query
            context_dict['result_list'] = result_list
    return render(request, 'rango/search.html', context=context_dict)




# register feature

def register(request):
    registered = False
    
    if request.method == 'POST':
        user_form = UserForm(data=request.POST)
        profile_form = UserProfileForm(data=request.POST)
        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save()
            user.set_password(user.password)
            user.save()
 
            #now deal with profile
            profile = profile_form.save(commit=False)
            profile.user = user
            
            if 'picture' in request.FILES:
                profile.picture = request.FILES['picture']

            profile.save()
        
            registered = True
        else:
            print(user_form.errors, profile_form.errors)
    else:
        user_form = UserForm()
        profile_form = UserProfileForm()

    return render(request, 'rango/register.html', {'user_form' : user_form, 'profile_form': profile_form, 'registered' : registered})       
   

# login feature
def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        u = User.objects.filter(username=username)
        if u: # username is valid 
            user = authenticate(username=username, password=password)
            if user:
                if user.is_active:
                    login(request, user)
                    return HttpResponseRedirect(reverse('index'))
                else:
                    return HttpResponse(' accout is disabled')
            else:
                print("your accout 's password is incorrect")
                return HttpResponse("your accout 's password is incorrect , Plz input again")
        else:
            return HttpResponse("invalid username")
 
        #if user:
        #    if user.is_active:
        #        login(request, user)
        #        return HttpResponseRedirect(reverse('index'))
        #    else:
        #        return HttpResponse('Your Rango account is disabled')
        #else:
        #    print("Invalid  login details: {0}, {1}".format(username, password))
        #    return HttpResponse("Invalid  login details supplied")
    else:
        return render(request, 'rango/login.html', {})

#third party tools views
class MyRegistrationView(RegistrationView):
    def get_success_url(self, user):
        return '/rango/'

# logout
@login_required
def user_logout(request):
    logout(request)
    return HttpResponseRedirect(reverse('index'))

@login_required
def restricted(request):
    #return HttpResponse("Since you are logged in, you can see this text")
    return render(request, 'rango/restricted.html', {})



@login_required
def like_category(request):
    cat_id = None
    if request.method == 'GET':
        cat_id = request.GET['category_id']
    likes = 0
    if cat_id:
        cat = Category.objects.get(id=int(cat_id))
        if cat:
            likes = cat.likes + 1
            cat.likes = likes
            cat.save()
    return HttpResponse(likes)



def get_server_side_cookie(request, cookie, default_val=None):
    val = request.session.get(cookie)
    if not val:
        val = default_val
    return val

# cookie in server
def visitor_cookie_handler(request):
    visits = int(get_server_side_cookie(request, 'visits', '1'))
    last_visit_cookie = get_server_side_cookie(request, 'last_visit', str(datetime.now()))
    last_visit_time = datetime.strptime(last_visit_cookie[:-7], '%Y-%m-%d %H:%M:%S')

    if (datetime.now() - last_visit_time).days > 0:
        visits = visits + 1
        request.session['last_visit'] = str(datetime.now())
    else:
        request.session['last_visit'] = last_visit_cookie

    request.session['visits'] = visits






# cookie in client 
#def visitor_cookie_handler(request, response):
#    visits = int(request.COOKIES.get('visits', '1'))
#
#    last_visit_cookie = request.COOKIES.get('last_visit', str(datetime.now()))
#    last_visit_time = datetime.strptime(last_visit_cookie[:-7], '%Y-%m-%d %H:%M:%S')
#    
#    if (datetime.now() - last_visit_time).days > 0:
#        visits = visits + 1
#        response.set_cookie('last_visit', str(datetime.now()))
#
#    else:
#        response.set_cookie('last_visit', last_visit_cookie)
#
#    response.set_cookie('visits', visits)


# Create your views here.


def index(request):
    request.session.set_test_cookie()
    #visit = request.session.get('visits', '1')
    context_dict = {'hide' : 123}
    #print('the number of visits: {}'.format(visit))
    #context_dict = {'visits': visit} 
    visitor_cookie_handler(request)
    context_dict['visits'] = request.session['visits']
    print(request.GET)
    print(type(request.GET))
    response = render(request, 'rango/index.html', context=context_dict)
    return response

#def show_views(request, category_name_slug):
def show_views(request):

    #cate = Category.objects.get(slug=category_name_slug)
    #chose_page = Page.objects.get(category=cate)
    
    view_list = Category.objects.order_by('-likes')[:5]
    page_list = Page.objects.order_by('-views')[:5]

    context_dict = {'aha' : view_list , 'pagge':  page_list, }
    return render(request, 'rango/views.html', context = context_dict)


def about(request):
    #context_big_dict = {'my_key' : 'all about  it', 'your_name': 'go go go'}
    #return render(request, 'rango/about.html', context = context_big_dict)
    if request.session.test_cookie_worked():
        print('Test cookie worked')
        request.session.delete_test_cookie()
    print(request.method)
    print(request.user)
    return render(request, 'rango/about.html', {})

    #return HttpResponse("<h1>Rango says here is the about page.</h1> <br/> <a href='/rango'> ranggooo </a>")

def show_category(request, category_name_slug):
    context_dict = {}
    try:
        
        category = Category.objects.get(slug=category_name_slug)
	#pages type is django.db.models.query.QuerySet, every element in pages, is also a object, you can use for xunhuan
        #fangwen pages de yuansu
        pages = Page.objects.filter(category=category)
        
        context_dict['pages'] = pages
        context_dict['category'] = category
    except Category.DoesNotExist:
        context_dict['pages'] = None
        context_dict['category'] = None

    return render(request, 'rango/category.html', context_dict)
 
def add_page(request, category_name_slug):

    try:
        category = Category.objects.get(slug=category_name_slug)
    except Category.DoesNotExist:
        category = None

    form = PageForm()
    if request.method == 'POST':
        form = PageForm(request.POST)
        if form.is_valid():
            if category:
                page = form.save(commit=False)
                page.category = category
                page.views = 0
                print(page, page.category)
                page.save()
            return show_category(request, category_name_slug)
        else:
            print(form.errors)
    
    context_dict = {'form' : form, 'category': category }
    return render(request, 'rango/add_page.html', context_dict)




def add_category(request):

    form = CategoryForm()

    if request.method == 'POST':
        form = CategoryForm(request.POST)
        # is form datasource vaild ??? if condition is True, save it to database
        # if condition is False , it means error , please print it
        if form.is_valid():
            cat = form.save(commit=True)
            print(cat, cat.slug, cat.name)
            return index(request)
        else:
            print(form.errors)

    return render(request, 'rango/add_category.html', {'form': form})



