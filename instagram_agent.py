import os
from typing import Dict, Optional, Union
from datetime import datetime
import requests
from PIL import Image
from io import BytesIO
from gemini_helper import generate_caption
import base64
from customer_search import ImageSearch


class InstagramAgent:
    def __init__(self):
        self.post_history: Dict[str, datetime] = {}
        self.image_cache: Dict[str, bytes] = {}
        self.instagram_access_token = os.getenv("INSTAGRAM_ACCESS_TOKEN")
        self.instagram_account_id = os.getenv("INSTAGRAM_ACCOUNT_ID")
        self.customer_search = ImageSearch()

    def _search_image(self, query: str) -> Optional[str]:
        """
        Google Custom Search API kullanarak görsel araması yapar.

        Args:
            query (str): Arama sorgusu

        Returns:
            Optional[str]: Bulunan görselin URL'si
        """

        return self.customer_search.search_image(query)

    def _download_image(self, image_url: str) -> Optional[bytes]:
        """
        URL'den görseli indirir ve cache'ler.

        Args:
            image_url (str): Görsel URL'si

        Returns:
            Optional[bytes]: İndirilen görselin binary verisi
        """
        try:
            if image_url in self.image_cache:
                return self.image_cache[image_url]

            response = requests.get(image_url)
            if response.status_code == 200:
                image_data = response.content
                self.image_cache[image_url] = image_data
                return image_data
            return None

        except Exception as e:
            print(f"Görsel indirme hatası: {str(e)}")
            return None

    def _upload_to_instagram(self, image_data: bytes, caption: str) -> Dict:
        """
        Görseli ve açıklamayı Instagram'a yükler.

        Args:
            image_data (bytes): Yüklenecek görsel
            caption (str): Post açıklaması

        Returns:
            Dict: Yükleme sonucu
        """
        try:
            if not self.instagram_access_token or not self.instagram_account_id:
                raise ValueError("Instagram API bilgileri eksik!")

            # 1. Görseli Facebook'a yükle
            url = f"https://graph.facebook.com/v18.0/{self.instagram_account_id}/media"
            image_b64 = base64.b64encode(image_data).decode('utf-8')

            data = {
                "image_url": f"data:image/jpeg;base64,{image_b64}",
                "caption": caption,
                "access_token": self.instagram_access_token
            }

            response = requests.post(url, data=data)
            response.raise_for_status()
            creation_id = response.json()["id"]

            # 2. Yüklenen görseli yayınla
            publish_url = f"https://graph.facebook.com/v18.0/{self.instagram_account_id}/media_publish"
            publish_data = {
                "creation_id": creation_id,
                "access_token": self.instagram_access_token
            }

            response = requests.post(publish_url, data=publish_data)
            response.raise_for_status()

            return {
                "success": True,
                "post_id": response.json()["id"],
                "message": "Post başarıyla paylaşıldı!"
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "Post paylaşımı başarısız oldu!"
            }

    def create_post(self,
                    product_name: str,
                    description: str,
                    image_path: Optional[str] = None,
                    publish_to_instagram: bool = False) -> Dict:
        """
        Instagram postu oluşturur ve isteğe bağlı olarak paylaşır.

        Args:
            product_name (str): Ürün adı
            description (str): Ürün açıklaması
            image_path (str, optional): Yüklenecek görselin dosya yolu
            publish_to_instagram (bool): Instagram'da paylaşılacak mı?

        Returns:
            Dict: Post detayları ve paylaşım sonucu
        """
        # Gemini ile caption oluştur
        caption = generate_caption(product_name, description)

        # Görsel işleme
        image_data = None
        if image_path:
            # Kullanıcının yüklediği görseli kullan
            try:
                with open(image_path, 'rb') as f:
                    image_data = f.read()
            except Exception as e:
                print(f"Görsel yükleme hatası: {str(e)}")
        else:
            # Web'den görsel ara
            search_query = f"{product_name} {description}"
            found_image_url = self._search_image(search_query)
            if found_image_url:
                image_data = self._download_image(found_image_url)

        # Post bilgilerini kaydet
        post_id = f"post_{len(self.post_history) + 1}"
        self.post_history[post_id] = datetime.now()

        result = {
            "post_id": post_id,
            "caption": caption,
            "product_name": product_name,
            "description": description,
            "image_data": image_data,
            "created_at": self.post_history[post_id]
        }

        # Instagram'da paylaş
        if publish_to_instagram and image_data:
            instagram_result = self._upload_to_instagram(image_data, caption)
            result["instagram"] = instagram_result

        return result

    def get_post_history(self) -> Dict[str, datetime]:
        """
        Oluşturulan postların geçmişini döndürür.

        Returns:
            Dict[str, datetime]: Post ID'leri ve oluşturulma tarihleri
        """
        return self.post_history


#if __name__ == "__main__":
    # Test
 #   agent = InstagramAgent()
  #  post = agent.create_post(
   #     product_name="Altın Kolye",
     #   description="El işçiliği, zarif tasarım"
    #)
    #print("Oluşturulan Post:")
    #print(f"Caption: {post['caption']}")
    #print(f"Ürün: {post['product_name']}")
    #print(f"Görsel verisi mevcut: {'Evet' if post['image_data'] else 'Hayır'}")