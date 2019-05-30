from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from tethys_sdk.gizmos import Button

@login_required()
def home(request):
    """
    Controller for the app home page.
    """
   

    context = {

    }

    return render(request, 'glo_vli/home.html', context)