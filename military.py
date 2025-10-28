import random


class Division:
    def __init__(self, name, commander, division_type, soldiers, experience=50, morale=70, equipment=80):
        self.name = name
        self.commander = commander
        self.type = division_type
        self.soldiers = soldiers
        self.experience = experience
        self.morale = morale
        self.equipment = equipment
        self.is_engaged = False

    def calculate_attack_power(self, resources):
        """Расчет силы атаки по формуле из GDD"""
        if self.soldiers <= 0:
            return 0

        base_power = (self.soldiers * 0.4) + (self.experience * 0.3) + (self.morale * 0.2) + (self.equipment * 0.1)

        # Модификаторы
        if self.type == 'motorized':
            base_power *= 1.3

        # Штрафы за нехватку ресурсов
        if resources.ammunition < self.soldiers * 10:
            base_power *= 0.7
        if self.type == 'motorized' and resources.fuel < self.soldiers * 5:
            base_power *= 0.5

        return max(0, base_power)

    def calculate_defense_power(self, resources, in_building=False):
        """Расчет силы защиты"""
        if self.soldiers <= 0:
            return 0.1  # Минимальная защита чтобы избежать деления на 0

        base_power = (self.soldiers * 0.4) + (self.experience * 0.3) + (self.morale * 0.2) + (self.equipment * 0.1)

        if in_building:
            base_power *= 1.5

        return max(0.1, base_power)  # Минимум 0.1 чтобы избежать деления на 0

    def take_casualties(self, casualties):
        """Принять потери"""
        self.soldiers = max(0, self.soldiers - casualties)
        self.morale = max(0, self.morale - casualties * 0.1)


class MilitaryManager:
    def __init__(self):
        self.divisions = self.initialize_divisions()
        self.enemy_force = 5000
        self.battles_today = 0
        self.patrols_today = 2

    def initialize_divisions(self):
        """Инициализация дивизий Березовского Рейха"""
        divisions = [
            Division("1-я пехотная СС", "Альберт Каспрак", "infantry", 150, 80, 90, 85),
            Division("2-я пехотная СС", "Николас Кейдж", "infantry", 150, 70, 75, 80),
            Division("3-я моторизованная СС", "Ислам Зам", "motorized", 140, 75, 80, 75),
            Division("1-я пехотная Вермахт", "Сергей Демиденко", "infantry", 150, 60, 70, 70),
            Division("2-я пехотная Вермахт", "Титаев Всеволод", "infantry", 150, 65, 75, 72),
            Division("3-я пехотная Вермахт", "Александр Новченко", "infantry", 150, 55, 65, 68),
            Division("4-я пехотная Вермахт", "Стас Ярушин", "infantry", 150, 58, 68, 65),
            Division("5-я пехотная Вермахт", "Максим Старый", "infantry", 150, 50, 60, 60),
        ]

        return {div.name: div for div in divisions}

    def get_total_soldiers(self):
        return sum(div.soldiers for div in self.divisions.values())

    def get_motorized_divisions(self):
        return [div for div in self.divisions.values() if div.type == 'motorized']

    def simulate_battle(self, resources, is_defense=True):
        """Симуляция боя с защитой от деления на ноль"""
        if self.battles_today >= 3:
            return {"result": "no_battle", "message": "Превышен лимит боев за день"}

        self.battles_today += 1

        # Выбор дивизий для боя
        available_divs = [div for div in self.divisions.values() if not div.is_engaged and div.soldiers > 0]
        if not available_divs:
            return {"result": "no_battle", "message": "Нет доступных дивизий"}

        defending_division = random.choice(available_divs)
        defending_division.is_engaged = True

        # Расчет сил с защитой от нуля
        defense_power = defending_division.calculate_defense_power(resources, is_defense)
        attack_power = max(0.1, self.enemy_force * 0.1 * random.uniform(0.8, 1.2))  # Минимум 0.1

        # Расчет потерь с защитой от экстремальных значений
        if defense_power > 0 and attack_power > 0:
            attacker_losses = (defense_power / attack_power) * 0.3 * random.uniform(0.8, 1.2)
            defender_losses = (attack_power / defense_power) * 0.2 * random.uniform(0.8, 1.2)
        else:
            # Если что-то пошло не так, используем безопасные значения
            attacker_losses = 0.1
            defender_losses = 0.1

        # Ограничение потерь разумными пределами
        attacker_losses = min(attacker_losses, 0.8)  # Максимум 80% потерь
        defender_losses = min(defender_losses, 0.8)

        # Применение потерь
        defender_casualties = int(defending_division.soldiers * defender_losses)
        defending_division.take_casualties(defender_casualties)

        enemy_casualties = int(self.enemy_force * attacker_losses)
        self.enemy_force = max(0, self.enemy_force - enemy_casualties)

        # Определение результата
        if defense_power > attack_power:
            result = "victory"
            message = f"{defending_division.name} отбила атаку! Потери: {defender_casualties} солдат"
        else:
            result = "defeat"
            message = f"{defending_division.name} потерпела поражение. Потери: {defender_casualties} солдат"

        return {
            "result": result,
            "message": message,
            "defender_casualties": defender_casualties,
            "attacker_casualties": enemy_casualties
        }

    def reset_daily_engagement(self):
        """Сброс статуса занятости дивизий"""
        for division in self.divisions.values():
            division.is_engaged = False
        self.battles_today = 0

    def to_dict(self):
        divisions_data = {}
        for name, div in self.divisions.items():
            divisions_data[name] = {
                'commander': div.commander,
                'type': div.type,
                'soldiers': div.soldiers,
                'experience': div.experience,
                'morale': div.morale,
                'equipment': div.equipment
            }

        return {
            'divisions': divisions_data,
            'enemy_force': self.enemy_force,
            'battles_today': self.battles_today,
            'patrols_today': self.patrols_today
        }

    def from_dict(self, data):
        for name, div_data in data['divisions'].items():
            if name in self.divisions:
                for key, value in div_data.items():
                    if hasattr(self.divisions[name], key):
                        setattr(self.divisions[name], key, value)

        self.enemy_force = data['enemy_force']
        self.battles_today = data['battles_today']
        self.patrols_today = data['patrols_today']