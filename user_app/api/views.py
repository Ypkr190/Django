from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
# from rest_framework_simplejwt.tokens import RefreshToken

from rest_framework import status

from user_app.api.serializers import RegistrationSerializer

from user_app import models

# from django.core.mail import send_mail
# from watchmate.settings import EMAIL_HOST_USER

@api_view(['POST',])
def logout_view(request):
    
    if request.method == 'POST':
        request.user.auth_token.delete()
        return Response(status=status.HTTP_200_OK)


@api_view(['POST',])
def registration_view(request):
    
    if request.method == 'POST':
        serializer = RegistrationSerializer(data=request.data)
        
        data = {}
        
        if serializer.is_valid():
            account = serializer.save()
            
            data['respone'] = 'Registration Successful!'
            data['username'] = account.username
            data['email'] = account.email
            
            
            token = Token.objects.get(user=account).key
            
            data['token'] = token
            
            # changed
            # Email Notification after registration
            """"
            subject = "Thanking for registration to our application"
            message = "Dear Customer" + ' ' + data['username'] + " Succesfully Registored"
            email = data['email']
            recipient_list = [email]
            
            send_mail(subject,message,EMAIL_HOST_USER,recipient_list,fail_silently=True)
            """
            
            # refresh = RefreshToken.for_user(account)
            # data['token'] = {
            #     'refresh': str(refresh),
            #     'access': str(refresh.access_token),
            # }
        else:
            data = serializer.errors
            
        return Response(data,status=status.HTTP_201_CREATED)

