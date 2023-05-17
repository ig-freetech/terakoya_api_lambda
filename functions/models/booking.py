from pydantic import BaseModel


class BookingItem(BaseModel):
    """
    Item that is converted from a request body sent via API Gateway and then to be inserted into DynamoDB  
    """
    date: str
    email: str
    terakoya_type: int
    place: int
    name: str
    grade: str
    arrival_time: int
    terakoya_experience: int
    study_subject: str
    study_subject_detail: str
    study_style: str
    school_name: str
    first_choice_school: str
    course_choice: str
    future_free: str
    like_thing_free: str
    how_to_know_terakoya: str
    remarks: str
