import os
import jinja2
import itertools
import src.utils as utils

class HTMLSurvey:
    def __init__(self, playlist, num_videos):
        # Make sure the videos in playlist fit in the survey
        if len(playlist['videos']) < num_videos:
            raise ValueError(f"Your playlist '{playlist['title']}' only has "
                f"{len(playlist['videos'])} but you want {num_videos} videos "
                "per survey\n Please try again and choose a number <= "
                f"{len(playlist['videos'])}\n")

        # Create text for all files
        self.survey = self.create_survey(num_videos)
        self.sample_survey = self.create_sample_survey(playlist, num_videos)
        self.csv_file = self.create_csv(playlist, num_videos)


    def create_survey(self, num_videos):
        """ Create html of the survey """
        env = jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.dirname(os.path.abspath(__file__))))
        template = env.get_template("survey_template.html")
        return template.render(
            num_videos=num_videos,
            questions=self.get_questions(),
        )


    def create_sample_survey(self, playlist, num_videos):
        """ Create sample html for a single survey """
        sample_survey = self.create_survey(num_videos)
        for i in range(num_videos):
            sample_survey = sample_survey.replace(f"${{video_url_{i}}}", playlist['videos'][i]["url"])
        return sample_survey


    def create_csv(self, playlist, num_videos):
        """ Create the accompanying csv file to upload to mechanical turk """
        video_urls = [vid['url'] for vid in playlist['videos']]
        vid_combinations = itertools.combinations(video_urls, num_videos)
        csv_text = ",".join([f"video_url_{i}" for i in range(num_videos)])
        for vids in vid_combinations:
            csv_text += "\n" + ",".join(vids)
        return csv_text


    def save_survey(self, survey_file, sample_survey_file, csv_file):
        """ Save out survey and accompanying csv along with a sample survey """
        utils.save_text(survey_file, self.survey)
        utils.save_text(sample_survey_file, self.sample_survey)
        utils.save_text(csv_file, self.csv_file)
        print(f"Survey is here: {os.path.abspath(survey_file)}")
        print(f"Sample survey is here: {os.path.abspath(sample_survey_file)}")
        print(f"Accompanying csv is here: {os.path.abspath(csv_file)}")


    def get_questions(self):
        return [
        {
            "title": "Depth Perception",
            "options": [
                "1 - Constantly overshoots target, wide swings, slow to correct",
                "2",
                "3 - Some overshooting or missing of target, but quick to correct",
                "4",
                "5 - Accurately directs instruments in the correct plane to target",
            ]
        },
        {
            "title": "Bimanual Dexterity",
            "options": [
                "1 - Uses only one hand, ignores non-dominant hand, poor coordination",
                "2",
                "3 - Uses both hands, but does not optimize interactions between hands",
                "4",
                "5 - Expertly uses both hands in a complementary way to provide best exposure",
            ]
        },
        {
            "title": "Efficiency",
            "options": [
                "1 - Inefficient efforts; many uncertain movements; constantly changing focus or persisting without progress",
                "2",
                "3 - Slow, but planned movements are reasonably organized",
                "4",
                "5 - Confident, efficient and safe conduct, maintains focus on task, fluid progression",
            ]
        },
        {
            "title": "Force Sensitivity",
            "options": [
                "1 - Rough moves, tears tissue, injures nearby structures, poor control, frequent suture breakage",
                "2",
                "3 - Handles tissues reasonably well, minor trauma to adjacent tissue, rare suture breakage",
                "4",
                "5 - Applies appropriate tension, negligible injury to adjacent structures, no suture breakage",
            ]
        },
        {
            "title": "Robotic Control",
            "options": [
                "1 - Consistently does not optimize view, hand position, or repeated collisions even with guidance",
                "2",
                "3 - View is sometimes not optimal. Occasionally needs to relocate arms. Occasional collisions and obstruction of assistant.",
                "4",
                "5 - Controls camera and hand position optimally and independently. Minimal collisions or obstruction of assistant",
            ]
        },
    ]
