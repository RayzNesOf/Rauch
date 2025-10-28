# game_state.py
import json
import random
from datetime import datetime, timedelta


class GameState:
    def __init__(self):
        self.current_day = 1
        self.game_over = False
        self.victory_type = None
        self.defeat_reason = None

        # Основные параметры
        self.population = 25000
        self.morale = 50
        self.health = 70

        # Флаги событий
        self.events_triggered = []
        self.active_events = []

        # Новости дня
        self.daily_news = []

    def next_day(self):
        """Переход на следующий день"""
        self.current_day += 1
        self.daily_news = []  # Очищаем новости дня

        # Проверка условий победы/поражения
        self.check_victory_conditions()
        self.check_defeat_conditions()

    def check_victory_conditions(self):
        """Проверка условий победы"""
        # Победа 1: "Чудо обороны"
        if (self.current_day >= 45 and
                self.population >= 12500 and
                not self.game_over):
            self.game_over = True
            self.victory_type = "defense_miracle"

    def check_defeat_conditions(self):
        """Проверка условий поражения"""
        # Поражение от восстания
        if self.morale < 10:
            self.game_over = True
            self.defeat_reason = "uprising"

    def add_news(self, news_text):
        """Добавить новость дня"""
        self.daily_news.append(news_text)

    def to_dict(self):
        """Сериализация состояния для сохранения"""
        return {
            'current_day': self.current_day,
            'population': self.population,
            'morale': self.morale,
            'health': self.health,
            'game_over': self.game_over,
            'victory_type': self.victory_type,
            'defeat_reason': self.defeat_reason,
            'daily_news': self.daily_news
        }

    def from_dict(self, data):
        """Загрузка состояния из словаря"""
        for key, value in data.items():
            if hasattr(self, key):
                setattr(self, key, value)
