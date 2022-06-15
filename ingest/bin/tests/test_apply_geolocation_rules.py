import pytest
from ..apply_geolocation_rules import load_geolocation_rules, get_annotated_geolocation


def write_file_with_lines(tmpdir, lines):
    """Write a file `test_file.txt` with the provided lines."""
    geolocation_rules_file = tmpdir.join("test_file.txt")
    with open(geolocation_rules_file, 'w') as f:
            f.write('\n'.join(lines))
    return geolocation_rules_file


def get_geolocation_rules(tmpdir, lines):
    """Get geolocation rules from the provided lines."""
    geolocation_rules_file = write_file_with_lines(tmpdir, lines)
    return load_geolocation_rules(geolocation_rules_file)


class TestLoadGeolocationRules:
    "Tests for loading geolocation rules files."

    def test_load_with_comment(self, tmpdir):
        """Test that a line starting with `#` is skipped."""
        lines = (
            "# This is a comment",
        )
        geolocation_rules_file = write_file_with_lines(tmpdir, lines)
        geolocation_rules = load_geolocation_rules(geolocation_rules_file)
        assert geolocation_rules == {}

    def test_load_with_inline_comment(self, tmpdir):
        """Test that `#` and any following characters are treated as an inline comment."""
        lines = (
            "a/b/c/d\t1/2/3/4 # this is a comment",
            "a/b/c/e\t1/2/3/# 4 this is a comment",
        )
        geolocation_rules_file = write_file_with_lines(tmpdir, lines)
        geolocation_rules = load_geolocation_rules(geolocation_rules_file)
        assert geolocation_rules["a"]["b"]["c"]["d"] == ("1", "2", "3", "4")
        assert geolocation_rules["a"]["b"]["c"]["e"] == ("1", "2", "3", "")

    def test_load_with_wildcard_character(self, tmpdir):
        """Test that `*` characters can be loaded."""
        lines = (
            "a/b/*/*\t1/2/*/*",
            "a/b/c/*\t1/2/3/4",
        )
        geolocation_rules_file = write_file_with_lines(tmpdir, lines)
        geolocation_rules = load_geolocation_rules(geolocation_rules_file)
        assert geolocation_rules["a"]["b"]["*"]["*"] == ("1", "2", "*", "*")
        assert geolocation_rules["a"]["b"]["c"]["*"] == ("1", "2", "3", "4")

    def test_load_with_empty(self, tmpdir):
        """Test that an empty field can be loaded in the raw and/or annotated column."""
        lines = (
            "a/b//\ta/b/c/d",
            "a/b/c/d\ta/b//",
            "a/c//\ta/b//",
        )
        geolocation_rules_file = write_file_with_lines(tmpdir, lines)
        geolocation_rules = load_geolocation_rules(geolocation_rules_file)
        assert geolocation_rules["a"]["b"][""][""] == ("a", "b", "c", "d")
        assert geolocation_rules["a"]["b"]["c"]["d"] == ("a", "b", "", "")
        assert geolocation_rules["a"]["c"][""][""] == ("a", "b", "", "")


class TestGetAnnotatedGeolocation:
    "Tests for getting an annotated geolocation."

    def test_simple_rule(self, tmpdir):
        """Test that a simple rule works."""
        lines = (
            "a/b/c/d\t1/2/3/4",
        )
        geolocation_rules = get_geolocation_rules(tmpdir, lines)
        assert get_annotated_geolocation(geolocation_rules, ("a", "b", "c", "d")) == ("1", "2", "3", "4")

    def test_none_if_no_matching_rule(self, tmpdir):
        """Test that `None` is returned when there is no matching rule."""
        lines = (
            "a/b/c/d\t1/2/3/4",
        )
        geolocation_rules = get_geolocation_rules(tmpdir, lines)
        assert get_annotated_geolocation(geolocation_rules, ("a", "a", "a", "a")) is None

    def test_get_annotated_geolocation_wildcards(self, tmpdir):
        """Test that wildcards work."""
        lines = (
            "a/b/*/*\t1/2/*/*",
        )
        geolocation_rules = get_geolocation_rules(tmpdir, lines)
        assert get_annotated_geolocation(geolocation_rules, ("a", "b", "c", "d")) == ("1", "2", "*", "*")

    @pytest.mark.parametrize(
        "raw_location, matching_annotation",
        [
            (("a", "b", "c", "d"), ("*", "2", "3", "4")),
            (("e", "f", "g", "h"), ("5", "*", "7", "8")),
            (("i", "j", "k", "l"), ("9", "10", "*", "12")),
            (("m", "n", "o", "p"), ("13", "14", "15", "*")),
            (("q", "r", "s", "t"), ("17", "*", "*", "20")),
            (("u", "v", "w", "x"), ("*", "*", "*", "24")),
        ]
    )
    def test_wildcards_work_in_all_fields(self, tmpdir, raw_location, matching_annotation):
        """Test that wildcards work in any field."""
        lines = (
            "*/b/c/d\t*/2/3/4",
            "e/*/g/h\t5/*/7/8",
            "i/j/*/l\t9/10/*/12",
            "m/n/o/*\t13/14/15/*",
            "q/*/*/t\t17/*/*/20",
            "*/*/*/x\t*/*/*/24",
        )
        geolocation_rules = get_geolocation_rules(tmpdir, lines)
        assert get_annotated_geolocation(geolocation_rules, raw_location) == matching_annotation

    def test_matching_rule_over_wildcards(self, tmpdir):
        """Test that matching rules are used over wildcards."""
        lines = (
            "a/b/c/d\t1/2/3/4",
            "a/*/*/*\t1/*/*/*",
        )
        geolocation_rules = get_geolocation_rules(tmpdir, lines)
        assert get_annotated_geolocation(geolocation_rules, ("a", "b", "c", "d")) == ("1", "2", "3", "4")

    def test_wildcards_work_if_partial_match_exists(self, tmpdir):
        """Test wildcards still work even when partial matches exist."""
        lines = (
            "a/b/c/d\t1/2/3/4",
            "a/*/*/z\t1/*/*/26",
        )
        geolocation_rules = get_geolocation_rules(tmpdir, lines)
        assert get_annotated_geolocation(geolocation_rules, ("a", "b", "c", "z")) == ("1", "*", "*", "26")
