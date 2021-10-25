import os
import glob
import datetime
import googleapiclient.discovery
import google_auth_oauthlib
from googleapiclient.http import MediaFileUpload


ACCEPTED_EXTENSIONS = [
    ".MOV", ".MPEG-1", ".MPEG-2", ".MPEG4", ".MP4",
    ".MPG", ".AVI", ".WMV", ".MPEGPS", ".FLV",
]


class YouTubeAccount:
    """Helper class for interfacing with the YouTube API

    Attributes:
        secrets_file (str): Path to the JSON file that contains your OAuth 2.0
            credentials for the YouTube Data API. Info on how to obtain:
            https://developers.google.com/youtube/v3/quickstart/python#step_1_set_up_your_project_and_credentials
    """
    def __init__(self, secrets_file):
        self.secrets_file = secrets_file
        self.credentials = None


    def login(self):
        """ Login using OAuth

        Checks to see if logged in already. If not, this will automatically
        open a browser page to ask for access.
        """
        if not self.credentials or self.credentials.valid == False:
            print("Need to log in and authorize google account.")
            print("If this doesn't open a browser, use the link below:")
            scopes = [
                # "https://www.googleapis.com/auth/youtube",
                "https://www.googleapis.com/auth/youtube.readonly",
                # "https://www.googleapis.com/auth/youtube.upload"
            ]
            flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
                self.secrets_file, scopes
            )
            self.credentials = flow.run_local_server()


    def get_playlist(self, playlist_title):
        """ Get info for a specific playlist """
        self.login()
        playlists = self.get_playlists_info()
        for p in playlists:
            if p['title'] == playlist_title:
                return p

        # Couldn't find playlist
        print(f"Could not find playlist '{playlist_title}' in your YouTube account")
        return None


    def get_playlists_info(self):
        """ Get info on playlists in the YouTube account.

        Returns:
            A dictionary containing info on all playlists in the user's account
        """

        self.login()
        youtube = googleapiclient.discovery.build(
            "youtube", "v3", credentials=self.credentials
        )

        def get_playlists():
            """Get basic info of all playlists in the account.

            Returns:
                list: List of dicts with info on each playlist in the account.
            """
            request = youtube.playlists().list(
                part="snippet,contentDetails,status,player,id",
                maxResults=50, mine=True
            )
            playlists = []
            while request is not None:
                response = request.execute()
                for playlist in response['items']:
                    playlists.append({
                        'id': playlist['id'],
                        'title': playlist['snippet']['title'],
                        'description': playlist['snippet']['description'],
                        'privacy_status': playlist['status']['privacyStatus'],
                    })
                request = youtube.playlistItems().list_next(request, response)
            return playlists

        def get_videos(playlist_id):
            """ Get info about all videos in a playlist.

            Args:
                playlist_id (str): Unique playlist ID.

            Returns:
                list: List of dicts with info on each video in the playlist.
            """
            request = youtube.playlistItems().list(
                part='contentDetails,status,snippet',
                maxResults=50, playlistId=playlist_id
            )
            videos = []
            while request is not None:
                response = request.execute()
                for vid in response['items']:
                    videos.append({
                        'id': vid['contentDetails']['videoId'],
                        'title': vid['snippet']['title'],
                        'description': vid['snippet']['description'],
                        'privacy_status': vid['status']['privacyStatus'],
                        'url': f"https://www.youtube.com/embed/{vid['contentDetails']['videoId']}"
                    })
                request = youtube.playlistItems().list_next(request, response)
            return videos

        playlists = get_playlists()
        for p in playlists:
            p['videos'] = get_videos(p['id'])
        return playlists


    def upload_to_playlist(self, video_dir_path, playlist_name):
        """ Upload a directory of videos to a playlist.
        The title of the video in YouTube will be the name of the file (minus the extension)

        Args:
            video_dir_path (str): The directory where the videos are located.
            playlist_name (str): The name of the playlist to create.
        """
        # Get the files to upload, check if valid
        video_files = sorted(glob.glob(os.path.join(video_dir_path, "*")))
        for v in video_files:
            if not os.path.splitext(os.path.basename(v))[1].upper() in ACCEPTED_EXTENSIONS:
                print(f"Video {v} not an accepted video file, ignoring")
                video_files.remove(v)
        if len(video_files) == 0:
            print(f"No video files found in {video_dir_path}. Exiting.")
            return

        # Login to YouTube API and build API client
        self.login()
        youtube = googleapiclient.discovery.build(
            "youtube", "v3", credentials=self.credentials
        )

        # Create playlist

        # Upload all videos
        for idx, v in enumerate(video_files):
            # Upload video
            video_name = os.path.splitext(os.path.basename(v))[0]
            print(f"Uploading video {video_name} ({idx+1}/{len(video_files)})..")
            request = youtube.videos().insert(
                part='snippet,status',
                body={
                    'snippet': {
                        'title': video_name,
                        'description': f'Video {idx}',
                        'categoryId': 27,
                        'tags': ['annotation', 'crowdsourcing']
                    },
                    'status': {
                        'privacyStatus': 'unlisted',
                        'selfDeclaredMadeForKids': False,
                    },
                    'notifySubscribers': False
                },
                media_body=MediaFileUpload(v, chunksize=-1)
            )
            response = request.execute()
            print(response)

            # Insert video into playlist

