from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.hashers import make_password
from django.shortcuts import render

from django.http.response import JsonResponse
from rest_framework.mixins import CreateModelMixin
from rest_framework.parsers import JSONParser
from rest_framework import status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import GenericAPIView, CreateAPIView
from rest_framework.viewsets import GenericViewSet

from ..models.models import CustomUser
from ..serializers.serializers import CustomUserSerializer

from rest_framework.decorators import api_view
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
import kwargs as kwargs
import sounddevice as sd
from scipy.io.wavfile import write
import wavio as wv
import numpy as np
from mysql.connector import MySQLConnection, Error
import time
import torch
import wave
import numpy as np
from django_apis.core.record import check_user, record_log_in, record_signup, _login

# Login
@api_view(['POST'])
def login2(request):
    audio = request.FILES['wav']

    fs = FileSystemStorage(location="data")
    filename = fs.save(audio.name, audio)

    result = _login(f"data/{audio.name}")
    try:
        tutorial = CustomUser.objects.get(id=result)
        tutorial_serializer = CustomUserSerializer(tutorial)
        return Response(tutorial_serializer.data, status.HTTP_200_OK)
    except CustomUser.DoesNotExist:
        return Response({'message': 'The User does not exist'}, status=status.HTTP_204_NO_CONTENT)


@api_view(['GET', 'POST', 'DELETE'])
def tutorial_list(request):
    if request.method == 'GET':
        tutorials = CustomUser.objects.all()

        username = request.GET.get('username', None)
        if username is not None:
            tutorials = tutorials.filter(title__icontains=username)

        tutorials_serializer = CustomUserSerializer(tutorials, many=True)
        return JsonResponse(tutorials_serializer.data, safe=False)
        # 'safe=False' for objects serialization

    elif request.method == 'POST':
        tutorial_data = JSONParser().parse(request)
        tutorial_serializer = CustomUserSerializer(data=tutorial_data)
        if tutorial_serializer.is_valid():
            tutorial_serializer.save()
            return JsonResponse(tutorial_serializer.data, status=status.HTTP_201_CREATED)
        return JsonResponse(tutorial_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        count = CustomUser.objects.all().delete()
        return JsonResponse({'message': '{} User were deleted successfully!'.format(count[0])},
                            status=status.HTTP_204_NO_CONTENT)


@api_view(['GET', 'PUT', 'DELETE'])
def tutorial_detail(request, pk):
    try:
        tutorial = CustomUser.objects.get(pk=pk)
    except user_feature.DoesNotExist:
        return JsonResponse({'message': 'The User does not exist'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        tutorial_serializer = CustomUserSerializer(tutorial)
        return JsonResponse(tutorial_serializer.data)

    elif request.method == 'PUT':
        tutorial_data = JSONParser().parse(request)
        tutorial_serializer = CustomUserSerializer(tutorial, data=tutorial_data)
        if tutorial_serializer.is_valid():
            tutorial_serializer.save()
            return JsonResponse(tutorial_serializer.data)
        return JsonResponse(tutorial_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        tutorial.delete()
        return JsonResponse({'message': 'User was deleted successfully!'}, status=status.HTTP_204_NO_CONTENT)


# Create your views here.
def index(request):
    # if 'id' in request.session.keys():
    #     return redirect('/success')
    # else:
    #     return render(request, 'login_register_app/index.html')
    return render(request, 'login_register_app/index.html')


def register(request):
    if request.method == "POST":
        firstname = request.POST['firstname']
        lastname = request.POST['lastname']
        dob = request.POST['dob']
        gender = request.POST['gender']
        email = request.POST['email']
        user = CustomUser.objects.create(firstname = request.POST['firstname'],lastname = request.POST['lastname'],dob = request.POST['dob'],gender = request.POST['gender'],email = request.POST['email'])
        record_signup(firstname, lastname, dob, gender, email)
        request.session['id'] = user.id
        return redirect("/success")
    else:
        return redirect("/")


def login(request):
    # user = CustomUser.objects.get(pk=id)
    if request.method == "POST":
        errors = CustomUser.objects.login_validator(request.POST)
        if len(errors):
            for key, value in errors.items():
                messages.add_message(request, messages.ERROR, value, extra_tags='login')
            return redirect('/')
        else:
            user = CustomUser.objects.get(username=request.POST['username'])
            request.session['id'] = user.id
            return redirect("/wall")


def wall(request):
    if 'id' not in request.session:
        return redirect('/')
    else:
        context = {
            "user": CustomUser.objects.get(id=request.session['id'])
        }
        return render(request, 'login_register_app/dash.html', context)


def success(request):
    if 'id' not in request.session:
        return redirect('/')
    else:
        context = {
            "user": CustomUser.objects.get(id=request.session['id'])
        }
        return render(request, 'login_register_app/success.html', context)


def reset(request):
    # user = CustomUser.objects.get(pk=id)
    if 'id' not in request.session:
        return redirect('/')
    else:
        request.session.clear()
        print("session has been cleared")
        return redirect("/")
