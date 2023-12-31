from time import sleep
from furhat_remote_api import FurhatRemoteAPI
from numpy.random import randint
import numpy as np
from sentence_transformers import SentenceTransformer, util


embedding_model = SentenceTransformer("sentence-transformers/all-mpnet-base-v2")

FURHAT_IP = "localhost"

furhat = FurhatRemoteAPI(FURHAT_IP)


def predict_answer(user_input, answers):
    """
    Predicts the most suitable answer from a list of possible answers based on the user input.

    Args:
        user_input (str): The input provided by the user.
        answers (list): A list of possible answers.

    Returns:
        tuple: A tuple containing the predicted answer index and the cosine similarity score.
    """
    answer_embeddings = embedding_model.encode(answers, convert_to_tensor=True)
    input_embedding = embedding_model.encode(user_input, convert_to_tensor=True)
    cos_scores = util.pytorch_cos_sim(input_embedding, answer_embeddings)[0]
    return cos_scores.argmax(), cos_scores.max()


def valence_str(valence_nr):
    if valence_nr < -0.1:
        return "negative"
    if valence_nr > 0:
        return "positive"
    return "neutral"


def get_valence(shared_list):
    try:
        avg_valence = np.mean(shared_list)
        valence = valence_str(avg_valence)
    except Exception as e:
        print(e)
        return "neutral"
    return valence


# Say with blocking (blocking say, bsay for short)
def bsay(line):
    furhat.say(text=line, blocking=True)


# answers = [1, 2, 3, 4, 5]
def score(answer_idx):
    return answer_idx + 1


def confirm_answer():
    bsay("Are you sure about your answer?")
    while True:
        result = furhat.listen()
        confirmation = result.message.lower()
        if "yes" in confirmation:
            return True
        elif "no" in confirmation:
            bsay("Okay, please think it over again. How do you really feel?")
            return False

        bsay("I did not get that, please answer yes or no.")


def listen(tries=3):
    for _ in range(tries):
        result = furhat.listen()
        answer = result.message.lower()
        if answer:
            return answer
        bsay("You did not say anything, please try again.")
    # Throw exception. mic is not working
    raise Exception("Mic is not working properly.")


def ask_question(shared_list, question, answers):
    while True:
        bsay(question)
        answer = listen()
        valence = get_valence(shared_list)
        print(shared_list)
        print("Valence: ", valence)
        print(answer)
        answer_idx, probability = predict_answer(answer, answers)
        print(answer_idx)
        print(probability)
        if probability < 0.4:
            bsay("I did not get that, please give me a valid answer")
            continue

        # Negative answer
        if answer_idx < 2 and valence != "positive":
            bsay("Okey, sorry to hear that.")

        # Neutral answer
        elif answer_idx == 2 and valence == "neutral":
            bsay("Okey!")

        # Positive answer
        elif answer_idx > 2 and valence != "negative":
            bsay("Thats nice to hear!")

        # Answer does not match valence
        else:
            yes = confirm_answer()
            if not yes:
                continue

        return score(answer_idx)


def introduction():
    while True:
        bsay(
            "Hi! I'm a virtual therapist and I specialize in students' well-being. I'm happy to see you here today! Please state your name."
        )
        name = listen()
        bsay("Nice to meet you, " + name + ". Lets get into it.")

        return name


def recommendation(score, name):
    bsay("Thank you for answering all of my questions" + name)
    bsay("I have now calculated your average score which is" + str(score))

    if score < 2.5:
        bsay(
            "Based on your score, I would recommend you to seek further help from a professional therapist."
        )

    elif score > 3.5:
        bsay(
            "Based on your score, I believe that you're doing very well. Keep up the good work!"
        )

    else:
        bsay(
            "Based on your score, I believe you're doing okay but might benefit from taking a minute to slow down. Reflect on how you handle stress and learn to say no."
        )

    bsay(
        "Thank you for a nice chat, I hope my virtual therapy helped you in your well-being as a student. Feel free to contact me if you need any more help, I'm available twenty-four seven."
    )
