from time import sleep
from furhat_remote_api import FurhatRemoteAPI
from numpy.random import randint
import numpy as np

FURHAT_IP = "localhost"

furhat = FurhatRemoteAPI(FURHAT_IP)
furhat.set_led(red=100, green=50, blue=50)


"""How would you rate your overall well-being as a student? [horrible, bad, neutral, good, excellent]

On a scale of 1 to 5, how would you rate your stress levels on average? [1, 2, 3, 4, 5]

Have you experienced any significant changes in your mental health while being a student? [none, some, neutral, few, many]

How do you feel that your mental health is supported and prioritized by your educational institution? [horrible, bad, neutral, good, excellent]

How often do you feel overwhelmed by academic responsibilities and deadlines? [never, sometimes, neutral, often, always]

Have you experienced any symptoms of anxiety, such as excessive worry or restlessness? [none, some, neutral, few, many]

How much sleep are you getting on a regular basis? [1, 2, 3, 4, 5]

Do you engage in regular physical activity and maintain a healthy lifestyle?  [never, sometimes, neutral, regularly, frequently]

How would you rate your school-life balance? [1, 2, 3, 4, 5]"""

""" Subsystem 2
1. Ask question
    - possible answers 1-5
2. - If user invalid answer  
        - Interact error with furhat
        - Repeat 1.
    - If user answer 1-5    
        - If  valence is off
            - Ask if user is sure about answer
            - If no
                - Repeat 1.
            - If yes
                - Save score
                - Move on to next
        - Save score
        - Move on to next question
3.  """


def valence_str(valence_nr):
    if valence_nr < -0.1:
        return "negative"
    if valence_nr > 0.1:
        return "positive"
    return "neutral"


# Say with blocking (blocking say, bsay for short)
def bsay(line):
    furhat.say(text=line, blocking=True)


# answers = [1, 2, 3, 4, 5]
answers = ["one", "two", "three", "four", "five"]
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


def score_counter(answer, answers):
    score = 0
    if answer == answers[0]:
        score = 1
    elif answer == answers[1]:
        score = 2
    elif answer == answers[2]:
        score = 3
    elif answer == answers[3]:
        score = 4
    elif answer == answers[4]:
        score = 5

    return score


def ask_question(shared_list, question, answers):
    while True:
        bsay(question)
        result = furhat.listen()
        avg_valence = np.mean(shared_list)
        valence = valence_str(avg_valence)
        answer = result.message
        if result.message not in answers:
            bsay(
                "I did not get that, please give me a valid answer"
            )  # one on these... "answers"
            continue

        elif result.message in answers:
            if answers[0] or answers[1] in result.message and valence == "negative":
                bsay("Okey, sorry to here that")
                return score_counter(answer)

            if answers[2] in result.message and valence == "neutral":
                bsay("Okey!")
                return score_counter(answer)
            if answers[3] or answers[4] in result.message and valence == "positive":
                bsay("That makes me happy!")
                return score_counter(answer)

            else:
                bsay("Are you sure about your answer?")

                if "yes" in result.message:
                    return score_counter(answer)
                elif "no" in result.message:
                    bsay("Think it over agian, how do you really feel?")


if __name__ == "__main__":
    score = ask_question(questions[0], answers)
