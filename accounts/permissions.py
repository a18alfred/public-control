from rest_framework.permissions import BasePermission


class IsSuperUserOrModeratorUser(BasePermission):
    """
    Является ли пользователь модератором или суперюзером
    """

    def has_permission(self, request, view):
        if (not request.user.is_anonymous) and request.user.is_authenticated:
            if request.user.is_superuser:
                return True
            if request.user.is_moderator:
                return True
        return False


class IsResponderUser(BasePermission):
    """
    Является ли пользователь представителем власти или представителем УК
    """

    def has_permission(self, request, view):
        if (not request.user.is_anonymous) and request.user.is_authenticated:
            if request.user.is_government:
                return True
            if request.user.is_management_company:
                return True
        return False


class IsSuperUser(BasePermission):
    """
    Является ли пользователь суперюзером
    """

    def has_permission(self, request, view):
        return (not request.user.is_anonymous) and request.user.is_authenticated and request.user.is_superuser


class IsOwner(BasePermission):
    """
    Редактировать/читать объект может только владелец (профайла) или создатель проблемы.
    """

    def has_object_permission(self, request, view, obj):
        return obj.account == request.user


class IsOwnerOrSuperUser(BasePermission):
    """
    Редактировать/читать объект может только владелец (профайла) или создатель проблемы или суперюзер
    """

    def has_object_permission(self, request, view, obj):
        if (not request.user.is_anonymous) and request.user.is_authenticated and request.user.is_superuser:
            return True

        return obj.account == request.user


class IsOwnerOrSuperUserOrModerator(BasePermission):
    """
    Редактировать/читать объект может только владелец (профайла) или создатель проблемы или суперюзер
    или модератор
    """

    def has_object_permission(self, request, view, obj):
        if (not request.user.is_anonymous) and request.user.is_authenticated:
            if request.user.is_superuser:
                return True
            if request.user.is_moderator:
                return True

        return obj.account == request.user


class IsOwnerOrSpecialUser(BasePermission):
    """
    Возвращает True если пользователь обладает особыми правами (модератор, представитель и тд)
    или пользователь создатель проблемы
    """

    def has_object_permission(self, request, view, obj):
        if (not request.user.is_anonymous) and request.user.is_authenticated:
            if request.user.is_superuser:
                return True
            if request.user.is_moderator:
                return True
            if request.user.is_government:
                return True
            if request.user.is_management_company:
                return True

        return obj.account == request.user


class IsSpecialUser(BasePermission):
    """
    Возвращает True если пользователь обладает особыми правами (модератор, представитель и тд)
    """

    def has_permission(self, request, view):
        if (not request.user.is_anonymous) and request.user.is_authenticated:
            if request.user.is_superuser:
                return True
            if request.user.is_moderator:
                return True
            if request.user.is_government:
                return True
            if request.user.is_management_company:
                return True

        return False
