from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from .models import Patient, Specialist, Specialization, CustomUser, Ailments, Report, Prescription
from .serializers import PatientSerializer, SpecializationSerializer, SpecialistSerializer, CustomUserSerializer, AilmentSerializer, ReportSerializer, PrescriptionSeriaizer

from rest_framework import status, permissions, response
from rest_framework.decorators import api_view, permission_classes
from rest_framework_simplejwt.tokens import RefreshToken

# function to create a custom user
@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def create_custom_user_view(request):
    serializer = CustomUserSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return response.Response({'message': 'Custom user created successfully!'}, status=status.HTTP_201_CREATED)
    return response.Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# create an admin
@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def create_admin_user_view(request):
    serializer = CustomUserSerializer(data=request.data)
    if serializer.is_valid():
        # create the user first
        user = CustomUser.objects.create_user(
            email = serializer.validated_data['email'],
            username = serializer.validated_data['username'].title(),
            first_name = serializer.validated_data['first_name'].title(),
            last_name = serializer.validated_data['last_name'].title(),
            password = serializer.validated_data['password'],
            is_admin = True,
            is_staff = True,
            is_superuser = True,
            is_active = True
        )
        return response.Response({'message': 'Admin user Created succeffully!'}, status=status.HTTP_201_CREATED)
    return response.Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# function to give a token
@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def user_login_view(request):
    # take an already registered email and password
    email = request.data.get('email')
    password = request.data.get('password')

    try:
        user = CustomUser.objects.get(email=email)

        if user.check_password(password):

            refresh_token = RefreshToken.for_user(user)
            access_token = refresh_token.access_token

            return response.Response({
                'message': 'Login Successful!',
                'access': str(access_token),
                'refresh': str(refresh_token),
                'user_id': user.id,
                'user_email': user.email,
                'is_admin': user.is_admin,
                'is_specialist': user.is_specialist,
                'is_patient': user.is_patient,
                'is_superuser': user.is_superuser
            }, status=status.HTTP_200_OK)
        else:
            return response.Response({'password': 'Incorrect Password!'}, status= status.HTTP_400_BAD_REQUEST)
    except CustomUser.DoesNotExist:
        return response.Response({'email': 'Email does not exist!'}, status=status.HTTP_204_NO_CONTENT)
    
# class to create an admin so as to have their priviledges
class IsAdmin(permissions.BasePermission):

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_admin
    
# function to create a apecialization by an authorized admin
@api_view(['POST'])
@permission_classes([IsAdmin])
def create_specialization_view(request):
    serializer = SpecializationSerializer(data=request.data)
    if serializer.is_valid():
        name = serializer.validated_data['name']
        serializer.save()
        return response.Response({'message': f'Specialization "{name} "Created!'}, status=status.HTTP_201_CREATED)
    return response.Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def create_patient_view(request):
    serializer = PatientSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return response.Response({'message': 'Patient Created Successfully!'}, status=status.HTTP_201_CREATED)
    return response.Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# function to create a specialist
@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def create_specialist_view(request):
    serializer = SpecialistSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return response.Response({'message': 'Specialist Created!'}, status=status.HTTP_201_CREATED)
    return response.Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# function to ensure an authorized admin can create ailments
@api_view(['POST'])
@permission_classes([IsAdmin])
def create_ailment_view(request):
    serializer = AilmentSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return response.Response({'message': 'Ailment Created!'}, status=status.HTTP_201_CREATED)
    return response.Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Specialist class
class IsSpecialist(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_specialist
    
# function to ensure that an authenticated specialist can create a report
@api_view(['POST'])
@permission_classes([IsSpecialist])
def create_report_view(request):
    serializer = ReportSerializer(data=request.data, context={'request': request})
    if serializer.is_valid():
        serializer.save()
        return response.Response({'message': 'Report Created Successfully!'}, status=status.HTTP_201_CREATED)
    return response.Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([IsSpecialist])
def create_prescription_view(request):
    serializer = PrescriptionSeriaizer(data=request.data, context={'request': request})
    if serializer.is_valid():
        serializer.save()
        return response.Response({'message': 'Prescription created!'}, status=status.HTTP_201_CREATED)
    return response.Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
