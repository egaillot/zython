"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""
import json
from time import sleep
from django.test import TestCase
from django.test.client import Client
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from brew.models import *


class RecipeTest(TestCase):
    user_info = {'username': 'martyn',
                 'password': 'magicpony',
                 'email': 'martyn@example.com'}
    user2_info = {'username': 'chuck',
                 'password': 'magicpony',
                 'email': 'chuck@example.com'}

    def setUp(self):
        # Set up the main user
        user = User(
            username=self.user_info['username'], 
            email=self.user_info['email']
        )
        user.set_password(self.user_info['password'])
        user.save()
        self.user = user

        user2 = User(
            username=self.user2_info['username'], 
            email=self.user2_info['email']
        )
        user2.set_password(self.user2_info['password'])
        user2.save()
        self.user2 = user2

        # Main client
        self.client = Client()

        # Set up the main recipe
        style = BeerStyle.objects.filter(name__icontains="Doppelbock")[0]
        recipe = Recipe(
            user=self.user, 
            name="Test Recipe PoneyPoneyPoney", 
            batch_size="50.3",
            style=style,
            recipe_type="allgrain",
            private=False, 
            efficiency="75",
        )
        recipe.save()
        self.recipe = recipe
    
    def get_logged_client(self):
        self.client.login(
            username=self.user_info['username'], 
            password=self.user_info['password']
        )
        return self.client

    def i18n_client(self, language="en", client=None):
        if not client:
            client = self.client
        client.post('/i18n/setlang/', {'language':language})
        return client

    def reload_recipe(self):
        # This hack is used to get a fresh cache_key
        # Tests are faster than user, the cachekey is a datetime
        # multiple datas can be saved in the same second in tests. 
        # I consider modifying the cache_key system to have a unique 
        # key each time the object is saved.
        sleep(0.5)
        self.recipe.save()
        self.recipe = Recipe.objects.get(pk=self.recipe.pk)

    def test_1_malt(self):
        malt = Malt.objects.filter(name__icontains="Maris Otter")[0]
        url_addition = reverse('brew_recipe_addingredient', args=[self.recipe.id, "malt"])
        datas = {'amount': "12.5", "malt_id": malt.id, "color": malt.color}

        # Test with anonymous client
        c = self.client
        response = c.post(url_addition, datas)
        self.assertEqual(response.status_code, 302)

        # Test with logged in client
        c = self.get_logged_client()
        response = c.post(url_addition, datas)
        content = json.loads(response.content)
        self.assertEqual(content.get('valid'), 1)

        # Test with coma amount for FR
        c = self.i18n_client('fr', c)
        datas['amount'] = datas['amount'].replace(".", ",")
        response = c.post(url_addition, datas)
        content = json.loads(response.content)
        self.assertEqual(content.get('valid'), 1)

        self.reload_recipe()

        # Do we have 2 Malts ?
        self.assertEqual(self.recipe.recipemalt_set.all().count(), 2)
        # We should have an OG > 1.1
        self.assertGreater(float(self.recipe.get_original_gravity()), 1.1)
        # We should have a color > 16EBC
        self.assertGreater(float(self.recipe.get_ebc()), 16)
        # We should have more than 11% alcool, waw! 
        self.assertGreater(float(self.recipe.get_abv()), 11)
        # We should have 0 IBU
        self.assertEqual(float(self.recipe.get_ibu()), 0)

        for malt in self.recipe.recipemalt_set.all():
            # Both malts should be 50/50%
            self.assertEqual(float(malt.percent()), 50)

        # Clear all malts
        self.recipe.recipemalt_set.all().delete()

    def test_2_hop(self):
        hop = Hop.objects.filter(name__icontains="Styrian")[0]
        url_addition = reverse('brew_recipe_addingredient', args=[self.recipe.id, "hop"])
        datas = {'amount': "80.5", "boil_time":"30.5", "hop_id": hop.id, "acid_alpha": hop.acid_alpha}

        # Test with anonymous client
        c = self.client
        response = c.post(url_addition, datas)
        self.assertEqual(response.status_code, 302)

        # Test with logged in client
        c = self.get_logged_client()
        response = c.post(url_addition, datas)
        content = json.loads(response.content)
        self.assertEqual(content.get('valid'), 1)

        # Test with coma amount for FR
        c = self.i18n_client('fr', c)
        datas['amount'] = datas['amount'].replace(".", ",")
        datas['boil_time'] = datas['boil_time'].replace(".", ",")
        response = c.post(url_addition, datas)
        content = json.loads(response.content)
        self.assertEqual(content.get('valid'), 1)

        self.reload_recipe()

        # Do we have 2 Hops ?
        self.assertEqual(self.recipe.recipehop_set.all().count(), 2)
        # We should have total IBU > 46
        self.assertGreater(float(self.recipe.get_ibu()), 46)
        # We should have no color
        self.assertEqual(float(self.recipe.get_ebc()), 0)
        # We should have no alcool :(
        self.assertEqual(float(self.recipe.get_abv()), 0)
        
        for hop in self.recipe.recipehop_set.all():
            # Both hops should give more than 22 IBU
            self.assertGreater(float(hop.ibu()), 22)
            # We did not change the time unit, so we have minutes and not days
            self.assertIn("min", hop.unit_time())

        # Clear all hops
        self.recipe.recipehop_set.all().delete()

    def test_3_misc(self):
        misc_id = Misc.objects.filter(name__icontains="Coriander").values_list("id", flat=True)[0]
        url_addition = reverse('brew_recipe_addingredient', args=[self.recipe.id, "misc"])
        datas = {
            "amount": "50.5", 
            "use_in": "boil",
            "time":"30.5", 
            "time_unit":"min", 
            "misc_id": misc_id
        }
        # Test with anonymous client
        c = self.client
        response = c.post(url_addition, datas)
        self.assertEqual(response.status_code, 302)

        # Test with logged in client
        c = self.get_logged_client()
        response = c.post(url_addition, datas)
        content = json.loads(response.content)
        self.assertEqual(content.get('valid'), 1)

        # Test with coma amount for FR
        c = self.i18n_client('fr', c)
        datas['amount'] = datas['amount'].replace(".", ",")
        datas['time'] = datas['time'].replace(".", ",")
        response = c.post(url_addition, datas)
        content = json.loads(response.content)
        self.assertEqual(content.get('valid'), 1)

        # Do we have 2 Miscs ?
        self.assertEqual(self.recipe.recipemisc_set.all().count(), 2)

        # Clear all miscs
        self.recipe.recipemisc_set.all().delete()

    def test_4_yeast(self):
        yeast_id = Yeast.objects.filter(product_id__icontains="58").values_list("id", flat=True)[0]
        url_addition = reverse('brew_recipe_addingredient', args=[self.recipe.id, "yeast"])
        datas = {
            "yeast_id": yeast_id
        }
        # Test with anonymous client
        c = self.client
        response = c.post(url_addition, datas)
        self.assertEqual(response.status_code, 302)

        # Test with logged in client
        c = self.get_logged_client()
        response = c.post(url_addition, datas)
        content = json.loads(response.content)
        self.assertEqual(content.get('valid'), 1)

        # Do we have 1 yeast ?
        self.assertEqual(self.recipe.recipeyeast_set.all().count(), 1)

        # Clear all yeasts
        self.recipe.recipeyeast_set.all().delete()

    def test_5_recipe_private(self):
        recipe = self.recipe
        recipe_name = "PoneyPoneyPoney"
        client2 = Client()
        client2.login(
            username=self.user2_info['username'], 
            password=self.user2_info['password']
        )
        client_author = Client()
        client_author.login(
            username=self.user_info['username'], 
            password=self.user_info['password']
        )

        # Anonymous should see recipe
        response = self.client.get('/')
        self.assertContains(response, recipe_name)

        # Other users should see it too
        response = client2.get('/')
        self.assertContains(response, recipe_name)

        # Recipe author should see it
        response = client_author.get('/')
        self.assertContains(response, recipe_name)

        # Set the recipe to private
        recipe.private = True
        recipe.save()

        # Anonymous shouldn't see this recipe
        response = self.client.get('/')
        self.assertNotContains(response, recipe_name)

        # Other users shouldn't see it
        response = client2.get('/')
        self.assertNotContains(response, recipe_name)

        # Recipe author should see it
        response = client_author.get('/')
        self.assertContains(response, recipe_name)

        # Set the recipe to public
        recipe.private = False
        recipe.save()

