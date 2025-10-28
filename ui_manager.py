import pygame
import os


class Colors:
    DARK_GRAY = (40, 40, 40)
    GRAY = (80, 80, 80)
    LIGHT_GRAY = (120, 120, 120)
    RED = (200, 50, 50)
    GREEN = (50, 200, 50)
    BLUE = (50, 100, 200)
    YELLOW = (200, 200, 50)
    WHITE = (240, 240, 240)
    BLACK = (20, 20, 20)
    BROWN = (139, 69, 19)
    DARK_RED = (120, 30, 30)


class Fonts:
    def __init__(self):
        self.small = pygame.font.Font(None, 20)
        self.medium = pygame.font.Font(None, 24)
        self.large = pygame.font.Font(None, 32)
        self.title = pygame.font.Font(None, 48)

        try:
            if os.path.exists("fonts/cyrillic.ttf"):
                self.medium = pygame.font.Font("fonts/cyrillic.ttf", 24)
                self.large = pygame.font.Font("fonts/cyrillic.ttf", 32)
                self.title = pygame.font.Font("fonts/cyrillic.ttf", 48)
        except:
            pass


class Button:
    def __init__(self, x, y, width, height, text, color=Colors.GRAY, hover_color=Colors.LIGHT_GRAY, action=None):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.current_color = color
        self.is_hovered = False
        self.action = action  # Новое поле для действия кнопки

    def draw(self, screen, fonts):
        pygame.draw.rect(screen, self.current_color, self.rect)
        pygame.draw.rect(screen, Colors.WHITE, self.rect, 2)

        text_surf = fonts.medium.render(self.text, True, Colors.WHITE)
        text_rect = text_surf.get_rect(center=self.rect.center)
        screen.blit(text_surf, text_rect)

    def update(self, mouse_pos):
        self.is_hovered = self.rect.collidepoint(mouse_pos)
        self.current_color = self.hover_color if self.is_hovered else self.color
        return self.is_hovered

    def is_clicked(self, mouse_pos, mouse_click):
        return self.rect.collidepoint(mouse_pos) and mouse_click


class Panel:
    """Базовый класс панели"""

    def __init__(self, x, y, width, height, title=""):
        self.rect = pygame.Rect(x, y, width, height)
        self.title = title
        self.visible = True

    def draw(self, screen, fonts):
        """Отрисовка панели"""
        if not self.visible:
            return

        # Фон панели
        pygame.draw.rect(screen, Colors.DARK_GRAY, self.rect)
        pygame.draw.rect(screen, Colors.LIGHT_GRAY, self.rect, 2)

        # Заголовок
        if self.title:
            title_surf = fonts.medium.render(self.title, True, Colors.WHITE)
            screen.blit(title_surf, (self.rect.x + 10, self.rect.y + 10))


class ResourcePanel(Panel):
    """Панель ресурсов"""

    def __init__(self, x, y, width, height):
        super().__init__(x, y, width, height, "Ресурсы Рейха")
        self.resource_data = {}

    def update_resources(self, resources):
        """Обновление данных о ресурсах"""
        self.resource_data = {
            "Продовольствие": resources.food,
            "Боеприпасы": resources.ammunition,
            "Топливо": resources.fuel,
            "Электричество": resources.electricity
        }

    def draw(self, screen, fonts):
        super().draw(screen, fonts)

        y_offset = 50
        for resource, amount in self.resource_data.items():
            # Иконка ресурса (простой прямоугольник)
            icon_rect = pygame.Rect(self.rect.x + 15, self.rect.y + y_offset, 20, 20)
            color = Colors.GREEN if "Продовольствие" in resource else \
                Colors.RED if "Боеприпасы" in resource else \
                    Colors.YELLOW if "Топливо" in resource else Colors.BLUE

            pygame.draw.rect(screen, color, icon_rect)
            pygame.draw.rect(screen, Colors.WHITE, icon_rect, 1)

            # Текст
            text = f"{resource}: {int(amount)}"
            text_surf = fonts.small.render(text, True, Colors.WHITE)
            screen.blit(text_surf, (self.rect.x + 45, self.rect.y + y_offset))

            y_offset += 30


