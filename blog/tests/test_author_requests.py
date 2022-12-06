from typing import Callable, Dict
import pytest
from strawberry.test import Response

from blog.models import User, UserStatus


@pytest.mark.django_db(transaction=True, reset_sequences=True)
def test_create_update_and_query_author_request(
    auth: Callable,
    import_query: Callable,
    client_query: Callable,
) -> None:
    auth(is_author=False)

    user = User.objects.get(username='jane.doe@blogapp.lo')
    user_status = UserStatus.objects.get(user=user)
    assert user_status.is_author is False

    query: str = import_query('createAuthorRequest.graphql')
    response: Response = client_query(query)
    assert response is not None
    author_request_wrapper: Dict = response.data.get('createAuthorRequest', None)
    assert author_request_wrapper is not None

    success: Dict = author_request_wrapper.get('success', None)
    assert success is not None
    assert success is True
    errors: Dict = author_request_wrapper.get('errors', None)
    assert errors is None

    author_request: Dict = author_request_wrapper.get('authorRequest', None)
    assert author_request is not None
    assert author_request.get('dateOpened', None) is not None
    assert author_request.get('dateClosed', None) is None
    assert author_request.get('status', None) == 'PENDING'

    author_request_input = {
        'authorRequestInput': {
            'user': 1,
            'status': 'ACCEPTED',
        }
    }

    query: str = import_query('updateAuthorRequest.graphql')
    response: Response = client_query(query, author_request_input)
    assert response is not None
    author_request_wrapper: Dict = response.data.get('updateAuthorRequest', None)
    assert author_request_wrapper is not None

    success: Dict = author_request_wrapper.get('success', None)
    assert success is not None
    assert success is True
    errors: Dict = author_request_wrapper.get('errors', None)
    assert errors is None

    author_request: Dict = author_request_wrapper.get('authorRequest', None)
    assert author_request is not None
    assert author_request.get('dateOpened', None) is not None
    assert author_request.get('dateClosed', None) is not None
    assert author_request.get('status', None) == 'ACCEPTED'

    query: str = import_query('getAuthorRequestByUser.graphql')
    response: Response = client_query(query)
    assert response is not None
    author_request: Dict = response.data.get('authorRequestByUser', None)
    assert author_request is not None
    assert author_request.get('dateOpened', None) is not None
    assert author_request.get('dateClosed', None) is not None
    assert author_request.get('status', None) == 'ACCEPTED'

    user_status = UserStatus.objects.get(user=user)
    assert user_status.is_author is True


@pytest.mark.django_db(transaction=True, reset_sequences=True)
def test_query_author_requests(
    auth: Callable,
    create_author_requests: Callable,
    import_query: Callable,
    client_query: Callable,
) -> None:
    auth(is_author=False)
    create_author_requests()

    author_requests_input = {
        'status': 'ACCEPTED',
        'activePage': 1,
    }

    query: str = import_query('getAuthorRequests.graphql')
    response: Response = client_query(query)
    assert response is not None
    paginated_author_requests: Dict = response.data.get('paginatedAuthorRequests', author_requests_input)
    assert paginated_author_requests is not None

    num_pages: Dict = paginated_author_requests.get('numPages', None)
    assert num_pages is not None
    assert num_pages == 1

    author_requests: Dict = paginated_author_requests.get('authorRequests', None)
    assert author_requests is not None
    assert len(author_requests) == 2
    author_request_status1 = author_requests[0].get('status', None)
    assert author_request_status1 is not None
    assert author_request_status1 == 'REJECTED'
    author_request_status2 = author_requests[1].get('status', None)
    assert author_request_status2 is not None
    assert author_request_status2 == 'PENDING'
