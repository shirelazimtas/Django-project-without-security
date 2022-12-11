from django.db import connection
from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import UserRegisterForm, ResetPasswordEnterToken, UserUpdateForm, ProfileUpdateForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm, PasswordResetForm, AuthenticationForm
# from django.contrib.auth.models import User
from django.contrib.auth import get_user_model, authenticate, login

User = get_user_model()
from django.contrib.auth.hashers import make_password, check_password
import datetime


# unprotected register method
def register(request):
    if request.method == "POST":
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            # Insert Trough ORM the right way:
            # form.save()
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password1")
            encrypted = make_password(password)
            email = form.cleaned_data.get("email")
            # # Direct SQL Queries - the wrong way
            cursor = connection.cursor()
            query = "INSERT INTO users_customusers (is_active, is_superuser, is_staff, username, password, " \
                    "first_name, last_name, date_joined, email) VALUES ('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s')" \
                    % (1, 0, 0, username, encrypted, 'fn', 'ln', datetime.datetime.now(), email)
            cursor.execute(query)
            cursor.close()
            messages.success(request, f'Account {username} Created! Please Sign In')
            return redirect('signin')

    else:
        form = UserRegisterForm()
    return render(request, 'users/register.html', {'form': form})

# protected register method
# def register(request):
#     if request.method == "POST":
#         form = UserRegisterForm(request.POST)
#         if form.is_valid():
#             form.save()
#             username = form.cleaned_data.get("username")
#             messages.success(request, f'Account {username} Created! Please Sign In')
#             return redirect('signin')
#
#     else:
#         form = UserRegisterForm()
#     return render(request, 'users/register.html', {'form': form})


#unprotected signin method
def signin(request):
    if request.method == "POST":
        form = AuthenticationForm(request, request.POST)
        username = form.data.get("username")
        password = form.data.get("password")
        # # Direct SQL Queries - the wrong way
        query = f'SELECT * FROM auth_user WHERE username=="{username}"'
        print(query)
        cursor = connection.cursor()
        result = cursor.execute(query)
        # xxx = User.objects.raw(query)
        if result:
            for single_user in result:
                if check_password(password, single_user[1]):
                    user = authenticate(request, username=username, password=password)
                    if user is not None:
                        login(request, user)
                        print("password match and user autnitcated --> redirect and preform login")
                    return redirect('project-home')
                else:
                    print("wrong password")
                    messages.error(request, f'wrong password')
        else:
            print("wrong username")
            messages.error(request, f'wrong username')
        cursor.close()
    else:
        form = AuthenticationForm()

    return render(request, 'users/login.html', {'form': form})


# protected signin method
# def signin(request):
#     if request.method == "POST":
#         form = AuthenticationForm(request, request.POST)
#         if form.is_valid():
#             user = authenticate(request, username=form.cleaned_data.get('username'),
#                                 password=form.cleaned_data.get('password'))
#             if user is not None:
#                 login(request, user)
#                 return redirect('customers-home-page')
#     else:
#         form = AuthenticationForm()
#     return render(request, 'users/signin.html', {'form': form})


@login_required
def change_password(request):
    if request.method == "POST":
        change_password_form = PasswordChangeForm(user=request.user, data=request.POST)
        if change_password_form.is_valid():
            change_password_form.save()
            messages.success(request, f'Password successfully changed for user {change_password_form.user.username}!')
            return redirect('project-home')

    else:
        change_password_form = PasswordChangeForm(User)
    return render(request, "users/change_password.html", {'form': change_password_form})


def reset_password(request):
    if request.method == "POST":
        reset_password_form = PasswordResetForm(request.POST)
        if reset_password_form.is_valid():
            reset_password_form.save(request=request, email_template_name='users/email_rest_password.html')
            email = reset_password_form.cleaned_data.get("email")
            messages.success(request, f'If the email: {email} exist in our records, '
                                      f'we will send a instruction to reset password!')
            return redirect('project-home')

    else:
        reset_password_form = PasswordResetForm()
    return render(request, "users/change_password.html", {'form': reset_password_form, "button": "Send Reset Email"})


def password_reset_enter_token(request, uidb64):
    check_token = ResetPasswordEnterToken()
    if request.method == "POST":
        check_token = ResetPasswordEnterToken(request.POST)
        if check_token.is_valid():
            token = check_token.cleaned_data.get("verification_code")
            return redirect('reset-password-confirm', uidb64=uidb64, token=token)

    return render(request, "users/change_password.html", {'form': check_token, "button": "Process"})


def password_reset_complete(request):
    messages.success(request, f'Password Reset Done, Please Sign In')
    return redirect('signin')

@login_required
def profile(request):
    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(request.POST,
                                   request.FILES,
                                   instance=request.user.profile)
        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, f'Your account has been updated!')
            return redirect('profile')

    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=request.user.profile)

    context = {
        'u_form': u_form,
        'p_form': p_form
    }