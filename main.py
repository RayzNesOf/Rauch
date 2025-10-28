import pygame
import sys
import random
from game_state import GameState
from resources import ResourceManager
from buildings import BuildingManager
from ministers import MinisterManager
from military import MilitaryManager
from events import EventManager
from save_system import SaveSystem
from ui_manager import UIManager, Colors, Button


class BerezovskyReichGame:
    def __init__(self):
        pygame.init()

        self.ui = UIManager()
        self.game_state = GameState()
        self.resources = ResourceManager()
        self.buildings = BuildingManager()
        self.ministers = MinisterManager()
        self.military = MilitaryManager()
        self.events = EventManager()
        self.save_system = SaveSystem()

        self.ui.initialize_map(self.buildings)

        self.current_event = None
        self.selected_building = None
        self.selected_minister = None
        self.selected_division = None

        self.clock = pygame.time.Clock()
        self.fps = 60

    def start_new_game(self):
        self.show_splash_screen()

    def show_splash_screen(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                    running = False

            self.ui.screen.fill(Colors.BLACK)

            title_surf = self.ui.fonts.title.render("БЕРЕЗОВСКИЙ РЕЙХ", True, Colors.WHITE)
            subtitle_surf = self.ui.fonts.large.render("ПОСЛЕДНИЙ РУБЕЖ", True, Colors.RED)
            info_surf = self.ui.fonts.medium.render("Год 2025. Гражданская война в России.", True, Colors.WHITE)
            prompt_surf = self.ui.fonts.medium.render("Нажмите любую клавишу для продолжения...", True, Colors.YELLOW)

            self.ui.screen.blit(title_surf, (self.ui.screen_width // 2 - title_surf.get_width() // 2, 200))
            self.ui.screen.blit(subtitle_surf, (self.ui.screen_width // 2 - subtitle_surf.get_width() // 2, 270))
            self.ui.screen.blit(info_surf, (self.ui.screen_width // 2 - info_surf.get_width() // 2, 350))
            self.ui.screen.blit(prompt_surf, (self.ui.screen_width // 2 - prompt_surf.get_width() // 2, 450))

            pygame.display.flip()
            self.clock.tick(self.fps)

    def daily_update(self):
        print(f"\n=== ДЕНЬ {self.game_state.current_day} ===")

        minister_efficiency = self.ministers.get_minister_efficiency()

        production = self.resources.calculate_daily_production(minister_efficiency)
        consumption = self.resources.calculate_daily_consumption(
            self.game_state.population,
            self.military.get_total_soldiers(),
            self.military.battles_today,
            self.military.patrols_today,
            len(self.military.get_motorized_divisions())
        )

        self.resources.update_resources(production, consumption)

        battle_count = self.simulate_random_battles()

        daily_events = self.events.check_daily_events(
            self.game_state, self.resources, self.ministers, self.military
        )

        self.update_morale(production[0], battle_count)

        self.military.reset_daily_engagement()

        self.game_state.next_day()

        return daily_events

    def simulate_random_battles(self):
        battle_count = 0
        battle_chance = 0.6

        for _ in range(3):
            if random.random() < battle_chance:
                battle_result = self.military.simulate_battle(self.resources, is_defense=True)
                if battle_result["result"] != "no_battle":
                    print(f"БОЙ: {battle_result['message']}")
                    battle_count += 1

        return battle_count

    def update_morale(self, food_production, battle_count):
        food_per_person = food_production / self.game_state.population if self.game_state.population > 0 else 0

        morale_change = (food_per_person * 2) - (battle_count * 0.3)

        propaganda_efficiency = self.ministers.get_minister_efficiency()['propaganda']
        morale_change += propaganda_efficiency * 0.5

        self.game_state.morale = max(0, min(100, self.game_state.morale + morale_change))

    def handle_event_choice(self, choice_index):
        if self.current_event and 0 <= choice_index < len(self.current_event.choices):
            result = self.events.apply_event_choice(
                self.current_event, choice_index, self.game_state,
                self.resources, self.ministers, self.military
            )
            self.current_event = None
            self.ui.current_screen = "main"
            return result
        return "Неверный выбор"

    def load_game_data(self, save_data):
        """Загрузка данных игры из сохранения"""
        self.game_state.from_dict(save_data['game_state'])
        self.resources.from_dict(save_data['resources'])
        self.buildings.from_dict(save_data['buildings'])
        self.ministers.from_dict(save_data['ministers'])
        self.military.from_dict(save_data['military'])

    def handle_building_action(self, action):
        """Обработка действий с зданиями"""
        if action == "upgrade_building" and self.selected_building:
            building = self.selected_building['building']
            if building.upgrade():
                return "Здание улучшено!"
            else:
                return "Невозможно улучшить здание"
        elif action == "repair_building" and self.selected_building:
            building = self.selected_building['building']
            if building.repair():
                return "Здание восстановлено!"
            else:
                return "Невозможно восстановить здание"
        elif action == "close_detail":
            self.ui.current_screen = "main"
            return "Закрыто"
        return "Неизвестное действие"

    def load_game_menu(self):
        """Меню загрузки игры"""
        saves = self.save_system.list_saves()
        if not saves:
            print("Нет сохраненных игр!")
            return False

        print("\n--- ЗАГРУЗКА ИГРЫ ---")
        for i, save in enumerate(saves, 1):
            print(f"{i}. День {save['day']} - {save['filename']}")

        try:
            choice = int(input("Выберите сохранение (номер): ")) - 1
            if 0 <= choice < len(saves):
                save_data = self.save_system.load_game(saves[choice]['filename'])
                if save_data:
                    self.load_game_data(save_data)
                    print(f"Игра загружена! День {self.game_state.current_day}")
                    return True
                else:
                    print("Ошибка загрузки!")
            else:
                print("Неверный выбор!")
        except ValueError:
            print("Введите число!")

        return False

    def show_load_game_screen(self):
        """Графический экран загрузки игры"""
        saves = self.save_system.list_saves()
        if not saves:
            # Сообщение об отсутствии сохранений
            self.ui.screen.fill(Colors.BLACK)
            message_surf = self.ui.fonts.large.render("Нет сохраненных игр!", True, Colors.RED)
            prompt_surf = self.ui.fonts.medium.render("Нажмите любую клавишу для возврата", True, Colors.WHITE)

            self.ui.screen.blit(message_surf, (self.ui.screen_width // 2 - message_surf.get_width() // 2, 300))
            self.ui.screen.blit(prompt_surf, (self.ui.screen_width // 2 - prompt_surf.get_width() // 2, 350))
            pygame.display.flip()

            waiting = True
            while waiting:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        sys.exit()
                    if event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                        waiting = False
            return False

        # Отображение списка сохранений
        running = True
        selected_save = None

        while running:
            self.ui.screen.fill(Colors.DARK_GRAY)

            title_surf = self.ui.fonts.large.render("ЗАГРУЗКА ИГРЫ", True, Colors.YELLOW)
            self.ui.screen.blit(title_surf, (self.ui.screen_width // 2 - title_surf.get_width() // 2, 50))

            # Отображение сохранений
            y_offset = 100
            save_buttons = []
            for i, save in enumerate(saves):
                text = f"День {save['day']} - {save['filename']}"
                text_surf = self.ui.fonts.medium.render(text, True, Colors.WHITE)
                button_rect = pygame.Rect(200, y_offset, 800, 30)

                # Выделение выбранного сохранения
                if selected_save == i:
                    pygame.draw.rect(self.ui.screen, Colors.YELLOW, button_rect, 2)

                self.ui.screen.blit(text_surf, (210, y_offset))
                save_buttons.append((button_rect, i))
                y_offset += 40

            # Кнопки действий
            load_button = Button(400, 500, 200, 40, "Загрузить", Colors.GREEN)
            back_button = Button(600, 500, 200, 40, "Назад", Colors.RED)

            load_button.draw(self.ui.screen, self.ui.fonts)
            back_button.draw(self.ui.screen, self.ui.fonts)

            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = pygame.mouse.get_pos()

                    # Проверка кликов по сохранениям
                    for button_rect, save_index in save_buttons:
                        if button_rect.collidepoint(mouse_pos):
                            selected_save = save_index

                    # Проверка кнопок действий
                    if load_button.is_clicked(mouse_pos, True) and selected_save is not None:
                        save_data = self.save_system.load_game(saves[selected_save]['filename'])
                        if save_data:
                            self.load_game_data(save_data)
                            print(f"Игра загружена! День {self.game_state.current_day}")
                            return True

                    if back_button.is_clicked(mouse_pos, True):
                        return False

        return False

    def run(self):
        running = True

        while running:
            mouse_pos = pygame.mouse.get_pos()
            mouse_click = False

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        mouse_click = True
                elif event.type == pygame.KEYDOWN:
                    if self.ui.current_screen == "event" and self.current_event:
                        if pygame.K_1 <= event.key <= pygame.K_3:
                            choice_index = event.key - pygame.K_1
                            result = self.handle_event_choice(choice_index)
                            print(f"Результат события: {result}")
                    elif event.key == pygame.K_ESCAPE:
                        if self.ui.current_screen in ["building_detail", "minister_detail", "division_detail", "info"]:
                            self.ui.current_screen = "main"

            self.ui.update_ui(self.game_state, self.resources, self.ministers, self.military)
            self.ui.update_buttons(mouse_pos)

            if mouse_click:
                result = self.ui.handle_click(mouse_pos, mouse_click)

                if result == "next_day":
                    daily_events = self.daily_update()
                    if daily_events:
                        self.current_event = daily_events[0]
                        self.ui.current_screen = "event"

                    if self.game_state.game_over:
                        self.show_end_game()
                        running = False

                elif result == "save_game":
                    filename = self.save_system.save_game(
                        self.game_state, self.resources, self.buildings,
                        self.ministers, self.military
                    )
                    print(f"Игра сохранена как {filename}")

                elif result == "load_game":  # Новая обработка загрузки
                    success = self.show_load_game_screen()
                    if success:
                        # Обновляем UI после загрузки
                        self.ui.update_ui(self.game_state, self.resources, self.ministers, self.military)

                elif result == "show_info":  # Новая обработка информации
                    self.ui.current_screen = "info"

                elif result in ["upgrade_building", "repair_building", "close_detail"]:
                    # Обработка действий с зданиями
                    action_result = self.handle_building_action(result)
                    print(f"Действие с зданием: {action_result}")
                    if result == "close_detail":
                        self.ui.current_screen = "main"

                elif result and isinstance(result, tuple):
                    if result[0] == "building_click":
                        self.selected_building = result[1]
                        self.ui.current_screen = "building_detail"
                    elif result[0] == "minister_click":
                        self.selected_minister = result[1]
                        self.ui.current_screen = "minister_detail"
                    elif result[0] == "division_click":
                        self.selected_division = result[1]
                        self.ui.current_screen = "division_detail"

            # Отрисовка
            if self.ui.current_screen == "main":
                self.ui.draw_main_screen()
            elif self.ui.current_screen == "event" and self.current_event:
                self.ui.draw_event_screen(self.current_event)
            elif self.ui.current_screen == "building_detail":
                self.ui.draw_main_screen()
                self.ui.draw_building_detail(self.selected_building)
            elif self.ui.current_screen == "minister_detail":
                self.ui.draw_main_screen()
                self.ui.draw_minister_detail(self.selected_minister)
            elif self.ui.current_screen == "division_detail":
                self.ui.draw_main_screen()
                self.ui.draw_division_detail(self.selected_division)
            elif self.ui.current_screen == "info":  # Новый экран информации
                self.ui.draw_info_screen()

            pygame.display.flip()
            self.clock.tick(self.fps)

        pygame.quit()

    def show_end_game(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                    running = False

            self.ui.screen.fill(Colors.BLACK)

            if self.game_state.victory_type:
                title = "ПОБЕДА!"
                color = Colors.GREEN
                if self.game_state.victory_type == "defense_miracle":
                    message = "Чудо обороны! Березовский Рейх выстоял 45 дней!"
            else:
                title = "ПОРАЖЕНИЕ"
                color = Colors.RED
                if self.game_state.defeat_reason == "uprising":
                    message = "Народ восстал! Мораль упала до критического уровня."

            title_surf = self.ui.fonts.title.render(title, True, color)
            message_surf = self.ui.fonts.large.render(message, True, Colors.WHITE)
            stats_surf = self.ui.fonts.medium.render(
                f"Вы продержались {self.game_state.current_day} дней. "
                f"Население: {self.game_state.population}. "
                f"Финальная мораль: {self.game_state.morale}%",
                True, Colors.YELLOW
            )
            prompt_surf = self.ui.fonts.medium.render("Нажмите любую клавишу для выхода...", True, Colors.WHITE)

            self.ui.screen.blit(title_surf, (self.ui.screen_width // 2 - title_surf.get_width() // 2, 200))
            self.ui.screen.blit(message_surf, (self.ui.screen_width // 2 - message_surf.get_width() // 2, 300))
            self.ui.screen.blit(stats_surf, (self.ui.screen_width // 2 - stats_surf.get_width() // 2, 350))
            self.ui.screen.blit(prompt_surf, (self.ui.screen_width // 2 - prompt_surf.get_width() // 2, 450))

            pygame.display.flip()
            self.clock.tick(self.fps)


def main():
    game = BerezovskyReichGame()

    print("=== БЕРЕЗОВСКИЙ РЕЙХ: ПОСЛЕДНИЙ РУБЕЖ ===")
    print("Запуск графической версии...")

    game.start_new_game()
    game.run()


if __name__ == "__main__":
    main()