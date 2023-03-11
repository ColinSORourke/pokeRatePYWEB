
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

        

        if (!currPoke["significantForm"]){
            fullDex["Pokemon"][i]["category"] = "Ignore"
        }
        else {
            var j = 0;
            while (j < fullDex["categories"].length){
                currCategory = fullDex["categories"][j]
                var rightGen = (currPoke[ currCategory["criteria"][0]["field"] ] == currCategory["criteria"][0]["values"]);
                var rightForm = (currCategory["criteria"][1]["values"].includes(currPoke[ currCategory["criteria"][1]["field"] ]));
                if (rightGen && rightForm){
                    fullDex["Pokemon"][i]["category"] = currCategory["title"];
                    j = fullDex["categories"].length
                }
                j += 1;
            }
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