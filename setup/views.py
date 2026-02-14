from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages

# ======================
# DASHBOARD SETUP
# ======================

@login_required
def setup_dashboard(request):
    return render(request, 'setup/dashboard.html')


# ======================
# LIST USER
# ======================

@login_required
def user_list(request):
    users = User.objects.all().order_by('username')
    return render(request, 'setup/user_list.html', {
        'users': users
    })


# ======================
# TAMBAH USER
# ======================

@login_required
def user_add(request):

    if request.method == "POST":

        username = request.POST['username']
        password = request.POST['password']
        email = request.POST.get('email')

        User.objects.create_user(
            username=username,
            password=password,
            email=email
        )

        messages.success(request, "User berhasil ditambahkan")

        return redirect('user_list')

    return render(request, 'setup/user_form.html')


# ======================
# EDIT USER
# ======================

@login_required
def user_edit(request, id):

    user = get_object_or_404(User, id=id)

    if request.method == "POST":

        user.username = request.POST['username']
        user.email = request.POST.get('email')

        password = request.POST.get('password')

        if password:
            user.set_password(password)

        user.save()

        messages.success(request, "User berhasil diupdate")

        return redirect('user_list')

    return render(request, 'setup/user_form.html', {
        'user_edit': user
    })


# ======================
# DELETE USER
# ======================

@login_required
def user_delete(request, id):

    user = get_object_or_404(User, id=id)
    user.delete()

    messages.success(request, "User berhasil dihapus")

    return redirect('user_list')
