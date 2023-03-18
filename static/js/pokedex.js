import VueLazyload from 'vue-lazyload'
// This will be the object that will contain the Vue attributes
// and be used to initialize it.
let app = {};

// Given an empty app object, initializes it filling its attributes,
// creates a Vue instance, and then initializes the Vue instance.
let init = (app) => {

    // This is the Vue data.
    app.data = {

        myDexJSON: dexJSON,
        myCategories: dexJSON["categories"],
        myPokemon: dexJSON["Pokemon"],
        pokemonPerCategory: {},
        ratingText: "Rating Received!",
        ratingCount: 0,
        showNotif: false,
        fadeCountdown: 0,
        showModal: false,
        modalPokemon: dexJSON["Pokemon"][0]
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
            axios.post(set_rating_url, {"pokID": p.id, "rating": i}).then((response) => {
                app.vue.showNotif = true;

                app.vue.fadeCountdown += 3;
                setTimeout(function () {
                    console.log("3 Seconds passed")
                    app.vue.fadeCountdown -= 3;
                    if (app.vue.fadeCountdown == 0){
                        console.log("Begin Fade")
                        app.vue.showNotif = false;
                        app.vue.ratingCount = 0;
                    }
                }, 3000)

                app.vue.ratingCount += 1;
                
                console.log(app.vue.ratingCount)
                if (app.vue.ratingCount > 1){
                    app.vue.ratingText = "Rating Received! (" + app.vue.ratingCount + ")";
                } else {
                    app.vue.ratingText = "Rating Received!"
                }
            }).catch((error) => {
                console.log(error)
                alert("Log in to post ratings!")
            })
        },
        toggleModal(p){
            app.vue.showModal = !app.vue.showModal;
            app.vue.modalPokemon = p;
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

        app.vue.myCategories = app.data.myCategories;
        pokemonPerCategory = {};
        i = 0;
        while (i < app.data.myCategories.length){
            pokemonPerCategory[app.data.myCategories[i]["title"]] = [];
            i += 1
        }

        app.addRateData(app.data.myPokemon)
        axios.get(get_all_ratings_url).then((result) => {
            console.log(result.data.allRatings)
            console.log(result.data.userRatings)
            j = 0;
            p = 0;
            u = 0;
            while (j < result.data.allRatings.length){
                pok = app.data.myPokemon[p]
                rating = result.data.allRatings[j];
                if (pok['id'] != rating['pokemon']){
                    rl = app.data.myPokemon[p].ratings;
                    app.data.myPokemon[p].globalAverage = (rl[0] + 2*rl[1] + 3*rl[2] + 4*rl[3] + 5*rl[4]) / app.data.myPokemon[p].totalRatings;
                    while (pok['id'] != rating['pokemon']){
                        p += 1;
                        pok = app.data.myPokemon[p];
                    }
                }
                if (u < result.data.userRatings.length){
                    if (app.data.myPokemon[p]['id'] == result.data.userRatings[u]['pokemon']){
                        if (result.data.userRatings[u]['rating'] == 6){
                            app.data.myPokemon[p].userFavorite = true;
                        } else {
                            app.data.myPokemon[p].userRating = result.data.userRatings[u]['rating'];
                        }
                        u += 1
                    }
                }
                app.data.myPokemon[p].totalRatings += 1;
                app.data.myPokemon[p].ratings[rating['rating'] - 1] += 1
                j += 1
            }
            
            i = 0;
        
            while (i < app.data.myPokemon.length){
                currPoke = app.data.myPokemon[i];
                if (currPoke["category"] != "Ignore"){
                    pokemonPerCategory[currPoke["category"]].push(currPoke);
                    currPoke.categoryIndex = pokemonPerCategory[currPoke["category"]].length - 1
                }
                i += 1
            }

            app.vue.pokemonPerCategory = pokemonPerCategory;
        })  
    };



    // Call to the initializer.
    app.init();
};

// This takes the (empty) app object, and initializes it,
// putting all the code i
init(app);


