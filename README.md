# Video Crowdsourcing
Software to help automate collecting crowdsourced annotations using Mechanical Turk.

The goal of this project is to enable crowdsourced collection of annotations on video data. This was built to collect skill annotations on medium length snippets of video (1-2 minutes), but was built with flexibility in mind so researchers can adapt the code to fit their needs.

<br>

# How it Works

Videos from a YouTube playlist are used to programatically build surveys, including a "qualification" survey to verify responses. These surveys are sent to Mechanical Turk to create HITs for crowd workers. Once on Mechanical Turk, this software includes tools to manage payments to workers who do and do not pass the qualification questions. Finally, all responses from the workers can be collected in one place.

<br>

# Instructions
## 1) Install requirements

You will need:
- Access to a command line (terminal)
- Download of this respository
    - `git clone https://github.com/mpeven/Video_Crowdsourcing.git`
- Python
    - Note: this can be done easily using [Conda](https://conda.io/projects/conda/en/latest/user-guide/install/index.html) to install Python and required libraries
- Installation of required libraries
    - If using conda: `conda install --file requirements.txt`
    - If using pip: `pip install -r requirements.txt`

## 2) Run Command Line Interface (CLI)

The CLI can be run with `python main.py` and should guide you through the rest of steps outlined below. Refer to this README if more details are needed.

## 3) Upload videos

1. Upload videos to YouTube
    - Go to https://studio.youtube.com/ and click 'Create' to upload videos
    - Make sure videos are published and do not have 'Draft' status
    - _**IMPORTANT**_: Make sure videos are listed as Unlisted or Public (Private YouTube videos can't be seen in the survey)
2. Create YouTube playlists for qualification videos and survey (un-annotated) videos
    - Once the videos are uploaded, create these two playlists and move them into the correct playlist
3. Put title of the YouTube playlists in the SURVEY section of the [config file](config.yml)

## 4) Create surveys

1. Get access to YouTube Data API
    - Instructions here: [link](https://developers.google.com/youtube/v3/quickstart/python#step_1_set_up_your_project_and_credentials)
    - _**IMPORTANT**_: Make sure you set "Application type" as `Desktop app` when you are on the page "Create OAuth client ID"
2. Fill out the needed sections of the [config file](config.yml)
    - YOUTUBE section: oauth client secrets file
    - SURVEY section: number of videos per survey
3. Create surveys using the option in the CLI
4. Verify the survey is correct by opening the sample survey in a web browser

## 5) MTURK steps

1. Create an AWS account
    - Instructions here: [link](https://docs.aws.amazon.com/general/latest/gr/aws-sec-cred-types.html#access-keys-and-secret-access-keys)
    - Put the access keys in the config file
2. Create a Mechanical Turk Account
    - URL: https://requester.mturk.com/create/projects/new
    - Link your AWS account to your Mechanical Turk Account in the "My Account" tab
3. Create a Mechanical Turk "Sandbox" Account for testing
    - URL: https://requester.mturk.com/developer/sandbox
    - Link your AWS account to your Mechanical Turk "Sandbox" Account in the "My Account" tab
4. Upload sandbox-mode HITs using CLI
5. Upload live HITs using CLI
6. Periodically check on status and manage payments

<br>

# Authors

- Michael Peven (main contact - <span>m</span><span>p</span><span>e</span><span>v</span><span>e</span><span>n</span><span>@</span><span>j</span><span>h</span><span>u</span><span>.</span><span>e</span><span>d</span><span>u</span>)
- Tingwen Guo

This work builds upon previous work done by Anand Malpani and Colin Lea

<br>

# Acknowledgements

We would like to thank the following for support and funding:
- Swaroop Vedula
- Gregory Hager
- Science of Learning Institute
