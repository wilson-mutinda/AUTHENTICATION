from rest_framework import serializers
import re
from django.core.validators import RegexValidator
from datetime import date
from django.contrib.auth.hashers import make_password

from .models import CustomUser, Patient, Specialist, Specialization, Ailments, Report, Prescription

# ailment serializer
class AilmentSerializer(serializers.ModelSerializer):

    name = serializers.CharField()
    class Meta:
        model = Ailments
        fields = ['id', 'name']

    def validate_name(self, ailment_name):
        expected_name = ['cardiovascular', 'neurological', 'respiratory', 'orthopedic', 'mental']
        # convert to lower case
        lowercased_name = ailment_name.lower()

        if lowercased_name not in expected_name:
            raise serializers.ValidationError({'name': f'Invalid Disease! Please select from either of: {', '.join(expected_name)}'})
        return ailment_name
    
    def create(self, validated_data):
        # check if name already exists
        name = validated_data.get('name')
        if Ailments.objects.filter(name=name).exists():
            raise serializers.ValidationError({'name': f'Type ({name}) Already Exists!'})
        validated_data['name'] = validated_data['name'].title()
        return super().create(validated_data)

# Specialization serializer
class SpecializationSerializer(serializers.ModelSerializer):

    name = serializers.CharField()

    class Meta:
        model = Specialization
        fields = ['id', 'name']

    def validate_name(self, specialization_name):
        expected_names = ['nurse', 'dentist', 'doctor']

        normalized_name = specialization_name.lower()
        if normalized_name not in expected_names:
            raise serializers.ValidationError({'name': f'Name not expected. Please use one of {', '.join(expected_names)}'})
        return specialization_name.title()
    
    def create(self, validated_data):
        name = validated_data['name']
        if Specialization.objects.filter(name=name).exists():
            raise serializers.ValidationError({'name': f'{name} Already Exists!'})
        validated_data['name'] = validated_data.pop('name').title()
        return super().create(validated_data)
    
    def update(self, instance, validated_data):
        if 'name' in validated_data:
            validated_data['name'] = validated_data['name'].title()
        return super().update(instance, validated_data)
    
# Custom user serializer
class CustomUserSerializer(serializers.ModelSerializer):

    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)
    class Meta:
        model = CustomUser
        fields = ['id', 'first_name', 'last_name', 'username', 'email', 'password', 'confirm_password']

    # validate both password and confirm password
    def validate(self, data):
        password = data.get('password')
        confirm_password = data.get('confirm_password')

        if password and confirm_password and password != confirm_password:
            raise serializers.ValidationError({'confirm_password': 'Password Mismatch!'})
        
        if len(password) < 8:
            raise serializers.ValidationError({'password': 'Password should have at least 8 characters!'})
        
        if not re.search(r'\d', password) or not re.search(r'[A-Za-z]', password):
            raise serializers.ValidationError({'password': 'Password should have both letters and digits!'})
        
        return data
    
    def create(self, validated_data):
        validated_data.pop('confirm_password')
        validated_data['is_active'] = True
        validated_data['password'] = make_password(validated_data['password'])
        validated_data['first_name'] = validated_data['first_name'].title()
        validated_data['last_name'] = validated_data['last_name'].title()
        return super().create(validated_data)
    
# Patient serializer
class PatientSerializer(serializers.ModelSerializer):

    user = CustomUserSerializer()
    phone = serializers.CharField(
        validators = [
            RegexValidator(regex=r'^(01|07)\d{8}$', message='Invalid Phone Number!')
        ]
    )
    patient_photo = serializers.ImageField()
    adress = serializers.CharField()
    date_of_birth = serializers.DateField(format='%Y-%M-%d')
    patient_code = serializers.CharField(read_only=True)
    patient_age = serializers.IntegerField(read_only=True)

    class Meta:
        model = Patient
        fields = ['id', 'user', 'phone', 'patient_photo', 'adress', 'date_of_birth', 'patient_code', 'patient_age']

    # validate phone number
    def validate_phone(self, phone):
        if len(phone) != 10:
            raise serializers.ValidationError('Invalid Phone Number!')
        
        if not (phone.startswith('01') or phone.startswith('07')):
            raise serializers.ValidationError('Invalid Phone Number!')
        
        return phone
    
    # validate date of birth
    def validate_date_of_birth(self, dates):
        today = date.today()

        if dates >= today:
            raise serializers.ValidationError('Invalid Date of birth!')
        return dates
    
    def create(self, validated_data):
        # user info
        user_info = validated_data.pop('user')
        user_info.pop('confirm_password')

        # check if phone number already exists
        user_phone = validated_data.pop('phone')

        if Patient.objects.filter(phone=user_phone).exists():
            raise serializers.ValidationError({'phone': 'Phone already exists!'})
        

        # create custom user
        user = CustomUser.objects.create_user(**user_info)
        user.is_patient = True
        user.save()

        # create patient
        patient = Patient.objects.create(user=user, **validated_data)
        return patient
    
