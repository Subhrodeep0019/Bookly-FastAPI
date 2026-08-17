import uuid
from datetime import datetime
from src.books.schemas import ModelBook, ModelCreateBook, ModelUpdBook


book_url_prefix = "/v1/books"

fake_book_data = [{
        "uid": str(uuid.uuid4()),
        "title": "Test Book",
        "author": "Test Author",
        "publisher": "Test Publisher",
        "publish_date": "2024-01-01",
        "page_count": 200,
        "language": "English",
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat(),
    }]



def test_get_all_books(test_client, fake_book_service, fake_session):

    fake_book_service.get_all_books.return_value = fake_book_data

    response = test_client.get(url=f"{book_url_prefix}/")

    assert response.status_code == 200
    assert response.json() == fake_book_data
    fake_book_service.get_all_books.assert_called_once_with(fake_session)


def test_get_my_books(fake_uid_fixture, test_client, fake_book_service, fake_session):

    fake_book_service.get_my_books.return_value = fake_book_data

    response = test_client.get(url=f"{book_url_prefix}/my_books/")

    assert response.status_code == 200
    assert response.json() == fake_book_data
    fake_book_service.get_my_books.assert_called_once_with(fake_uid_fixture, fake_session)


def test_get_a_book(fake_uid_fixture, test_client, fake_book_service, fake_session):

    fake_rev_uid = uuid.uuid4()
    fake_book_data_with_review = {
        "uid": str(fake_uid_fixture),
        "title": "Test Book",
        "author": "Test Author",
        "publisher": "Test Publisher",
        "publish_date": "2024-01-01",
        "page_count": 200,
        "language": "English",
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat(),
        "reviews": [{
            "uid": str(fake_rev_uid),
            "rating": 5,
            "review_text": "test review",
            "user_uid": str(fake_uid_fixture),
            "book_uid": str(fake_uid_fixture),
            "created_at": datetime.now().isoformat(),
        }]
    }

    fake_book_service.get_a_book.return_value = fake_book_data_with_review

    response = test_client.get(url=f"{book_url_prefix}/{fake_uid_fixture}/")

    assert response.status_code == 200
    assert response.json() == fake_book_data_with_review
    fake_book_service.get_a_book.assert_called_once_with(fake_uid_fixture, fake_session)

response_book = ModelBook(
    uid = uuid.uuid4(),
    title = "test book",
    author = "test author",
    publisher = "test publisher",
    publish_date = datetime.now().date(),
    page_count = 999,
    language = "English",
    created_at = datetime.now(),
    updated_at = datetime.now(),
)


def test_add_book(fake_uid_fixture, test_client, fake_book_service, fake_session):
    create_book = ModelCreateBook(
        title = "test book",
        author = "test author",
        publisher = "test publisher",
        publish_date = datetime.now().date(),
        page_count = 999,
        language = "English",
    )
    fake_book_service.create_book.return_value = response_book
    response = test_client.post(url=f"{book_url_prefix}/", json=create_book.model_dump(mode="json"))
    assert response.status_code == 201
    assert ModelBook(**response.json()) == response_book
    fake_book_service.create_book.assert_called_once_with(create_book, str(fake_uid_fixture), fake_session)


def test_upd_book(test_client, fake_uid_fixture, fake_book_service, fake_session):
    update_det = ModelUpdBook(
        title="test book",
        author="test author",
        publisher="test publisher",
        publish_date=datetime.now().date(),
        page_count=999,
        language="English",
    )
    fake_book_service.update_book.return_value = response_book
    response = test_client.patch(
        url=f"{book_url_prefix}/{fake_uid_fixture}",
        json=response_book.model_dump(mode="json")
    )

    assert response.status_code == 200
    assert ModelBook(**response.json()) == response_book

    fake_book_service.update_book.assert_called_once_with(fake_uid_fixture, update_det, fake_session)


def test_del_book(test_client, fake_uid_fixture, fake_book_service, fake_session):
     fake_book_service.delete_book.return_value = response_book

     response = test_client.delete(url=f"{book_url_prefix}/{fake_uid_fixture}")
     assert response.status_code == 200
     assert ModelBook(**response.json()) == response_book

     fake_book_service.delete_book.assert_called_once_with(fake_uid_fixture, fake_session)