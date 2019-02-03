import os
import base64
import requests
import json
import pandas as pd

from dotenv import load_dotenv
dotenv_path = ('.env')
load_dotenv(dotenv_path)


SECRET_KEY = os.getenv("KEY")
PASSWORD = os.getenv("PASSWORD")


# Request to My Sports Data Feed API which receives 2018-2019 NFL Regular Season Schedule
def scheduleRequest():

    try:
        response = requests.get(
            url="https://api.mysportsfeeds.com/v1.0/pull/nfl/2018-2019-regular/full_game_schedule.json",
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


# Retrieves all attempted passes for every game in the 2018-2019 regular season
def getPassesGames():

    with open("schedule.json", "r") as read_file:
        data = json.load(read_file)
        games = data["fullgameschedule"]["gameentry"]
        j = 240
        gameDict = {}
        for i in range(240, len(games)):
            date = games[i]["date"]
            awayTeam = games[i]["awayTeam"]["Abbreviation"]
            homeTeam = games[i]["homeTeam"]["Abbreviation"]
            url = "https://api.mysportsfeeds.com/v1.0/pull/nfl/2018-2019-regular/game_playbyplay.json?gameid=%s-%s-%s&playtype=pass" % (date, awayTeam, homeTeam)
            try:
                response = requests.get(
                    url=url,
                    params={
                        "fordate": "20161121"
                    },
                    headers={
                        "Authorization": "Basic " + base64.b64encode('{}:{}'.format(SECRET_KEY, PASSWORD).encode('utf-8')).decode('ascii')
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
def getCompletedDeepPasses():
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
                if gamePasses[str(j)]["isCompleted"] == "false" and gamePasses[str(j)].has_key("interceptingPlayer") and int(gamePasses[str(j)]["yardsPassed"]) > 20:
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
# getPassesGames()

passes = getPasses()
deepPasses = getPassesOver20Yards()
completedDeepPasses = getCompletedDeepPasses()
incompletedPasses = getIncompletedPasses()
interceptedPasses = getInterceptedPasses()
passInterferencePasses = getPassInterferencePasses()


pi_percent_list = []
catch_percent_list = []
positivePlay_percent_list = []
interception_percent_list = []
deepBall_list = []

for i in range(0,256):

    pi_percent = (float(len(passInterferencePasses[i])) / float(len(deepPasses[i]))) * 100
    catch_percent = (float(len(completedDeepPasses[i])) / float(len(deepPasses[i]))) * 100
    positivePlay_percent = ((float(len(passInterferencePasses[i])) + float(len(completedDeepPasses[i]))) / float(len(deepPasses[i]))) * 100

    interception_percent = (float(len(interceptedPasses[i])) / float(len(deepPasses[i]))) * 100


    pi_percent_list.append(pi_percent)
    catch_percent_list.append(catch_percent)
    positivePlay_percent_list.append(positivePlay_percent)

    interception_percent_list.append(interception_percent)

    deepBall_list.append(float(len(deepPasses[i])))


pi_percent_series = pd.Series(pi_percent_list) 
catch_percent_series = pd.Series(catch_percent_list)
positivePlay_percent_series = pd.Series(positivePlay_percent_list)

interception_percent_series = pd.Series(interception_percent_list)

print '\n'
print("What % of deep balls result in a pass interference call?")
print pi_percent_series.describe()

print '\n'
print '\n'
print '\n'

print("What % of deep balls result in a catch?")
print catch_percent_series.describe()

print '\n'
print '\n'
print '\n'

print("What % of deep balls result in a net positive play? (Either a catch or a PI call)")
print positivePlay_percent_series.describe()

print '\n'
print '\n'
print '\n'

print("What % of deep balls thrown result in an interception?")
print interception_percent_series.describe()

print '\n'
print '\n'
print '\n'

print "What % of passes thrown are deep balls? (Passes > 20 yards)"
print (float(sum(deepBall_list)) / float(sum(passes))) * 100
















