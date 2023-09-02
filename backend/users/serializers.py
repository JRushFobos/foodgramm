from django.contrib.auth import get_user_model
from rest_framework import serializers

from recipes.models import Recipe
from .models import Subscription

User = get_user_model()


class CustomUserSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField(
        method_name="get_is_subscribed"
    )

    def get_is_subscribed(self, obj):
        user = self.context["request"].user

        if user.is_anonymous:
            return False

        return Subscription.objects.filter(user=user, author=obj).exists()

    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "first_name",
            "last_name",
            "email",
            "is_subscribed",
        )
        ordering = (
            "id",
            "username",
            "first_name",
            "last_name",
            "email",
            "is_subscribed",
        )


class RecipeInSubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ("id", "name", "image", "cooking_time")
        read_only_fields = ("id", "name", "image", "cooking_time")


class SubscriptionSerializer(CustomUserSerializer):
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            "id",
            "email",
            "username",
            "first_name",
            "last_name",
            "is_subscribed",
            "recipes",
            "recipes_count",
        )

    def get_recipes(self, obj):
        request = self.context.get("request")
        limit = request.GET.get("recipes_limit")
        queryset = obj.recipes.all()
        if limit is not None:
            try:
                limit = int(limit)
                if limit >= 0:
                    queryset = queryset[:limit]
                else:
                    return {
                        "error": "Кол-во рецептов не может "
                        "быть отрицательным числом",
                    }
            except ValueError:
                return {
                    "error": "Кол-во рецептов должен быть целым числом",
                }
        else:
            return RecipeInSubscriptionSerializer(queryset, many=True).data

    def get_recipes_count(self, obj):
        return obj.recipes.all().count()


class CheckSubscriptionSerializer(serializers.ModelSerializer):
    """Сериализатор проверки подписки"""

    class Meta:
        model = Subscription
        fields = (
            "user",
            "author",
        )

    def validate(self, attrs):
        user = attrs["user"]
        author = attrs["author"]
        subscribed = user.subscribers.filter(author=author).exists()

        if self.context.get("request").method == "POST":
            if user == author:
                raise serializers.ValidationError(
                    "Ошибка, на себя подписка не разрешена"
                )
            if subscribed:
                raise serializers.ValidationError("Ошибка, вы уже подписались")
        if self.context.get("request").method == "DELETE":
            if user == author:
                raise serializers.ValidationError(
                    "Ошибка, отписка от самого себя не допустима"
                )
            if not subscribed:
                raise serializers.ValidationError(
                    {"errors": "Ошибка, вы уже отписались"}
                )
        return attrs
