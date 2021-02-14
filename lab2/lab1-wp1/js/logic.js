var form = document.getElementById('visitor-form');
var apigClient = apigClientFactory.newClient();

const queryString = window.location.search;
const urlParams = new URLSearchParams(queryString);
const faceid = urlParams.get('faceid');
const image = urlParams.get('image');

form.addEventListener('submit', function(event) {
  event.preventDefault();

  var name = document.getElementById('name').value;
  var phone = document.getElementById('phone').value;
  
  var params = {};

  var body = {
    name: name,
    phone: phone,
    faceid: faceid,
    image: image
  }

  var additionalParams = {
    headers: {},
    queryParams: {}
  };

  apigClient.visitorPost(params, body, additionalParams)
    .then(function(result){
        // success callback
        swal('Well Done!', `You have created a new record for ${name} with phone number ${phone}`, 'success');
        var response = result.data.body;
        console.log(response);
    }).catch(function(result){
        // error callback
        swal('Oops...', 'Something went wrong!', 'error');
    });
}, false);