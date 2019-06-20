from django.shortcuts import render
from django.contrib.auth.decorators import login_required, user_passes_test
from tethys_sdk.gizmos import Button, MVDraw, MapView
from .utils import add_points, user_permission_test


def home(request):
    """
    Controller for the app home page.
    """

    # add_points()

    context = {

    }

    return render(request, 'glo_vli/home.html', context)

@user_passes_test(user_permission_test)
def add_point(request):

    context = {

    }

    return render(request, 'glo_vli/add_point.html', context)