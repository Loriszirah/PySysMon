#-*- coding: utf-8 -*-
from django.shortcuts import render
from django.http import HttpResponse


def home(request):
    """ Trigger de la page d'accueil """

    return render(request, 'base.html')
