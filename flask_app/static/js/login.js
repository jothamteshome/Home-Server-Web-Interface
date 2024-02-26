// Number of times authentication has failed
let count = 0

// The submit button responsible for submitting the form data
const submitButton = document.getElementById("login-submit");

// Update and display then number of failed authentications
const updateFailedAuthentications = function() {
    // Get the element displaying the failed authentications
    const failed_auth = document.getElementById("submission-failed");

    // Display the element containing the failure message
    failed_auth.textContent = `Authentications failed: ${count.toString()}`;
}


const processCredentials = function () {
  // Get the username and password from the form fields
  const username = document.getElementById("username").value;
  const password = document.getElementById("password").value;

  jQuery.ajax({
    url: '/processlogin',
    data: {'username': username, 'password': password},
    type: "POST",
    success:function(returned_data){
          returned_data = JSON.parse(returned_data);
          
          // Determine next route location
          let nextLocation = window.location.href.split('next=')[1];

          // If no location set, redirect home
          if (!nextLocation) { nextLocation = '/'; }

          if (returned_data['success'] === 0) {
            count++;
            updateFailedAuthentications();
          } else {
            window.location.href = nextLocation;
          }
        }
});
}

// Add onClick listener to submit button
submitButton.addEventListener("click", processCredentials);