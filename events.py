# events.py
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
            ),

            Event(
                "Обнаружение заговора",
                "Разведка докладывает о возможном заговоре среди министров.",
                lambda gs, res, min, mil: min.discover_conspiracy(gs) is not None,
                [
                    {
                        "text": "Арестовать заговорщиков",
                        "effects": {"morale": -15, "order": 20, "remove_conspirators": True}
                    },
                    {
                        "text": "Перевербовать заговорщиков",
                        "effects": {"resources_cost": 0.3, "loyalty_chance": 0.7}
                    },
                    {
                        "text": "Инсценировать ловушку для врага",
                        "effects": {"double_agent_chance": 0.5, "risk": 0.4}
                    },
                    {
                        "text": "Проигнорировать",
                        "effects": {"coup_risk": 0.3}
                    }
                ]
            ),
            Event(
                "Голодные дети в больнице",
                "Дети в больнице умирают от голода. Врачи просят дополнительные пайки для спасения жизней.",
                lambda gs, res, min, mil: res.food < 300 and gs.health < 60,
                [
                    {
                        "text": "Отдать детские пайки",
                        "effects": {"food": -50, "morale": 10, "soldier_health": -15, "humanism": 20}
                    },
                    {
                        "text": "Оставить как есть",
                        "effects": {"morale": -20, "cruelty": 15, "rumor": "жестокость"}
                    },
                    {
                        "text": "Конфисковать еду у богатых",
                        "effects": {"morale": -30, "food": 100, "elite_morale": -40, "pragmatism": 10}
                    }
                ]
            ),

            Event(
                "Пленный командир врага",
                "Взят в плен бывший друг детства Макара. Он предлагает сотрудничество.",
                lambda gs, res, min, mil: random.random() < 0.3 and gs.current_day > 10,
                [
                    {
                        "text": "Казнить как предателя",
                        "effects": {"morale_radicals": 10, "morale_diplomats": -15, "cruelty": 25, "ideology": 15}
                    },
                    {
                        "text": "Предложить перейти на свою сторону",
                        "effects": {"conversion_chance": 0.4, "betrayal_risk": 0.3, "pragmatism": 20}
                    },
                    {
                        "text": "Обменять на своих солдат",
                        "effects": {"soldiers_rescued": 50, "prestige_loss": 20, "humanism": 25}
                    }
                ]
            ),

            Event(
                "Саботаж на фабрике",
                "Рабочие саботируют производство из-за голодных условий труда.",
                lambda gs, res, min, mil: res.food < 200 and gs.morale < 40,
                [
                    {
                        "text": "Жестоко наказать зачинщиков",
                        "effects": {"morale": -20, "production_boost": 1.3, "cruelty": 30}
                    },
                    {
                        "text": "Улучшить пайки рабочим",
                        "effects": {"food_daily": -100, "morale": 15, "humanism": 20}
                    },
                    {
                        "text": "Найти компромисс",
                        "effects": {"food": -10, "morale": 5, "pragmatism": 15, "negotiation_success": 0.8}
                    }
                ]
            )
        ]

        return events



    def check_daily_events(self, game_state, resources, ministers, military):
        """Проверка событий на текущий день"""
        triggered_events = []

        # Проверяем заговоры
        ministers.check_conspiracies(game_state)

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

            # Обработка заговора
            if event.name == "Обнаружение заговора":
                conspirator = ministers.discover_conspiracy(game_state)
                if conspirator:
                    if choice_index == 0:  # Арест
                        conspirator.is_conspirator = False
                        conspirator.conspiracy_level = 0
                        conspirator.loyalty = 0
                        game_state.add_news(f"Министр {conspirator.name} арестован за заговор!")
                    elif choice_index == 1:  # Перевербовать
                        if random.random() < effects["loyalty_chance"]:
                            conspirator.loyalty = 80
                            conspirator.is_conspirator = False
                            conspirator.conspiracy_level = 0
                            game_state.add_news(f"Министр {conspirator.name} перевербован!")
                    elif choice_index == 3:  # Проигнорировать
                        conspirator.conspiracy_level = 100

            return f"Принято решение: {choice['text']}"

        return "Неверный выбор"