
fullDex = dexJSON

typeList = ["Any", "Normal", "Grass", "Fire", "Water", "Electric", "Rock", "Ground", "Steel", "Fighting", "Flying", "Psychic", "Fairy", "Dark", "Ghost", "Dragon", "Bug", "Poison", "Ice", "Generation 1", "Generation 2", "Generation 3", "Generation 4", "Generation 5", "Generation 6", "Generation 7", "Generation 8", "Generation 9"]
typeDict = {}
pairs = []

var i = 0;
while (i < typeList.length){
    typeDict[typeList[i]] = {}
    alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    var j = 0;
    while (j < 26){
        typeDict[typeList[i]][alphabet[j]] = 0
        j += 1
    }
    i += 1
}

i = 0
while (i < fullDex.length){
    var currPoke = fullDex[i]
    typeDict["Any"][currPoke['name'][0]] += 1
    typeDict[currPoke['types'][0]][currPoke['name'][0]] += 1
    if (currPoke['types'].length == 2){
        typeDict[currPoke['types'][1]][currPoke['name'][0]] += 1
    }
    if (currPoke["generation"] != "Generation 8.5"){
        typeDict[currPoke['generation']][currPoke['name'][0]] += 1
    }

    var j = i + 1;
    while (j < fullDex.length && fullDex[j]['generation'] == currPoke['generation']){
        if (currPoke['name'][0] == fullDex[j]['name'][0] && matchTypes(currPoke, fullDex[j]) && currPoke['form'] == "Basic" && fullDex[j]['form'] == "Basic"){
            pairs.push( [currPoke['name'], fullDex[j]['name']] )
            if (currPoke['bst'] == fullDex[j]['bst']){
                console.log("THE AWFUL PAIR HAS BEEN FOUND")
                console.log(currPoke['name'] + " AND " + fullDex[j]['name'])
            }
        }
        j += 1;
    }
    i += 1;
}

console.log(pairs)
console.log(typeDict)

function matchTypes(pokA, pokB){
    if (pokA['types'].length == 2 && pokB['types'].length == 2){
        return pokB['types'].includes(pokA['types'][0]) && pokB['types'].includes(pokA['types'][1]);
    } else if (pokA['types'].length == 1 && pokB['types'].length == 1){
        return pokB['types'].includes(pokA['types'][0])
    } else {
        return false
    }
}