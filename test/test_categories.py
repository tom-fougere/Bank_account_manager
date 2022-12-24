import unittest
from source.categories import *


class CategoriesTest(unittest.TestCase):
    def test_get_list_categories(self):
        self.assertEqual(len(get_list_categories()), len(ALL_CATEGORIES))
        for cat in get_list_categories():
            self.assertTrue(cat in list(ALL_CATEGORIES.keys()))

    def test_get_list_categories_and_sub(self):
        self.assertEqual(len(get_list_categories_and_sub()), len(ALL_CATEGORIES))

        for cat, sub_cats in get_list_categories_and_sub().items():
            self.assertEqual(sub_cats, list(ALL_CATEGORIES[cat]["Sub-categories"].keys()))

    def test_get_sub_categories(self):
        for cat in get_list_categories():
            self.assertEqual(get_sub_categories(cat), list(ALL_CATEGORIES[cat]["Sub-categories"].keys()))

    def test_get_default_occasion(self):
        for cat, cat_info in ALL_CATEGORIES.items():
            if len(cat_info['Sub-categories']) > 0:
                for sub_cat in list(cat_info['Sub-categories'].keys()):
                    occasion = get_default_occasion(
                        category=cat,
                        sub_category=sub_cat,
                    )
                    self.assertEqual(occasion, cat_info['Sub-categories'][sub_cat]['Default_occasion'])
            else:
                occasion = get_default_occasion(
                    category=cat,
                    sub_category=None,
                )
                self.assertEqual(occasion, cat_info['Default_occasion'])


if __name__ == '__main__':
    unittest.main()
