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

        # Параметры для концовок
        self.humanism = 0
        self.cruelty = 0
        self.pragmatism = 0
        self.ideology = 0
        self.prestige = 50
        self.elite_morale = 50

        # Статистика для концовок
        self.executed_ministers = 0
        self.suppressed_rebellions = 0
        self.civilians_saved = 0
        self.peace_negotiations = 0

        # Флаги событий
        self.events_triggered = []
        self.active_events = []

        # Новости дня
        self.daily_news = []

    def add_news(self, news_text):
        """Добавление новости (отсутствовавший метод)"""
        self.daily_news.append(news_text)
        # Ограничиваем количество новостей
        if len(self.daily_news) > 10:
            self.daily_news = self.daily_news[-10:]

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

        # Новые концовки на основе параметров
        if not self.game_over:
            # Кровавый тиран
            if (self.cruelty > 80 and
                    self.executed_ministers >= 5 and
                    self.suppressed_rebellions >= 3):
                self.game_over = True
                self.victory_type = "bloody_tyrant"

            # Народный мученик
            elif (self.humanism > 70 and
                  self.civilians_saved >= 1000 and
                  self.morale < 20):  # Жертва собой
                self.game_over = True
                self.victory_type = "people_martyr"

            # Прагматичный лидер
            elif (self.pragmatism > 60 and
                  self.peace_negotiations >= 2 and
                  self.population >= 20000):
                self.game_over = True
                self.victory_type = "pragmatic_leader"

            # Идеалист-фанатик
            elif (self.ideology > 75 and
                  self.cruelty < 30 and
                  self.morale > 80):
                self.game_over = True
                self.victory_type = "idealist_fanatic"

    def check_defeat_conditions(self):
        """Проверка условий поражения"""
        # Поражение от восстания
        if self.morale < 10:
            self.game_over = True
            self.defeat_reason = "uprising"

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
            # Новые параметры
            'humanism': self.humanism,
            'cruelty': self.cruelty,
            'pragmatism': self.pragmatism,
            'ideology': self.ideology,
            'prestige': self.prestige,
            'elite_morale': self.elite_morale,
            'executed_ministers': self.executed_ministers,
            'suppressed_rebellions': self.suppressed_rebellions,
            'civilians_saved': self.civilians_saved,
            'peace_negotiations': self.peace_negotiations,
            'daily_news': self.daily_news
        }

    def from_dict(self, data):
        """Загрузка состояния из словаря"""
        for key, value in data.items():
            if hasattr(self, key):
                setattr(self, key, value)