# Reference template for Python test generation. Not loaded at runtime —
# the generator builds test content programmatically via render_python().
#
# pytest fixtures: use @pytest.fixture for setup/teardown if needed
# @pytest.fixture
# def my_fixture():
#     yield resource
#     cleanup()
#
# Parametrize: use @pytest.mark.parametrize for multiple test cases
# @pytest.mark.parametrize("value", [1, 2, 3])
# def test_example(value):
#     assert value > 0


def test_scenario():
    assert False, "RED: scenario description"
