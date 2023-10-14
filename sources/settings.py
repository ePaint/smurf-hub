import os
from pathlib import Path
from typing import List
from pydantic import BaseModel, root_validator
from definitions import PROJECT_FOLDER

SETTINGS_PATH = str(PROJECT_FOLDER.joinpath('settings.json'))
print(SETTINGS_PATH)


class Settings(BaseModel):
    lol_path: str = None
    lol_client_path: str = None
    lol_client_args: str = '--launch-product=league_of_legends --launch-patchline=live'
    lol_process_names: List[str] = ['RiotClientServices.exe', 'LeagueClient.exe']
    keepass_enabled: bool = False
    keepass_path: str = None

    def save(self):
        print(self.json(indent=4))
        with open(SETTINGS_PATH, 'w+') as f:
            f.write(self.json(indent=4))

    @root_validator
    def build_extra_fields(cls, values):
        lol_path = values.get('lol_path')
        if lol_path:
            path = Path(lol_path)
            values['lol_client_path'] = str(path.parent.joinpath('Riot Client').joinpath('RiotClientServices.exe'))
        return values


try:
    SETTINGS: Settings = Settings.parse_raw(open(SETTINGS_PATH, 'r+').read())
except FileNotFoundError as e:
    SETTINGS: Settings = Settings()
