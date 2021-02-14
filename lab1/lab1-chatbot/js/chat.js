var apigClient = apigClientFactory.newClient();
const id = Math.floor(Math.random()*10000);

var chatWindow = new Bubbles(document.getElementById("chat"), "chatWindow", {
  // this function returns an object with some data that we can process from user input
  // and understand the context of it

  // this function atches the text user typed to one of the answer bubbles
  inputCallbackFn: function(o) {
    //This is where any header, path, or querystring request params go. The key is the parameter named as defined in the API
    var params = {};

    var body = {
      query: o.input,
      userId: 'user' + id.toString()
    }

    var additionalParams = {
        //If there are any unmodeled query parameters or headers that need to be sent with the request you can add them here
        headers: {},
        queryParams: {}
    };

    var respond = function(s) {
      chatWindow.talk(
        {"bot": {says: [s]}},
        "bot"
      )
    }

    console.log(id);

    apigClient.chatbotPost(params, body, additionalParams)
    .then(function(result){
        // success callback
        console.log("success");
        var response = result.data.body;
        console.log(response);
        respond(response.slice(1,-1));
    }).catch( function(result){
        // error callback
        console.log("Sorry, API Gateway is not responding");
        respond("Sorry, can you repeat?");
    });
  }
})

chatWindow.talk({
  ice: {
    says: ["I am a dining bot :)"]
  }
})