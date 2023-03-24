// This will be the object that will contain the Vue attributes
// and be used to initialize it.
let app = {};

// Given an empty app object, initializes it filling its attributes,
// creates a Vue instance, and then initializes the Vue instance.
let init = (app) => {

    // This is the Vue data.
    app.data = {

        myDexJSON: dexJSON,
        myPokemon: dexJSON["Pokemon"],

        topFiveRate: [],
        bottomFiveRate: [],
        topFiveFave: [],
        bottomFiveFave: [],

        types: {},
        games: {},
        generations: {},

        userFavorites: [],

        ratingText: "Rating Received!",
        ratingCount: 0,
        showNotif: false,
        fadeCountdown: 0,
        // Complete as you see fit.
    };

    app.enumerate = (a) => {
        // This adds an _idx field to each element of the array.
        let k = 0;
        a.map((e) => {e._idx = k++;});
        return a;
    };


    // This contains all the methods.
    app.methods = {
        // Complete as you see fit.
        pokemonImagePath(p) {
            return "images/PokemonArt/" + p['generation'] + "/" + p["fullname"].replace("\u2640", "Female").replace("\u2642", "Male").replaceAll("\u00e9", "e")  + ".png";
        },
        pokemonNumber(p) {
            return "#" + p['number'];
        },
        starID(p){
            return "star" + p['id'];
        },
        starIDRate(p, i){
            return "star" + i + "_" + p['id'];
        },
        faveID(p){
            return "fave" + p['id'];
        },
        typeImagePath(p, i) {
            return "images/Types/" + p.types[i] + "_en.png";
        },
        widthPerc(p){
            return "width: " + p.globalAverage*20 + "%;"
        },
        check(p, i){
            return (p.userRating == i)
        },
        ratePok(p, i){
            var postData = {"pokID": p.id, "rating": i};
            axios.post(set_rating_url, postData).then((response) => {
                if (response.data == "10 favorites already!"){
                    alert("Max number of favorites!")
                } else {
                    app.vue.showNotif = true;
                    app.vue.fadeCountdown += 3;
                    setTimeout(function () {
                        app.vue.fadeCountdown -= 3;
                        if (app.vue.fadeCountdown == 0){
                            app.vue.showNotif = false;
                            app.vue.ratingCount = 0;
                        }
                    }, 3000)

                    app.vue.ratingCount += 1;
                
                    if (app.vue.ratingCount > 1){
                        app.vue.ratingText =  response.data + "(" + app.vue.ratingCount + ")";
                    } else {
                        app.vue.ratingText = response.data
                    }
                }

                
            }).catch((error) => {
                console.log(error)
                alert("Log in to post ratings!")
            })
        },
    };

    // This creates the Vue instance.
    app.vue = new Vue({
        el: "#vue-target",
        data: app.data,
        methods: app.methods
    });

    app.addRateData = (myPokemon) => {
        myPokemon.map((pok) => {
            pok.totalRatings = 0;
            pok.ratings = [0,0,0,0,0,0]
            pok.globalAverage = 2.5;
            pok.userRating = 0;
            pok.userFavorite = false;
            pok.categoryIndex = 0;
        })
    }

    // And this initializes it.
    app.init = () => {
        // Put here any initialization code.
        // Typically this is a server GET call to load the data.
        


        axios.get(get_all_ratings_url).then((result) => {
            id_map = {};
            derived_rates = result.data.allRatings;
            i = 0;
            while (i < result.data.allRatings.length){
                currPoke = app.data.myPokemon[i];
                currPoke.totalRatings = result.data.allRatings[i]['ratingcount'];
                currPoke.ratings = [derived_rates[i]['onestar'], derived_rates[i]['twostar'], derived_rates[i]['threestar'], derived_rates[i]['fourstar'], derived_rates[i]['fivestar'], derived_rates[i]['favorites']];
                currPoke.ratings[5] = Math.floor(Math.random() * 10000);
                if (currPoke.totalRatings > 0){
                    currPoke.globalAverage = ( currPoke.ratings[0] + currPoke.ratings[1]*2 + currPoke.ratings[2]*3 + currPoke.ratings[3]*4 + currPoke.ratings[4]*5 ) / currPoke.totalRatings;
                } else {
                    currPoke.globalAverage = -1;
                }

                if (currPoke['significantForm']){
                    currPoke['types'].forEach((type) => {
                        if (app.data.types[type] == null){
                            //console.log("Adding " + type + " type");
                            app.data.types[type] = {
                                total: 1,
                                ratings: [currPoke.globalAverage],
                                favorites: [currPoke.ratings[5]],
                                bestRating: currPoke.globalAverage,
                                bestPoke: currPoke,
                                worstRating: currPoke.globalAverage,
                                worstPoke: currPoke,
                                mostFaves: currPoke.ratings[5],
                                mostFavesPoke: currPoke,
                                leastFaves: currPoke.ratings[5],
                                leastFavesPoke: currPoke
                            }
                        } else {
                            app.data.types[type]['total'] += 1;
                            app.data.types[type]['ratings'].push(currPoke.globalAverage)
                            app.data.types[type]['ratings'].push(currPoke.ratings[5])
                            if (currPoke.globalAverage > app.data.types[type]['bestRating']) {
                                app.data.types[type]['bestRating'] = currPoke.globalAverage;
                                app.data.types[type]['bestPoke'] = currPoke;
                            }
                            if (currPoke.globalAverage < app.data.types[type]['worstRating'] || app.data.types[type]['worstRating'] == -1) {
                                app.data.types[type]['worstRating'] = currPoke.globalAverage;
                                app.data.types[type]['worstPoke'] = currPoke;
                            }

                            if (currPoke.ratings[5] > app.data.types[type]['mostFaves']) {
                                app.data.types[type]['mostFaves'] = currPoke.ratings[5];
                                app.data.types[type]['mostFavesPoke'] = currPoke;
                            }

                            if (currPoke.ratings[5] < app.data.types[type]['leastFaves']) {
                                app.data.types[type]['leastFaves'] = currPoke.ratings[5];
                                app.data.types[type]['leastFavesPoke'] = currPoke;
                            }
                        }
                    });
                    currPoke['gameList'].forEach((game) => {
                        if (game.includes("X/Y")){
                            game = "X/Y"
                        }
                        //console.log("Adding " + game + " game");
                        if(app.data.games[game] == null){
                            app.data.games[game] = {
                                total: 1,
                                ratings: [currPoke.globalAverage],
                                favorites: [currPoke.ratings[5]],
                                bestRating: currPoke.globalAverage,
                                bestPoke: currPoke,
                                worstRating: currPoke.globalAverage,
                                worstPoke: currPoke,
                                mostFaves: currPoke.ratings[5],
                                mostFavesPoke: currPoke,
                                leastFaves: currPoke.ratings[5],
                                leastFavesPoke: currPoke
                            }
                        } else {
                            app.data.games[game]['total'] += 1;
                            app.data.games[game]['ratings'].push(currPoke.globalAverage);
                            app.data.games[game]['favorites'].push(currPoke.ratings[5])
                            if (currPoke.globalAverage >  app.data.games[game]['bestRating']) {
                                app.data.games[game]['bestRating'] = currPoke.globalAverage;
                                app.data.games[game]['bestPoke'] = currPoke;
                            }
                            if (currPoke.globalAverage <  app.data.games[game]['worstRating'] || app.data.games[game]['worstRating'] == -1) {
                                app.data.games[game]['worstRating'] = currPoke.globalAverage;
                                app.data.games[game]['worstPoke'] = currPoke;
                            }

                            if (currPoke.ratings[5] >  app.data.games[game]['mostFaves']) {
                                app.data.games[game]['mostFaves'] = currPoke.ratings[5];
                                app.data.games[game]['mostFavesPoke'] = currPoke;
                            }

                            if (currPoke.ratings[5] <  app.data.games[game]['leastFaves']) {
                                app.data.games[game]['leastFaves'] = currPoke.ratings[5];
                                app.data.games[game]['leastFavesPoke'] = currPoke;
                            }
                        }
                    });
    
                    gen = currPoke['generation']
                    if (gen == "Generation 8.5"){
                        gen = "Generation 8"
                    }
                    if (app.data.generations[gen] == null){
                        //console.log("Adding " + gen);
                        app.data.generations[gen] = {
                            total: 1,
                            ratings: [currPoke.globalAverage],
                            favorites: [currPoke.ratings[5]],
                            bestRating: currPoke.globalAverage,
                            bestPoke: currPoke,
                            worstRating: currPoke.globalAverage,
                            worstPoke: currPoke,
                            mostFaves: currPoke.ratings[5],
                            mostFavesPoke: currPoke,
                            leastFaves: currPoke.ratings[5],
                            leastFavesPoke: currPoke
                        } 
                    } else {
                        app.data.generations[gen]['total'] += 1
                        app.data.generations[gen]['ratings'].push(currPoke.globalAverage);
                        app.data.generations[gen]['favorites'].push(currPoke.ratings[5])
                        if (currPoke.globalAverage > app.data.generations[gen]['bestRating']) {
                            app.data.generations[gen]['bestRating'] = currPoke.globalAverage;
                            app.data.generations[gen]['bestPoke'] = currPoke;
                        }
                        if (currPoke.globalAverage < app.data.generations[gen]['worstRating'] || app.data.generations[gen]['worstRating'] == -1) {
                            app.data.generations[gen]['worstRating'] = currPoke.globalAverage;
                            app.data.generations[gen]['worstPoke'] = currPoke;
                        }

                        if (currPoke.ratings[5] > app.data.generations[gen]['mostFaves']) {
                            app.data.generations[gen]['mostFaves'] = currPoke.ratings[5];
                            app.data.generations[gen]['mostFavesPoke'] = currPoke;
                        }

                        if (currPoke.ratings[5] < app.data.generations[gen]['leastFaves']) {
                            app.data.generations[gen]['leastFaves'] = currPoke.ratings[5];
                            app.data.generations[gen]['leastFavesPoke'] = currPoke;
                        }
                    }

                    j = 0;
                    modified = [false, false, false, false]
                    while (j < 5){
                        if (!modified[0]){
                            if (j == app.data.topFiveRate.length){
                                app.data.topFiveRate.push(currPoke)
                                modified[0] = true;
                            } else if (j < app.data.topFiveRate.length){
                                if (currPoke.globalAverage > app.data.topFiveRate[j].globalAverage){
                                    app.data.topFiveRate.splice(j, 0, currPoke);
                                    modified[0] = true;
                                } 
                                if (app.data.topFiveRate.length > 5) app.data.topFiveRate.pop();
                            }
                        }
                        if (!modified[1]){
                            if (j == app.data.bottomFiveRate.length){
                                app.data.bottomFiveRate.push(currPoke)
                                modified[1] = true
                            } else if (j < app.data.bottomFiveRate.length){
                                if (currPoke.globalAverage < app.data.bottomFiveRate[j].globalAverage){
                                    app.data.bottomFiveRate.splice(j, 0, currPoke);
                                    modified[1] = true;
                                } 
                                if (app.data.bottomFiveRate.length > 5) app.data.bottomFiveRate.pop();
                            }
                        }
                        if (!modified[2]){
                            if (j == app.data.topFiveFave.length){
                                app.data.topFiveFave.push(currPoke)
                                modified[2] = true;
                            } else if (j < app.data.topFiveFave.length){
                                if (currPoke.ratings[5] > app.data.topFiveFave[j].ratings[5]){
                                    app.data.topFiveFave.splice(j, 0, currPoke);
                                    modified[2] = true;
                                } 
                                if (app.data.topFiveFave.length > 5) app.data.topFiveFave.pop();
                            }
                        }
                        if (!modified[3]){
                            if (j == app.data.bottomFiveFave.length){
                                app.data.bottomFiveFave.push(currPoke)
                                modified[3] = true;
                            } else if (j < app.data.bottomFiveFave.length){
                                if (currPoke.ratings[5] < app.data.bottomFiveFave[j].ratings[5]){
                                    app.data.bottomFiveFave.splice(j, 0, currPoke);
                                    modified[3] = true;
                                } 
                                if (app.data.bottomFiveFave.length > 5) app.data.bottomFiveFave.pop();
                            }
                        }
                        
                        j += 1
                    }
                }

                app.data.myPokemon[i] = currPoke
                id_map[currPoke['id']] = i;
                i += 1;
            }

            i=0
            while (i < result.data.userRatings.length){
                pokInd = id_map[ result.data.userRatings[i]['pokemon'] ]
                if (result.data.userRatings[i]['rating'] == 6){
                    app.data.myPokemon[pokInd].userFavorite = true;
                    app.data.userFavorites.push(app.data.myPokemon[pokInd]);
                } else {
                    app.data.myPokemon[pokInd].userRating = result.data.userRatings[i]['rating'];
                }
                i += 1;
            }
        });
    };



    // Call to the initializer.
    app.init();
};

// This takes the (empty) app object, and initializes it,
// putting all the code i
init(app);


