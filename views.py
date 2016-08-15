from django.views import generic
import models
# Create your views here.


class DashboardView(generic.ListView):
    model = models.TVHServer

    def get_queryset(self):
        return super(DashboardView, self).get_queryset().filter(owner=self.request.user)

