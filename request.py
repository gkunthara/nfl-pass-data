import base64
import requests
import json
import os
import pandas as pd

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



# returns a list containing total passes for each game
def getPasses():
    passes = []
    with open("passes.json", "r") as read_file:
        data = json.load(read_file)
        for i in range(len(data)):
            plays = len(data[str(i)]["gameplaybyplay"]["plays"]["play"])
            passes.append(plays)
    return passes


# returns a dict containing all passes attempted over 20 yards for each game
def getPassesOver20Yards():

    allPlays = {}
    term = "deep"
    with open("passes.json", "r") as read_file:
        games = json.load(read_file)
        for i in range(len(games)):
            plays = games[str(i)]["gameplaybyplay"]["plays"]["play"]
            k = 0
            game = {}
            for j in range(len(plays)):
                playDescription = plays[j]["description"]
                words = playDescription.split()
                if term.lower() in words:
                    game[k] = plays[j]["passingPlay"]
                    k+= 1
            allPlays[i] = game
    
    with open("passes-over-20-yards.json", "w") as write_file:
        json.dump(allPlays, write_file)

    return allPlays


# returns a dict containing all completed passes over 20 yards for each game
def getCompletedPasses():
    completedPasses = {}
    
    with open("passes-over-20-yards.json", "r") as read_file:
        games = json.load(read_file)
        for i in range(len(games)):
            k = 0
            game = {}
            gamePasses = games[str(i)]
            for j in range(len(gamePasses)):
                if gamePasses[str(j)]["isCompleted"] == "true":
                    game[k] = gamePasses[str(j)]
                    k += 1
                   
            completedPasses[i] = game

    with open("passes-completed.json", "w") as write_file:
        json.dump(completedPasses, write_file)

    return completedPasses


# returns a dict containing all incompletions for passes > 20 yards for each game
def getIncompletedPasses():
    incompletedPasses = {}
    with open("passes-over-20-yards.json", "r") as read_file:
        games = json.load(read_file)
        for i in range(len(games)):
            game = {}
            k = 0
            gamePasses = games[str(i)]
            for j in range(len(gamePasses)):
                if gamePasses[str(j)]["isCompleted"] == "false" and not gamePasses[str(j)].has_key("interceptingPlayer") :
                    game[k] = gamePasses[str(j)]
                    k+=1
            incompletedPasses[i] = game
                

    with open("passes-incompleted.json", "w") as write_file:
        json.dump(incompletedPasses, write_file)

    return incompletedPasses


# returns a dict containing all interceptions for passes attempted > 20 yards for each game
def getInterceptedPasses():
    interceptedPasses = {}
    with open("passes-over-20-yards.json", "r") as read_file:
        games = json.load(read_file)
        for i in range(len(games)):
            game = {}
            k = 0
            gamePasses = games[str(i)]
            for j in range(len(gamePasses)):
                if gamePasses[str(j)]["isCompleted"] == "false" and gamePasses[str(j)].has_key("interceptingPlayer") :
                    game[k] = gamePasses[str(j)]
                    k+=1

            interceptedPasses[i] = game
                

    with open("passes-intercepted.json", "w") as write_file:
        json.dump(interceptedPasses, write_file)

    return interceptedPasses



# returns a dict containing all incomplete passes thrown > 20 yards that resulted in defensive
# pass interference for every game
def getPassInterferencePasses():
    interferencePasses = {}
    with open("passes-over-20-yards.json", "r") as read_file:
        games = json.load(read_file)
        for i in range(len(games)):
            game = {}
            k = 0
            gamePasses = games[str(i)]
            for j in range(len(gamePasses)):
                if gamePasses[str(j)].has_key("penalties"):
                    if gamePasses[str(j)]["isCompleted"] == "false" and gamePasses[str(j)]["penalties"]["penalty"][0]["description"] == "Defensive Pass Interference":
                        game[k] = gamePasses[str(j)]
                        k+=1

            interferencePasses[i] = game

    with open("passes-interference.json", "w") as write_file:
        json.dump(interferencePasses, write_file)

    return interferencePasses



# scheduleRequest() 
# passesRequest()
# getPassesGames()

# passes = getPasses()
# deepPasses = getPassesOver20Yards()
# completedPasses = getCompletedPasses()
# incompletedPasses = getIncompletedPasses()
# interceptedPasses = getInterceptedPasses()
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


# pass_series = pd.Series(passes)
# print(pass_series.mode())
#deepPass_series = pd.Series(deepPasses)

