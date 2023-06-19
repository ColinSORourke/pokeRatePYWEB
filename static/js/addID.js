const fs = require("fs");
fs.readFile("../FullDex.json", "utf8", (err, jsonString) => {
    if (err){
        console.log("File Read failed: ", err)
        return;
    }
    fullDex = JSON.parse(jsonString)

    var i = 0;
    while (i < fullDex.length){
        var currPoke = fullDex[i]

        if (currPoke['form'] == "Gigantamax "){
            currPoke['pokID'] = String( Number(currPoke['pokID']) + 1).padStart(6, '0')
        }

        i += 1
    }

    fs.writeFile('../FullDex.json', JSON.stringify(fullDex), err => {
        if (err) {
            console.log('Error writing file', err)
        } else {
            console.log('Successfully wrote file')
        }
    })
})