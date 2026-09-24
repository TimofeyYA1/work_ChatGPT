from vfs_france_monitor.vfs import parse_slot_response


def test_earliest_date_means_available() -> None:
    result = parse_slot_response(200, {"earliestDate": "10/09/2026 00:00:00", "error": None})
    assert result.available is True
    assert result.status == "available"
    assert result.earliest_date == "10/09/2026 00:00:00"


def test_error_without_date_means_no_slots() -> None:
    result = parse_slot_response(200, {"earliestDate": "", "error": "No slots"})
    assert result.available is False
    assert result.status == "no_slots"


def test_non_json_response_is_unknown() -> None:
    result = parse_slot_response(502, "upstream error")
    assert result.available is False
    assert result.status == "unknown"
