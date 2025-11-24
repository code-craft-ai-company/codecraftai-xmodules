import unittest

from automojo.xmodules.xvariables import (
    assert_section_name,
    assert_variable_name,
    VariableDesc,
    VariableSource,
    VariableReader
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
        class SampleVariables:
            APP_SETTING = VariableDesc(section="DEFAULT")

        var_desc = SampleVariables.APP_SETTING
        self.assertEqual(var_desc.name, "APP_SETTING")
        self.assertEqual(var_desc.section, "DEFAULT")
        self.assertEqual(var_desc.key, "DEFAULT->APP_SETTING")
        return

    def test_variable_desc_preserves_metadata(self):
        def to_upper(value):
            return value.upper()

        class SampleVariables:
            FEATURE_FLAG = VariableDesc(
                section="FEATURES",
                default="false",
                overrides=False,
                context_path="features.flag",
                source=VariableSource.ENVIRONMENT,
                converter=to_upper
            )

        var_desc = SampleVariables.FEATURE_FLAG

        self.assertEqual(var_desc.key, "FEATURES->FEATURE_FLAG")
        self.assertEqual(var_desc.default, "false")
        self.assertFalse(var_desc.overrides)
        self.assertEqual(var_desc.context_path, "features.flag")
        self.assertIs(var_desc.converter, to_upper)
        self.assertEqual(var_desc.source, VariableSource.ENVIRONMENT)
        return


class TestVariableReader(unittest.TestCase):

    def test_variable_reader_invokes_perform_read(self):
        call_record = {}

        class SampleReader(VariableReader):
            def perform_read(self, instance, owner):
                call_record["var_desc"] = self._var_desc
                call_record["instance"] = instance
                call_record["owner"] = owner
                return f"value-for-{self._var_desc.name}"

        class VariableDeclarations:
            CUSTOM = VariableDesc(section="DEFAULT")

        var_desc = VariableDeclarations.CUSTOM

        class SampleVariables:
            CUSTOM = SampleReader(var_desc)

        value = SampleVariables.CUSTOM

        self.assertEqual(value, "value-for-CUSTOM")
        self.assertIs(call_record["var_desc"], var_desc)
        self.assertIsNone(call_record["instance"])
        self.assertIs(call_record["owner"], SampleVariables)
        return

    def test_variable_reader_passes_instance_when_bound(self):
        call_record = {}

        class SampleReader(VariableReader):
            def perform_read(self, instance, owner):
                call_record["instance"] = instance
                call_record["owner"] = owner
                return "instance-value"

        class VariableDeclarations:
            BOUND = VariableDesc(section="DEFAULT")

        var_desc = VariableDeclarations.BOUND

        class SampleVariables:
            BOUND = SampleReader(var_desc)

        sample = SampleVariables()

        value = sample.BOUND

        self.assertEqual(value, "instance-value")
        self.assertIs(call_record["owner"], SampleVariables)
        self.assertIs(call_record["instance"], sample)
        return

    def test_variable_reader_requires_variable_desc_instance(self):
        with self.assertRaises(AssertionError):
            VariableReader(var_desc="not-a-variable-desc")
        return

    def test_variable_reader_requires_matching_attribute_name(self):
        class SampleReader(VariableReader):
            def perform_read(self, instance, owner):
                return "irrelevant"

        class VariableDeclarations:
            EXPECTED = VariableDesc(section="DEFAULT")

        var_desc = VariableDeclarations.EXPECTED

        with self.assertRaises(AssertionError):
            class SampleVariables:
                DIFFERENT = SampleReader(var_desc)
        return


if __name__ == '__main__':
    unittest.main()
