from django.contrib.auth import get_user_model
from django_filters import FilterSet, rest_framework
from rest_framework.filters import SearchFilter

from recipes.models import Recipe, Tag

User = get_user_model()


class RecipesFilter(FilterSet):
    """Фильтры для shoppinglist и favourites рецептов"""

    is_favorited = rest_framework.filters.BooleanFilter(
        method='filter_favorited'
    )
    is_in_shopping_cart = rest_framework.filters.BooleanFilter(
        method='filter_shopping_cart'
    )
    tags = rest_framework.filters.ModelMultipleChoiceFilter(
        field_name='tags__slug',
        queryset=Tag.objects.all(),
        to_field_name='slug',
    )

    def filter_by_list(self, queryset, name, value, list_name):
        if value and self.request.user.is_authenticated:
            return Recipe.objects.filter(
                id__in=getattr(self.request.user, list_name).values_list(
                    'recipe_id'
                )
            )
        return queryset

    def filter_favorited(self, queryset, name, value):
        return self.filter_by_list(queryset, name, value, 'favourites')

    def filter_shopping_cart(self, queryset, name, value):
        return self.filter_by_list(queryset, name, value, 'shoppinglist')

    class Meta:
        model = Recipe
        fields = ("author", "tags", "is_favorited", "is_in_shopping_cart")


class IngredientsFilter(SearchFilter):
    """Фильтр ингредиентов."""

    search_param = 'name'
