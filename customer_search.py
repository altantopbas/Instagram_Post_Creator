import requests
from typing import Optional, List, Dict


class ImageSearch:
    def __init__(self):
        try:
            self.api_key = open('API_KEY').read().strip()
            self.search_engine_id = open('SEARCH_ENGINE_ID').read().strip()
        except FileNotFoundError:
            print("API_KEY veya SEARCH_ENGINE_ID dosyaları bulunamadı!")
            self.api_key = None
            self.search_engine_id = None

    def search_image(self, query: str) -> Optional[str]:
        """
        Google Custom Search API kullanarak görsel araması yapar.

        Args:
            query (str): Arama sorgusu

        Returns:
            Optional[str]: Bulunan görselin URL'si
        """
        try:
            if not self.api_key or not self.search_engine_id:
                raise ValueError("Google API bilgileri eksik!")

            url = "https://www.googleapis.com/customsearch/v1"
            params = {
                'q': query,
                'key': self.api_key,
                'cx': self.search_engine_id,
                'searchType': 'image',
                'timeRestrict': '2020-01-01:2025-12-31'
            }

            response = requests.get(url, params=params)
            response.raise_for_status()

            data = response.json()
            if 'items' in data and len(data['items']) > 0:
                return data['items'][0]['link']
            return None

        except Exception as e:
            print(f"Görsel arama hatası: {str(e)}")
            return None

    def search_images(self, query: str) -> List[Dict]:
        """
        Google Custom Search API kullanarak birden fazla görsel araması yapar.

        Args:
            query (str): Arama sorgusu

        Returns:
            List[Dict]: Bulunan görsellerin listesi
        """
        try:
            if not self.api_key or not self.search_engine_id:
                raise ValueError("Google API bilgileri eksik!")

            url = "https://www.googleapis.com/customsearch/v1"
            params = {
                'q': query,
                'key': self.api_key,
                'cx': self.search_engine_id,
                'searchType': 'image',
                'timeRestrict': '2020-01-01:2025-12-31'
            }

            response = requests.get(url, params=params)
            response.raise_for_status()

            data = response.json()
            if 'items' in data:
                return data['items']
            return []

        except Exception as e:
            print(f"Görsel arama hatası: {str(e)}")
            return []


if __name__ == "__main__":
    # Test
    searcher = ImageSearch()

    # Tek görsel arama testi
    image_url = searcher.search_image("altın kolye")
    if image_url:
        print(f"Bulunan görsel URL'si: {image_url}")
    else:
        print("Görsel bulunamadı")

    # Çoklu görsel arama testi
    images = searcher.search_images("altın kolye")
    print(f"\nBulunan toplam görsel sayısı: {len(images)}")
    for item in images:
        print(item['link'])