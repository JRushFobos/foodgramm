from http import HTTPStatus

from django.conf import settings
from django.db import transaction
from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import SAFE_METHODS, AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from recipes.models import (
    FavouriteRecipe,
    Ingredient,
    Recipe,
    RecipeIngredients,
    ShoppingList,
    Tag,
)
from users.models import User

from .filters import IngredientsFilter, RecipesFilter
from .paginations import PageNumberPagination
from .permissions import IsAuthorOrReadOnly
from .serializers import (
    CheckSubscriptionSerializer,
    FavouriteSerializer,
    IngredientsSerializer,
    RecipesReadSerializer,
    RecipesWriteSerializer,
    ShoppingCartSerializer,
    ShortRecipeSerializer,
    SubscriptionSerializer,
    TagsSerializer,
    UserSerializer,
)


class UserViewSet(GenericViewSet):
    """Вью сет пользователей и подписок."""

    serializer_class = UserSerializer
    queryset = User.objects.all()
    permission_classes = (AllowAny,)
    search_fields = ("username", "email")

    @action(
        detail=False,
        methods=("GET",),
        serializer_class=SubscriptionSerializer,
    )
    def subscriptions(self, request):
        """Получение списка польвателей"""
        user = self.request.user
        user_subscriptions = user.subscribes.all()
        authors = user_subscriptions.values_list('author__id', flat=True)
        queryset = User.objects.filter(pk__in=authors)
        paginated_queryset = self.paginate_queryset(queryset)
        serializer = self.get_serializer(paginated_queryset, many=True)

        return self.get_paginated_response(serializer.data)

    @action(
        detail=True,
        methods=("POST", "DELETE"),
        serializer_class=CheckSubscriptionSerializer,
    )
    def subscribe(self, request, pk=None):
        """Создание и удаление подписок."""
        user = self.request.user
        author = get_object_or_404(User, pk=pk)
        data = {
            "user": user.id,
            "author": author.id,
        }

        if self.request.method == "POST":
            serializer = CheckSubscriptionSerializer(
                data=data,
                context={"request": request},
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            serializer = SubscriptionSerializer(
                author, context={"request": request}
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if self.request.method == "DELETE":
            serializer = CheckSubscriptionSerializer(
                data=data,
                context={"request": request},
            )
            serializer.is_valid(raise_exception=True)
            user.subscribes.filter(author=author).delete()

            return Response(status=status.HTTP_204_NO_CONTENT)


class TagsViewSet(viewsets.ReadOnlyModelViewSet):
    """Вьюсет тегов."""

    permission_classes = (AllowAny,)
    queryset = Tag.objects.all()
    serializer_class = TagsSerializer
    pagination_class = None


class IngredientsViewSet(viewsets.ReadOnlyModelViewSet):
    """Вьюсет ингридиентов."""

    permission_classes = (AllowAny,)
    queryset = Ingredient.objects.all()
    serializer_class = IngredientsSerializer
    filter_backends = (IngredientsFilter,)
    search_fields = ('^name',)
    pagination_class = None


class RecipesViewSet(viewsets.ModelViewSet):
    """Вьюсет для рецептов."""

    queryset = Recipe.objects.all()
    permission_classes = (IsAuthorOrReadOnly,)
    filterset_class = RecipesFilter
    pagination_class = PageNumberPagination

    def get_serializer_class(self):
        if self.request.method in SAFE_METHODS:
            return RecipesReadSerializer
        return RecipesWriteSerializer

    @action(
        detail=True, methods=["POST"], permission_classes=(IsAuthenticated,)
    )
    def favorite(self, request, pk=None):
        data = {
            "user": request.user.id,
            "recipe": pk,
        }
        serializer = FavouriteSerializer(
            data=data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        return self.add_object(FavouriteRecipe, request.user, pk)

    @favorite.mapping.delete
    def del_favorite(self, request, pk=None):
        data = {
            "user": request.user.id,
            "recipe": pk,
        }
        serializer = FavouriteSerializer(
            data=data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        return self.delete_object(FavouriteRecipe, request.user, pk)

    @action(
        detail=True, methods=["POST"], permission_classes=(IsAuthenticated,)
    )
    def shopping_cart(self, request, pk=None):
        data = {
            "user": request.user.id,
            "recipe": pk,
        }
        serializer = ShoppingCartSerializer(
            data=data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        return self.add_object(ShoppingList, request.user, pk)

    @shopping_cart.mapping.delete
    def del_shopping_cart(self, request, pk=None):
        data = {
            "user": request.user.id,
            "recipe": pk,
        }
        serializer = ShoppingCartSerializer(
            data=data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        return self.delete_object(ShoppingList, request.user, pk)

    @transaction.atomic()
    def add_object(self, model, user, pk):
        recipe = get_object_or_404(Recipe, id=pk)
        model.objects.create(user=user, recipe=recipe)
        serializer = ShortRecipeSerializer(recipe)
        return Response(serializer.data, status=HTTPStatus.CREATED)

    @transaction.atomic()
    def delete_object(self, model, user, pk):
        model.objects.filter(user=user, recipe__id=pk).delete()
        return Response(status=HTTPStatus.NO_CONTENT)

    @action(
        methods=["GET"], detail=False, permission_classes=(IsAuthenticated,)
    )
    def download_shopping_cart(self, request):
        shopping_cart = ShoppingList.objects.filter(user=self.request.user)
        recipes = [item.recipe.id for item in shopping_cart]
        buy_list = (
            RecipeIngredients.objects.filter(recipe__in=recipes)
            .values("ingredient")
            .annotate(amount=Sum("amount"))
        )

        buy_list_text = settings.TITLE_SHOP_LIST
        for item in buy_list:
            ingredient = Ingredient.objects.get(pk=item["ingredient"])
            amount = item["amount"]
            buy_list_text += (
                f"{ingredient.name}, {amount} "
                f"{ingredient.measurement_unit}\n"
            )

        response = HttpResponse(buy_list_text, content_type="text/plain")
        response[
            "Content-Disposition"
        ] = f"attachment; filename={settings.FILE_NAME}"

        return response
