// This will be the object that will contain the Vue attributes
// and be used to initialize it.
let app = {};

// Given an empty app object, initializes it filling its attributes,
// creates a Vue instance, and then initializes the Vue instance.
let init = (app) => {

    // This is the Vue data.
    app.data = {

        randomPokes: [],
        highlightPoke: null,
        ratingText: "Rating Received!",
        ratingCount: 0,
        showNotif: false,
        fadeCountdown: 0,
        dex_url: dex_url,
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
            if (p['pokID'] != undefined ){
                return "images/PokemonArt/" + p['generation'] + "/" + p["fullName"].replace("\u2640", "Female").replace("\u2642", "Male").replaceAll("\u00e9", "e")  + ".png";
            }
            return "images/PokemonArt/Generation 1/Bulbasaur.png"
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
            if (p.globalAverage == -1 || isNaN(p.globalAverage)){
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
        abbrevNum(n){
            return Intl.NumberFormat('en-US', {
                notation: "compact",
                maximumFractionDigits: 1
              }).format(n);
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
        randomPokes = randomJSON;
        highlightPoke = highlightJSON;

        app.addRateData(randomPokes)
        highlightPoke.totalRatings = 0
        highlightPoke.ratings = [0,0,0,0,0,0]
        highlightPoke.globalAverage = 2.5;
        highlightPoke.userRating = 0;
        highlightPoke.userFavorite = false;

        i = 0;
        while(i < 4){
            currPoke = randomPokes[i]
            j = 0;
            while(j < pokeRatings.length){
                if (pokeRatings[j][1] == currPoke['id']){
                    currPoke.totalRatings = pokeRatings[j][8]
                    currPoke.ratings = [pokeRatings[j][2], pokeRatings[j][3], pokeRatings[j][4], pokeRatings[j][5], pokeRatings[j][6], pokeRatings[j][7]]
                    currPoke.globalAverage = ( currPoke.ratings[0] + currPoke.ratings[1]*2 + currPoke.ratings[2]*3 + currPoke.ratings[3]*4 + currPoke.ratings[4]*5 ) / currPoke.totalRatings;
                    randomPokes[i] = currPoke
                }
                if (pokeRatings[j][1] == highlightPoke['id'] && highlightPoke.totalRatings == 0){
                    highlightPoke.totalRatings = pokeRatings[j][8]
                    highlightPoke.ratings = [pokeRatings[j][2], pokeRatings[j][3], pokeRatings[j][4], pokeRatings[j][5], pokeRatings[j][6], pokeRatings[j][7]]
                    highlightPoke.globalAverage = (highlightPoke.ratings[0] + highlightPoke.ratings[1]*2 + highlightPoke.ratings[2]*3 + highlightPoke.ratings[3]*4 + highlightPoke.ratings[4]*5) / highlightPoke.totalRatings;
                }
                j += 1  
            }

            j = 0;
            while(j < userRatings.length){
                if (userRatings[j][0] == currPoke['id']){
                    if (userRatings[j][1] == 6){
                        randomPokes[i].userFavorite = true;
                    } else {
                        randomPokes[i].userRating = userRatings[j][1];
                    }
                }
                if (userRatings[j][0] == highlightPoke['id']){
                    if (userRatings[j][1] == 6){
                        highlightPoke.userFavorite = true;
                    } else {
                        highlightPoke.userRating = userRatings[j][1];
                    }
                }
                j += 1
            }
            i += 1
        }

        app.data.randomPokes = randomPokes;
        app.data.highlightPoke = highlightPoke;
    };



    // Call to the initializer.
    app.init();
};

// This takes the (empty) app object, and initializes it,
// putting all the code i
init(app);