class StatusPanel(Panel):
    """Панель статуса"""

    def __init__(self, x, y, width, height):
        super().__init__(x, y, width, height, "Статус Рейха")
        self.status_data = {}

    def update_status(self, game_state, military):
        """Обновление статуса"""
        self.status_data = {
            "День": game_state.current_day,
            "Население": game_state.population,
            "Мораль": f"{game_state.morale}%",
            "Здоровье": f"{game_state.health}%",
            "Солдаты": military.get_total_soldiers(),
            "Сила врага": military.enemy_force
        }

    def draw(self, screen, fonts):
        super().draw(screen, fonts)

        y_offset = 50
        for stat, value in self.status_data.items():
            text = f"{stat}: {value}"
            text_surf = fonts.small.render(text, True, Colors.WHITE)
            screen.blit(text_surf, (self.rect.x + 15, self.rect.y + y_offset))
            y_offset += 25


class MapPanel(Panel):
    """Панель карты района"""

    def __init__(self, x, y, width, height):
        super().__init__(x, y, width, height, "Карта Центрального Района")
        self.buildings = []
        self.selected_building = None

    def initialize_buildings(self, building_manager):
        """Инициализация зданий на карте"""
        self.buildings = []

        # Позиции зданий на карте (относительные координаты)
        building_positions = {
            "Рейхстаг": (100, 100),
            "Завод продуктов": (200, 150),
            "Пекарня": (250, 200),
            "Подземная фабрика": (150, 250),
            "Электростанция": (300, 100),
            "Котельная": (350, 180),
            "Стадион": (400, 250),
            "Больница": (180, 320),
            "Общага": (280, 300),
            "Церковь Св. Николая": (120, 380),
            "Церковь Покрова": (380, 350),
            "Отделение СС": (220, 80)
        }

        for name, pos in building_positions.items():
            building = building_manager.get_building(name)
            if building:
                self.buildings.append({
                    'name': name,
                    'position': (self.rect.x + pos[0], self.rect.y + pos[1]),
                    'building': building,
                    'rect': pygame.Rect(self.rect.x + pos[0] - 20, self.rect.y + pos[1] - 20, 40, 40)
                })

    def draw(self, screen, fonts):
        super().draw(screen, fonts)

        # Отрисовка зданий
        for bld in self.buildings:
            color = Colors.DARK_RED if bld['building'].is_destroyed else \
                Colors.BROWN if "Рейхстаг" in bld['name'] else \
                    Colors.GRAY

            pygame.draw.rect(screen, color, bld['rect'])
            pygame.draw.rect(screen, Colors.WHITE, bld['rect'], 1)

            # Название здания (сокращенное)
            short_name = bld['name'].split()[-1]  # Берем последнее слово
            text_surf = fonts.small.render(short_name, True, Colors.WHITE)
            text_rect = text_surf.get_rect(center=bld['rect'].center)
            screen.blit(text_surf, text_rect)

            # Выделение выбранного здания
            if self.selected_building == bld['name']:
                pygame.draw.rect(screen, Colors.YELLOW, bld['rect'], 3)

    def handle_click(self, mouse_pos):
        """Обработка клика по карте"""
        for bld in self.buildings:
            if bld['rect'].collidepoint(mouse_pos):
                self.selected_building = bld['name']
                return bld
        self.selected_building = None
        return None


