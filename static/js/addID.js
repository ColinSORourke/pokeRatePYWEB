const fs = require("fs");
fs.readFile("../FullDex.json", "utf8", (err, jsonString) => {
    if (err){
        console.log("File Read failed: ", err)
        return;
    }
    fullDex = JSON.parse(jsonString)

    var i = 0;
    while (i < fullDex["Pokemon"].length){
        var currPoke = fullDex["Pokemon"][i]

        var formIndex = currPoke['formList'].indexOf(currPoke['fullname'])

        var id = currPoke['number'] + String(formIndex).padStart(2, '0')

        fullDex["Pokemon"][i]['id'] = id
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