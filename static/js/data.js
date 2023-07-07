// This will be the object that will contain the Vue attributes
// and be used to initialize it.
let app = {};

// Given an empty app object, initializes it filling its attributes,
// creates a Vue instance, and then initializes the Vue instance.
let init = (app) => {

    // This is the Vue data.
    app.data = {

        myDexJSON: dexJSON,
        myPokemon: dexJSON,

        displayType: "Rate",

        topFiveRate: [],
        bottomFiveRate: [],
        topFiveFave: [],
        bottomFiveFave: [],

        types: {},
        generations: {},

        userFavorites: [],
        userData: false,

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
            return "images/PokemonArt/" + p['generation'] + "/" + p["fullName"].replace("\u2640", "Female").replace("\u2642", "Male").replaceAll("\u00e9", "e")  + ".png";
        },
        pokemonNumber(p) {
            return "#" + p['number'];
        },
        starID(p){
            return "star" + p['pokID'];
        },
        starIDRate(p, i){
            return "star" + i + "_" + p['pokID'];
        },
        faveID(p){
            return "fave" + p['pokID'];
        },
        typeImagePath(p, i) {
            return "images/Types/" + p.types[i].toLowerCase() + "_en.png";
        },
        typeImagePathB(t) {
            return "images/Types/" + t.toLowerCase() + "_en.png";
        },
        widthPerc(p){
            if (p.globalAverage == -1){
                return "width: 50%;";
            }
            return "width: " + p.globalAverage*20 + "%;"
        },
        check(p, i){
            return (p.userRating == i)
        },
        ratePok(p, i){
            var postData = {"id": p.id, "rating": i};
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
        dexPath(p){
            return dex_url + "/" + p["pokID"]
        },
        setDisplayType(t){
            app.data.displayType = t;
        },
        getGen(n){
            key = "Generation " + n
            return(app.data.generations[key]);
        },
        abbrevNum(n){
            if (isNaN(n)){
                return "No data!"
            }
            if (n < 9999){
                return Intl.NumberFormat('en-US', {
                    notation: "standard",
                    maximumSignificantDigits: 4,
                  }).format(n);
            } else {
                return Intl.NumberFormat('en-US', {
                    notation: "compact",
                    maximumSignificantDigits: 4,
                  }).format(n);
            }
            
        }
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
                // Regular Calculations
                currPoke = app.data.myPokemon[i];
                currPoke.totalRatings = result.data.allRatings[i]['ratingcount'];
                currPoke.ratings = [derived_rates[i]['onestar'], derived_rates[i]['twostar'], derived_rates[i]['threestar'], derived_rates[i]['fourstar'], derived_rates[i]['fivestar'], derived_rates[i]['favorites']];
                if (currPoke.totalRatings > 0){
                    currPoke.globalAverage = ( currPoke.ratings[0] + currPoke.ratings[1]*2 + currPoke.ratings[2]*3 + currPoke.ratings[3]*4 + currPoke.ratings[4]*5 ) / currPoke.totalRatings;
                } else {
                    currPoke.globalAverage = -1;
                }

                // Add to overall data
                if (currPoke['significantForm']){
                    currPoke['types'].forEach((type) => {
                        if (app.data.types[type] == null){
                            //console.log("Adding " + type + " type");
                            app.data.types[type] = {
                                typeName: type,
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
                                leastFavesPoke: currPoke,
                                userRates: [],
                                statuses: [0,0,0]
                            }
                        } else {
                            app.data.types[type]['total'] += 1;
                            app.data.types[type]['ratings'].push(currPoke.globalAverage)
                            app.data.types[type]['favorites'].push(currPoke.ratings[5])
                            if (currPoke.globalAverage > app.data.types[type]['bestRating']) {
                                app.data.types[type]['bestRating'] = currPoke.globalAverage;
                                app.data.types[type]['bestPoke'] = currPoke;
                            }
                            if (currPoke.globalAverage < app.data.types[type]['worstRating'] || ( app.data.types[type]['worstRating'] == -1 && currPoke.globalAverage != -1 ) ) {
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

                    gen = currPoke['generation']
                    if (gen == "Generation 8.5"){
                        gen = "Generation 8"
                    }
                    if (app.data.generations[gen] == null){
                        app.data.generations[gen] = {
                            genName: gen,
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
                            leastFavesPoke: currPoke,
                            userRates: [],
                            statuses: [0,0,0]
                        } 
                    } else {
                        app.data.generations[gen]['total'] += 1
                        app.data.generations[gen]['ratings'].push(currPoke.globalAverage);
                        app.data.generations[gen]['favorites'].push(currPoke.ratings[5])
                        if (currPoke.globalAverage > app.data.generations[gen]['bestRating']) {
                            app.data.generations[gen]['bestRating'] = currPoke.globalAverage;
                            app.data.generations[gen]['bestPoke'] = currPoke;
                        }
                        if (currPoke.globalAverage < app.data.generations[gen]['worstRating'] || ( app.data.generations[gen]['worstRating'] == -1 && currPoke.globalAverage != -1) ) {
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
                app.data.userData = true;
                pokInd = id_map[ result.data.userRatings[i]['pokemon'] ]
                if (result.data.userRatings[i]['rating'] == 6){
                    app.data.myPokemon[pokInd].userFavorite = true;
                    app.data.userFavorites.push(app.data.myPokemon[pokInd]);
                } else {
                    app.data.myPokemon[pokInd].userRating = result.data.userRatings[i]['rating'];
                    if (app.data.myPokemon[pokInd]['significantForm']){
                        app.data.myPokemon[pokInd].types.forEach((type) => {
                            app.data.types[type].userRates.push(result.data.userRatings[i]['rating']);
                        });
                        gen = app.data.myPokemon[pokInd].generation;
                        if (gen == "Generation 8.5"){
                            gen = "Generation 8"
                        }
                        app.data.generations[gen].userRates.push(result.data.userRatings[i]['rating'])
                    }
                }
                i += 1;
            }


            bestGens = ["Generation 1", "Generation 1", "Generation 1"]
            bestGenVals = [0, 0, 0]
            worstGens = ["Generation 1", "Generation 1", "Generation 1"]
            worstGenVals = [5, Infinity, 5]

            

            for (var key in app.data.generations){
                gen = app.data.generations[key];
                gen['rateTotal'] = gen['total']
                sum = 0;
                faveSum = 0;
                userSum = 0;
                i = 0;

                while(i < gen['ratings'].length){
                    if (gen['ratings'][i] == -1){
                        gen['rateTotal'] -= 1;
                    } else {
                        sum += gen['ratings'][i];
                        faveSum += gen['favorites'][i];
                    }
                    if (i < gen['userRates'].length){
                        userSum += gen['userRates'][i];
                    }
                    i += 1;
                } 
                app.data.generations[key]['average'] = sum / gen['rateTotal'];
                if (app.data.generations[key]['average'] > bestGenVals[0]){
                    bestGens[0] = key;
                    bestGenVals[0] = app.data.generations[key]['average'];
                }
                if (app.data.generations[key]['average'] < worstGenVals[0]){
                    worstGens[0] = key;
                    worstGenVals[0] = app.data.generations[key]['average'];
                }

                app.data.generations[key]['favesum'] = faveSum;
                if (app.data.generations[key]['favesum'] > bestGenVals[1]){
                    bestGens[1] = key;
                    bestGenVals[1] = app.data.generations[key]['favesum'];
                }
                if (app.data.generations[key]['favesum'] < worstGenVals[1]){
                    worstGens[1] = key;
                    worstGenVals[1] = app.data.generations[key]['favesum'];
                }


                if (gen['userRates'].length > 0){
                    app.data.generations[key]['userAve'] = userSum / gen['userRates'].length;
                    if (app.data.generations[key]['userAve'] > bestGenVals[2]){
                        bestGens[2] = key;
                        bestGenVals[2] = app.data.generations[key]['userAve'];
                    }
                    if (app.data.generations[key]['userAve'] < worstGenVals[2]){
                        worstGens[2] = key;
                        worstGenVals[2] = app.data.generations[key]['userAve'];
                    }
                } else {
                    app.data.generations[key]['userAve'] = "No ratings!"
                }
            }
            app.data.generations[bestGens[0]]['statuses'][0] = 1
            app.data.generations[bestGens[1]]['statuses'][1] = 1
            if (bestGens[2] != "Generation 0") { app.data.generations[bestGens[2]]['statuses'][2] = 1 }
            app.data.generations[worstGens[0]]['statuses'][0] = -1
            app.data.generations[worstGens[1]]['statuses'][1] = -1
            if (worstGens[2] != "Generation 0") { app.data.generations[worstGens[2]]['statuses'][2] = -1 }

            bestTypes = ["Fire", "Fire", "Fire"]
            bestTypeVals = [0, 0, 0]
            worstTypes = ["Fire", "Fire", "Fire"]
            worstTypeVals = [5, Infinity, 5]
            for (var key in app.data.types){
                type = app.data.types[key];
                type['rateTotal'] = type['total'];
                faveSum = 0;
                sum = 0;
                userSum = 0;
                i = 0;
                while(i < type['ratings'].length){
                    if (type['ratings'][i] == -1){
                        type['rateTotal'] -= 1;
                    } else {
                        sum += type['ratings'][i];
                        faveSum += type['favorites'][i];
                    }
                    if (i < type['userRates'].length){
                        userSum += type['userRates'][i];
                    }
                    i += 1;
                }
                app.data.types[key]['average'] = sum / type['rateTotal'];
                if (app.data.types[key]['average'] > bestTypeVals[0]){
                    bestTypes[0] = key;
                    bestTypeVals[0] = app.data.types[key]['average'];
                }
                if (app.data.types[key]['average'] < worstTypeVals[0]){
                    worstTypes[0] = key;
                    worstTypeVals[0] = app.data.types[key]['average'];
                }

                app.data.types[key]['favesum'] = faveSum 
                if (app.data.types[key]['favesum'] > bestTypeVals[1]){
                    bestTypes[1] = key;
                    bestTypeVals[1] = app.data.types[key]['favesum'];
                }
                if (app.data.types[key]['favesum'] < worstTypeVals[1]){
                    worstTypes[1] = key;
                    worstTypeVals[1] = app.data.types[key]['favesum'];
                }

                if (type['userRates'].length > 0){
                    app.data.types[key]['userAve'] = userSum / type['userRates'].length;
                    if (app.data.types[key]['userAve'] > bestTypeVals[2]){
                        bestTypes[2] = key;
                        bestTypeVals[2] = app.data.types[key]['userAve'];
                    }
                    if (app.data.types[key]['userAve'] < worstTypeVals[2]){
                        worstTypes[2] = key;
                        worstTypeVals[2] = app.data.types[key]['userAve'];
                    }
                } else {
                    app.data.types[key]['userAve'] = "No ratings!"
                }
            }
            app.data.types[bestTypes[0]]['statuses'][0] = 1
            app.data.types[bestTypes[1]]['statuses'][1] = 1
            if (bestTypes[2] != "Generation 0") { app.data.types[bestTypes[2]]['statuses'][2] = 1 }
            app.data.types[worstTypes[0]]['statuses'][0] = -1
            app.data.types[worstTypes[1]]['statuses'][1] = -1
            if (worstTypes[2] != "Generation 0") { app.data.types[worstTypes[2]]['statuses'][2] = -1 }
        });

    };



    // Call to the initializer.
    app.init();
};

// This takes the (empty) app object, and initializes it,
// putting all the code i
init(app);