class MinisterPanel(Panel):
    """Панель министров"""

    def __init__(self, x, y, width, height):
        super().__init__(x, y, width, height, "Министры Рейха")
        self.ministers = []
        self.selected_minister = None
        self.scroll_offset = 0
        self.max_visible = 8  # Максимум видимых министров
        self.scroll_up_button = Button(x + width - 30, y + 40, 25, 25, "↑", Colors.GRAY)
        self.scroll_down_button = Button(x + width - 30, y + height - 30, 25, 25, "↓", Colors.GRAY)

    def update_ministers(self, minister_manager):
        """Обновление списка министров"""
        self.ministers = list(minister_manager.ministers.values())

    def draw(self, screen, fonts):
        super().draw(screen, fonts)

        # Отрисовка кнопок прокрутки
        self.scroll_up_button.draw(screen, fonts)
        self.scroll_down_button.draw(screen, fonts)

        y_offset = 50 - self.scroll_offset
        visible_count = 0

        for i, minister in enumerate(self.ministers):
            if visible_count >= self.max_visible:
                break

            if y_offset < self.rect.height - 30 and y_offset > 0:
                # Цвет в зависимости от лояльности
                loyalty_color = Colors.GREEN if minister.loyalty >= 70 else \
                    Colors.YELLOW if minister.loyalty >= 50 else Colors.RED

                # Имя и должность (сокращаем если слишком длинное)
                position = minister.position
                if len(position) > 20:
                    position = position[:20] + "..."

                text = f"{minister.name} - {position}"
                text_surf = fonts.small.render(text, True, Colors.WHITE)
                screen.blit(text_surf, (self.rect.x + 15, self.rect.y + y_offset))

                # Полоска лояльности
                loyalty_rect = pygame.Rect(self.rect.x + 15, self.rect.y + y_offset + 20,
                                           min(minister.loyalty * 2, 200), 8)  # Ограничиваем длину полоски
                pygame.draw.rect(screen, loyalty_color, loyalty_rect)
                pygame.draw.rect(screen, Colors.WHITE, loyalty_rect, 1)

                # Текст лояльности
                loyalty_text = f"{minister.loyalty}%"
                loyalty_surf = fonts.small.render(loyalty_text, True, Colors.WHITE)
                screen.blit(loyalty_surf, (self.rect.x + 220, self.rect.y + y_offset + 15))

                # Выделение выбранного министра
                if self.selected_minister == minister.name:
                    highlight_rect = pygame.Rect(self.rect.x + 10, self.rect.y + y_offset - 5,
                                                 self.rect.width - 40, 35)  # Учитываем место для кнопок
                    pygame.draw.rect(screen, Colors.YELLOW, highlight_rect, 2)

                visible_count += 1

            y_offset += 40

    def handle_click(self, mouse_pos):
        """Обработка клика по списку министров"""
        # Проверка кнопок прокрутки
        if self.scroll_up_button.is_clicked(mouse_pos, True):
            self.scroll_offset = max(0, self.scroll_offset - 40)
            return None
        if self.scroll_down_button.is_clicked(mouse_pos, True):
            max_scroll = max(0, len(self.ministers) * 40 - (self.rect.height - 50))
            self.scroll_offset = min(max_scroll, self.scroll_offset + 40)
            return None

        y_offset = 50 - self.scroll_offset
        for minister in self.ministers:
            minister_rect = pygame.Rect(self.rect.x + 10, self.rect.y + y_offset - 5,
                                        self.rect.width - 40, 35)  # Учитываем место для кнопок

            if minister_rect.collidepoint(mouse_pos):
                self.selected_minister = minister.name
                return minister

            y_offset += 40

        self.selected_minister = None
        return None


class MilitaryPanel(Panel):
    def __init__(self, x, y, width, height):
        super().__init__(x, y, width, height, "Военные силы")
        self.divisions = []
        self.scroll_offset = 0
        self.division_buttons = []  # Новое: кнопки для дивизий

    def update_divisions(self, military_manager):
        self.divisions = list(military_manager.divisions.values())
        self.division_buttons = []

        # Создаем кнопки для каждой дивизии
        y_offset = 50
        for division in self.divisions:
            button_rect = pygame.Rect(self.rect.x + 10, self.rect.y + y_offset - 5,
                                      self.rect.width - 20, 45)
            self.division_buttons.append({
                'rect': button_rect,
                'division': division
            })
            y_offset += 50

    def draw(self, screen, fonts):
        super().draw(screen, fonts)

        y_offset = 50 - self.scroll_offset
        for i, division in enumerate(self.divisions):
            if y_offset < self.rect.height - 30 and y_offset > 0:
                color = Colors.RED if "СС" in division.name else Colors.BLUE
                status_color = Colors.GREEN if not division.is_engaged else Colors.RED

                # Название дивизии
                text = f"{division.name}"
                text_surf = fonts.small.render(text, True, color)
                screen.blit(text_surf, (self.rect.x + 15, self.rect.y + y_offset))

                # Статус и численность
                status = "СВОБОДНА" if not division.is_engaged else "ЗАНЯТА"
                details = f"{division.soldiers} солдат - {status}"
                details_surf = fonts.small.render(details, True, status_color)
                screen.blit(details_surf, (self.rect.x + 15, self.rect.y + y_offset + 20))

                # Полоска морали
                morale_rect = pygame.Rect(self.rect.x + 15, self.rect.y + y_offset + 35,
                                          division.morale * 2, 6)
                pygame.draw.rect(screen, Colors.YELLOW, morale_rect)
                pygame.draw.rect(screen, Colors.WHITE, morale_rect, 1)

            y_offset += 50

    def handle_click(self, mouse_pos):
        """Обработка клика по дивизиям"""
        for button_data in self.division_buttons:
            if button_data['rect'].collidepoint(mouse_pos):
                return ("division_click", button_data['division'])
        return None


