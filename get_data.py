import httpx
from bs4 import BeautifulSoup
import re
import logging

logger = logging.getLogger(__name__)

async def extract_text_from_url(url: str) -> str:
    """
    دالة ذكية تسحب النص الصافي من اللينكات المختلفة
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    try:
        # تأمين: لو اللينك مش بيبدأ بـ http
        if not url.startswith(("http://", "https://")):
            url = "https://" + url

        # التعامل الخاص مع بعض المنصات المعقدة (أمثلة بديلة)
        if "twitter.com" in url or "x.com" in url:
            # تويتر محمي جداً، الطرق المجانية السريعة بتحوله لـ nitter (نسخة مفتوحة تقرأ التويتة)
            url = url.replace("twitter.com", "nitter.net").replace("x.com", "nitter.net")
        
        async with httpx.AsyncClient(timeout=10.0, headers=headers, follow_redirects=True) as client:
            response = await client.get(url)
            
            if response.status_code != 200:
                logger.error(f"Failed to fetch URL: {url} | Status: {response.status_code}")
                return ""
            
            # استخدام BeautifulSoup لتنظيف الـ HTML
            soup = BeautifulSoup(response.text, "html.parser")
            
            # حذف أكواد الجافا سكريبت والـ CSS التي لا نحتاجها
            for script in soup(["script", "style", "header", "footer", "nav"]):
                script.decompose()
                
            # أخذ النص الصافي
            text = soup.get_text()
            
            # تنظيف الفراغات السطور الزائدة
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            clean_text = " ".join(chunk for chunk in chunks if chunk)
            
            # تقليص النص لو كان طويل جداً (مثلاً أول 2000 حرف) عشان الـ Tokens بتاعة Groq
            return clean_text[:4000]

    except Exception as e:
        logger.error(f"Error scraping URL {url}: {e}")
        return ""