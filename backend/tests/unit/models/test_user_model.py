from models.user import UserRow


def test_registration_profile_fields_are_optional() -> None:
    profile_fields = (
        "dob",
        "address_line",
        "city",
        "county",
        "postcode",
    )

    for field_name in profile_fields:
        assert UserRow.__table__.c[field_name].nullable is True
