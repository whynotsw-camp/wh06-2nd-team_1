import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


class OTTSearcher:
    def __init__(self, api_key, cse_id):
        self.api_key = api_key
        self.cse_id = cse_id
        self.session = self._create_retry_session()

    def _create_retry_session(self):
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,  # 재시도 간 딜레이 (1s, 2s, 4s ...)
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "OPTIONS"]
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session = requests.Session()
        session.mount("https://", adapter)
        return session

    def find(self, movie_title, ott_names):
        try:
            query = f"{movie_title} site:justwatch.com"
            params = {
                "q": query,
                "key": self.api_key,
                "cx": self.cse_id,
            }
            response = self.session.get("https://www.googleapis.com/customsearch/v1", params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            result_string = str(data).lower()
            return {platform: (platform.lower() in result_string) for platform in ott_names}

        except requests.exceptions.SSLError as e:
            print(f"🚨 SSL 오류: {type(e).__name__} - {e}")
            return {platform: False for platform in ott_names}
        except requests.exceptions.RequestException as e:
            print(f"🚨 요청 오류: {type(e).__name__} - {e}")
            return {platform: False for platform in ott_names}
