import httpx
import urllib.parse
import logging
import re
from typing import List, Dict, Any
from fastapi import HTTPException
from app.config import API_KEY, API_URL
from transliterate import translit

logger = logging.getLogger(__name__)

# Словарь русско-английских сленговых соответствий
SLANG_DICT = {
    "изи": "easy",
    "еазы": "easy",
    "легко": "easy",
}

async def fetch_groups(group_type: str = "campaigns") -> List[Dict[str, Any]]:
    # Используем корректный URL для API групп
    
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{API_URL}/groups",
            params={"type": group_type},
            headers={
                "accept": "application/json",
                "Api-Key": API_KEY
            }
        )
        if response.status_code != 200:
            raise HTTPException(status_code=500, detail=f"Failed to fetch groups: {response.text}")
        
        return response.json()

def normalize_text(text: str) -> str:
    """Приводит текст к нормализованному виду для поиска, удаляя все кроме букв и цифр"""
    return re.sub(r'[^a-zA-Z0-9а-яА-Я]', '', text.lower())

def get_slang_equivalents(word: str) -> List[str]:
    """Получает эквиваленты слова на основе словаря сленга"""
    result = []
    word_lower = word.lower()
    
    # Проверяем прямые соответствия
    if word_lower in SLANG_DICT:
        result.append(SLANG_DICT[word_lower])
    
    # Проверяем обратные соответствия (английский -> русский)
    for rus, eng in SLANG_DICT.items():
        if word_lower == eng:
            result.append(rus)
    
    return result

async def search_groups_by_substring(substring: str, group_type: str = "campaigns") -> List[Dict[str, Any]]:
    # Используем unquote_plus вместо unquote для правильной обработки знака +
    decoded_substring = urllib.parse.unquote_plus(substring).strip()
    logger.info(f"Decoded substring for search: '{decoded_substring}'")
    
    # Транслитерируем поисковую строку
    translit_substring = translit(decoded_substring, 'ru', reversed=True)
    logger.info(f"Transliterated search term: '{translit_substring}'")
    
    # Разбиваем запрос на отдельные слова для поиска
    search_words = [word.strip().lower() for word in decoded_substring.split() if word.strip()]
    translit_words = [word.strip().lower() for word in translit_substring.split() if word.strip()]
    
    # Добавляем сленговые эквиваленты
    slang_words = []
    for word in search_words + translit_words:
        slang_equivalents = get_slang_equivalents(word)
        slang_words.extend(slang_equivalents)
    
    # Объединяем все поисковые слова
    all_search_words = search_words + translit_words + slang_words
    
    # Удаляем дубликаты
    all_search_words = list(set(all_search_words))
    
    logger.info(f"Search words (including transliterated and slang): {all_search_words}")
    
    # Нормализуем поисковую строку для полного сравнения
    norm_search = normalize_text(decoded_substring)
    norm_translit = normalize_text(translit_substring)
    
    groups = await fetch_groups(group_type)
    logger.info(f"Total groups fetched: {len(groups)}")
    
    # Три способа поиска с разной степенью гибкости
    filtered_groups = []
    for group in groups:
        group_name = group.get("name", "")
        group_name_lower = group_name.lower()
        group_name_translit = translit(group_name, 'ru', reversed=True).lower()
        
        # 1. Точное вхождение всей подстроки (включая транслитерацию и сленг)
        if decoded_substring.lower() in group_name_lower or translit_substring.lower() in group_name_lower:
            logger.info(f"Exact match found: '{group_name}' contains '{decoded_substring}' or '{translit_substring}'")
            filtered_groups.append(group)
            continue
            
        # 2. Нормализованный поиск (игнорируем пробелы, дефисы и т.д.)
        norm_group_name = normalize_text(group_name)
        if norm_search in norm_group_name or norm_translit in norm_group_name:
            logger.info(f"Normalized match found: '{norm_group_name}' contains '{norm_search}' or '{norm_translit}'")
            filtered_groups.append(group)
            continue
            
        # 3. Поиск по отдельным словам (подходит, если хотя бы ОДНО слово найдено)
        for word in all_search_words:
            if word in group_name_lower or word in group_name_translit:
                logger.info(f"Word match found: '{group_name}' contains word '{word}'")
                filtered_groups.append(group)
                break
    
    logger.info(f"Filtered groups count: {len(filtered_groups)}")
    if filtered_groups:
        group_names = [g.get('name', 'No name') for g in filtered_groups[:3]]
        logger.info(f"First matches: {', '.join(group_names)}")
    
    return filtered_groups 