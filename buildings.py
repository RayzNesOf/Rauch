class Building:
    def __init__(self, name, building_type, level=1, efficiency=1.0, is_destroyed=False):
        self.name = name
        self.type = building_type
        self.level = level
        self.efficiency = efficiency
        self.is_destroyed = is_destroyed
        self.workers = 0

    def upgrade(self):
        """Улучшение здания"""
        if self.level < 3:  # Максимальный уровень
            self.level += 1
            self.efficiency *= 1.2
            return True
        return False

    def repair(self):
        """Ремонт здания"""
        if self.is_destroyed:
            self.is_destroyed = False
            self.efficiency = max(0.5, self.efficiency)
            return True
        return False

    def take_damage(self, damage_chance=0.1):
        """Получение урона от вражеских обстрелов"""
        import random
        if random.random() < damage_chance:
            self.efficiency *= 0.8
            if self.efficiency < 0.3:
                self.is_destroyed = True
            return True
        return False

class BuildingManager:
    def __init__(self):
        self.buildings = self.initialize_buildings()

    def initialize_buildings(self):
        """Инициализация всех зданий Березовского Рейха"""
        buildings = [
            Building("Рейхстаг", "government", 2, 1.0),
            Building("Завод продуктов", "food_production", 1, 1.0),
            Building("Пекарня", "food_production", 1, 1.0),
            Building("Подземная фабрика", "military_production", 1, 1.0),
            Building("Электростанция", "power", 1, 1.0),
            Building("Котельная", "fuel", 1, 1.0),
            Building("Больница", "health", 1, 1.0),
            Building("Пожарная часть", "safety", 1, 1.0),
            Building("Церковь Св. Николая", "morale", 1, 1.0),
            Building("АЗС", "fuel", 1, 1.0),
            Building("Церковь Покрова", "morale", 1, 1.0),
            Building("Отделение СС", "military", 1, 1.0),
        ]
        return {bld.name: bld for bld in buildings}

    def get_building(self, name):
        return self.buildings.get(name)

    def get_production_buildings(self):
        return [bld for bld in self.buildings.values() if
                bld.type in ['food_production', 'military_production', 'power', 'fuel']]

    def to_dict(self):
        return {name: {
            'type': bld.type,
            'level': bld.level,
            'efficiency': bld.efficiency,
            'is_destroyed': bld.is_destroyed
        } for name, bld in self.buildings.items()}

    def from_dict(self, data):
        for name, bld_data in data.items():
            if name in self.buildings:
                for key, value in bld_data.items():
                    if hasattr(self.buildings[name], key):
                        setattr(self.buildings[name], key, value)