// This will be the object that will contain the Vue attributes
// and be used to initialize it.
let app = {};

// Given an empty app object, initializes it filling its attributes,
// creates a Vue instance, and then initializes the Vue instance.
let init = (app) => {

    // This is the Vue data.
    app.data = {
        // Complete as you see fit.
        myDexJSON: dexJSON,
        myPokemon: dexJSON.filter((pokemon) => 
            pokemon.form == "Basic"
        ),
        targetPokemon: {},
        solved: false,
        query: "",
        acSuggestions: [],
        myGuesses: [],
        noGuess: true,
        showModal: false,
        showStats: false,
        statsLoaded: false,
        userStats: [0, 0, 0, 0, [0, 0, 0, 0, 0, 0]],
        loading: 0,
        recentGuess: {},
    };

    app.enumerate = (a) => {
        // This adds an _idx field to each element of the array.
        let k = 0;
        a.map((e) => {e._idx = k++;});
        return a;
    };


    // This contains all the methods.
    app.methods = {
        onchange() {
            if (app.vue.query != ""){
                app.vue.acSuggestions = app.vue.myPokemon.filter((pokemon) => pokemon.name.toLowerCase().indexOf(app.vue.query.toLowerCase()) == 0).slice(0,5) 
            } else {
                app.vue.acSuggestions = [];
            }
            
        },
        acFill(p) {
            app.vue.query = p.name;
            app.vue.acSuggestions = [];
        },
        submitGuess(){
            let guess = app.vue.myPokemon.find(p => p.name == app.vue.query);

            if (guess != undefined){
                guess['globalAverage'] = 2.5
                app.vue.myGuesses.push(guess);
                app.vue.recentGuess = guess;
                app.vue.query = '';
                app.vue.loading += 1;
                axios.get(get_rating_url, { params: { id: guess.id } }).then(result => {
                    let totalRates = (result.data.fiveRates) + (result.data.fourRates) + (result.data.threeRates) + (result.data.twoRates ) + (result.data.oneRates)
                    app.vue.myGuesses[app.vue.myGuesses.length - 1]['globalAverage'] = ( (result.data.fiveRates * 5) + (result.data.fourRates * 4) + (result.data.threeRates * 3) + (result.data.twoRates * 2) + (result.data.oneRates) ) / totalRates;
                    app.vue.loading -= 1;
                    app.vue.noGuess = false;
                    app.vue.recentGuess = app.vue.myGuesses[app.vue.myGuesses.length - 1];
                })
                let dateString = app.vue.dateString()

                guessesStr = ""
                if (typeof(Storage) !== "undefined") {
                    if (localStorage.getItem(dateString) !== null){
                        prevGuesses = localStorage.getItem(dateString)
                        prevGuesses = prevGuesses + "---" + guess.name;
                        guessesStr = prevGuesses
                        localStorage.setItem(dateString, prevGuesses);
                    } else {
                        guessesStr = guess.name;
                        localStorage.setItem(dateString, guess.name);
                    }
                } else {
                    // Sorry! No Web Storage support..
                }

                if (guess.name == app.vue.targetPokemon.name || myGuesses.length == 6){
                    app.vue.solved = true;
                    var postData = {"guesses": guessesStr};
                    axios.post(post_plays_url, postData)
                }
            }
        },
        pokemonImagePath(p) {
            return "images/PokemonArt/" + p['generation'] + "/" + p["fullName"].replace("\u2640", "Female").replace("\u2642", "Male").replaceAll("\u00e9", "e")  + ".png";
        },
        setGuess(p){
            app.vue.recentGuess = p;
        },
        pokemonNumber(p) {
            return "#" + p['number'];
        },
        typeImagePath(p, i) {
            return "images/Types/" + p.types[i].toLowerCase() + ".png";
        },
        widthPerc(p){
            if (p.globalAverage == -1){
                return "width: 50%;";
            }
            return "width: " + p.globalAverage*20 + "%;"
        },
        checkAlph(p){
            if (p.name[0] < app.vue.targetPokemon.name[0]){
                return "fa fa-arrow-circle-right"
            } else if (p.name[0] > app.vue.targetPokemon.name[0]){
                return "fa fa-arrow-circle-left"
            } else {
                return "fa fa-check-circle"
            }
        },
        checkGen(p){
            guessGen = p.generation[11]
            targetGen = app.vue.targetPokemon.generation[11]
            if (guessGen == targetGen){
                return "fa fa-check-circle"
            } else {
                return "fa fa-times-circle"
            }
        },
        getGen(p){
            return "Generation " + p.generation[11];
        },
        checkTypePrim(p){
            if (app.vue.targetPokemon.types.includes(p.types[0])){
                return "fa fa-check-circle"
            } else {
                return "fa fa-times-circle"
            }
        },
        checkTypeSecond(p){
            if (p.types.length == 1 && app.vue.targetPokemon.types.length == 1){
                return "fa fa-check-circle"
            } else if (p.types.length == 1){
                return "fa fa-times-circle"
            } else {
                if (app.vue.targetPokemon.types.includes(p.types[1])){
                    return "fa fa-check-circle"
                } else {
                    return "fa fa-times-circle"
                }
            }
        },
        checkBST(p){
            if (p.bst == app.vue.targetPokemon.bst){
                return "fa fa-check-circle"
            } else if (p.bst < app.vue.targetPokemon.bst){
                return "fa fa-arrow-circle-up"
            } else {
                return "fa fa-arrow-circle-down"
            }
        },
        checkRate(p){
            if (app.vue.loading != 0){
                return "fa fa-spinner"
            } else if (p.globalAverage.toFixed(2) == app.vue.targetPokemon.globalAverage.toFixed(2)){
                return "fa fa-check-circle"
            } else if (p.globalAverage.toFixed(2) < app.vue.targetPokemon.globalAverage.toFixed(2)){
                return "fa fa-arrow-circle-up"
            } else {
                return "fa fa-arrow-circle-down"
            }
        },
        mostRecentGuess(){
            if (app.vue.recentGuess != {}){
                return app.vue.recentGuess
            } else if (app.vue.myGuesses.length > 0){
                return app.vue.myGuesses[app.vue.myGuesses.length - 1]
            } else {
                return {name: "None"}
            }  
        },
        parseGuesses(guessesStr){
            let guesses = guessesStr.split('---')
            var i = 0;
            while (i < guesses.length){
                pokName = guesses[i]
                let guess = app.vue.myPokemon.find(p => p.name == pokName);
                guess["globalAverage"] = 2.5
                app.vue.myGuesses.push(guess);
                app.vue.recentGuess = guess;
                if (guess.name == app.vue.targetPokemon.name){
                    app.vue.solved = true;
                }
                app.vue.loading += 1
                axios.get(get_rating_url, { params: { id: guess.id} }).then(result => {
                    let totalRates = (result.data.fiveRates) + (result.data.fourRates) + (result.data.threeRates) + (result.data.twoRates ) + (result.data.oneRates)
                    j = 0
                    while (j < app.vue.myGuesses.length){
                        if (app.vue.myGuesses[j].id == guess.id){
                            app.vue.myGuesses[j]['globalAverage'] = ( (result.data.fiveRates * 5) + (result.data.fourRates * 4) + (result.data.threeRates * 3) + (result.data.twoRates * 2) + (result.data.oneRates) ) / totalRates;
                            app.vue.noGuess = false;
                            if (guess.name == app.vue.targetPokemon.name || myGuesses.length == 6){
                                app.vue.solved = true;
                                var postData = {"guesses": guessesStr};
                                axios.post(post_plays_url, postData)
                            }
                        }
                        j += 1
                    }
                    app.vue.loading -= 1;
                })                
                i += 1
            }
        },
        dateString(){
            const months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
            let d = new Date(new Date().toLocaleString("en-US", {timeZone: "America/New_York"}));
            return months[d.getMonth()] + d.getDate() + "y" + d.getFullYear();
        },
        barHeight(n){
            let maxRates = 0;
            let j = 0;
            while (j < 6){
                if (app.vue.userStats[4][j] > maxRates){
                    maxRates = app.vue.userStats[4][j];
                }
                j += 1;
            }
            if(maxRates == 0){
                maxRates = 1;
            }
            return "height: " + (app.vue.userStats[4][n-1]/maxRates) * 100 + "%;"
        }
    }
    // This creates the Vue instance.
    app.vue = new Vue({
        el: "#vue-target",
        data: app.data,
        methods: app.methods,
    });

    // And this initializes it.
    app.init = () => {
        randIndex = Math.floor(Math.random() * app.vue.myPokemon.length)
        app.vue.targetPokemon = targetPokemon;
        app.vue.targetPokemon['globalAverage'] = 2.5

        app.vue.loading += 1
        axios.get(get_rating_url, { params: { id: app.vue.targetPokemon.id } }).then(result => {
            let totalRates = (result.data.fiveRates) + (result.data.fourRates) + (result.data.threeRates) + (result.data.twoRates ) + (result.data.oneRates)
            app.vue.targetPokemon['globalAverage'] = ( (result.data.fiveRates * 5) + (result.data.fourRates * 4) + (result.data.threeRates * 3) + (result.data.twoRates * 2) + (result.data.oneRates) ) / totalRates;
            app.vue.loading -= 1;
        })

        
        let dateString = app.vue.dateString()
        if (typeof(Storage) !== "undefined") {
            if (localStorage.getItem(dateString) !== null){
                app.vue.parseGuesses(localStorage.getItem(dateString))
            }

            if (localStorage.getItem("visitedPuzzle") == null){
                localStorage.setItem("visitedPuzzle", "true")
                app.vue.showModal = true;
            }
        } else {
            // Sorry! No Web Storage support..
        }

        axios.get(get_plays_url).then(result => {
            console.log(result);
            if (result.data.userPlays.length != 0){
                userPlays = result.data.userPlays
    
                i = 0;
                solves = [0, 0, 0, 0, 0, 0]
                app.vue.userStats[0] = userPlays.length;

                streakPos = new Date(new Date().toLocaleString("en-US", {timeZone: "America/New_York"}));
                streakPos.setHours(0)
                streakPos.setMinutes(0)
                streakPos.setSeconds(0)
                streakPos.setMilliseconds(0)
                currStreak = 0;
                presentStreak = true;
                if ((streakPos - new Date(userPlays[0][0])) / (60 * 60 * 24 * 1000) == 0){
                    app.vue.parseGuesses(userPlays[0][2])
                }

                while (i < userPlays.length){
                    thisPlay = userPlays[i]
                    
                    if (thisPlay[1] == "T"){
                        app.vue.userStats[1] += 1;
                    }
                    solves[thisPlay[3] - 1] += 1;
                    


                    if ( (streakPos - new Date(thisPlay[0])) / (60 * 60 * 24 * 1000) <= 1){
                        currStreak += 1;
                    } else {
                        if (presentStreak){
                            app.vue.userStats[3] = currStreak;
                        }
                        presentStreak = false;
                        if (currStreak > app.vue.userStats[2]){
                            app.vue.userStats[2] = currStreak;
                        }
                        currStreak = 1;
                    }
                    streakPos = new Date(thisPlay[0])
                    i += 1;
                }
                if (currStreak > app.vue.userStats[2]){
                    app.vue.userStats[2] = currStreak;
                }
                app.vue.userStats[4] = solves;
                app.vue.statsLoaded = true;
            }
        })

    };



    // Call to the initializer.
    app.init();
};

// This takes the (empty) app object, and initializes it,
// putting all the code i
init(app);


