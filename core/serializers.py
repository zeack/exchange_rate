import uuid
import logging
from datetime import datetime, timedelta

from django.contrib.auth import get_user_model
from django.conf import settings
from django.utils import timezone
from django.utils.timezone import utc

from rest_framework import serializers

from core.models import ApiKey

logger = logging.getLogger(__name__)
User = get_user_model()


class UUIDSerializer(serializers.Serializer):
    api_key = serializers.UUIDField(format='hex_verbose')


class ApiKeySerializer(serializers.ModelSerializer):
    class Meta:
        model = ApiKey
        fields = ['id', 'user_id', 'name', 'api_key']
        read_only_fields = ['api_key']

    def create(self, validated_data):
        user = self.context['request'].user
        validated_data['api_key'] = uuid.uuid4()
        validated_data['user_id'] = user.pk
        return ApiKey.objects.create(**validated_data)


class UserSerializer(serializers.HyperlinkedModelSerializer):
    password = serializers.CharField(
        required=True, write_only=True, style={'input_type': 'password'}
    )
    percentage_usage = serializers.SerializerMethodField()
    keys = ApiKeySerializer(many=True, read_only=True)

    class Meta:
        model = User
        fields = [
            'email',
            'first_name',
            'last_name',
            'is_active',
            'username',
            'email',
            'password',
            'usage_end_date',
            'percentage_usage',
            'keys',
        ]
        read_only_fields = [
            'uuid',
            'is_active',
            'usage_end_date',
        ]

    def get_percentage_usage(self, obj):
        today = timezone.now().date()
        if obj.usage is None or obj.usage_end_date is None:
            obj.usage_end_date = today
            obj.save(update_fields=['usage_end_date'])
            return 0
        else:
            if obj.usage_end_date > today:
                obj.usage_end_date = today
                obj.save(update_fields=['usage_end_date'])
                return 0
            else:
                if obj.usage < 1:
                    return 0
                else:
                    return (settings.MAX_REQUEST_USAGE * obj.usage) / 100

    def validate_email(self, value):
        if User.objects.filter(email=value).count() > 0:
            raise serializers.ValidationError('This email has been used')
        return value

    def create(self, validated_data):
        dt = datetime.utcnow().replace(tzinfo=utc) + timedelta(days=30)
        validated_data['usage_end_date'] = dt.date()
        return User.objects.create_user(**validated_data)
