import urllib

from .core import BaseWrapper


class SpoonacularAPIWrapper(BaseWrapper):

    def __init__(self, api_key):
        self.api_endpoint = "https://spoonacular-recipe-food-nutrition-v1.p.mashape.com/"
        self.headers = {
            'X-Mashape-Key': api_key,
            'Accept': 'application/json'
        }

    def get_recipe_by_ingredients(self, ingredients=None):
        """ get the recipe by the list of ingredients """
        endpoint = self.api_endpoint + "recipes/findByIngredients?fillIngredients=true&ingredients=%s" \
                                       "&limitLicense=true&number=100&ranking=2" % ingredients
        return self._get_endpoint(endpoint)

    def get_recipe_by_id(self, recipe_id=None):
        """ gets a recipe by the recipe id """
        endpoint = self.api_endpoint + "recipes/%s/information?includeNutrition=true" % recipe_id
        return self._get_endpoint(endpoint)

    def generate_meal_plan(self, **kwargs):
        """
        diet: "vegetarian", "vegan", "paleo"
        exclude: shellfish, olives
        calories: targert calories
        timeFrame: day or week.
        """
        query_string = urllib.urlencode(kwargs)

        endpoint = self.api_endpoint + "recipes/mealplans/generate?%s" % query_string
        return self._get_endpoint(endpoint)

    def map_ingredients_to_grocery(self, data):
        """ map the ingredients to gricery items """
        endpoint = self.api_endpoint + "food/ingredients/map"
        self.data = data
        return self._get_endpoint(endpoint)

    def get_random_recipe(self, **kwargs):
        """ get a random recipe """
        query_string = urllib.urlencode(kwargs)
        endpoint = self.api_endpoint + "recipes/random?%s" % query_string
        return self._get_endpoint(endpoint)

    def search_recipies(self, **kwargs):
        """
        cuisine: 
            african, chinese, japanese, korean, vietnamese, thai, indian, british, irish, french, italian, mexican,
            spanish, middle eastern, jewish, american, cajun, southern, greek, german, nordic,
            eastern european, caribbean, or latin american.

        diet
            pescetarian, lacto vegetarian, ovo vegetarian, vegan, and vegetarian.

        excludeIngredients
            comma separated ingredients list

        instructionsRequired
            true or false

        intolerances
            A comma-separated list of intolerances. 

        number
            The number of results to return (between 0 and 100).

        query
            The (natural language) recipe search query.

        type
            main course, side dish, dessert, appetizer, salad, bread, breakfast, soup, beverage, sauce, or drink.

        """
        query_string = urllib.urlencode(kwargs)
        endpoint = self.api_endpoint + "recipes/search?%s" % query_string
        return self._get_endpoint(endpoint)
