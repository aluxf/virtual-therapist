from time import sleep
from furhat_remote_api import FurhatRemoteAPI
from numpy.random import randint

FURHAT_IP = "localhost"

furhat = FurhatRemoteAPI(FURHAT_IP)
furhat.set_led(red=100, green=50, blue=50)


def idle_animation():
    furhat.gesture(name="GazeAway")
    gesture = {
        "frames": [
            {
                "time": [0.33],
                "persist": True,
                "params": {
                    "NECK_PAN": randint(-4, 4),
                    "NECK_TILT": randint(-4, 4),
                    "NECK_ROLL": randint(-4, 4),
                },
            }
        ],
        "class": "furhatos.gestures.Gesture",
    }
    furhat.gesture(body=gesture, blocking=True)


def LOOK_BACK(speed):
    return {
        "frames": [
            {
                "time": [0.33 / speed],
                "persist": True,
                "params": {"LOOK_DOWN": 0, "LOOK_UP": 0, "NECK_TILT": 0},
            },
            {
                "time": [1 / speed],
                "params": {"NECK_PAN": 0, "LOOK_DOWN": 0, "LOOK_UP": 0, "NECK_TILT": 0},
            },
        ],
        "class": "furhatos.gestures.Gesture",
    }


# DO NOT CHANGE
def LOOK_DOWN(speed=1):
    return {
        "frames": [
            {
                "time": [0.33 / speed],
                "persist": True,
                "params": {
                    #                'LOOK_DOWN' : 1.0
                },
            },
            {"time": [1 / speed], "persist": True, "params": {"NECK_TILT": 20}},
        ],
        "class": "furhatos.gestures.Gesture",
    }


# Say with blocking (blocking say, bsay for short)
def bsay(line):
    furhat.say(text=line, blocking=True)


def laughter():
    furhat.say(text="hahaha", blocking=False)
    furhat.gesture(name="BigSmile")
    sleep(1)
    furhat.gesture(name="BigSmile")
    furhat.gesture(name="Wink")


def therapist_interaction():
    sleep(2)  # time to start video
    bsay("Hi!")

    while True:
        result = furhat.listen()
        # valence = get_valence(cam, detector, valence_model)
        client_mood = "happy"

        if result.success == True:
            print(result)
            if "hello" in result.message or "hi" in result.message:
                bsay("Hello. I'm your virtual therapist. What's your name?")

            elif "Alex" in result.message or "Eva" in result.message:
                name = result.message
                bsay(
                    "Hello, "
                    + name
                    + ". Amazing, lets get into it. Can you tell me a bit about yourself and your background?"
                )

                result = {"message": "hobbies", "success": True}
            elif "hobbies" in result.message or "hobby" in result.message:
                bsay("Oh that's nice! What brings you here today?")

            elif "I'm feeling great!" in result.message and client_mood == "happy":
                bsay(
                    "I'm glad to see you in good spirits! What positive things are happening in your life that you'd like to share?"
                )
                if "work is going well" in result.message:
                    bsay("Great to hear!")

            elif (
                "I've been feeling a bit down lately!" in result.message
                and client_mood == "sad"
            ):
                bsay(
                    "I'm sad to here that! What hard things are happening in your life that you'd like to share?"
                )
                if "work is very challenging at the moment" in result.message:
                    bsay("Sorry to hear that!")

                bsay(
                    "How are you feeling emotionally, mentally, and physically lately?"
                )

            elif (
                "good" in result.message
                or "happy" in result.message
                and client_mood == "happy"
            ):
                bsay("That's great to hear, I love that you're feeling well.")

            elif (
                "not good" in result.message
                or "stress" in result.message
                and client_mood == "sad"
            ):
                bsay(
                    "Oh no, what are some of the main challenges you're facing right now?"
                )
                if "I just went through a breakup" in result.message:
                    bsay("Sorry to hear that!")

                bsay(
                    "Have there been any major life changes or events recently that have affected you?"
                )

            elif "promotion" in result.message and client_mood == "happy":
                bsay("Wow, congratulations!")

            elif (
                "death" in result.message
                or "loss" in result.message
                and client_mood == "sad"
            ):
                bsay("I'm so sorry for your loss!")

            # bsay("What do you think might be contributing to the way you're feeling right now?")

            elif "thank you" in result.message or "bye" in result.message:
                bsay("Good bye")
                sleep(1)
                break

            else:
                bsay("I didn't get that, can you repeat?")
        else:
            bsay(
                "Sorry, there was an issue with the interaction. Can we try that again?"
            )


if __name__ == "__main__":
    therapist_interaction()
    idle_animation()
