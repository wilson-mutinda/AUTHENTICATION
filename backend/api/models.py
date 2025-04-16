from django.db import models
from django.utils import timezone
from datetime import date
from django.conf import settings

from django.contrib.auth.models import PermissionsMixin, AbstractBaseUser, BaseUserManager

# Baseusermanager
class CustomUserManager(BaseUserManager):
    # function to create a custom user
    def create_user(self, email, password=None, **extra_fields):
        if not email and not password:
            raise ValueError("Both Email and Password are required!")
        
        email = self.normalize_email(email)
        extra_fields.setdefault("is_active", True)
        extra_fields.setdefault("is_admin", False)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    # create superuser
    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_active", True)
        extra_fields.setdefault("is_admin", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_staff", True)
        return self.create_user(email, password, **extra_fields)
    
# custom user model
class CustomUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=200)
    last_name = models.CharField(max_length=200)
    username = models.CharField(max_length=200, unique=True)

    is_active = models.BooleanField(default=True)
    is_superuser = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)
    is_patient = models.BooleanField(default=False)
    is_specialist = models.BooleanField(default=False)

    last_login = models.DateTimeField(null=True, blank=True)
    date_joined = models.DateTimeField(default=timezone.now)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'username']

    objects = CustomUserManager()

    def __str__(self):
        return f'{self.username} ({self.email})'
    
# Patient model
class Patient(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='patients')
    phone = models.CharField(max_length=10, unique=True)
    patient_photo = models.ImageField(upload_to='patient_photos')
    adress = models.TextField()
    date_of_birth = models.DateField()
    patient_code = models.CharField(max_length=10, unique=True)
    patient_age = models.IntegerField()

    # class method to generate a patient code
    @classmethod
    def generate_patient_code(cls):
        # get the last saved patient
        last_patient = cls.objects.order_by('-id').first()
        # if last patient, then get the code
        if last_patient and last_patient.patient_code:
            last_code = int(last_patient.patient_code.split('-')[1])
            next_code = last_code + 1
        else:
            next_code = 1
        return f'PAT-{next_code:03d}'
    
    # calucate the current age of a patient_age
    def calculate_patient_age(self):
        today = date.today()
        return today.year - self.date_of_birth.year - (
            (today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day)
        )


    def __str__(self):
        return f'{self.user.username} ({self.phone})'
    
    def save(self, *args, **kwargs):
        if not self. patient_code:
            self.patient_code = self.generate_patient_code()

        if not self.patient_age:
            self.patient_age = self.calculate_patient_age()

        super().save(*args, **kwargs)

# Specialist model
class Specialist(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='specialists')
    phone = models.CharField(max_length=10, unique=True)
    specialist_photo = models.ImageField(upload_to='specialist_photos')
    address = models.TextField()
    date_of_birth = models.DateField()
    specialist_code = models.CharField(max_length=10, unique=True)
    specialist_age = models.IntegerField()

    # class methid to generate a specialist code
    @classmethod
    def generate_specialist_code(cls):
        # get the last code of the last saved specialist
        last_specialist = cls.objects.order_by('-id').first()
        # if last specialist, then cretreive the code
        if last_specialist and last_specialist.specialist_code:
            last_code = int(last_specialist.specialist_code.split('-')[1])
            next_code = last_code + 1
        else:
            next_code = 1
        return f'SPEC-{next_code:03d}'
    
    # instance method to calculate the age of a specialist
    def calculate_specialist_age(self):
        today = date.today()
        return today.year - self.date_of_birth.year - ((today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day))

    def __str__(self):
        return f'{self.user.username} ({self.phone})'
    
    def save(self, *args, **kwargs):
        if not self.specialist_code:
            self.specialist_code = self.generate_specialist_code()

        if not self.specialist_age:
            self.specialist_age = self.calculate_specialist_age()

        super().save(*args, **kwargs)

# specialialization model
class Specialization(models.Model):
    name = models.CharField(max_length=10, unique=True)

    def __str__(self):
        return self.name
    
# Ailment model
class Ailments(models.Model):
    name = models.CharField(max_length=200, unique=True)

    def __str__(self):
        return self.name
    
# prescription model
class Prescription(models.Model):
    specialist = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='prescriptions')
    patient = models.CharField(max_length=100)
    feelings = models.TextField()
    ailments = models.CharField(max_length=200)
    prescriptions = models.TextField()

    def __str__(self):
        return f'{self.patient} ({self.prescriptions})'
    
# Report model
class Report(models.Model):
    name = models.CharField(max_length=200)
    specialist = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reports')
    patient = models.CharField(max_length=200)
    ailment = models.CharField(max_length=200)
    description = models.TextField()

    def __str__(self):
        return f'{self.name} for {self.patient}'
