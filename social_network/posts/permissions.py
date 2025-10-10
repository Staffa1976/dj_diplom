from rest_framework import permissions

class IsAuthorOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        # Для безопасных методов разрешаем всем
        if request.method in permissions.SAFE_METHODS:
            return True
        # Проверяем, является ли пользователь автором
        return obj.user == request.user