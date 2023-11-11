from django.contrib import admin

from .models import (
    FavouriteRecipe,
    Ingredient,
    Recipe,
    RecipeIngredients,
    ShoppingList,
    Tag,
)


@admin.register(Tag)
class TagInAdmin(admin.ModelAdmin):
    """Класс тегов для отображения в админке."""

    empty_value_display = "значение отсутствует"
    list_display = ("id", "name", "color", "slug")
    search_fields = ("name",)


@admin.register(Ingredient)
class IngredientInAdmin(admin.ModelAdmin):
    """Класс ингредиентов для отображения в админке."""

    empty_value_display = "значение отсутствует"
    list_display = ("id", "name", "measurement_unit")
    search_fields = ("name",)


class IngredientsInLine(admin.TabularInline):
    model = RecipeIngredients
    extra = 0
    min_num = 1


@admin.register(Recipe)
class RecipeInAdmin(admin.ModelAdmin):
    """Класс рецептов для отображения в админке."""

    list_display = (
        "id",
        "name",
        "cooking_time",
        "image",
        "author",
        "text",
        "favorites_count",
    )
    search_fields = ("name",)
    list_filter = (
        "author",
        "name",
        "cooking_time",
    )
    list_editable = ("name",)
    inlines = (IngredientsInLine,)
    empty_value_display = "-пусто-"

    def favorites_count(self, obj):
        return obj.favorites_count()

    favorites_count.short_description = "Количество добавлений в избранное"


@admin.register(FavouriteRecipe)
class FavouriteRecipeInAdmin(admin.ModelAdmin):
    """Класс избранных для отображения в админке."""

    empty_value_display = "значение отсутствует"
    list_display = ("id", "user", "recipe")
    search_fields = ("user", "recipe")
    list_filter = ("user", "recipe")


@admin.register(ShoppingList)
class ShoppingListInAdmin(admin.ModelAdmin):
    """Класс избранных для отображения в админке."""

    empty_value_display = "значение отсутствует"
    list_display = ("id", "user", "recipe")
    search_fields = ("user", "recipe")
    list_filter = ("user", "recipe")
