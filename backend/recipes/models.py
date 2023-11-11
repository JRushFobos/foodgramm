from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, RegexValidator
from django.db import models

from api.validators import validate_name

User = get_user_model()


class Tag(models.Model):
    """Модель тегов."""

    name = models.CharField(
        verbose_name="Название тега",
        max_length=settings.MAX_CHAR_LENGTH,
        unique=True,
        validators=[validate_name],
    )
    color = models.CharField(
        verbose_name="Цвет тега в формате HEX",
        max_length=settings.MAX_COLOR_LENGTH,
        unique=True,
        validators=[
            RegexValidator(
                "#([a-fA-F0-9]{3,6})",
                message="Поле только для HEX формата данных",
            )
        ],
    )
    slug = models.SlugField(
        verbose_name="Слаг тега",
        max_length=settings.MAX_CHAR_LENGTH,
        unique=True,
    )

    class Meta:
        verbose_name = "Тег"
        verbose_name_plural = "Теги"

    def __str__(self):
        return f"{self.name}"


class Ingredient(models.Model):
    """Модель ингредиентов."""

    name = models.CharField(
        verbose_name="Название ингредиента",
        max_length=settings.MAX_CHAR_LENGTH,
        validators=[validate_name],
    )
    measurement_unit = models.CharField(
        verbose_name="Eдиница измерения ингредиента",
        max_length=settings.MAX_CHAR_LENGTH,
    )

    class Meta:
        verbose_name = "ингредиент"
        verbose_name_plural = "ингредиенты"
        constraints = (
            models.UniqueConstraint(
                fields=("name", "measurement_unit"),
                name="unique_name_measurement_unit",
            ),
        )

    def __str__(self):
        return f"{self.name}"


class Recipe(models.Model):
    """Модель рецептов."""

    author = models.ForeignKey(
        User,
        verbose_name="Автор рецепта",
        on_delete=models.CASCADE,
        related_name="recipes",
    )
    tags = models.ManyToManyField(
        Tag,
        verbose_name="Список id тегов рецепта",
        related_name="recipes",
        help_text="Список id тегов рецепта",
    )
    image = models.ImageField(
        verbose_name="Изображение рецепта",
        blank=False,
        upload_to="image_recipe/",
    )
    name = models.CharField(
        verbose_name="Название рецепта",
        max_length=settings.MAX_CHAR_LENGTH,
        validators=[validate_name],
    )

    text = models.TextField(
        verbose_name="Описание рецепта",
        help_text="Описание рецепта",
    )
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name="Время приготовления (в минутах)",
        validators=[
            MinValueValidator(
                1,
                ("Ошибка, время приготовления рецепта должно быть >= 1 мин."),
            )
        ],
    )
    pub_date = models.DateTimeField(
        verbose_name="Дата публикации", auto_now_add=True
    )

    class Meta:
        verbose_name = "Рецепт"
        verbose_name_plural = "Рецепты"
        ordering = ("-pub_date",)

    def __str__(self):
        return f"{self.name}"

    def favorites_count(self):
        return FavouriteRecipe.objects.filter(recipe=self).count()


class RecipeIngredients(models.Model):
    """Модель ингредиентов в рецепте."""

    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name="ingredients",
        verbose_name="Рецепт",
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name="+",
        verbose_name="Ингредиент",
    )
    amount = models.PositiveSmallIntegerField(
        default=1,
        verbose_name="Количество ингредиентов в рецепте",
        validators=[
            MinValueValidator(
                1, "Ошибка, в рецепте должен быть хотя бы один ингредиент"
            )
        ],
    )

    class Meta:
        verbose_name = "Ингредиент для рецепта"
        verbose_name_plural = "Ингредиенты для рецепта"

    def __str__(self):
        return (
            f"Рецепт {self.recipe} содержит ингредиент "
            f"{self.ingredient.name} в количестве: {self.amount}"
        )


class FavouriteRecipe(models.Model):
    """Модель избранных рецептов."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="favourites",
        verbose_name="Пользователь",
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name="+",
        verbose_name="Рецепт",
    )

    class Meta:
        verbose_name = "Избранный рецепт"
        verbose_name_plural = "Избранные рецепты"

        constraints = (
            models.UniqueConstraint(
                fields=("user", "recipe"), name="unique_user_recipe"
            ),
        )

    def __str__(self):
        return f"{self.user} - {self.recipe.name}"


class ShoppingList(models.Model):
    """Модель списка покупок."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="shoppinglist",
        verbose_name="Пользователь",
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name="+",
        verbose_name="Рецепт",
    )

    class Meta:
        verbose_name = "Список покупок"
        verbose_name_plural = "Корзина для продуктов"
        ordering = ("-id",)
        constraints = [
            models.UniqueConstraint(
                fields=("user", "recipe"), name="unique_list_user"
            )
        ]
