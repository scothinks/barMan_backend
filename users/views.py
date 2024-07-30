import logging
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth import get_user_model
from .serializers import UserSerializer, UserCreateSerializer
from rest_framework.permissions import AllowAny, IsAuthenticated

logger = logging.getLogger(__name__)

User = get_user_model()

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAdminUser]

    def get_serializer_class(self):
        if self.action == 'create':
            return UserCreateSerializer
        return UserSerializer

    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def me(self, request):
        try:
            logger.info(f"Fetching current user data for user: {request.user.username}")
            serializer = self.get_serializer(request.user)
            logger.info(f"Successfully serialized user data for: {request.user.username}")
            return Response(serializer.data)
        except Exception as e:
            logger.error(f"Error in me action for user {request.user.username}: {str(e)}", exc_info=True)
            return Response({"error": "An unexpected error occurred"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=True, methods=['patch'])
    def update_permissions(self, request, pk=None):
        try:
            user = self.get_object()
            serializer = UserSerializer(user, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                logger.info(f"Permissions updated for user: {user.username}")
                return Response(serializer.data)
            logger.warning(f"Invalid data for updating permissions: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Error in update_permissions action: {str(e)}", exc_info=True)
            return Response({"error": "An unexpected error occurred"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            instance._prefetched_objects_cache = {}

        return Response(serializer.data)

    def perform_update(self, serializer):
        serializer.save()

class CurrentUserView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            logger.info(f"Fetching current user data for user: {request.user.username}")
            serializer = UserSerializer(request.user)
            logger.info(f"Successfully serialized user data for: {request.user.username}")
            return Response(serializer.data)
        except Exception as e:
            logger.error(f"Error in CurrentUserView for user {request.user.username}: {str(e)}", exc_info=True)
            return Response({"error": "An unexpected error occurred"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class CustomAuthToken(ObtainAuthToken):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        logger.info(f"Attempting authentication for user: {request.data.get('username')}")
        logger.debug(f"Request data: {request.data}")
        serializer = self.serializer_class(data=request.data, context={'request': request})
        try:
            if serializer.is_valid():
                user = serializer.validated_data['user']
                token, created = Token.objects.get_or_create(user=user)
                logger.info(f"Authentication successful for user: {user.username}")
                logger.info(f"Token created: {created}")
                response_data = {
                    'token': token.key,
                    'user_id': user.pk,
                    'email': user.email,
                    'username': user.username,
                    'can_update_inventory': user.can_update_inventory,
                    'can_report_sales': user.can_report_sales,
                    'can_create_customers': user.can_create_customers,
                    'can_create_tabs': user.can_create_tabs,
                    'can_update_tabs': user.can_update_tabs,
                    'can_manage_users': user.can_manage_users,
                }
                logger.debug(f"Response data: {response_data}")
                return Response(response_data)
            logger.error(f"Authentication failed: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.exception(f"Unexpected error during authentication: {str(e)}")
            return Response({"error": "An unexpected error occurred"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
