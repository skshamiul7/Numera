from html.parser import HTMLParser

from django.test import TestCase, override_settings
from django.urls import reverse

from .views import TOOL_META


class NavigationLinkParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.in_main_nav = False
        self.links = []

    def handle_starttag(self, tag, attrs):
        attributes = dict(attrs)
        if tag == 'nav' and attributes.get('id') == 'mainNav':
            self.in_main_nav = True
        elif tag == 'a' and self.in_main_nav and 'href' in attributes:
            self.links.append(attributes['href'])

    def handle_endtag(self, tag):
        if tag == 'nav' and self.in_main_nav:
            self.in_main_nav = False


TEST_STORAGES = {
    'default': {
        'BACKEND': 'django.core.files.storage.FileSystemStorage',
    },
    'staticfiles': {
        'BACKEND': 'django.contrib.staticfiles.storage.StaticFilesStorage',
    },
}


@override_settings(STORAGES=TEST_STORAGES)
class ToolPageTests(TestCase):
    def test_all_navigation_links_open_a_page(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)

        parser = NavigationLinkParser()
        parser.feed(response.content.decode())
        self.assertTrue(parser.links)

        for link in parser.links:
            with self.subTest(link=link):
                self.assertEqual(self.client.get(link).status_code, 200)

    def test_all_tool_pages_render(self):
        tool_names = [
            'evenodd', 'factorial', 'fibonacci', 'prime', 'gcd', 'palindrome',
            *TOOL_META,
        ]
        for name in tool_names:
            with self.subTest(tool=name):
                response = self.client.get(reverse(name))
                self.assertEqual(response.status_code, 200)

    def test_modular_exponentiation_calculates_result(self):
        response = self.client.post(
            reverse('mod_exp'),
            {'base': '2', 'exp': '10', 'mod': '7'},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '(2^10) mod 7 = 2')

    def test_modular_exponentiation_rejects_nonpositive_modulus(self):
        response = self.client.post(
            reverse('mod_exp'),
            {'base': '2', 'exp': '10', 'mod': '0'},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Modulus must be &gt; 0')
