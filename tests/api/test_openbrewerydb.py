import pytest
import allure
import requests
import json
from dataclasses import dataclass
from typing import Optional, Dict, Any

BASE_URL = "https://api.openbrewerydb.org/v1"


@dataclass
class APIResponse:
    status_code: int
    headers: Dict[str, str]
    body: Any
    text: str
    elapsed: float

    def __str__(self):
        return f"Status: {self.status_code}, Elapsed: {self.elapsed:.2f}s"


class BreweryAPI:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(
            {"Accept": "application/json", "User-Agent": "OpenBreweryDB-Tests/1.0"}
        )

    def _request(self, method: str, endpoint: str, **kwargs) -> APIResponse:
        url = f"{BASE_URL}/{endpoint.lstrip('/')}"

        with allure.step(f"{method.upper()} {url}"):
            response = self.session.request(method, url, **kwargs)
            api_response = APIResponse(
                status_code=response.status_code,
                headers=dict(response.headers),
                body=response.json() if response.text else None,
                text=response.text,
                elapsed=response.elapsed.total_seconds(),
            )

            allure.attach(
                json.dumps(
                    {
                        "method": method,
                        "url": url,
                        "params": kwargs.get("params"),
                        "elapsed": api_response.elapsed,
                        "status": api_response.status_code,
                    },
                    indent=2,
                ),
                name="request_details",
                attachment_type=allure.attachment_type.JSON,
            )

            return api_response

    def get_breweries(self, **params) -> APIResponse:
        return self._request("GET", "/breweries", params=params)

    def get_brewery(self, brewery_id: str) -> APIResponse:
        return self._request("GET", f"/breweries/{brewery_id}")

    def search_breweries(self, query: str) -> APIResponse:
        return self._request("GET", "/breweries/search", params={"query": query})

    def get_random_brewery(self, size: Optional[int] = None) -> APIResponse:
        params = {"size": size} if size else None
        return self._request("GET", "/breweries/random", params=params)

    def get_metadata(self) -> APIResponse:
        return self._request("GET", "/breweries/meta")


@pytest.fixture(scope="module")
def api():
    return BreweryAPI()


@pytest.fixture(autouse=True)
def check_status_code(request, api):
    yield

    if request.node.name in ["test_error_structure", "test_invalid_brewery_id"]:
        return

    response = getattr(request.node, "result", None) or request.node.funcargs.get(
        "response"
    )

    if response and hasattr(response, "status_code"):
        assert (
            response.status_code == 200
        ), f"Ожидался статус 200, получен {response.status_code}."


@allure.feature("OpenBreweryDB")
@allure.story("Тестирование API запросов")
class TestOpenBreweryDB:
    @allure.title("Получение списка пивоварен")
    def test_get_all_breweries(self, api):
        response = api.get_breweries()
        assert isinstance(response.body, list)
        assert len(response.body) > 0

    @allure.title("Фильтрация по штату")
    @pytest.mark.parametrize("state", ["california", "new_york", "ohio"])
    def test_filter_by_state(self, api, state):
        response = api.get_breweries(by_state=state)
        for brewery in response.body:
            assert brewery["state"].lower() == state.replace("_", " ")

    @allure.title("Поиск по названию")
    def test_search_by_name(self, api):
        response = api.get_breweries(by_name="dog")
        assert any("dog" in brewery["name"].lower() for brewery in response.body)

    @allure.title("Получение пивоварни по ID")
    def test_get_brewery_by_id(self, api):
        brewery_id = api.get_breweries().body[0]["id"]
        response = api.get_brewery(brewery_id)
        assert response.body["id"] == brewery_id

    @allure.title("Пагинация результатов")
    def test_pagination(self, api):
        page1 = api.get_breweries(page=1, per_page=5).body
        page2 = api.get_breweries(page=2, per_page=5).body
        assert len(page1) == 5
        assert len(page2) == 5
        assert page1[0]["id"] != page2[0]["id"]

    @allure.title("Сортировка по названию")
    def test_sort_by_name(self, api):
        response = api.get_breweries(sort="name")
        breweries = response.body
        assert breweries == sorted(breweries, key=lambda x: x["name"])

    @allure.title("Фильтр по типу пивоварни")
    @pytest.mark.parametrize("brewery_type", ["micro", "regional", "brewpub"])
    def test_filter_by_type(self, api, brewery_type):
        response = api.get_breweries(by_type=brewery_type)
        assert all(b["brewery_type"] == brewery_type for b in response.body)

    @allure.title("Поиск по городу")
    def test_filter_by_city(self, api):
        city = "san_diego"
        response = api.get_breweries(by_city=city)
        assert all(b["city"].lower() == city.replace("_", " ") for b in response.body)

    @allure.title("Количество результатов на странице")
    @pytest.mark.parametrize("per_page", [1, 5, 10])
    def test_per_page(self, api, per_page):
        response = api.get_breweries(per_page=per_page)
        assert len(response.body) == per_page

    @allure.title("Поиск по почтовому индексу")
    def test_filter_by_postal_code(self, api):
        zip_code = "92101"
        response = api.get_breweries(by_postal=zip_code)
        assert all(zip_code in b["postal_code"] for b in response.body)

    @allure.title("Автозаполнение")
    def test_autocomplete(self, api):
        query = "houston"
        response = api._request(
            "GET", "/breweries/autocomplete", params={"query": query}
        )
        assert any(brewery["city"].lower() == query for brewery in response.body)

    @allure.title("Проверка метаданных")
    def test_metadata(self, api):
        response = api.get_metadata()
        assert isinstance(response.body["total"], int)
        assert response.body["total"] > 0

    @allure.title("Неверный ID пивоварни")
    def test_invalid_brewery_id(self, api):
        response = api.get_brewery("invalid_id123")
        assert response.status_code == 404

    @allure.title("Случайная пивоварня")
    def test_random_brewery(self, api):
        response = api.get_random_brewery()
        assert isinstance(response.body, list)
        assert len(response.body) == 1

    @allure.title("Проверка структуры ответа")
    def test_brewery_structure(self, api):
        brewery = api.get_breweries().body[0]
        expected_keys = {
            "id",
            "name",
            "brewery_type",
            "city",
            "state_province",
            "country",
        }
        assert expected_keys.issubset(brewery.keys())

    @allure.title("Фильтр по стране")
    def test_filter_by_country(self, api):
        response = api.get_breweries(by_country="united_states")
        assert all(b["country"] == "United States" for b in response.body)

    @allure.title("Поиск по телефону")
    def test_search_by_phone(self, api):
        phone = "619"
        response = api.get_breweries(by_phone=phone)
        assert any(b.get("phone", "").startswith(phone) for b in response.body)

    @allure.title("Комбинированные фильтры")
    def test_combined_filters(self, api):
        state = "california"
        brewery_type = "micro"
        response = api.get_breweries(by_state=state, by_type=brewery_type)
        for brewery in response.body:
            assert brewery["state"] == "California"
            assert brewery["brewery_type"] == "micro"

    @allure.title("Несколько случайных пивоварен")
    def test_multiple_random_breweries(self, api):
        response = api.get_random_brewery(size=3)
        assert len(response.body) == 3

    @allure.title("Проверка пустого ответа")
    def test_empty_response(self, api):
        response = api.get_breweries(by_name="nonexistentname123")
        assert len(response.body) == 0

    @allure.title("Проверка структуры ошибки")
    def test_error_structure(self, api):
        response = api._request("GET", "/invalid_endpoint")
        assert response.status_code == 404
        assert "message" in response.body
