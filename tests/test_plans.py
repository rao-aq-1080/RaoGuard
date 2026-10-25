from backend.services.plans import get_plan, limit_message


def _u(projects=0, total=0, month=0, seats=1):
    return {
        "active_projects": projects,
        "analyses_total": total,
        "analyses_month": month,
        "seats": seats,
    }


def test_free_is_the_trial():
    p = get_plan("free")
    assert p["price"] == 0
    assert p["max_active_projects"] == 1
    assert p["max_analyses_total"] == 20
    assert p["max_seats"] == 1


def test_paid_catalog():
    assert get_plan("starter")["price"] == 29
    assert get_plan("studio")["price"] == 59
    assert get_plan("agency")["price"] == 89
    assert get_plan("agency")["white_label"] is True


def test_free_allows_first_project():
    assert limit_message("project", get_plan("free"), _u(projects=0)) is None


def test_free_blocks_second_project():
    msg = limit_message("project", get_plan("free"), _u(projects=1))
    assert msg and "1 live project" in msg


def test_free_allows_check_under_cap():
    assert limit_message("analyze", get_plan("free"), _u(total=19)) is None


def test_free_blocks_21st_check():
    msg = limit_message("analyze", get_plan("free"), _u(total=20))
    assert msg and "20 SOW checks" in msg


def test_free_blocks_extra_seat():
    msg = limit_message("seat", get_plan("free"), _u(seats=1))
    assert msg and "one seat" in msg


def test_starter_month_cap():
    msg = limit_message("analyze", get_plan("starter"), _u(month=100))
    assert msg and "100" in msg


def test_studio_unlimited():
    p = get_plan("studio")
    u = _u(projects=99, total=999, month=999, seats=20)
    assert limit_message("project", p, u) is None
    assert limit_message("analyze", p, u) is None
    assert limit_message("seat", p, u) is None
