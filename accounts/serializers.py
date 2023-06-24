from rest_framework import serializers
from .models import Account, Profile


class ProfileBasicsSerializer(serializers.ModelSerializer):
    region = serializers.CharField(source='get_region_iso_display')

    class Meta:
        model = Profile
        fields = ('id', 'first_name', 'middle_name', 'last_name', 'full_name', 'avatar', 'region')


class ProfileBasicsCommentSerializer(serializers.ModelSerializer):
    region = serializers.CharField(source='get_region_iso_display')

    class Meta:
        model = Profile
        fields = ('first_name', 'middle_name', 'last_name', 'full_name', 'avatar', 'region')


class AccountSerializer(serializers.ModelSerializer):
    profile = ProfileBasicsSerializer(read_only=True, source='account_profile')

    class Meta:
        model = Account
        fields = ('id', 'email', 'is_active', 'is_superuser', 'is_moderator', 'is_government', 'is_management_company',
                  'phone_number', 'is_phone_confirmed', 'profile')


class AccountWithoutProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = ('id', 'email', 'is_active', 'is_superuser', 'is_moderator', 'is_government', 'is_management_company',
                  'phone_number', 'is_phone_confirmed',)


class AccountUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = ('is_active', 'is_superuser', 'is_moderator', 'is_government', 'is_management_company')


class AccountCommentSerializer(serializers.ModelSerializer):
    profile = ProfileBasicsCommentSerializer(read_only=True, source='account_profile')

    class Meta:
        model = Account
        fields = ('is_superuser', 'is_moderator', 'is_government', 'is_management_company', 'profile')


class ProfileSerializer(serializers.ModelSerializer):
    account = AccountWithoutProfileSerializer(read_only=True)

    class Meta:
        model = Profile
        fields = '__all__'


class ProfileShortSerializer(serializers.ModelSerializer):
    region = serializers.CharField(source='get_region_iso_display')

    class Meta:
        model = Profile
        fields = ('id', 'first_name', 'middle_name', 'last_name', 'full_name', 'avatar', 'region_iso', 'region')


class AccountShortSerializer(serializers.ModelSerializer):
    profile = ProfileShortSerializer(read_only=True, source='account_profile')

    class Meta:
        model = Account
        fields = ('id', 'profile')
