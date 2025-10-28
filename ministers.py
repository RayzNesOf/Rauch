import random


class Minister:
    def __init__(self, name, position, skills, loyalty, triggers=None):
        self.name = name
        self.position = position
        self.skills = skills  # Словарь {навык: уровень}
        self.loyalty = loyalty
        self.triggers = triggers or []
        self.is_traitor = False

    def calculate_efficiency(self):
        """Расчет эффективности министра на основе навыков и лояльности"""
        base_efficiency = sum(self.skills.values()) / len(self.skills)
        loyalty_modifier = self.loyalty / 100.0
        return base_efficiency * loyalty_modifier

    def update_loyalty(self, change):
        """Изменение лояльности"""
        self.loyalty = max(0, min(100, self.loyalty + change))

    def check_triggers(self, game_state, resources):
        """Проверка триггеров для событий"""
        events = []

        for trigger in self.triggers:
            # Пример: триггер при низкой морали
            if "мораль" in trigger and "низк" in trigger:
                if game_state.morale < 30:
                    events.append(f"{self.name}: {trigger}")

            # Триггер при нехватке ресурсов
            if "еда" in trigger and resources.food < 500:
                events.append(f"{self.name}: {trigger}")

        return events


class MinisterManager:
    def __init__(self):
        self.ministers = self.initialize_ministers()

    def initialize_ministers(self):
        """Инициализация всех министров Березовского Рейха"""
        ministers = [
            Minister("Макар Лысенко", "Рейхсфюрер",
                     {"Администрация": 8, "Пропаганда": 9, "Боевая_подготовка": 7}, 100),

            Minister("Сергей Демиденко", "Культура, спорт",
                     {"Пропаганда": 7, "Администрация": 6, "Боевая_подготовка": 5}, 85),

            Minister("Титаев Всеволод", "Оборона, экономика",
                     {"Экономика": 8, "Боевая_подготовка": 9, "Администрация": 7}, 90),

            Minister("Платон Литвинчук", "Пропаганда, юстиция",
                     {"Пропаганда": 10, "Администрация": 6, "Дипломатия": 4}, 95),

            Minister("Александр Новченко", "МИД, церковь",
                     {"Дипломатия": 7, "Пропаганда": 6, "Администрация": 5}, 80),

            Minister("Арсений Ватутин", "Логистика, транспорт",
                     {"Логистика": 8, "Администрация": 6, "Экономика": 5}, 75),

            Minister("Александр Петров", "С/х, строительство",
                     {"Экономика": 7, "Администрация": 6, "Логистика": 5}, 88),

            Minister("Алексей Портнов", "Здравоохранение",
                     {"Медицина": 8, "Администрация": 6, "Логистика": 4}, 82),

            Minister("Стас Ярушин", "МВД",
                     {"Боевая_подготовка": 7, "Администрация": 6, "Пропаганда": 5}, 70),

            Minister("Максим Старый", "Промышленность",
                     {"Экономика": 6, "Логистика": 5, "Администрация": 4}, 65),

            Minister("Альберт Каспрак", "СС",
                     {"Боевая_подготовка": 10, "Администрация": 7, "Пропаганда": 6}, 100),

            Minister("Ислам Зам", "Моторизованная СС",
                     {"Боевая_подготовка": 8, "Логистика": 7, "Администрация": 5}, 78),

            Minister("Николас Кейдж", "Пехота СС",
                     {"Боевая_подготовка": 7, "Пропаганда": 5, "Администрация": 4}, 72),

            Minister("Марк Волков", "Губернатор",
                     {"Администрация": 7, "Экономика": 6, "Пропаганда": 5}, 85),

            Minister("Стас Ватутин", "Бизнесмен",
                     {"Экономика": 9, "Логистика": 8, "Дипломатия": 7}, 60),
        ]

        return {min.name: min for min in ministers}

    def get_minister_efficiency(self):
        """Получить общую эффективность министров по категориям"""
        efficiencies = {
            'agriculture': 1.0,
            'industry': 1.0,
            'resources': 1.0,
            'propaganda': 1.0
        }

        # Расчет эффективности на основе соответствующих министров
        for minister in self.ministers.values():
            eff = minister.calculate_efficiency()

            if "сельхоз" in minister.position or "продовольствие" in minister.position:
                efficiencies['agriculture'] *= eff
            elif "промышленность" in minister.position:
                efficiencies['industry'] *= eff
            elif "ресурс" in minister.position or "природ" in minister.position:
                efficiencies['resources'] *= eff
            elif "пропаганда" in minister.position:
                efficiencies['propaganda'] *= eff

        return efficiencies

    def to_dict(self):
        return {name: {
            'position': min.position,
            'skills': min.skills,
            'loyalty': min.loyalty,
            'is_traitor': min.is_traitor
        } for name, min in self.ministers.items()}

    def from_dict(self, data):
        for name, min_data in data.items():
            if name in self.ministers:
                for key, value in min_data.items():
                    if hasattr(self.ministers[name], key):
                        setattr(self.ministers[name], key, value)