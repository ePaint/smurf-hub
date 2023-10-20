from pathlib import Path
from typing import List
from pydantic import BaseModel, root_validator
from definitions import SETTINGS_PATH


class Settings(BaseModel):
    lol_path: str = None
    lol_client_path: str = None
    lol_client_args: str = '--launch-product=league_of_legends --launch-patchline=live'
    lol_process_names: List[str] = ['RiotClientServices.exe', 'LeagueClient.exe']
    keepass_path: str = None

    def save(self):
        print(self.json(indent=4))
        with open(SETTINGS_PATH, 'w+') as f:
            f.write(self.json(indent=4))

    def set_lol_path(self, value):
        self.lol_path = value
        if value:
            path = Path(value)
            self.lol_client_path = str(path.parent.joinpath('Riot Client').joinpath('RiotClientServices.exe'))
        else:
            self.lol_client_path = ''

    @root_validator
    def build_extra_fields(cls, values):
        lol_path = values.get('lol_path')
        if lol_path:
            path = Path(lol_path)
            values['lol_client_path'] = str(path.parent.joinpath('Riot Client').joinpath('RiotClientServices.exe'))
        else:
            values['lol_client_path'] = ''
        return values


try:
    SETTINGS: Settings = Settings.parse_raw(open(SETTINGS_PATH, 'r+').read())
except FileNotFoundError as e:
    SETTINGS: Settings = Settings()
