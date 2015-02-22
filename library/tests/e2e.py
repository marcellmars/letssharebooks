import unittest
from selenium import webdriver
from selenium.webdriver.common.keys import Keys

class TestLSBWebApp(unittest.TestCase):

    def setUp(self):
        self.driver = webdriver.Firefox()

    def test_initial_load(self):
        self.driver.get('http://localhost:4321')
        self.assertEqual(self.driver.title, 'memory of the world library')
        # assert that there are some books on the site initially
        books = self.driver.find_elements_by_class_name('cover')
        self.assertGreater(len(books), 0)

    def test_book_modal(self):
        self.driver.get('http://localhost:4321')
        # there should be no displayed modals initially
        displayed_modals = [i for i in self.driver.find_elements_by_id('book-modal') if i.is_displayed()]
        self.assertEqual(len(displayed_modals), 0)
        # locate first book and click it
        first_book = self.driver.find_element_by_class_name('cover')
        first_book.find_element_by_class_name('more_about').click()
        # there should be single modal displayed
        displayed_modals = [i for i in self.driver.find_elements_by_id('book-modal') if i.is_displayed()]
        self.assertEqual(len(displayed_modals), 1)

    def test_paging(self):
        self.driver.get('http://localhost:4321')
        # previous page is not active initially
        prev_page = self.driver.find_element_by_class_name('prev_page')
        self.assertIn('not-active', prev_page.get_attribute('class'))
        # next page is active
        next_page = self.driver.find_element_by_class_name('next_page')
        self.assertIn('active', next_page.get_attribute('class'))
        # get next page
        next_page.click()
        # previous page should now be active ...
        prev_page2 = self.driver.find_element_by_class_name('prev_page')
        self.assertIn('active', prev_page2.get_attribute('class'))
        # ... and url should contain "page=2"
        self.assertGreater(self.driver.current_url.find('page=2'), -1)

    def tearDown(self):
        self.driver.close()

if __name__ == "__main__":
    unittest.main()
