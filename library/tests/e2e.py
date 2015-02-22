import unittest
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

class TestLSBWebApp(unittest.TestCase):

    def setUp(self):
        self.base_url = 'http://localhost:4321'
        #self.base_url = 'https://library.memoryoftheworld.org'
        self.driver = webdriver.Firefox()
        self.wait = WebDriverWait(self.driver, 10)

    def test_initial_load(self):
        self.driver.get(self.base_url)
        self.wait.until(EC.presence_of_element_located((By.CLASS_NAME,'cover')))
        self.assertEqual(self.driver.title, 'memory of the world library')
        # assert that there are some books on the site initially
        books = self.driver.find_elements_by_class_name('cover')
        self.assertGreater(len(books), 0)

    def test_book_modal(self):
        self.driver.get(self.base_url)
        self.wait.until(EC.presence_of_element_located((By.CLASS_NAME,'cover')))
        # there should be no displayed modals initially
        self.assertEqual(len(self.driver.find_elements_by_class_name('ui-dialog')), 0)
        # locate first book and click it
        first_book = self.driver.find_element_by_class_name('cover')
        first_book.find_element_by_class_name('more_about').click()
        self.wait.until(EC.presence_of_element_located((By.CLASS_NAME,'ui-dialog')))
        # there should be single modal displayed
        self.assertEqual(len(self.driver.find_elements_by_class_name('ui-dialog')), 1)

    # def test_book_modal_navigation(self):
    #     self.driver.get(self.base_url)
    #     # locate first book and click it
    #     first_book = self.driver.find_element_by_class_name('cover')
    #     first_book.find_element_by_class_name('more_about').click()
    #     # there should be single modal displayed
    #     displayed_modals = [i for i in self.driver.find_elements_by_id('book-modal') if i.is_displayed()]
    #     self.assertEqual(len(displayed_modals), 1)
    #     # nagivate to left modal
    #     displayed_modals[0].send_keys(Keys.LEFT)
    #     # there should be no modals displayed
    #     displayed_modals = [i for i in self.driver.find_elements_by_id('book-modal') if i.is_displayed()]
    #     self.assertEqual(len(displayed_modals), 0)

    def test_paging(self):
        self.driver.get(self.base_url)
        self.wait.until(EC.presence_of_element_located((By.CLASS_NAME,'cover')))
        # previous page is not active initially
        prev_page = self.driver.find_element_by_class_name('prev_page')
        self.assertIn('not-active', prev_page.get_attribute('class'))
        # next page is active
        next_page = self.driver.find_element_by_class_name('next_page')
        self.assertIn('active', next_page.get_attribute('class'))
        # get next page
        next_page.click()
        self.wait.until(EC.presence_of_element_located((By.CLASS_NAME,'cover')))
        # previous page should now be active ...
        prev_page2 = self.driver.find_element_by_class_name('prev_page')
        self.assertIn('active', prev_page2.get_attribute('class'))
        # ... and url should contain "page=2"
        self.assertGreater(self.driver.current_url.find('page=2'), -1)

    def test_search(self):
        
        def form_clear(form):
            form['title'].clear()
            form['author'].clear()
            form['search_all'].clear()
            form['librarian'].select_by_value('')
            
        self.driver.get(self.base_url)
        form = {}
        form['search'] = self.driver.find_element_by_id('search')
        form['title'] = self.driver.find_element_by_id('titles')
        form['author'] = self.driver.find_element_by_id('authors')
        form['search_all'] = self.driver.find_element_by_id('search_all')
        form['librarian'] = Select(self.driver.find_element_by_id('librarian'))
        
        # search by TITLE
        # search for all books for library 0
        form_clear(form)
        form['title'].send_keys('MCL0')
        form['search'].click()
        self.wait.until(EC.presence_of_element_located((By.CLASS_NAME,'cover')))
        books = self.driver.find_elements_by_class_name('cover')
        self.assertGreater(len(books), 0)
        # search for all books for library 1
        form_clear(form)
        form['title'].send_keys('MCL1')
        form['search'].click()
        self.wait.until(EC.presence_of_element_located((By.CLASS_NAME,'cover')))
        books = self.driver.find_elements_by_class_name('cover')
        self.assertGreater(len(books), 0)

        # search by AUTHOR
        form_clear(form)
        form['author'].send_keys('John The First')
        form['search'].click()
        self.wait.until(EC.presence_of_element_located((By.CLASS_NAME,'cover')))
        books = self.driver.find_elements_by_class_name('cover')
        self.assertEqual(len(books), 1)

        # search by SEARCH_ALL
        form_clear(form)
        form['search_all'].send_keys('the')
        form['search'].click()
        self.wait.until(EC.presence_of_element_located((By.CLASS_NAME,'cover')))
        books = self.driver.find_elements_by_class_name('cover')
        self.assertGreater(len(books), 0)

        # search by LIBRARIAN
        form_clear(form)
        form['librarian'].select_by_value('Joseph Of Byzantium')
        form['search'].click()
        self.wait.until(EC.presence_of_element_located((By.CLASS_NAME,'cover')))
        books = self.driver.find_elements_by_class_name('cover')
        self.assertGreater(len(books), 0)

    def tearDown(self):
        self.driver.close()

if __name__ == "__main__":
    unittest.main()
