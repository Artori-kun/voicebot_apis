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

from ..models.models import user_feature
from ..serializers.serializers import User_featureSerializer

from rest_framework.decorators import api_view
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
import kwargs as kwargs
import sounddevice as sd
from scipy.io.wavfile import write
import wavio as wv
import numpy as np
from core.voice_utils import extra_feature
from core.voice_utils import compare_similarity, compare_feautures
from mysql.connector import MySQLConnection, Error
import time
import torch
import wave
import numpy as np
from core.record import check_user, record_log_in, record_signup, _login


# signup
@api_view(['POST'])
def registration_view(request):
    if request.method == 'POST':
        user_data = JSONParser().parse(request)
        user_serializer = User_featureSerializer(data=user_data)
        if user_serializer.is_valid():
            user_serializer.save()
            username = user_serializer.data['username']
            vector = user_serializer.data['vector']
            record_signup(username, vector)
            return JsonResponse(user_serializer.data, status=status.HTTP_201_CREATED)
        return JsonResponse(user_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Login
@api_view(['GET'])
def login(request):
    result = record_log_in()
    request.method = 'GET'
    user = user_feature.objects.filter(username=result)
    user_serializer = User_featureSerializer(user, many=True)
    return JsonResponse(user_serializer.data, safe=False)

@api_view(['GET'])
def login2(request, file_name):
    resule = _login(file_name)
    request.method = 'GET'
    user = user_feature.objects.filter(username = result)
    user_serializer = User_featureSerializer(user, many=True)
    return JsonResponse(user_serializer.data, safe=False)

@api_view(['GET', 'POST', 'DELETE'])
def tutorial_list(request):
    if request.method == 'GET':
        tutorials = user_feature.objects.all()

        username = request.GET.get('username', None)
        if username is not None:
            tutorials = tutorials.filter(title__icontains=username)

        tutorials_serializer = User_featureSerializer(tutorials, many=True)
        return JsonResponse(tutorials_serializer.data, safe=False)
        # 'safe=False' for objects serialization

    elif request.method == 'POST':
        tutorial_data = JSONParser().parse(request)
        tutorial_serializer = User_featureSerializer(data=tutorial_data)
        if tutorial_serializer.is_valid():
            tutorial_serializer.save()
            return JsonResponse(tutorial_serializer.data, status=status.HTTP_201_CREATED)
        return JsonResponse(tutorial_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        count = user_feature.objects.all().delete()
        return JsonResponse({'message': '{} User were deleted successfully!'.format(count[0])},
                            status=status.HTTP_204_NO_CONTENT)


@api_view(['GET', 'PUT', 'DELETE'])
def tutorial_detail(request, pk):
    try:
        tutorial = user_feature.objects.get(pk=pk)
    except user_feature.DoesNotExist:
        return JsonResponse({'message': 'The User does not exist'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        tutorial_serializer = User_featureSerializer(tutorial)
        return JsonResponse(tutorial_serializer.data)

    elif request.method == 'PUT':
        tutorial_data = JSONParser().parse(request)
        tutorial_serializer = User_featureSerializer(tutorial, data=tutorial_data)
        if tutorial_serializer.is_valid():
            tutorial_serializer.save()
            return JsonResponse(tutorial_serializer.data)
        return JsonResponse(tutorial_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        tutorial.delete()
        return JsonResponse({'message': 'User was deleted successfully!'}, status=status.HTTP_204_NO_CONTENT)





