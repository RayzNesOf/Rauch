import random


class Event:
    def __init__(self, name, description, condition, choices):
        self.name = name
        self.description = description
        self.condition = condition  # Функция, проверяющая условие события
        self.choices = choices  # Список вариантов выбора

    def is_triggered(self, game_state, resources, ministers, military):
        """Проверка, сработало ли условие события"""
        return self.condition(game_state, resources, ministers, military)


class EventManager:
    def __init__(self):
        self.events = self.initialize_events()
        self.daily_events = []

    def initialize_events(self):
        """Инициализация всех событий"""
        events = [
            Event(
                "Голод",
                "Запасы продовольствия критически низки. Народ начинает голодать.",
                lambda gs, res, min, mil: res.food < 100,
                [
                    {
                        "text": "Ввести карточную систему",
                        "effects": {"morale": -20, "food_efficiency": 1.5}
                    },
                    {
                        "text": "Отправить экспедицию за едой",
                        "effects": {"soldiers": -100, "food_chance": 0.6, "food_on_success": 500}
                    },
                    {
                        "text": "Конфисковать еду у богатых",
                        "effects": {"morale": -30, "food": 300}
                    }
                ]
            ),

            Event(
                "Измена",
                "Один из министров проявляет признаки нелояльности.",
                lambda gs, res, min, mil: any(m.loyalty < 30 for m in min.ministers.values()),
                [
                    {
                        "text": "Арестовать министра",
                        "effects": {"morale": -20, "remove_minister": True}
                    },
                    {
                        "text": "Простить и дать шанс",
                        "effects": {"loyalty_all": 10, "betrayal_risk": 0.3}
                    },
                    {
                        "text": "Предложить сделку",
                        "effects": {"resources_cost": 0.2, "loyalty_target": 50}
                    }
                ]
            )
        ]

        return events

    def check_daily_events(self, game_state, resources, ministers, military):
        """Проверка событий на текущий день"""
        triggered_events = []

        for event in self.events:
            if (event.is_triggered(game_state, resources, ministers, military) and
                    event.name not in game_state.events_triggered):
                triggered_events.append(event)
                game_state.events_triggered.append(event.name)

        return triggered_events

    def apply_event_choice(self, event, choice_index, game_state, resources, ministers, military):
        """Применение выбора игрока в событии"""
        if 0 <= choice_index < len(event.choices):
            choice = event.choices[choice_index]
            effects = choice.get("effects", {})

            # Применение эффектов
            if "morale" in effects:
                game_state.morale += effects["morale"]
            if "food" in effects:
                resources.food += effects["food"]
            if "soldiers" in effects:
                # Уменьшение солдат в случайной дивизии
                available_divs = list(military.divisions.values())
                if available_divs:
                    div = random.choice(available_divs)
                    div.soldiers = max(0, div.soldiers + effects["soldiers"])

            return f"Принято решение: {choice['text']}"

        return "Неверный выбор"