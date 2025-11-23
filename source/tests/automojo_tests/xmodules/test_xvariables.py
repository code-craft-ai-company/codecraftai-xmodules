import unittest

from automojo.xmodules.xvariables import (
    assert_section_name,
    assert_variable_name,
    VariableDesc
)


class TestXVariables(unittest.TestCase):

    def test_assert_variable_name_accepts_valid_names(self):
        for var_name in ["VAR_NAME", "_var1", "Name_123"]:
            with self.subTest(var_name=var_name):
                result = assert_variable_name(var_name)
                self.assertEqual(result, var_name)
        return

    def test_assert_variable_name_rejects_leading_digit(self):
        with self.assertRaises(AssertionError):
            assert_variable_name("1INVALID")
        return

    def test_assert_variable_name_rejects_invalid_characters(self):
        with self.assertRaises(AssertionError):
            assert_variable_name("INVALID-NAME")
        return

    def test_assert_section_name_accepts_standard_names(self):
        for section_name in ["DEFAULT", "Service Config"]:
            with self.subTest(section_name=section_name):
                result = assert_section_name(section_name)
                self.assertEqual(result, section_name)
        return

    def test_assert_section_name_rejects_config_delimiters(self):
        with self.assertRaises(AssertionError):
            assert_section_name("bad[section")
        return

    def test_assert_section_name_rejects_empty_names(self):
        with self.assertRaises(AssertionError):
            assert_section_name("   ")
        return

    def test_variable_desc_validates_names(self):
        var_desc = VariableDesc(name="APP_SETTING", section="DEFAULT")
        self.assertEqual(var_desc.name, "APP_SETTING")
        self.assertEqual(var_desc.section, "DEFAULT")
        return


if __name__ == '__main__':
    unittest.main()
