from copy import Error
import os
import click
from termcolor import colored
import pprint
import webbrowser

from src.config import Config
from src.youtube import YouTubeAccount
from src.mturk import MTurkAccount
from src.survey import HTMLSurvey
import src.utils as utils

# TODOS:
# - Clean up the process_data.py  file (put it into mturk.py ) and get it to work with mturk instead of qualtrics
# - Figure out how to make the HIT only allow workers who have passed qualification

class CLI:
    def __init__(self):
        self.config = Config()
        self.youtube_account = YouTubeAccount(self.config["YOUTUBE"]["OAUTH_CLIENT_SECRETS_FILE"])
        self.mturk_account = MTurkAccount(self.config["AWS"]["ACCESS_KEY_ID"],
                                          self.config["AWS"]["SECRET_ACCESS_KEY"])
        self.qual_survey_files = [
            os.path.join(os.getcwd(), "surveys/qualification_survey.html"),
            os.path.join(os.getcwd(), "surveys/qualification_sample_survey_do_not_upload.html"),
            os.path.join(os.getcwd(), "surveys/qualification_survey.csv")
        ]
        self.survey_files = [
            os.path.join(os.getcwd(), "surveys/survey.html"),
            os.path.join(os.getcwd(), "surveys/sample_survey_do_not_upload.html"),
            os.path.join(os.getcwd(), "surveys/survey.csv")
        ]


    def prompt_user(self):
        self.config.load_config()
        prompts = {
            'display_config': 'a',
            'edit_config': 'b',
            'yt_playlists': 'c',
            'create_survey': 'd',
            'verify_survey': 'e',
            'create_sb_hit': 'f',
            'create_hit': 'g',
            'check_hit': 'h',
            'exit': 'x',
        }

        def get_prompt_text():
            """ Dynamically create prompt text based on checks """
            good = colored('✔', 'green')
            bad = colored('✘', 'red')
            youtube_config_filled = good if self.check_config("YOUTUBE") else bad
            playlist_status = self.check_playlists("SURVEY")
            playlist_created = good if playlist_status == "" else bad
            qual_playlist_status = self.check_playlists("SURVEY")
            qual_playlist_created = good if qual_playlist_status == "" else bad
            survey_config_filled = good if self.check_config("SURVEY") else bad
            survey_created = good if self.check_surveys("survey") else bad
            qual_survey_created = good if self.check_surveys("qual") else bad
            aws_config_filled = good if self.check_config("AWS") else bad
            mturk_config_filled = good if self.check_config("MTURK") else bad
            sandbox_hits_exist = good if self.check_hits(sandbox=True) else bad
            actual_hits_exist = good if self.check_hits(sandbox=False) else bad
            return ("Video Annotation CLI\n\n"
                "Steps\n"
                "-----\n"
                f"1) YouTube Steps\n"
                f" [{youtube_config_filled}] YouTube section of config.yml complete\n"
                f" [{playlist_created}] Survey playlist created {playlist_status}\n"
                f" [{qual_playlist_created}] Qualification playlist created {qual_playlist_status}\n"
                f"2) Survey Steps\n"
                f" [{survey_config_filled}] Survey section of config.yml complete\n"
                f" [{survey_created}] Survey html created\n"
                f" [{qual_survey_created}] Qualification survey html created\n"
                f"3) Create HITS in mechanical turk \n"
                f" [{aws_config_filled}] AWS section of config.yml complete\n"
                f" [{mturk_config_filled}] MTurk section of config.yml complete\n"
                f" [{sandbox_hits_exist}] Hits have been created in the sandbox mode of MTURK\n"
                f" [{actual_hits_exist}] Hits have been created in the normal mode of MTURK\n"
                "\nOptions (enter the letter of the action you wish to perform)\n"
                "------------------------------------------------------------\n"
                " Config\n"
                f"   {prompts['display_config']} - Display config file\n"
                f"   {prompts['edit_config']} - Edit config file\n"
                " YouTube\n"
                f"   {prompts['yt_playlists']} - Check status of YouTube playlists\n"
                " Survey HTML\n"
                f"   {prompts['create_survey']} - Create survey html for mechanical turk\n"
                f"   {prompts['verify_survey']} - Verify the sample survey is correct in your browser\n"
                " Mechanical Turk\n"
                f"   {prompts['create_sb_hit']} - Create HITs in mechanical turk sandbox mode\n"
                f"   {prompts['create_hit']} - Create HITs in mechanical turk\n"
                f"   {prompts['check_hit']} - Check status of HITs\n"
                "\n"
                f"   {prompts['exit']} - Exit\n")

        prompt_response = True
        while prompt_response:
            prompt_response = click.prompt(get_prompt_text(), prompt_suffix='', type=str).lower()
            if prompt_response == prompts['exit']:
                exit()
            elif prompt_response == prompts['display_config']:
                print(f"\nCONFIG\n------\n{self.config}\n")
            elif prompt_response == prompts['edit_config']:
                self.edit_config()
            elif prompt_response == prompts['yt_playlists']:
                self.youtube_check_status()
            elif prompt_response == prompts['create_survey']:
                self.create_surveys()
            elif prompt_response == prompts['verify_survey']:
                self.verify_survey()
            elif prompt_response == prompts['create_sb_hit']:
                self.mturk_create_hit(sandbox=True)
            elif prompt_response == prompts['create_hit']:
                self.mturk_create_hit(sandbox=False)
            elif prompt_response == prompts['check_hit']:
                self.mturk_check_hit_status()
            else:
                print("Invalid choice, please try again.")
                continue

            click.prompt(
                "\nPress enter to show CLI again",
                prompt_suffix='', default='', show_default=False, hide_input=True
            )


    def check_config(self, section="all"):
        """ Check that config file is filled out """
        return True if self.config.config_complete(section) else False


    def edit_config(self):
        """ Open config file using OS default app """
        import subprocess, os, platform
        if platform.system() == 'Darwin':       # macOS
            subprocess.call(('open', "config.yml"))
        elif platform.system() == 'Windows':    # Windows
            os.startfile("config.yml")
        else:                                   # linux variants
            subprocess.call(('xdg-open', "config.yml"))


    def check_playlists(self, type):
        """ Check that YouTube playlists have been created """
        playlist_name = self.config["SURVEY"][f"{type}_PLAYLIST"]
        if playlist_name == "":
            return "Playlist name not filled in config"
        playlist_data = self.youtube_account.get_playlist(playlist_name)
        if playlist_data == None:
            return "Playlist not found in YouTube Account"
        elif len(playlist_data['videos']) == 0:
            return "No videos in the playlist"
        else:
            return "" # All good


    def check_surveys(self, type):
        """ Check that survey files have been created """
        files = self.survey_files if type == "survey" else self.qual_survey_files
        for f in files:
            if not os.path.isfile(f):
                return False
        return True


    def youtube_check_status(self):
        """ Display playlists """
        playlists = self.youtube_account.get_playlists_info()
        print("\n\n\nHere are your playlists:")
        pprint.pprint(playlists, sort_dicts=False)
        print("\n")


    def create_surveys(self):
        """ Create survey using videos from a selected playlist"""
        # Get playlists
        qual_playlist = self.youtube_account.get_playlist(self.config["SURVEY"]["QUALIFICATION_PLAYLIST"])
        survey_playlist = self.youtube_account.get_playlist(self.config["SURVEY"]["SURVEY_PLAYLIST"])

        def upload(plist, num_vids):
            """ Ensure playlist has the correct number of videos """
            try:
                return HTMLSurvey(plist, num_vids)
            except ValueError as e:
                print(e)
            return "ERROR"

        # Upload videos
        qual_survey = upload(qual_playlist, self.config["SURVEY"]["QUALIFICATION_VIDEOS"])
        survey = upload(survey_playlist, self.config["SURVEY"]["SURVEY_VIDEOS"])
        if "ERROR" in [qual_survey, survey]:
            return

        # Save out files
        print("\n\n")
        qual_survey.save_survey(*self.qual_survey_files)
        survey.save_survey(*self.survey_files)
        print("\nCheck the sample surveys to ensure they look correct\n")


    def verify_survey(self):
        """ Open the sample survey in a webbrowser """
        file = f"file://{self.survey_files[1]}"
        webbrowser.open_new_tab(file)


    def mturk_create_hit(self, sandbox=True):
        """ Create HIT """
        self.mturk_account.create_hit(self.config["MTURK"], sandbox=sandbox)


    def check_hits(self, sandbox=True):
        """ Check if hits exist """
        hits = self.mturk_account.get_hits(sandbox=sandbox)
        return True if len(hits) > 0 else False


    def mturk_check_hit_status(self):
        """ Pring status of all HITS """
        print("HITS (sandbox):")
        pprint.pprint(self.mturk_account.get_hits(sandbox=True))
        print("HITS:")
        pprint.pprint(self.mturk_account.get_hits(sandbox=False))



if __name__ == '__main__':
    cli = CLI()
    cli.prompt_user()
