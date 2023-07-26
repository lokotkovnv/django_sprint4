from django.shortcuts import render
from django.views.generic import TemplateView


def handler404(request, exception):
    return render(request, 'pages/404.html', status=404)


def handler403(request, exception):
    return render(request, 'pages/403csrf.html', status=403)


def handler500(request, exception):
    return render(request, 'pages/500.html', status=500)


class About(TemplateView):
    template_name = 'pages/about.html'


class Rules(TemplateView):
    template_name = 'pages/rules.html'