class NewsPanel(Panel):
    """Панель новостей дня"""

    def __init__(self, x, y, width, height):
        super().__init__(x, y, width, height, "Новости дня")
        self.news_items = []
        self.scroll_offset = 0
        self.max_visible = 5

    def update_news(self, game_state):
        """Обновление новостей"""
        self.news_items = game_state.daily_news

    def draw(self, screen, fonts):
        super().draw(screen, fonts)

        y_offset = 50 - self.scroll_offset
        visible_count = 0

        for i, news in enumerate(self.news_items):
            if visible_count >= self.max_visible:
                break

            if y_offset < self.rect.height - 30 and y_offset > 0:
                # Разбиваем длинные новости на несколько строк
                words = news.split()
                lines = []
                current_line = ""

                for word in words:
                    test_line = current_line + word + " "
                    if fonts.small.size(test_line)[0] < self.rect.width - 30:
                        current_line = test_line
                    else:
                        if current_line:
                            lines.append(current_line.strip())
                        current_line = word + " "

                if current_line:
                    lines.append(current_line.strip())

                # Отрисовываем каждую строку новости
                for line in lines:
                    text_surf = fonts.small.render(line, True, Colors.WHITE)
                    screen.blit(text_surf, (self.rect.x + 15, self.rect.y + y_offset))
                    y_offset += 20
                    visible_count += 0.2  # Учитываем многострочность

                y_offset += 10  # Отступ между новостями
                visible_count += 1

    def handle_click(self, mouse_pos):
        """Обработка прокрутки новостей"""
        # Простая прокрутка при клике в области панели
        if self.rect.collidepoint(mouse_pos):
            max_scroll = max(0, len(self.news_items) * 30 - (self.rect.height - 50))
            self.scroll_offset = min(max_scroll, self.scroll_offset + 30)
        return None


