from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.validators import validate_email

User = get_user_model()

class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(required=True, write_only = True, validators=[validate_password])
    password2 = serializers.CharField(required=True, write_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'password','password2' , 'email']
        #extra_kwargs = {'password':{'write_only':True}}
    
    def validate(self, attrs):
        # Check if username already exists
        if User.objects.filter(username=attrs['username']).exists():
            raise serializers.ValidationError({"username": "A user with that username already exists."})

        # Check if email already exists
        if User.objects.filter(email=attrs['email']).exists():
            raise serializers.ValidationError({"email": "A user with that email already exists."})

        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError('passwords do not match!')
        return attrs
    
    def create(self, validated_data):
        validated_data.pop('password2')
        user = User.objects.create_user(**validated_data)

        return user
    
class UserLoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)



class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ['username', 'email', 'first_name', 'last_name'] 
        extra_kwargs = {'email': {'required': True},}