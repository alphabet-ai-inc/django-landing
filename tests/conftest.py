import pytest
from pytest import fixture
from faker import Faker

@fixture()
@pytest.mark.django_db
def user(django_user_model, faker: Faker, password):
    return django_user_model.objects.create_user(
        username=faker.user_name(),
        password=password,
        email=faker.email(),
        first_name=faker.first_name(),
        last_name=faker.last_name(),
        middle_name=faker.first_name(),
        group=None,
    )