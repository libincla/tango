#!/Data/apps/ENV3/bin/python
#coding:utf-8

import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tango_with_django_project.settings')

import django
django.setup()

from rango.models import Category, Page

def populate():

    python_pages = [{"title": "Official Python Tutorial", "url":"http://docs.python.org/2/tutorial/"}, {"title":"How to Think like a Computer Scientist", "url":"http://www.greenteapress.com/thinkpython/"}, {"title":"Learn Python in 10 Minutes", "url":"http://www.korokithakis.net/tutorials/python/"} ]
    django_pages = [{"title":"Official Django Tutorial", "url":"https://docs.djangoproject.com/en/1.9/intro/tutorial01/"}, {"title":"Django Rocks", "url":"http://www.djangorocks.com/"}, {"title":"How to Tango with Django", "url":"http://www.tangowithdjango.com/"}]
    other_pages = [{"title":"Bottle", "url":"http://bottlepy.org/docs/dev/"}, {"title":"Flask", "url":"http://flask.pocoo.org"}]

    python_cat = [{"views" : 128,  "likes" : 64}]
    django_cat = [{"views": 64, "likes": 32 }] 
    other_cat = [{"views": 32, "likes" : 16}]   

    cats = {"Python": {"pages": python_pages },"Django": {"pages": django_pages}, "Other Frameworks": {"pages": other_pages}}
    cats1 = {"Python" : {"haha_cat": python_cat }, "Django" : {"haha_cat": django_cat}, "Other Frameworks" : {"haha_cat": other_cat }}

   
    #for cat, cat_data in cats.items():
    #    c = add_cat(cat)
    #    for p in cat_data["pages"]:
    #        add_page(c, p["title"], p["url"])
  
    for exa, exa1 in cats1.items():
        for a in exa1["haha_cat"]:
            add_cat(exa, a["views"], a["likes"])
        

    #打印添加的分类
    for c in Category.objects.all():
        for p in Page.objects.filter(category=c):
            print("- {0} - {1}".format(str(c), str(p)))


def add_page(cat, title, url, views=0):
    p = Page.objects.get_or_create(category=cat, title=title)[0]
    p.url = url
    p.views = views
    p.save()
    print(p)
    return p


#def add_cate(views, likes):
#    ca = Category.objects.get_or_create(views=views, likes=likes)[0]
#    ca.views = views
#    ca.likes = likes
#    ca.save()
#    return ca

def add_cat(name, views, likes):
    c = Category.objects.get_or_create(name=name)[0]
    c.views = views
    c.likes = likes
    c.save()
    return c


if __name__ == '__main__':
    print("starting rango script....")
    populate()


