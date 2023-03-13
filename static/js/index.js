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
        pokemonPerCategory: {}
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
        }

    };

    // This creates the Vue instance.
    app.vue = new Vue({
        el: "#vue-target",
        data: app.data,
        methods: app.methods
    });

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

        i = 0;
        
        while (i < app.data.myPokemon.length){
            currPoke = app.data.myPokemon[i];
            if (currPoke["category"] != "Ignore"){
                pokemonPerCategory[currPoke["category"]].push(currPoke);
            }
            i += 1
        }

        app.vue.pokemonPerCategory = pokemonPerCategory;
    };



    // Call to the initializer.
    app.init();
};

// This takes the (empty) app object, and initializes it,
// putting all the code i
init(app);
