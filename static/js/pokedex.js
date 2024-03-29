// This will be the object that will contain the Vue attributes
// and be used to initialize it.
let app = {};

// Given an empty app object, initializes it filling its attributes,
// creates a Vue instance, and then initializes the Vue instance.
let init = (app) => {

    // This creates the Vue instance.
    

    // This is the Vue data.
    app.data = {

        myDexJSON: dexJSON,
        myCategories: dexJSON["categories"],
        myPokemon: dexJSON,
        pokemonPerCategory: {},
        ratingText: "Rating Received!",
        ratingCount: 0,
        showNotif: false,
        fadeCountdown: 0,
        showModal: false,
        modalPokemon: dexJSON[0],
        modalDisplayInd: 0,
        modalDisplayPokemon: dexJSON[0],
        query: "",
        userRatings: 0,
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
            return "images/PokemonArt/176Size/" + p['generation'] + "/" + p["fullName"].replace("\u2640", "Female").replace("\u2642", "Male").replaceAll("\u00e9", "e")  + ".png";
        },

        pokemonImagePathBig(p) {
            return "images/PokemonArt/OriginalSize/" + p['generation'] + "/" + p["fullName"].replace("\u2640", "Female").replace("\u2642", "Male").replaceAll("\u00e9", "e")  + ".png";
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
            return "images/Types/" + p.types[i].toLowerCase() + ".png";
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
                        app.vue.ratingText =  response.data + " (" + app.vue.ratingCount + ")";
                    } else {
                        app.vue.ratingText = response.data
                    }
                }

                
            }).catch((error) => {
                console.log(error)
                alert("Log in to post ratings!")
            })
        },
        unratePok(p){
            var postData = {"id": p.id};
            axios.post(remove_rating_url, postData).then((response) => {
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
                    app.vue.ratingText =  response.data + " (" + app.vue.ratingCount + ")";
                } else {
                    app.vue.ratingText = response.data
                }

                
            }).catch((error) => {
                console.log(error)
                alert("Log in to post ratings!")
            })
        },
        
        toggleModal(p){
            app.vue.showModal = !app.vue.showModal;
            app.vue.modalPokemon = p;
            app.vue.modalDisplayInd = 0;
            app.vue.modalDisplayPokemon = p;
        },
        incrementModal(i){
            p = app.vue.modalPokemon;

            if (p.categoryIndex + i > app.vue.pokemonPerCategory[p["category"]].length){
                // Do nothing
            }
            else if (p.categoryIndex + i < 0){
                // Do nothing
            } 
            else {
                app.vue.modalPokemon = app.vue.pokemonPerCategory[p["category"]][p.categoryIndex + i];
                app.vue.modalDisplayInd = 0;
                app.vue.modalDisplayPokemon = app.vue.pokemonPerCategory[p["category"]][p.categoryIndex + i];
            }
            
        },
        modalAltDisplay(){
            originalInd = app.vue.modalPokemon["dexIndex"];
            if (app.vue.modalPokemon["formList"].length > 1 && app.vue.modalPokemon['form'] == "Basic"){
                app.vue.modalDisplayInd += 1;
                newPokemon = app.vue.myPokemon[originalInd + app.vue.modalDisplayInd]
                while ( newPokemon["significantForm"] && newPokemon["number"] == app.vue.modalPokemon["number"] ){
                    app.vue.modalDisplayInd += 1;
                    newPokemon = app.vue.myPokemon[originalInd + app.vue.modalDisplayInd]
                }
                if (newPokemon["number"] != app.vue.modalPokemon["number"]){
                    app.vue.modalDisplayInd = 0;
                    newPokemon = app.vue.myPokemon[originalInd + app.vue.modalDisplayInd]
                }
                app.vue.modalDisplayPokemon = newPokemon;
            }
            
            
        },
        barHeight(i){
            p = app.vue.modalPokemon;
            let maxRates = 0;
            let j = 0;
            while (j < 5){
                if (p.ratings[j] > maxRates){
                    maxRates = p.ratings[j];
                }
                j += 1;
            }
            if(maxRates == 0){
                maxRates = 1;
            }
            return "height: " + (p.ratings[i-1]/maxRates) * 100 + "%;"
        },
        hideLeftArrow(){
            if(app.vue.modalPokemon.categoryIndex == 0){
                return "opacity: 0; cursor: auto;"
            }
            return ""
        },
        hideRightArrow(){
            if(app.vue.modalPokemon.categoryIndex + 1 == app.vue.pokemonPerCategory[app.vue.modalPokemon["category"]].length){
                return "opacity: 0; cursor: auto;"
            }
            return ""
        },
        abbrevNum(n){
            return Intl.NumberFormat('en-US', {
                notation: "compact",
                maximumFractionDigits: 1
              }).format(n);
        },
        filteredPokes(){
            normalizedQuery = app.vue.query.charAt(0).toUpperCase() + app.vue.query.toLowerCase().slice(1)
            if (app.vue.myCategories.includes(normalizedQuery)){
                return app.vue.pokemonPerCategory[normalizedQuery]
            }
            return app.vue.myPokemon.filter((pokemon) =>
                ( pokemon.fullName.toLowerCase().includes(app.vue.query.toLowerCase()) 
                || 
                  pokemon.types.includes(normalizedQuery))
                &&
                pokemon.significantForm
            );
        },
        categoryBinding(c){
            return "/pokedex#" + c
        }
    };

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
        app.vue.myCategories = ["Kanto", "Johto", "Hoenn", "Sinnoh", "Unova", "Kalos", "Mega", "Alola", "Galar", "Gigantamax", "Hisui", "Paldea"];
        pokemonPerCategory = {};
        i = 0;
        while (i < app.vue.myCategories.length){
            pokemonPerCategory[app.vue.myCategories[i]] = [];
            i += 1
        }

        app.addRateData(app.data.myPokemon)
        id_map = {};
        derived_rates = allRatings;
        i = 0;
        while (i < allRatings.length){
            currPoke = app.data.myPokemon[i];
            currPoke.totalRatings = allRatings[i]['ratingcount'];
            currPoke.ratings = [derived_rates[i]['onestar'], derived_rates[i]['twostar'], derived_rates[i]['threestar'], derived_rates[i]['fourstar'], derived_rates[i]['fivestar'], derived_rates[i]['favorites']];
            
            if (currPoke.totalRatings > 0){
                currPoke.globalAverage = ( currPoke.ratings[0] + currPoke.ratings[1]*2 + currPoke.ratings[2]*3 + currPoke.ratings[3]*4 + currPoke.ratings[4]*5 ) / currPoke.totalRatings;
            } else {
                currPoke.globalAverage = -1;
            }

            if (currPoke["significantForm"]){
                pokemonPerCategory[currPoke["category"]].push(currPoke);
                currPoke.categoryIndex = pokemonPerCategory[currPoke["category"]].length - 1
                currPoke.dexIndex = i;
            }

            app.data.myPokemon[i] = currPoke;
            id_map[currPoke['pokID']] = i;
            id_map[currPoke['id']] = i;
            i += 1;
        }

        i=0
        while (i < userRatings.length){
            pokInd = id_map[ userRatings[i]['pokemon'] ]
            if (userRatings[i]['rating'] == 6){
                app.data.myPokemon[pokInd].userFavorite = true;
            } else {
                app.data.myPokemon[pokInd].userRating = userRatings[i]['rating'];
                app.data.userRatings += 1;
            }
            i += 1;
        }

        if (target_poke != 0){
            target_poke = target_poke.padStart(4, 0)
            target_poke = target_poke.padEnd(6, 0)
        }

        if (id_map[target_poke] != null){
            if (app.data.myPokemon[id_map[target_poke]].significantForm){
                app.data.showModal = true
                app.data.modalPokemon = app.data.myPokemon[id_map[target_poke]]
                app.data.modalDisplayPokemon = app.data.myPokemon[id_map[target_poke]]
                app.data.modalDisplayInd = 0
            }   
        }

        app.vue.pokemonPerCategory = pokemonPerCategory; 
    };



    // Call to the initializer.
    app.init();
};

// This takes the (empty) app object, and initializes it,
// putting all the code i
init(app);


