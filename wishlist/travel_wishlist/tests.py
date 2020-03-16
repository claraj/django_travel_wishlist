from django.test import TestCase
from django.urls import reverse 

from .models import Place 

class TestHomePageIsEmptyList(TestCase):

    def test_load_home_page_shows_empty_list(self):
        response = self.client.get(reverse('place_list'))
        self.assertTemplateUsed(response, 'travel_wishlist/wishlist.html')
        self.assertFalse(response.context['places'])
        self.assertContains(response, 'You have no places in your wishlist')


class TestWishList(TestCase):

    fixtures = ['test_places']

    def test_view_wishlist_contains_not_visited_places(self):
        response = self.client.get(reverse('place_list'))
        self.assertTemplateUsed(response, 'travel_wishlist/wishlist.html')
        
        self.assertContains(response, 'Tokyo')
        self.assertContains(response, 'New York')
        self.assertNotContains(response, 'San Francisco')        
        self.assertNotContains(response, 'Moab')


    def test_view_places_visited_shows_visited_places(self):
        response = self.client.get(reverse('places_visited'))
        # Check correct template was used
        self.assertTemplateUsed(response, 'travel_wishlist/visited.html')

        self.assertNotContains(response, 'Tokyo')
        self.assertNotContains(response, 'New York')
        self.assertContains(response, 'San Francisco')        
        self.assertContains(response, 'Moab')


class TestAddNewPlace(TestCase):

    def test_add_new_unvisited_place_to_wishlist(self):

        response = self.client.post(reverse('place_list'), { 'name': 'Tokyo', 'visited': False }, follow=True)

        # Check correct template was used
        self.assertTemplateUsed(response, 'travel_wishlist/wishlist.html')

        # What data was used to populate the template?
        response_places = response.context['places']
        # Should be 1 item
        self.assertEqual(len(response_places), 1)
        tokyo_response = response_places[0]

        # Expect this data to be in the database. Use get() to get data with
        # the values expected. Will throw an exception if no data, or more than
        # one row, matches. Remember throwing an exception will cause this test to fail
        tokyo_in_database = Place.objects.get(name='Tokyo', visited=False)

        # Is the data used to render the template, the same as the data in the database?
        self.assertEqual(tokyo_response, tokyo_in_database)

        # And add another place - still works?
        response = self.client.post(reverse('place_list'), { 'name': 'Yosemite', 'visited': False}, follow=True)

        # Check correct template was used
        self.assertTemplateUsed(response, 'travel_wishlist/wishlist.html')

        # What data was used to populate the template?
        response_places = response.context['places']
        # Should be 2 items
        self.assertEqual(len(response_places), 2)

        # Expect this data to be in the database. Use get() to get data with
        # the values expected. Will throw an exception if no data, or more than
        # one row, matches. Remember throwing an exception will cause this test to fail
        place_in_database = Place.objects.get(name='Yosemite', visited=False)
        place_in_database = Place.objects.get(name='Tokyo', visited=False)

        places_in_database = Place.objects.all()  # Get all data

        # Is the data used to render the template, the same as the data in the database?
        self.assertCountEqual(list(places_in_database), list(response_places))


    def test_add_new_visited_place_to_wishlist(self):

        response =  self.client.post(reverse('place_list'), { 'name': 'Tokyo', 'visited': True }, follow=True)

        # Check correct template was used
        self.assertTemplateUsed(response, 'travel_wishlist/wishlist.html')

        # What data was used to populate the template?
        response_places = response.context['places']

        # Should be 0 items - have not added any un-visited places
        self.assertEqual(len(response_places), 0)

        # Expect this data to be in the database. Use get() to get data with
        # the values expected. Will throw an exception if no data, or more than
        # one row, matches. Remember throwing an exception will cause this test to fail
        place_in_database = Place.objects.get(name="Tokyo", visited=True)



class TestVisitPlace(TestCase):

    fixtures = ['test_places']

    def test_visit_place(self):

        # visit place pk = 2 ,  New York
      
        response = self.client.post(reverse('place_was_visited', args=(2,) ), follow=True)

        # Check correct template was used
        self.assertTemplateUsed(response, 'travel_wishlist/wishlist.html')

        # no New York in the response
        self.assertNotContains(response, "New York")

        # Is New York visited?
        new_york = Place.objects.get(pk=2)

        self.assertTrue(new_york.visited)

    def test_visit_non_existent_place(self):

        # visit place pk = 200 
      
        response = self.client.post(reverse('place_was_visited', args=(200,) ), follow=True)

        self.assertEqual(response.status_code, 404)  # not found