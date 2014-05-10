# Create your views here.

from haystack.views import SearchView
from django.shortcuts import redirect

class ProtectedSearchView(SearchView):

    def __call__(self, request):
        if not request.user.is_authenticated():
            return redirect('/login/?next=%s' % request.path)
        return super(ProtectedSearchView, self).__call__(request)
