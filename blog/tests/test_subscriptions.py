from datetime import datetime
from typing import Callable, Dict
import pytest
from strawberry.test import Response

from blog.models import Subscription, Notification


@pytest.mark.django_db(transaction=True, reset_sequences=True)
def test_create_subscription(
    auth: Callable,
    create_users: Callable,
    import_query: Callable,
    client_query: Callable,
) -> None:
    auth()
    create_users()

    subscription_input = {
        'subscriptionInput': {
            'subscriber': 1,
            'author': 3,
        }
    }

    query: str = import_query('createSubscription.graphql')
    response: Response = client_query(query, subscription_input)

    assert response is not None
    assert response.errors is None

    create_subscription: Dict = response.data.get('createSubscription', None)
    assert create_subscription is not None

    success: Dict = create_subscription.get('success', None)
    assert success is True
    errors: Dict = create_subscription.get('errors', None)
    assert errors is None

    subscription: Dict = create_subscription.get('subscription', None)
    assert subscription is not None

    subscriber: Dict = subscription.get('subscriber', None)
    assert subscriber is not None
    assert subscriber.get('id', None) == '1'

    author: Dict = subscription.get('author', None)
    assert author is not None
    assert author.get('id', None) == '3'


@pytest.mark.django_db(transaction=True, reset_sequences=True)
def test_create_duplicate_subscription(
    auth: Callable,
    create_users: Callable,
    import_query: Callable,
    client_query: Callable,
) -> None:
    auth()
    create_users()
    Subscription.objects.create(subscriber_id=1, author_id=3, date_created=datetime(2023, 3, 22, 00, 00, 00, 000000))

    subscription_input = {
        'subscriptionInput': {
            'subscriber': 1,
            'author': 3,
        }
    }

    query: str = import_query('createSubscription.graphql')
    response: Response = client_query(query, subscription_input)

    assert response is not None
    assert response.errors is None

    create_subscription: Dict = response.data.get('createSubscription', None)
    assert create_subscription is not None

    success: Dict = create_subscription.get('success', None)
    assert success is False
    errors: Dict = create_subscription.get('errors', None)
    assert errors is not None

    errors_list: Dict = errors.get('__all__', None)
    assert errors_list is not None
    assert errors_list[0].get('code', None) == 'unique_together'


@pytest.mark.django_db(transaction=True, reset_sequences=True)
def test_delete_subscription(
    auth: Callable,
    create_posts: Callable,
    import_query: Callable,
    client_query: Callable,
) -> None:
    create_posts()
    auth()

    Subscription.objects.create(subscriber_id=3, author_id=2, date_created=datetime(2023, 3, 22, 00, 00, 00, 000000))
    Notification.objects.create(user_id=3, post_id=2)

    assert len(Subscription.objects.all()) == 1
    assert len(Notification.objects.all()) == 1

    subscription_input = {
        'subscriptionInput': {
            'subscriber': 3,
            'author': 2,
        }
    }
    query: str = import_query('deleteSubscription.graphql')
    response: Response = client_query(query, subscription_input)
    assert response is not None
    assert response.errors is None
    assert response.data.get('deleteSubscription', None) is True

    assert len(Subscription.objects.all()) == 0
    assert len(Notification.objects.all()) == 0


@pytest.mark.django_db(transaction=True, reset_sequences=True)
def test_delete_subscription_unauthenticated(
    auth: Callable,
    create_posts: Callable,
    import_query: Callable,
    client_query: Callable,
) -> None:
    create_posts()

    Subscription.objects.create(subscriber_id=1, author_id=2, date_created=datetime(2023, 3, 22, 00, 00, 00, 000000))
    Notification.objects.create(user_id=1, post_id=2)

    assert len(Subscription.objects.all()) == 1
    assert len(Notification.objects.all()) == 1

    subscription_input = {
        'subscriptionInput': {
            'subscriber': 1,
            'author': 2,
        }
    }
    query: str = import_query('deleteSubscription.graphql')
    response: Response = client_query(query, subscription_input)

    assert response is not None
    assert response.data is None
    assert response.errors is not None

    assert len(response.errors) > 0
    error: Dict = response.errors[0]
    extensions = error.get('extensions', None)
    assert extensions is not None
    assert extensions.get('code', None) == 'PERMISSION_DENIED'

    assert len(Subscription.objects.all()) == 1
    assert len(Notification.objects.all()) == 1


@pytest.mark.django_db(transaction=True, reset_sequences=True)
def test_query_user_subscriptions(
    create_subscription: Callable,
    login: Callable,
    import_query: Callable,
    client_query: Callable,
) -> None:
    create_subscription()
    login('test_user1', 'password1')

    query: str = import_query('getUserSubscriptions.graphql')
    response: Response = client_query(query)

    assert response is not None
    assert response.errors is None

    user_subscriptions: Dict = response.data.get('userSubscriptions', None)
    assert user_subscriptions is not None
    assert len(user_subscriptions) == 1
    subscription = user_subscriptions[0]

    author: Dict = subscription.get('author', None)
    assert author is not None
    assert author.get('username', None) == 'test_user2'

    subscriber: Dict = subscription.get('subscriber', None)
    assert subscriber is not None
    assert subscriber.get('username', None) == 'test_user1'


@pytest.mark.django_db(transaction=True, reset_sequences=True)
def test_query_user_subscriptions_unauthenticated(
    create_subscription: Callable,
    import_query: Callable,
    client_query: Callable,
) -> None:
    create_subscription()

    query: str = import_query('getUserSubscriptions.graphql')
    response: Response = client_query(query)

    assert response is not None
    assert response.data is None
    assert response.errors is not None

    assert len(response.errors) > 0
    error: Dict = response.errors[0]
    extensions = error.get('extensions', None)
    assert extensions is not None
    assert extensions.get('code', None) == 'PERMISSION_DENIED'