# Specialization serializer
class SpecialistSerializer(serializers.ModelSerializer):

    user = CustomUserSerializer()
    phone = serializers.CharField(
        validators = [
            RegexValidator(regex=r'^(01|07)\d{8}$', message='Invalid Phone Number!')
        ]
    )
    specialist_photo = serializers.ImageField()
    address = serializers.CharField()
    date_of_birth = serializers.DateField(format="%Y-%M-%d")
    specialist_code = serializers.CharField(read_only=True)
    specialist_age = serializers.IntegerField(read_only=True)

    class Meta:
        model = Specialist
        fields = ['id', 'user', 'phone', 'specialist_photo', 'address', 'date_of_birth', 'specialist_code', 'specialist_age']

    # validate phone number
    def validate_phone_number(self, phone):
        if len(phone) != 10:
            raise serializers.ValidationError('Invalid Phone Number!')
        
        if not (phone.startswith('01') or phone.startswith('07')):
            raise serializers.ValidationError('Invalid Phone Number!')
        
        return phone
    
    # validate date_of_birth
    def validate_date_of_birth(self, dates):
        today = date.today()
        if dates >= today:
            raise serializers.ValidationError('Invalid Date Of Birth!')
        
        return dates
    
    def create(self, validated_data):

        # user info
        user_info = validated_data.pop('user')
        user_info.pop('confirm_password')

        # ensure user info is valid
        specialist_phone = validated_data.pop('phone')
        if Specialist.objects.filter(phone=specialist_phone).exists():
            raise serializers.ValidationError({'phone': 'Phone Already Exists!'})
        validated_data['phone'] = specialist_phone

        # create user
        user = CustomUser.objects.create_user(**user_info)
        user.is_specialist = True
        user.save()

        # create specialist
        specialist = Specialist.objects.create(user=user, **validated_data)
        return specialist

# Report serializer
class ReportSerializer(serializers.ModelSerializer):

    name = serializers.CharField()
    specialist = serializers.CharField(source='specialist.specialists.specialist_code', read_only=True)
    patient = serializers.CharField()
    ailment = serializers.CharField()
    description = serializers.CharField()

    class Meta:
        model = Report
        fields = ['id', 'name', 'specialist', 'patient', 'ailment', 'description']

    # validate ailment
    def validate_ailment(self, name):
        expected_ailments = ['cardiovascular', 'neurological', 'respiratory', 'orthopaedic', 'mental']
        lower_cased_names = name.lower()

        if lower_cased_names not in expected_ailments:
            raise serializers.ValidationError({'ailment': f'Invalid Ailment.Please use either of: {', '.join(expected_ailments)}'})
        return name
    
    # validate patient code
    def validate_patient(self, code):
        pattern = r'^PAT-\d+$'
        if not re.match(pattern, code):
            raise serializers.ValidationError({'patient': 'Invalid Patient Code! Expected Format: PAT-<number>'})
        return code
    
    def create(self, validated_data):
        # Assign the specialist from the request
        validated_data['specialist'] = self.context['request'].user

        # Validate that the patient code exists, but keep the code as string
        patient_code = validated_data['patient']
        if not Patient.objects.filter(patient_code=patient_code).exists():
            raise serializers.ValidationError({'patient': 'Patient does not exist!'})
        # Keep patient_code as-is

        # Validate that the ailment exists, but keep it as a string
        ailment_name = validated_data['ailment'].lower()
        if not Ailments.objects.filter(name__iexact=ailment_name).exists():
            raise serializers.ValidationError({'ailment': 'Ailment does not exist!'})
        
        validated_data['ailment'] = ailment_name.title()

        return super().create(validated_data)
    
# Prescription serializer
class PrescriptionSeriaizer(serializers.ModelSerializer):

    specialist = serializers.CharField(source='specialist.specialists.specialist_code', read_only=True)
    patient = serializers.CharField()
    feelings = serializers.CharField()
    ailments = serializers.CharField()
    prescriptions = serializers.CharField()

    class Meta:
        model = Prescription
        fields = ['id', 'specialist', 'patient', 'feelings', 'ailments', 'prescriptions']

    # validate patient code
    def validate_patient(self, code):
        pattern = r'^PAT-\d+$'
        if not re.match(pattern, code):
            raise serializers.ValidationError({'patient': f'Invalid Format.Please use the format PAT-<number>'})
        
        return code
    
    # validate ailments
    def validate_ailments(self, name):
        expected_ailments = ['cardiovascular', 'neurological', 'respiratory', 'orthopedic', 'mental']
        lowercased_names = name.lower()

        if lowercased_names not in expected_ailments:
            raise serializers.ValidationError({'ailments': f'Unexpected Ailment.Please use either of {', '.join(expected_ailments)}'})
        return name.title()
    
    def create(self, validated_data):

        # get the specialist automatically
        validated_data['specialist'] = self.context['request'].user

        # Patient
        patient = validated_data['patient']
        if not Patient.objects.filter(patient_code = patient).exists():
            raise serializers.ValidationError({'patient': 'Patient Does not Exist.'})
        
        # ailments
        ailment_name = validated_data['ailments'].lower()
        if not Ailments.objects.filter(name__iexact=ailment_name).exists():
            raise serializers.ValidationError({'ailment': 'Ailment does not exist!'})
        
        validated_data['ailments'] = ailment_name.title()
        
        return super().create(validated_data)

