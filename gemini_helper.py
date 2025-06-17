import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)

model = genai.GenerativeModel("gemini-2.0-flash-exp")


def detect_language(text: str) -> str:
    """
    Metnin dilini tespit eder.

    Args:
        text (str): Tespit edilecek metin

    Returns:
        str: Dil kodu (tr, en, de, fr, es, it)
    """
    prompt = f"""
    Aşağıdaki metnin dilini tespit et ve sadece dil kodunu döndür (tr, en, de, fr, es, it):

    Metin: {text}

    Sadece dil kodunu döndür, başka bir şey yazma.
    """

    response = model.generate_content(prompt)
    return response.text.strip().lower()


def generate_caption(product_name: str, description: str, language: str = None) -> str:
    """
    Ürün için Instagram post metni oluşturur.

    Args:
        product_name (str): Ürün adı
        description (str): Ürün açıklaması
        language (str, optional): İstenen dil kodu. Belirtilmezse açıklamadan tespit edilir.

    Returns:
        str: Oluşturulan caption
    """
    # Dil tespiti
    if not language:
        language = detect_language(description)

    # Dil bazlı prompt oluşturma
    language_prompts = {
        "tr": "Türkçe",
        "en": "English",
        "de": "German",
        "fr": "French",
        "es": "Spanish",
        "it": "Italian"
    }

    target_language = language_prompts.get(language, "English")

    prompt = f"""
    Product Name: {product_name}
    Product Description: {description}

    I want to share this product on Instagram. Write a creative, impressive caption in {target_language}.
    The text should be emotional and unique. Don't be too exaggerated, keep it casual and engaging.
    Include relevant hashtags at the end.
    Inform the user that an API is required for Instagram sharing. 
        -Also tell the user how to get the Instagram API step by step.

    Format:
    - Main caption
    - 5-7 relevant hashtags
    - Instagram API information
    - Line break
    """

    response = model.generate_content(prompt)
    return response.text.strip()


if __name__ == "__main__":
    # Test
    caption = generate_caption("Altın Küpe", "El işçiliği, zarif ve minimal tasarım.")
    print(caption)

