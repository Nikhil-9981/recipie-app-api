from rest_framework import serializers

from core.models import  Recipe, Tag, Ingredient


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ['id', 'name']
        read_only_fields = ['id']

class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'name']
        read_only_fields = ['id']


class RecipeSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True, required=False)
    ingredients = IngredientSerializer(many=True, required=False)

    class Meta:
        model = Recipe
        fields = ['id', 'title', 'time_minutes', 'price', 'link', 'tags', 'ingredients']
        read_only_fields = ['id']

    def _get_or_create_tags(self, tags, recipe):
        """Creates or retrieves Tag objects and associates them with a recipe."""
        auth_user = self.context['request'].user
        for tag in tags:
            tag_obj, _ = Tag.objects.get_or_create(user=auth_user, **tag)
            recipe.tags.add(tag_obj)

    def _get_or_create_ingredients(self, ingredients, recipe):
        """Creates or retrieves Ingredient objects and associates them with a recipe."""
        auth_user = self.context['request'].user
        for ingredient in ingredients:
            ingredient_obj, _ = Ingredient.objects.get_or_create(user=auth_user, **ingredient)
            recipe.ingredients.add(ingredient_obj)


    def create(self, validated_data):
        """
        Creates a new Recipe object. If the 'tags' key is in the validated_data,
        it will create new Tag objects and assign them to the Recipe.
        """
        tags = validated_data.pop('tags', [])  # default to an empty list
        ingredients = validated_data.pop('ingredients', [])
        recipe = Recipe.objects.create(**validated_data)
        self._get_or_create_tags(tags, recipe)
        self._get_or_create_ingredients(ingredients, recipe)
        return recipe

    def update(self, instance, validated_data):
        """
        Updates a Recipe object. If the 'tags' key is in the validated_data,
        it will update the Tag objects and assign them to the Recipe.
        """
        tags = validated_data.pop('tags', None)
        ingredients = validated_data.pop('ingredients', None)

        recipe = super().update(instance, validated_data)

        if tags is not None:
            instance.tags.clear()
            self._get_or_create_tags(tags, instance)
        if ingredients is not None:
            instance.ingredients.clear()
            self._get_or_create_ingredients(ingredients, instance)

        for attr, value in validated_data.items():
            setattr(recipe, attr, value)

        instance.save()

        return instance


class RecipeDetailSerializer(RecipeSerializer):
    class Meta(RecipeSerializer.Meta):
        fields = RecipeSerializer.Meta.fields + ['description', 'image']


class RecipeImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ['id', 'image']
        read_only_fields = ['id']
        extra_kwargs = {'image': {'required': 'True'}}




