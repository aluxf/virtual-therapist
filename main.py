from multiprocessing import Process, Manager
from valence import video_feed
from interaction import therapist

if __name__ == "__main__":

    answers = ["1", "2", "3", "4", "5"]
    questions = [
        "How would you rate your overall well-being as a student?",
        "On a scale of 1 to 5, how would you rate your stress levels on average?",
        #"Have you experienced any significant changes in your mental health while being a student?",
        #"How do you feel that your mental health is supported and prioritized by your educational institution?",
        #"How often do you feel overwhelmed by academic responsibilities and deadlines?",
        #"Have you experienced any symptoms of anxiety, such as excessive worry or restlessness?",
        #"How much sleep are you getting on a regular basis?",
        #"Do you engage in regular physical activity and maintain a healthy lifestyle?",
        #"How would you rate your school-life balance?",
    ]

    with Manager() as manager:
        valence_frames = manager.list()  # shared list
        prod = Process(target=video_feed.valence_feed, args=(valence_frames,))
        prod.start()

        total_score = 0
        for q in questions:
            score = therapist.ask_question(valence_frames, q, answers)
            total_score += score

        avg_score = total_score / len(questions)
        print("Your average score is: ", avg_score)

        prod.join()