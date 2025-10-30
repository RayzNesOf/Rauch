class ResourceManager:
    def __init__(self):
        # Стартовые ресурсы
        self.food = 5000
        self.ammunition = 10000
        self.fuel = 2000
        self.electricity = 100

        # Производственные мощности
        self.food_factory = 1
        self.bakery = 2
        self.underground_factory = 1
        self.power_plant = 1
        self.boiler_house = 1

        # Потребление
        self.food_consumption = 0
        self.ammo_consumption = 0
        self.fuel_consumption = 0

    def calculate_daily_production(self, minister_efficiency):
        """Расчет ежедневного производства - БАЛАНСИРОВКА"""
        # Увеличенное производство для баланса
        food_production = (self.food_factory * 300 + self.bakery * 150) * minister_efficiency.get('agriculture', 1.0)
        ammo_production = self.underground_factory * 400 * minister_efficiency.get('industry', 1.0)
        fuel_production = (self.boiler_house * 100 + self.power_plant * 50) * minister_efficiency.get('resources', 1.0)
        electricity_production = self.power_plant * 200

        return food_production, ammo_production, fuel_production, electricity_production

    def calculate_daily_consumption(self, population, soldiers, battles_count, patrols, motorized_divisions):
        """Расчет ежедневного потребления - БАЛАНСИРОВКА"""
        # Сбалансированное потребление
        food_consumption = population * 0.03 + soldiers * 0.1  # Уменьшено потребление
        ammo_consumption = battles_count * 200 + patrols * 50   # Уменьшено потребление
        fuel_consumption = motorized_divisions * 50             # Уменьшено потребление
        electricity_consumption = population * 0.005

        self.food_consumption = food_consumption
        self.ammo_consumption = ammo_consumption
        self.fuel_consumption = fuel_consumption

        return food_consumption, ammo_consumption, fuel_consumption, electricity_consumption

    def update_resources(self, production, consumption):
        """Обновление ресурсов после производства/потребления"""
        food_prod, ammo_prod, fuel_prod, electricity_prod = production
        food_cons, ammo_cons, fuel_cons, electricity_cons = consumption

        self.food += food_prod - food_cons
        self.ammunition += ammo_prod - ammo_cons
        self.fuel += fuel_prod - fuel_cons
        self.electricity = max(0, electricity_prod - electricity_cons)

        # Ресурсы не могут быть отрицательными
        self.food = max(0, self.food)
        self.ammunition = max(0, self.ammunition)
        self.fuel = max(0, self.fuel)
        self.electricity = max(0, self.electricity)

    def to_dict(self):
        return {
            'food': self.food,
            'ammunition': self.ammunition,
            'fuel': self.fuel,
            'electricity': self.electricity,
            'food_factory': self.food_factory,
            'bakery': self.bakery,
            'underground_factory': self.underground_factory,
            'power_plant': self.power_plant,
            'boiler_house': self.boiler_house
        }

    def from_dict(self, data):
        for key, value in data.items():
            if hasattr(self, key):
                setattr(self, key, value)