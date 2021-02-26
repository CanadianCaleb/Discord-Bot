import difflib

async def autocomp(word):

    print('Loading dataset')

    f = open('commands.txt', 'r')

    databaseRaw = f.read()

    database = databaseRaw.split('\n')

    f.close()

    for i in range(0, len(database)) :
        database[i] = database[i].lower()

    print('Loading dataset complete')
    usrInput = word

    wordSplit = list(usrInput.lower())

    usrInput = usrInput.lower()
        
    scores = []
    possibleWords = []

    score = 0

    wordSplit = list(usrInput)

    for i in range(0, len(database)) :

        databaseSplit = list(database[i])

        if databaseSplit[0] == wordSplit[0] :

            possibleWords.append(database[i])

    wordsChoice = difflib.get_close_matches(usrInput, possibleWords)

    wordSplit = list(usrInput)

    usrInNoDupes = [] 

    for i in range(0, len(wordSplit)) :

        if wordSplit[i] not in usrInNoDupes :

            usrInNoDupes.append(wordSplit[i])

    usrInNoDupes = ''.join(usrInNoDupes)
    
    for i in range(0, len(wordsChoice)) :

        score = 0
        wordChoiceSplit = list(wordsChoice[i])

        for j in range(0, len(list(usrInNoDupes))) :
                
            if usrInNoDupes[j] in wordChoiceSplit[i] :

                score += 1

        scores.append(score)

    if len(scores) > 0:
        return wordsChoice[scores.index(max(scores))]
    else:
        return None