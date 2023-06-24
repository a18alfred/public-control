from rest_framework import serializers
from .models import Category, Picture, Comment, Problem, Signature, Assignment
from accounts.serializers import AccountShortSerializer, AccountCommentSerializer
from .service import is_signed, is_assigned


class FilterCategoryListSerializer(serializers.ListSerializer):
    """
    Фильтр категорий, только parents
    """

    def to_representation(self, data):
        data = data.filter(parent=None)
        return super().to_representation(data)


class RecursiveSerializer(serializers.Serializer):
    """
    Вывод рекурсивно children
    """

    def to_representation(self, value):
        serializer = self.parent.parent.__class__(value, context=self.context)
        return serializer.data


class CategorySerializer(serializers.ModelSerializer):
    children = RecursiveSerializer(many=True)

    class Meta:
        list_serializer_class = FilterCategoryListSerializer
        model = Category
        fields = ['id', 'name', 'slug', 'icon', 'children']


class CategoryPostPutDeleteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'icon', 'parent']


class CategoryBasicSerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'icon', ]


class PictureSerializer(serializers.ModelSerializer):
    class Meta:
        model = Picture
        fields = '__all__'


class PictureShortSerializer(serializers.ModelSerializer):
    class Meta:
        model = Picture
        fields = ['id', 'uploaded_picture']


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = '__all__'


class CommentViewSerializer(serializers.ModelSerializer):
    account = AccountCommentSerializer(read_only=True)

    class Meta:
        model = Comment
        fields = ['id', 'comment', 'comment', 'date', 'uploaded_picture', 'account']


class SignatureSerializer(serializers.ModelSerializer):
    class Meta:
        model = Signature
        fields = '__all__'


class AssignmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Assignment
        fields = '__all__'


class ProblemCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Problem
        exclude = ['urgency', 'dateCreated', 'dateUnderReview', 'dateActive', 'dateInProgress',
                   'dateCompleted', 'dateClosed', 'dateRejected']

    def validate(self, attrs):
        if not 'category' in attrs or (not attrs['category']):
            raise serializers.ValidationError({"category": "Должена быть отправлена категория проблемы"})
        return attrs


class ProblemStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Problem
        fields = ['status', ]

    def validate(self, attrs):
        if not 'status' in attrs or (not attrs['status']):
            raise serializers.ValidationError({"status": "Должен быть отправлен статус проблемы"})
        return attrs


class ProblemOnlyStatusCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Problem
        fields = ['status', 'category', ]


class ProblemGetSerializer(serializers.ModelSerializer):
    category = CategoryBasicSerializer(read_only=True)
    account = AccountShortSerializer(read_only=True)
    region = serializers.CharField(source='get_region_iso_display')
    pictures = PictureShortSerializer(read_only=True, many=True, source='problem_picture')
    comments = CommentViewSerializer(read_only=True, many=True, source='problem_comment')
    is_signed = serializers.SerializerMethodField()
    is_assigned = serializers.SerializerMethodField()

    def get_is_signed(self, obj) -> bool:
        user = self.context.get('request').user
        return is_signed(obj, user)

    def get_is_assigned(self, obj) -> bool:
        user = self.context.get('request').user
        return is_assigned(obj, user)

    class Meta:
        model = Problem
        fields = '__all__'


class ProblemSuperSerializer(serializers.ModelSerializer):
    class Meta:
        model = Problem
        fields = '__all__'


class ProblemListSerializer(serializers.ModelSerializer):
    region = serializers.CharField(source='get_region_iso_display')
    category_name = serializers.CharField(source='category.name')
    urgency_name = serializers.CharField(source='get_urgency_display')
    signatures = serializers.IntegerField(source='signature_count')
    is_signed = serializers.SerializerMethodField()
    is_assigned = serializers.SerializerMethodField()

    def get_is_signed(self, obj) -> bool:
        user = self.context.get('request').user
        return is_signed(obj, user)

    def get_is_assigned(self, obj) -> bool:
        user = self.context.get('request').user
        return is_assigned(obj, user)

    class Meta:
        model = Problem
        fields = ['id', 'category', 'category_name', 'status', 'urgency', 'urgency_name', 'region_iso', 'region',
                  'latitude', 'longitude', 'dateCreated', 'signatures', 'is_signed', 'is_assigned']


class ProblemYandexMapListSerializer(serializers.ModelSerializer):
    geometry = serializers.SerializerMethodField()
    type = serializers.SerializerMethodField()
    properties = serializers.SerializerMethodField()

    def get_geometry(self, obj):
        response = {
            'type': 'Point',
            'coordinates': [obj.latitude, obj.longitude]
        }
        return response

    def get_type(self, obj):
        return 'Feature'

    def get_properties(self, obj):
        response = {
            'clusterCaption': obj.category.name
        }
        return response

    class Meta:
        model = Problem
        fields = ['id', 'type', 'geometry', 'properties']


class ProblemYandexMapBalloonSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name')

    class Meta:
        model = Problem
        fields = ['category_name', 'dateCreated', 'status', 'urgency']