class UIManager:
    def __init__(self, screen_width=1200, screen_height=800):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.screen = pygame.display.set_mode((screen_width, screen_height))
        pygame.display.set_caption("Березовский Рейх: Последний Рубеж v1.1.2А")

        self.fonts = Fonts()
        self.colors = Colors()

        # Создание панелей
        self.resource_panel = ResourcePanel(10, 10, 250, 180)
        self.status_panel = StatusPanel(10, 200, 250, 200)
        self.news_panel = NewsPanel(10, 410, 250, 180)  # Новая панель новостей
        self.map_panel = MapPanel(270, 10, 600, 400)
        self.minister_panel = MinisterPanel(880, 10, 310, 390)
        self.military_panel = MilitaryPanel(270, 420, 600, 370)

        # Кнопки управления
        self.next_day_button = Button(880, 410, 150, 40, "Следующий день", Colors.GREEN)
        self.save_button = Button(1040, 410, 150, 40, "Сохранить игру", Colors.BLUE)
        self.load_button = Button(880, 460, 150, 40, "Загрузить игру", Colors.YELLOW)
        self.info_button = Button(1040, 460, 150, 40, "Информация", Colors.LIGHT_GRAY)
        self.menu_buttons = [self.next_day_button, self.save_button, self.load_button, self.info_button]

        # Кнопки для детальных экранов
        self.detail_buttons = []

        self.current_screen = "main"

    def initialize_map(self, building_manager):
        self.map_panel.initialize_buildings(building_manager)

    def update_ui(self, game_state, resources, ministers, military):
        self.resource_panel.update_resources(resources)
        self.status_panel.update_status(game_state, military)
        self.news_panel.update_news(game_state)  # Обновляем новости
        self.minister_panel.update_ministers(ministers)
        self.military_panel.update_divisions(military)

    def draw_main_screen(self):
        self.screen.fill(Colors.BLACK)

        self.resource_panel.draw(self.screen, self.fonts)
        self.status_panel.draw(self.screen, self.fonts)
        self.news_panel.draw(self.screen, self.fonts)  # Отрисовываем новости
        self.map_panel.draw(self.screen, self.fonts)
        self.minister_panel.draw(self.screen, self.fonts)
        self.military_panel.draw(self.screen, self.fonts)

        for button in self.menu_buttons:
            button.draw(self.screen, self.fonts)

        title_surf = self.fonts.title.render("БЕРЕЗОВСКИЙ РЕЙХ", True, Colors.WHITE)
        subtitle_surf = self.fonts.medium.render("ПОСЛЕДНИЙ РУБЕЖ", True, Colors.RED)

        self.screen.blit(title_surf, (self.screen_width // 2 - title_surf.get_width() // 2, 450))
        self.screen.blit(subtitle_surf, (self.screen_width // 2 - subtitle_surf.get_width() // 2, 500))

    def draw_event_screen(self, event):
        self.screen.fill(Colors.DARK_GRAY)

        title_surf = self.fonts.large.render(f"СОБЫТИЕ: {event.name}", True, Colors.YELLOW)
        self.screen.blit(title_surf, (50, 50))

        desc_surf = self.fonts.medium.render(event.description, True, Colors.WHITE)
        self.screen.blit(desc_surf, (50, 100))

        y_offset = 200
        for i, choice in enumerate(event.choices):
            text = f"{i + 1}. {choice['text']}"
            choice_surf = self.fonts.medium.render(text, True, Colors.WHITE)
            self.screen.blit(choice_surf, (50, y_offset))
            y_offset += 40

    def draw_building_detail(self, building_data):
        if not building_data:
            return

        detail_panel = Panel(400, 200, 400, 300, building_data['name'])
        detail_panel.draw(self.screen, self.fonts)

        building = building_data['building']

        info_lines = [
            f"Тип: {building.type}",
            f"Уровень: {building.level}",
            f"Эффективность: {building.efficiency:.1f}",
            f"Состояние: {'РАЗРУШЕНО' if building.is_destroyed else 'ФУНКЦИОНИРУЕТ'}"
        ]

        y_offset = 50
        for line in info_lines:
            text_surf = self.fonts.medium.render(line, True, Colors.WHITE)
            self.screen.blit(text_surf, (410, 250 + y_offset))
            y_offset += 30

        # Создаем кнопки для этого экрана
        self.detail_buttons = []

        if not building.is_destroyed:
            upgrade_button = Button(450, 400, 120, 40, "Улучшить", Colors.GREEN, action="upgrade_building")
            self.detail_buttons.append(upgrade_button)
        else:
            repair_button = Button(450, 400, 120, 40, "Восстановить", Colors.YELLOW, action="repair_building")
            self.detail_buttons.append(repair_button)

        close_button = Button(600, 400, 120, 40, "Закрыть", Colors.RED, action="close_detail")
        self.detail_buttons.append(close_button)

        # Отрисовываем кнопки
        for button in self.detail_buttons:
            button.draw(self.screen, self.fonts)

    def draw_minister_detail(self, minister):
        if not minister:
            return

        detail_panel = Panel(400, 150, 400, 400, minister.name)
        detail_panel.draw(self.screen, self.fonts)

        info_lines = [
            f"Должность: {minister.position}",
            f"Лояльность: {minister.loyalty}%",
            f"Эффективность: {minister.calculate_efficiency():.2f}",
            "",
            "Навыки:"
        ]

        y_offset = 50
        for line in info_lines:
            text_surf = self.fonts.medium.render(line, True, Colors.WHITE)
            self.screen.blit(text_surf, (410, 200 + y_offset))
            y_offset += 30

        for skill, level in minister.skills.items():
            skill_text = f"  {skill}: {level}/10"
            skill_surf = self.fonts.medium.render(skill_text, True, Colors.WHITE)
            self.screen.blit(skill_surf, (410, 200 + y_offset))
            y_offset += 25

        # Кнопка закрытия
        self.detail_buttons = [Button(500, 500, 200, 40, "Закрыть", Colors.RED, action="close_detail")]
        for button in self.detail_buttons:
            button.draw(self.screen, self.fonts)

    def draw_division_detail(self, division):
        """Новый метод: детали дивизии"""
        if not division:
            return

        detail_panel = Panel(400, 200, 400, 350, division.name)  # Увеличили высоту
        detail_panel.draw(self.screen, self.fonts)

        info_lines = [
            f"Командир: {division.commander}",
            f"Тип: {'Моторизованная' if division.type == 'motorized' else 'Пехотная'}",
            f"Численность: {division.soldiers} солдат",
            f"Опыт: {division.experience}%",
            f"Мораль: {division.morale}%",
            f"Экипировка: {division.equipment}%",
            f"Статус: {'СВОБОДНА' if not division.is_engaged else 'ЗАНЯТА'}"
        ]

        y_offset = 50
        for line in info_lines:
            text_surf = self.fonts.medium.render(line, True, Colors.WHITE)
            self.screen.blit(text_surf, (410, 250 + y_offset))
            y_offset += 25

        # Кнопка закрытия - перемещена ниже
        self.detail_buttons = [Button(500, 520, 200, 40, "Закрыть", Colors.RED, action="close_detail")]
        for button in self.detail_buttons:
            button.draw(self.screen, self.fonts)

    def draw_info_screen(self):
        """Экран информации об игре"""
        self.screen.fill(Colors.DARK_GRAY)

        title_surf = self.fonts.title.render("БЕРЕЗОВСКИЙ РЕЙХ", True, Colors.WHITE)
        subtitle_surf = self.fonts.large.render("ПОСЛЕДНИЙ РУБЕЖ", True, Colors.RED)
        version_surf = self.fonts.medium.render("Версия 1.1.3", True, Colors.YELLOW)
        author_surf = self.fonts.medium.render("Разработчик: MATS STUDIO", True, Colors.WHITE)

        # Инструкция
        instructions = [
            "ОСНОВНОЕ УПРАВЛЕНИЕ:",
            "- Нажимайте на здания для просмотра информации и улучшения",
            "- Нажимайте на министров для просмотра их характеристик",
            "- Нажимайте на дивизии для просмотра их состояния",
            "- Кнопка 'Следующий день' - переход к следующему игровому дню",
            "- Следите за ресурсами и моралью населения",
            "",
            "ЦЕЛЬ ИГРЫ:",
            "Продержаться 45 дней или достичь одной из победных концовок"
        ]

        self.screen.blit(title_surf, (self.screen_width // 2 - title_surf.get_width() // 2, 50))
        self.screen.blit(subtitle_surf, (self.screen_width // 2 - subtitle_surf.get_width() // 2, 120))
        self.screen.blit(version_surf, (self.screen_width // 2 - version_surf.get_width() // 2, 170))
        self.screen.blit(author_surf, (self.screen_width // 2 - author_surf.get_width() // 2, 200))

        # Отрисовка инструкции
        y_offset = 250
        for line in instructions:
            text_surf = self.fonts.small.render(line, True, Colors.WHITE)
            self.screen.blit(text_surf, (100, y_offset))
            y_offset += 25

        # Кнопка возврата
        back_button = Button(self.screen_width // 2 - 100, 500, 200, 40, "Вернуться в игру", Colors.GREEN,
                             action="close_detail")
        back_button.draw(self.screen, self.fonts)
        self.detail_buttons = [back_button]

    def update_buttons(self, mouse_pos):
        for button in self.menu_buttons:
            button.update(mouse_pos)

        # Обновляем кнопки детальных экранов
        for button in self.detail_buttons:
            button.update(mouse_pos)

        # Обновляем кнопки прокрутки в панели министров
        self.minister_panel.scroll_up_button.update(mouse_pos)
        self.minister_panel.scroll_down_button.update(mouse_pos)

    def handle_click(self, mouse_pos, mouse_click):
        if self.current_screen == "main":
            # Проверка основных кнопок
            if self.next_day_button.is_clicked(mouse_pos, mouse_click):
                return "next_day"
            if self.save_button.is_clicked(mouse_pos, mouse_click):
                return "save_game"
            if self.load_button.is_clicked(mouse_pos, mouse_click):
                return "load_game"
            if self.info_button.is_clicked(mouse_pos, mouse_click):
                return "show_info"

            # Проверка кликов по панелям
            building_click = self.map_panel.handle_click(mouse_pos)
            if building_click:
                return ("building_click", building_click)

            minister_click = self.minister_panel.handle_click(mouse_pos)
            if minister_click:
                return ("minister_click", minister_click)

            division_click = self.military_panel.handle_click(mouse_pos)
            if division_click:
                return division_click

            # Проверка кликов по панели новостей
            news_click = self.news_panel.handle_click(mouse_pos)
            if news_click:
                return "news_scroll"

        elif self.current_screen in ["building_detail", "minister_detail", "division_detail", "info"]:
            # Проверка кнопок детальных экранов
            for button in self.detail_buttons:
                if button.is_clicked(mouse_pos, mouse_click):
                    return button.action

        return None
