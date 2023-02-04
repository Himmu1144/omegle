from django.shortcuts import render

# Create your views here.
def home(request):
    return render(request, 'home.html')

def new_chat_view(request):
    return render(request, 'new_chat.html')