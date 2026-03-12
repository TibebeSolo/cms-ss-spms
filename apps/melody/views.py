from django.shortcuts import render

def mezemran_list(request):
    return render(request, 'melody/mezemran_list.html')

def mezemran_roster(request):
    return render(request, 'melody/mezemran_roster.html')