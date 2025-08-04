import requests
from bs4 import BeautifulSoup
import logging
from typing import List, Optional
import time

logger = logging.getLogger(__name__)

class WebsiteMonitor:
    def __init__(self, target_url: str, search_names: List[str]):
        self.target_url = target_url
        self.search_names = [name.strip() for name in search_names if name.strip()]
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
    
    def fetch_page_content(self) -> Optional[str]:
        """Получает содержимое страницы"""
        try:
            response = self.session.get(self.target_url, timeout=30)
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            logger.error(f"Ошибка при получении страницы: {e}")
            return None
    
    def search_names_in_content(self, content: str) -> List[str]:
        """Ищет имена в содержимом страницы"""
        soup = BeautifulSoup(content, 'html.parser')
        text_content = soup.get_text()
        
        found_names = []
        for search_name in self.search_names:
            search_name_lower = search_name.lower()
            
            # Ищем частичные совпадения
            if search_name_lower in text_content.lower():
                # Находим полное имя/фамилию в контексте
                full_name = self._find_full_name_in_context(text_content, search_name)
                if full_name:
                    found_names.append(full_name)
                    logger.info(f"Найдено имя: {full_name} (поиск: {search_name})")
                else:
                    found_names.append(search_name)
                    logger.info(f"Найдено имя: {search_name}")
        
        return found_names
    
    def _find_full_name_in_context(self, text_content: str, search_name: str) -> str:
        """Находит полное имя/фамилию в контексте"""
        import re
        
        search_name_lower = search_name.lower()
        text_lower = text_content.lower()
        
        # Ищем позицию частичного совпадения
        pos = text_lower.find(search_name_lower)
        if pos == -1:
            return ""
        
        # Определяем границы слова (имени/фамилии)
        start = pos
        end = pos + len(search_name_lower)
        
        # Расширяем границы для поиска полного имени
        # Ищем начало слова (пробел, начало строки, пунктуация)
        while start > 0 and text_content[start - 1].isalpha():
            start -= 1
        
        # Ищем конец слова (пробел, конец строки, пунктуация)
        while end < len(text_content) and text_content[end].isalpha():
            end += 1
        
        # Извлекаем полное имя/фамилию
        full_name = text_content[start:end].strip()
        
        # Очищаем от лишних символов
        full_name = re.sub(r'[^\w\s]', '', full_name).strip()
        
        # Проверяем, что это действительно имя (содержит буквы)
        if full_name and any(c.isalpha() for c in full_name):
            return full_name
        
        return search_name
    
    def check_for_names(self) -> List[str]:
        """Основной метод для проверки появления имен"""
        content = self.fetch_page_content()
        if content is None:
            return []
        
        return self.search_names_in_content(content)
    
    def get_page_info(self) -> dict:
        """Получает информацию о странице"""
        content = self.fetch_page_content()
        if content is None:
            return {"error": "Не удалось получить содержимое страницы"}
        
        soup = BeautifulSoup(content, 'html.parser')
        return {
            "title": soup.title.string if soup.title else "Без заголовка",
            "url": self.target_url,
            "content_length": len(content),
            "search_names": self.search_names
        } 