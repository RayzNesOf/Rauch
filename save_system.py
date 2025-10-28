import json
import os
from datetime import datetime


class SaveSystem:
    def __init__(self, save_dir="saves"):
        self.save_dir = save_dir
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)

    def save_game(self, game_state, resources, buildings, ministers, military, filename=None):
        """Сохранение игры"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"save_{timestamp}.json"

        save_path = os.path.join(self.save_dir, filename)

        save_data = {
            'timestamp': datetime.now().isoformat(),
            'game_state': game_state.to_dict(),
            'resources': resources.to_dict(),
            'buildings': buildings.to_dict(),
            'ministers': ministers.to_dict(),
            'military': military.to_dict()
        }

        with open(save_path, 'w', encoding='utf-8') as f:
            json.dump(save_data, f, indent=2, ensure_ascii=False)

        return filename

    def load_game(self, filename):
        """Загрузка игры"""
        save_path = os.path.join(self.save_dir, filename)

        if not os.path.exists(save_path):
            return None

        with open(save_path, 'r', encoding='utf-8') as f:
            save_data = json.load(f)

        return save_data

    def list_saves(self):
        """Список сохранений"""
        saves = []
        for file in os.listdir(self.save_dir):
            if file.endswith('.json'):
                file_path = os.path.join(self.save_dir, file)
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    saves.append({
                        'filename': file,
                        'timestamp': data.get('timestamp', ''),
                        'day': data.get('game_state', {}).get('current_day', 1)
                    })

        return sorted(saves, key=lambda x: x['timestamp'], reverse=True)