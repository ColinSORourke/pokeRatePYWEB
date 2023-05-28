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
        myPokemon: dexJSON["Pokemon"].filter((pokemon) => 
            pokemon.form == "Basic"
        ),
        targetPokemon: {},
        solved: false,
        query: "",
        acSuggestions: [],
        myGuesses: [],
        mostRecentGuess: {name: "None"},
        noGuess: true,
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
        },
        submitGuess(){
            let guess = app.vue.myPokemon.find(p => p.name == app.vue.query);
            if (guess != undefined){
                app.vue.myGuesses.push(guess);
                app.vue.mostRecentGuess = guess;
                app.vue.noGuess = false;
                app.vue.query = '';
            }

            if (guess.name == app.vue.targetPokemon.name){
                app.vue.solved = true;
            }
        },
        pokemonImagePath(p) {
            return "images/PokemonArt/" + p['generation'] + "/" + p["fullname"].replace("\u2640", "Female").replace("\u2642", "Male").replaceAll("\u00e9", "e")  + ".png";
        },
        pokemonNumber(p) {
            return "#" + p['number'];
        },
        typeImagePath(p, i) {
            return "images/Types/" + p.types[i] + "_en.png";
        },
        widthPerc(p){
            if (p.globalAverage == -1){
                return "width: 50%;";
            }
            return "width: " + p.globalAverage*20 + "%;"
        },
        checkAlph(p){
            if (p.name[0] < app.vue.targetPokemon.name[0]){
                return "fa fa-arrow-circle-up"
            } else if (p.name[0] > app.vue.targetPokemon.name[0]){
                return "fa fa-arrow-circle-down"
            } else {
                return "fa fa-check-circle"
            }
        },
        checkGen(p){
            guessGen = p.generation[11]
            targetGen = app.vue.targetPokemon.generation[11]
            if (guessGen < targetGen){
                return "fa fa-arrow-circle-up"
            } else if (guessGen > targetGen){
                return "fa fa-arrow-circle-down"
            } else {
                return "fa fa-check-circle"
            }
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
        checkRate(p){
            
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
        app.vue.targetPokemon = app.vue.myPokemon[randIndex];
        console.log(app.vue.targetPokemon)
    };



    // Call to the initializer.
    app.init();
};

// This takes the (empty) app object, and initializes it,
// putting all the code i
init(app);

