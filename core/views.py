import logging
from datetime import datetime

from django.conf import settings
from django.utils.timezone import utc
from django.contrib.auth import get_user_model

from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework import viewsets
from django.shortcuts import get_object_or_404

from core.models import ExchangeRateHistory, ApiKey
from core.serializers import ApiKeySerializer, UserSerializer, UUIDSerializer
from utils.exchange_rates_sources import (
    get_dof_rate, get_fixer_rate, get_banxico_rate)
from utils.format_data import exchange_rate_format
from utils.permissions import SuperOnly, CurrentUserObj

logger = logging.getLogger(__name__)

User = get_user_model()


class ExchageRateView(APIView):
    def get(self, request, format=None):
        if request.user.is_authenticated:
            user = request.user
        else:
            temp_token = (
                request.headers.get(
                    'Authorization',
                    request.query_params.get('api_key', ''),
                )
                .replace('Token ', '')
                .strip()
            )

            token = UUIDSerializer(
                data={
                    'api_key': temp_token,
                }
            )
            token.is_valid(raise_exception=True)

            user = get_object_or_404(
                ApiKey,
                api_key=token.data.get('api_key', ''),
            ).user

        if user.check_usage_limit():
            return Response(
                {
                    'detail': 'You have reached your usage limit.',
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        dt = datetime.utcnow().replace(tzinfo=utc)
        last_rate = (
            ExchangeRateHistory.objects.filter()
            .order_by(
                '-created',
            )
            .first()
        )

        if last_rate is None:
            dof_data = get_dof_rate()
            fixer_data = get_fixer_rate()
            banxico_data = get_banxico_rate()
            if dof_data is None or fixer_data is None or banxico_data is None:
                return Response(
                    {
                        'detail': 'No data available',
                    },
                    status=status.HTTP_404_NOT_FOUND,
                )
            else:
                last_rate = ExchangeRateHistory.objects.create(
                    dof_rate=dof_data['rate'],
                    dof_date=dof_data['date'],
                    dof_last_updated=dt,
                    fixer_rate=fixer_data['rate'],
                    fixer_date=fixer_data['date'],
                    fixer_last_updated=dt,
                    banxico_rate=banxico_data['rate'],
                    banxico_date=banxico_data['date'],
                    banxico_last_updated=dt,
                )
        else:
            diff_dt = dt - last_rate.created
            if diff_dt.total_seconds() / 60.0 > settings.EXCHANGE_RATE_UPDATE_INTERVAL:
                dof_data = get_dof_rate()
                fixer_data = get_fixer_rate()
                banxico_data = get_banxico_rate()
                last_rate.pk = None
                if dof_data is not None:
                    last_rate.dof_rate = dof_data['rate']
                    last_rate.dof_date = dof_data['date']
                    last_rate.dof_last_updated = dt

                if fixer_data is not None:
                    last_rate.fixer_rate = fixer_data['rate']
                    last_rate.fixer_date = fixer_data['date']
                    last_rate.fixer_last_updated = dt

                if banxico_data is not None:
                    last_rate.banxico_rate = banxico_data['rate']
                    last_rate.banxico_date = banxico_data['date']
                    last_rate.banxico_last_updated = dt

                last_rate.save()

        user.usage = user.usage + 1
        user.save(update_fields=['usage'])

        return Response(exchange_rate_format(last_rate), status=status.HTTP_200_OK)


class UserViewSet(viewsets.ModelViewSet):
    serializer_class = UserSerializer
    queryset = User.objects.filter(is_active=True)
    permission_classes = [
        IsAuthenticated,
    ]
    lookup_field = 'pk'

    def get_queryset(self):
        user = self.request.user
        queryset = super().get_queryset()
        if self.action == 'list' and user.is_authenticated:
            queryset = queryset.filter(pk=user.pk)
        elif self.action == 'list' and not user.is_authenticated:
            queryset = queryset.filter(pk=0)
        return queryset

    def get_permissions(self):
        if self.action == 'create' or self.action == 'list':
            self.permission_classes = [
                AllowAny,
            ]
        elif (
            self.action == 'retrieve'
            or self.action == 'partial_update'
            or self.action == 'update'
        ):
            self.permission_classes = [
                CurrentUserObj,
            ]
        elif self.action == 'destroy':
            self.permission_classes = [
                SuperOnly,
            ]

        return super().get_permissions()
    
    def get_instance(self):
        return self.request.user

class ApiKeyViewSet(viewsets.ModelViewSet):
    serializer_class = ApiKeySerializer
    queryset = ApiKey.objects.filter()
    permission_classes = [
        IsAuthenticated,
    ]

    def get_queryset(self):
        user = self.request.user
        queryset = super().get_queryset().filter(user_id=user.pk)

        return queryset

    def get_permissions(self):
        if (
            self.action == 'create'
            or self.action == 'destroy'
            or self.action == 'retrieve'
            or self.action == 'partial_update'
            or self.action == 'update'
        ):
            self.permission_classes = [
                CurrentUserObj,
            ]

        return super().get_permissions()
