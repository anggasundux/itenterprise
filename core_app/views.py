from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect

def login_view(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None:
            login(request, user)

            next_url = request.GET.get('next')
            if next_url:
                return redirect(next_url)
            else:
                return redirect('/dashboard/')
        else:
            return render(request, 'auth/login.html', {
                'error': 'Username atau password salah'
            })

    return render(request, 'auth/login.html')
