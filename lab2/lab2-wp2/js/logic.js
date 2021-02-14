var apigClient = apigClientFactory.newClient();

document.getElementById('otp-form').addEventListener('submit', function(e) {
  e.preventDefault();
  
  var params = {};

  var body = {
    otp: document.getElementById('otp').value
  }

  var additionalParams = {
    headers: {},
    queryParams: {}
  };

  apigClient.otpPost(params, body, additionalParams)
    .then(function(result){
        // success callback
        var name = result.data.body.slice(1,-1);
        if (name == '') {
          swal('Permisson denied', 'The OTP you input is invalid.', 'error');
        } else {
          swal(`Hey ${name}!`, 'Welcome to Smart Door!', 'success');
        }
    }).catch(function(result){
        // error callback
        swal('Oops...', 'Something went wrong!', 'error');
        console.log("Sorry, API Gateway is not responding");
    });
}, false);