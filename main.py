from multiprocessing import Process, Manager
from valence import video_feed
from interaction import therapist

if __name__ == "__main__":
    questions = [
        "How would you rate your overall well-being as a student?",
        "On a scale of 1 to 5, how would you rate your stress levels on average?",
        "Have you experienced any significant changes in your mental health while being a student?",
        "How do you feel that your mental health is supported and prioritized by your educational institution?",
        "How often do you feel overwhelmed by academic responsibilities and deadlines?",
        "Have you experienced any symptoms of anxiety, such as excessive worry or restlessness?",
        "How much sleep are you getting on a regular basis?",
        "Do you engage in regular physical activity and maintain a healthy lifestyle?",
        "How would you rate your school-life balance?",
    ]

    question_set = [
        # General Well-being
        (
            "How is your overall well-being as a student?", 
            ["horrible", "bad", "okay", "good", "great"]
        ),
        
        # Mental Health
        (
            "Have you experienced any positive or negative changes in your mental health while being a student?", 
            ["worse", "negative", "same", "positive", "positive"]
        ),
        
        # Stress and Coping
        (
            "On a scale from 1 to 5, how would you rate your stress levels on average?", 
            ["5", "4", "3", "2", "1"]
        ),
        (
            "How often do you feel overwhelmed by academic responsibilities and deadlines?", 
            ["always", "often", "sometimes", "rarely", "never"]
        ),
        (
            "How well do you sleep on a regular basis?", 
            ["horrible", "bad", "okay", "good", "great"]
        ),
        
        # Physical and Emotional Well-being
        (
            "How often do you engage in physical activity each week?", 
            ["never", "once", "few", "often", "daily"]
        ),
        
        # Academic Experience
        (
            "On a scale from 1 to 5, how satisfied are you with your academic achievements and learning progress?", 
            ["1", "2", "3", "4", "5"]
        ),
        
        # Time Management
        (
            "How effective do you feel your time management skills are in balancing academic and personal life?", 
            ["horrible", "bad", "okay", "good", "great"]
        ),
        
        # Social and Institutional Support
        (
            "How do you feel that your mental health is supported and prioritized by your educational institution?", 
            ["horrible", "bad", "okay", "good", "great"]
        ),
        (
            "How is the support from your family and close ones regarding your education?", 
            ["horrible", "bad", "okay", "good", "great"]
        ),
        (
            "How is your participation in social activities or clubs outside of your academic responsibilities?", 
            ["horrible", "bad", "okay", "good", "great"]
        ),
        
        # Future Outlook
        (
            "On a scale from 1 to 5, how would you rate your school-life balance?", 
            ["5", "4", "3", "2", "1"]
        ),
        (
            "How do you feel about your career prospects or further education after your current studies?", 
            ["horrible", "bad", "okay", "good", "great"]
        )
    ]

    with Manager() as manager:
        valence_frames = manager.list()  # shared list
        prod = Process(target=video_feed.valence_feed, args=(valence_frames,))
        prod.start()

        name = therapist.introduction()

        total_score = 0
        for q, answers in question_set:
            score = therapist.ask_question(valence_frames, q, answers)
            total_score += score

        avg_score = total_score / len(questions)
        print("Your average score is: ", avg_score)

        therapist.recommendation(int(avg_score), name)

        prod.join()
