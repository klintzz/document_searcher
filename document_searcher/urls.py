from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

from haystack.forms import SearchForm
from haystack.views import SearchView

from doc_search.views import ProtectedSearchView

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'document_searcher.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
    url(r'^login/$', 'django.contrib.auth.views.login'),
    # url(r'^search/', include('haystack.urls')),
    url(r'^$', ProtectedSearchView(template='search/search.html', form_class=SearchForm), name='haystack_search'),
)
