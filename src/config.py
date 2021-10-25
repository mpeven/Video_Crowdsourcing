import os
import yaml
from termcolor import colored

config_defaults = {
    "YOUTUBE.OAUTH_CLIENT_SECRETS_FILE": {"default": None, "default_ok": False},
    "AWS.ACCESS_KEY_ID": {"default": None, "default_ok": False},
    "AWS.SECRET_ACCESS_KEY": {"default": None, "default_ok": False},
    "MTURK.TITLE": {"default": None, "default_ok": False},
    "MTURK.DESCRIPTION": {"default": None, "default_ok": False},
    "MTURK.KEYWORDS": {"default": None, "default_ok": False},
    "MTURK.REWARD": {"default": 0.0, "default_ok": False},
    "MTURK.MAX_ASSIGNMENTS": {"default": 100, "default_ok": True},
    "MTURK.LIFETIME_SECONDS": {"default": 604800, "default_ok": True},
    "MTURK.ASSIGNMENT_DURATION_SECONDS": {"default": 3600, "default_ok": True},
    "MTURK.AUTO_APPROVAL_SECONDS": {"default": 259200, "default_ok": True},
    "SURVEY.SURVEY_VIDEOS": {"default": 5, "default_ok": True},
    "SURVEY.SURVEY_PLAYLIST": {"default": None, "default_ok": False},
    "SURVEY.QUALIFICATION_VIDEOS": {"default": 5, "default_ok": True},
    "SURVEY.QUALIFICATION_PLAYLIST": {"default": None, "default_ok": False},
}

class Config(dict):
    def __init__(self):
        pass


    def load_config(self):
        return yaml.safe_load(open("config.yml", "r"))


    def __getitem__(self, key):
        config = self.load_config()
        return config[key]


    def __str__(self):
        """ String representation of config file
        This will display whether the info in config.yml has been filled out
        """
        config_string = ""
        config = self.load_config()
        def status(section, option, value):
            # Check that files have a valid path
            if "FILE" in option:
                if not os.path.isfile(value):
                    return f"[{colored('NOT A VALID PATH', 'red')}]"

            if value == config_defaults[f"{section}.{option}"]["default"]:
                if config_defaults[f"{section}.{option}"]["default_ok"]:
                    return f"({colored('default', 'yellow')}) - {value}"
                else:
                    return f"[{colored('INCOMPLETE', 'red')}]"
            else:
                return f"({colored('complete', 'green')}) - {value}"

        for section, options_dict in config.items():
            config_string += f"{section}:\n"
            for option, value in options_dict.items():
                config_string += f"  {option}: {status(section, option, value)}\n"

        if not self.config_complete():
            config_string += "\nINCOMPLETE options in config.yml, please fill out this file"

        return config_string


    def config_complete(self, section="all"):
        """ Returns whether the config.yml file is filled out or not """
        config = self.load_config()
        sections_complete = {}

        # Check each section
        for section, options_dict in config.items():
            section_options = []

            # Check all options in the section
            for option, value in options_dict.items():
                is_default = (value == config_defaults[f"{section}.{option}"]["default"])
                default_ok = config_defaults[f"{section}.{option}"]["default_ok"]

                # Ok if changed from default or is an ok default
                if (is_default == False) or (is_default and default_ok):
                    section_options.append(True)
                else:
                    section_options.append(False)
            sections_complete[section] = all(section_options)

        # Return whether all options are ok unless specificed
        if section == "all":
            return all(list(sections_complete.values()))
        else:
            return sections_complete[section]


