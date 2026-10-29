"""Запуск: python -m streamlit run frontend/app.py."""

import os

import httpx
import streamlit as st


API_URL = os.getenv("API_URL", "http://127.0.0.1:8000").rstrip("/")

st.set_page_config(page_title="Учет успеваемости", page_icon="🎓")
st.title("Учет успеваемости студентов")
st.write("Базовый интерфейс информационной системы.")
st.caption(f"Адрес API: {API_URL}")

if st.button("Проверить подключение к API"):
    try:
        response = httpx.get(f"{API_URL}/", timeout=5.0)
        response.raise_for_status()
        data = response.json()
    except httpx.HTTPError:
        st.error("API недоступен. Запустите FastAPI и проверьте адрес сервера.")
    except ValueError:
        st.error("Сервер вернул некорректный JSON.")
    else:
        st.success("Соединение с API установлено.")
        st.json(data)
