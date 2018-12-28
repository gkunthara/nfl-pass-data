import base64
import requests
import json
import os
from dotenv import load_dotenv
load_dotenv()


SECRET_KEY = os.getenv("KEY")
PASSWORD = os.getenv("PASSWORD")

def scheduleRequest():

    try:
        response = requests.get(
            url="https://api.mysportsfeeds.com/v1.0/pull/nfl/current/full_game_schedule.json?date=until-20181225",
            params={
                "fordate": "20161121"
            },
            headers={
                "Authorization": "Basic " + base64.b64encode('{}:{}'.format(SECRET_KEY,PASSWORD).encode('utf-8')).decode('ascii')
            }
        )
        print(response.status_code)
        content = response.content
        with open("schedule.json", "w") as write_file:
            json.dump(content, write_file, indent=4)
    except requests.exceptions.RequestException:
        print('HTTP Request failed')

def getPassesGames():

     with open("schedule.json", "r") as read_file:
        data = json.load(read_file)
        games = data["fullgameschedule"]["gameentry"]
        j = 199
        gameDict = {}
        for i in range(199, len(games)):
            date = games[i]["date"]
            awayTeam = games[i]["awayTeam"]["Abbreviation"]
            homeTeam = games[i]["homeTeam"]["Abbreviation"]
            url = "https://api.mysportsfeeds.com/v1.0/pull/nfl/current/game_playbyplay.json?gameid=%s-%s-%s&playtype=pass" % (date, awayTeam, homeTeam)
            try:
                response = requests.get(
                    url=url,
                    params={
                        "fordate": "20161121"
                    },
                    headers={
                        "Authorization": "Basic " + base64.b64encode('{}:{}'.format("e41168e0-18e0-47b3-ad26-b2bf0f","smallbaby").encode('utf-8')).decode('ascii')
                    }
                )
                print(response.status_code)
                print(i)
                gameDict[j] = response.content
                j += 1
            except requests.exceptions.RequestException:
                print('HTTP Request failed')
        with open("passes.json", "a") as write_file:
            json.dump(gameDict, write_file, indent=4)


def getPasses():
    passes = []
    with open("passes.json", "r") as read_file:
        data = json.load(read_file)
        for i in range(len(data)):
            plays = len(data[str(i)]["gameplaybyplay"]["plays"]["play"])
            passes.append(plays)
    return passes

def getPassesOver20Yards():

    newPlays = {}
    j = 0
    term = "deep"
    with open("passes.json", "r") as read_file:
        data = json.load(read_file)
        plays = data["gameplaybyplay"]["plays"]["play"]
        for i in range(len(plays)):
            playDescription = plays[i]["description"]
            words = playDescription.split()
            if term.lower() in words:
                newPlays[j] = plays[i]["passingPlay"]
                j+= 1
    
    with open("passes-over-20-yards.json", "w") as write_file:
        json.dump(newPlays, write_file)

    return len(newPlays)


def getCompletedPasses():
    completedPasses = {}
    j = 0
    with open("passes-over-20-yards.json", "r") as read_file:
        data = json.load(read_file)
        for i in range(len(data)):
            if data[str(i)]["isCompleted"] == "true":
                completedPasses[j] = data[str(i)]
                j+=1

    with open("passes-completed.json", "w") as write_file:
        json.dump(completedPasses, write_file)

    return len(completedPasses)


def getIncompletedOrInterceptedPasses():
    incompletedPasses = {}
    interceptedPasses = {}
    j = 0
    with open("passes-over-20-yards.json", "r") as read_file:
        data = json.load(read_file)
        for i in range(len(data)):
            if data[str(i)]["isCompleted"] == "false" and not data[str(i)].has_key("interceptingPlayer") :
                incompletedPasses[j] = data[str(i)]
                j+=1
            elif data[str(i)]["isCompleted"] == "false" and data[str(i)].has_key("interceptingPlayer") :
                interceptedPasses[j] = data[str(i)]
                j+=1

    with open("passes-incompleted-intercepted.json", "w") as write_file:
        json.dump(incompletedPasses, write_file)

    return len(incompletedPasses), len(interceptedPasses)


def getPassInterferencePasses():
    interferencePasses = {}
    j = 0
    with open("passes-over-20-yards.json", "r") as read_file:
        data = json.load(read_file)
        for i in range(len(data)):
            if data[str(i)].has_key("penalties"):
                if data[str(i)]["penalties"]["penalty"][0]["description"] == "Defensive Pass Interference":
                    interferencePasses[j] = data[str(i)]
                    j+=1

    with open("passes-interference.json", "w") as write_file:
        json.dump(interferencePasses, write_file)

    return len(interferencePasses)



# scheduleRequest() 
# passesRequest()
# getPassesGames()

passes = getPasses()
print(len(passes))
# deepPasses = getPassesOver20Yards()
# completedPasses = getCompletedPasses()
# incompletedPasses, interceptedPasses = getIncompletedOrInterceptedPasses()
# passInterferencePasses = getPassInterferencePasses()

# deepPlays = (float(deepPasses) / float(passes)) * 100
# piPlays = (float(passInterferencePasses) / float(deepPasses)) * 100
# positivePlays = ((float(completedPasses) + float(passInterferencePasses)) / float(deepPasses)) * 100
# incompletedPlays = (float(incompletedPasses) / float(deepPasses)) * 100
# interceptionPlays = (float(interceptedPasses) / float(deepPasses)) * 100

# print ("number of passes in this game: " + str(passes))
# print ("number of deep passes attempted in this game: " + str(deepPasses))
# print ("number of completed deep passes in this game: " + str(completedPasses))
# print ("number of incompleted deep passes in this game: " + str(incompletedPasses))
# print ("number of intercepted deep passes in this game: " + str(interceptedPasses))
# print ("number of defensive pass interference calls on deep passes in this game: " + str(passInterferencePasses))
# print('\n')
# print("percentage of deep passes in this game: " + str(deepPlays) + "%")
# print ("percentage of deep passes resulting in defensive PI : " + str(piPlays) + "%")
# print ("percentage of deep passes resulting in a POSITIVE PLAY: " + str(positivePlays) + "%")
# print ("percentage of deep passes resulting in an INCOMPLETION : " + str(incompletedPlays) + "%")
# print ("percentage of deep passes resulting in an INTERCEPTION: " + str(interceptionPlays) + "%")


