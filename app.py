import streamlit as st
from instagram_agent import InstagramAgent
import tempfile
import os
from dotenv import load_dotenv

# Environment variables yükle
load_dotenv()

# API anahtarlarını kontrol et
if not os.getenv("GEMINI_API_KEY"):
    st.error("GEMINI_API_KEY bulunamadı! Lütfen .env dosyasına ekleyin veya environment variable olarak ayarlayın.")
    st.stop()

if not os.getenv("UNSPLASH_ACCESS_KEY"):
    st.error("UNSPLASH_ACCESS_KEY bulunamadı! Lütfen .env dosyasına ekleyin veya environment variable olarak ayarlayın.")
    st.stop()

st.set_page_config(
    page_title="Instagram Post Oluşturucu",
    page_icon="📸",
    layout="wide"
)

st.title("📸 Instagram Post Oluşturucu")

# Sidebar
st.sidebar.header("Ayarlar")
st.sidebar.info(
    "Bu uygulama ile Instagram postları oluşturabilirsiniz. "
    "Ürün bilgilerini girin ve görsel seçin veya otomatik görsel arayın."
)

# Ana form
with st.form("post_form"):
    col1, col2 = st.columns(2)

    with col1:
        product_name = st.text_input("Ürün Adı", placeholder="Örn: Altın Kolye")
        description = st.text_area("Ürün Açıklaması",
                                   placeholder="Örn: El işçiliği, zarif tasarım, 14 ayar altın")

    with col2:
        st.subheader("Görsel Seçenekleri")
        image_option = st.radio(
            "Görsel kaynağını seçin:",
            ["Görsel Yükle", "Otomatik Görsel Ara"],
            horizontal=True
        )

        if image_option == "Görsel Yükle":
            uploaded_file = st.file_uploader("Görsel Yükle", type=["jpg", "jpeg", "png"])
        else:
            st.info("Ürün bilgilerine göre otomatik görsel aranacak")

    submit_button = st.form_submit_button("Post Oluştur")

# Form gönderildiğinde
if submit_button:
    if not product_name or not description:
        st.error("Lütfen ürün adı ve açıklaması girin!")
    else:
        try:
            with st.spinner("Post oluşturuluyor..."):
                agent = InstagramAgent()

                # Görsel işleme
                image_path = None
                if image_option == "Görsel Yükle" and uploaded_file is not None:
                    # Yüklenen dosyayı geçici olarak kaydet
                    with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as tmp_file:
                        tmp_file.write(uploaded_file.getvalue())
                        image_path = tmp_file.name

                # Post oluştur
                post = agent.create_post(
                    product_name=product_name,
                    description=description,
                    image_path=image_path
                )

                # Sonuçları göster
                st.success("Post başarıyla oluşturuldu!")

                # İki sütunlu görünüm
                col1, col2 = st.columns(2)

                with col1:
                    st.subheader("Post Detayları")
                    st.write(f"**Ürün:** {post['product_name']}")
                    st.write(f"**Açıklama:** {post['description']}")
                    st.write("**Caption:**")
                    st.info(post['caption'])

                with col2:
                    st.subheader("Görsel")
                    if post['image_data']:
                        st.image(post['image_data'], use_column_width=True)
                    else:
                        st.warning("Görsel bulunamadı!")

                # Geçici dosyayı temizle
                if image_path and os.path.exists(image_path):
                    os.unlink(image_path)

        except Exception as e:
            st.error(f"Bir hata oluştu: {str(e)}")

# Footer
st.markdown("---")
st.markdown("Made with ❤️ by AwishAI")