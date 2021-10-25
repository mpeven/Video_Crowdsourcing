import boto3
import xmltodict
import json


class MTurkAccount:
    """Helper class for all functions relating to Mechanical Turk.

    Args:
        aws_access_key_id (str): AWS access key id.
        aws_secret_access_key (str): AWS secret access key.

    Attributes:

    """
    def __init__(self, aws_access_key_id, aws_secret_access_key):
        self.sandbox_client = boto3.client(
            'mturk',
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            region_name='us-east-1',
            endpoint_url='https://mturk-requester-sandbox.us-east-1.amazonaws.com'
        )
        self.live_client = boto3.client(
            'mturk',
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            region_name='us-east-1',
            endpoint_url='https://mturk-requester.us-east-1.amazonaws.com'
        )


    def get_client(self, sandbox=False):
        return self.sandbox_client if sandbox else self.live_client


    def create_hit(self, hit_config, sandbox=False):
        # TODO - Add parameter to differentiate qualification hit from normal hit
        # TODO - Add in HITLayoutParameters as dict to put all questions in
        client = self.get_client(sandbox)

        # Read in survey html as string
        with open("surveys/survey.html", "r") as f:
            html_question = f.read()
        xml_question = f"""
        <HTMLQuestion xmlns=\"http://mechanicalturk.amazonaws.com/AWSMechanicalTurkDataSchemas/2011-11-11/HTMLQuestion.xsd\">
            <HTMLContent><![CDATA[<!DOCTYPE html>{html_question}]]></HTMLContent>
            <FrameHeight>0</FrameHeight>
        </HTMLQuestion>
        """

        # Create hit
        response = client.create_hit(
            Title = hit_config["TITLE"],
            Description = hit_config["DESCRIPTION"],
            Keywords = hit_config["KEYWORDS"],
            Reward = str(hit_config["REWARD"]),
            MaxAssignments = hit_config["MAX_ASSIGNMENTS"],
            LifetimeInSeconds = hit_config["LIFETIME_SECONDS"],
            AssignmentDurationInSeconds = hit_config["ASSIGNMENT_DURATION_SECONDS"],
            AutoApprovalDelayInSeconds = hit_config["AUTO_APPROVAL_SECONDS"],
            Question = xml_question
        )

        # Show results
        print("A new HIT has been created. You can preview it here:")
        print(f"https://worker{'sandbox' if sandbox else ''}.mturk.com/mturk/preview?groupId={response['HIT']['HITGroupId']}")
        print("HITID = " + response['HIT']['HITId'] + " (Use to Get Results)")


    def get_hits(self, sandbox=False):
        """ Get all hits from an mturk account"""
        client = self.get_client(sandbox)

        # Get all hits (using pagination if many pages)
        response = client.list_hits()
        all_hits = response['HITs']
        while 'NextToken' in response:
            response = client.list_hits(NextToken=response['NextToken'])
            all_hits.extend(response['HITs'])

        # Extract info from each hit response
        hit_info = []
        for hit in all_hits:
            hit_info.append({
                'id': hit['HITId'],
                'title': hit['Title'],
                'description': hit['Description'],
                'status': hit['HITStatus'],
                'qual_requirements': hit['QualificationRequirements'],
                'hits_available': hit['NumberOfAssignmentsAvailable'],
                'hits_complete': hit['NumberOfAssignmentsCompleted'],
                'responses': self.get_responses(hit['HITId'], sandbox)
            })
        return hit_info


    def get_responses(self, hit_id, sandbox=False):
        """ Get all worker responses from a specific hit """
        client = self.get_client(sandbox)

        # Get all assignments (using pagination if many pages)
        response = client.list_assignments_for_hit(
            HITId = hit_id,
            AssignmentStatuses = ['Submitted']
        )
        all_assignments = response['Assignments']
        while 'NextToken' in response:
            response = client.list_assignments_for_hit(
                HITId = hit_id,
                AssignmentStatuses = ['Submitted'],
                NextToken = response['NextToken']
            )
            all_assignments.extend(response['Assignments'])

        # Get responses from assignments
        responses = []
        for assignment in all_assignments:
            responses.append({
                'assignment_id': assignment["AssignmentId"],
                'worker_id': assignment["WorkerId"],
                'answers': json.loads(xmltodict.parse(assignment['Answer'])['QuestionFormAnswers']['Answer']['FreeText'])
            })
        return responses
