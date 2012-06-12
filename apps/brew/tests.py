"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""
from django.conf import settings
from django.test import TestCase
from django.test.utils import override_settings
from django.test.client import Client
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from brew.models import *

@override_settings(
    MIDDLEWARE_CLASSES=settings.MIDDLEWARE_CLASSES,
    TEMPLATE_CONTEXT_PROCESSORS=settings.TEMPLATE_CONTEXT_PROCESSORS,
)

class RecipeTest(TestCase):
    user_info = {'username': 'martyn',
                 'password': 'magicpony',
                 'email': 'martyn@example.com'}

    

    def setUp(self):
        # Set up the main user
        user = User(
            username=self.user_info['username'], 
            email=self.user_info['email']
        )
        user.set_password(self.user_info['password'])
        user.save()
        self.user = user
        self.client = Client()

        # Set up the main recipe
        style = BeerStyle.objects.filter(name__icontains="Doppelbock")[0]
        recipe = Recipe(
            user=self.user, 
            name="Test Recipe", 
            batch_size="50.3",
            style=style,
            recipe_type="allgrain",
            private=False, 
            efficiency="75",
        )
        recipe.save()
        self.recipe = recipe
    
    @override_settings(
        MIDDLEWARE_CLASSES=settings.MIDDLEWARE_CLASSES,
        TEMPLATE_CONTEXT_PROCESSORS=settings.TEMPLATE_CONTEXT_PROCESSORS,
    )
    def test_malt_addition(self):
        malt_id = Malt.objects.filter(name__icontains="Maris Otter").values_list("id", flat=True)[0]
        url_addition = reverse('brew_recipe_addingredient', args=[self.recipe.id, "malt"])
        c = Client()
        user = self.client.login(username=self.user_info['username'], password=self.user_info['password'])

        response = c.post('/accounts/login/', {'username': self.user_info['username'], 'password': self.user_info['password']})
        response = c.post(url_addition, {'amount': "12", "malt_id": malt_id})
        self.assertEqual(response.status_code, 302)

