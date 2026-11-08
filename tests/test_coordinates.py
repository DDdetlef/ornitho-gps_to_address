from scripts.coordinates import calculate_distance_meters, coordinates_are_valid


def test_coordinates_are_valid():
    assert coordinates_are_valid(52.5, 13.4)
    assert not coordinates_are_valid(95, 13.4)


def test_distance_same_point_is_zero():
    assert calculate_distance_meters(52.5, 13.4, 52.5, 13.4) == 0.0
