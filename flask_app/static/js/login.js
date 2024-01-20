// Number of times authentication has failed
let count = 0

// The submit button responsible for submitting the form data
const submitButton = document.getElementById("login-submit");

// The button responsible for redirecting to sign up page
const signUpButton = document.getElementById("login-sign_up");

// Update and display then number of failed authentications
const updateFailedAuthentications = function() {
    // Get the element displaying the failed authentications
    const failed_auth = document.getElementById("submission-failed");

    // Display the element containing the failure message
    failed_auth.textContent = `Authentications failed: ${count.toString()}`;
}

// Update and display the reason for failed creation
const updateFailedCreation = function() {
  // Get the element displaying the failed creations
  const failed_creation = document.getElementById("submission-failed");

  failed_creation.textContent = "Username already taken. Please try a different username.";
}


const processCredentials = function (processRoute) {
  // Get the username and password from the form fields
  const username = document.getElementById("username").value;
  const password = document.getElementById("password").value;

  jQuery.ajax({
    url: processRoute,
    data: {'username': username, 'password': password},
    type: "POST",
    success:function(returned_data){
          returned_data = JSON.parse(returned_data);
          
          // Determine next route location
          let nextLocation = window.location.href.split('next=')[1];

          // If no location set, redirect home
          if (!nextLocation) { nextLocation = '/'; }

          if (returned_data['success'] === 0) {
            if (processRoute === '/processlogin') {
              count++;
              updateFailedAuthentications();
            } else {
              updateFailedCreation();
            }
            
          } else {
            window.location.href = nextLocation;
          }
        }
});
}

// Add onClick listener to submit button
submitButton.addEventListener("click", function() {processCredentials('/processlogin');});
signUpButton.addEventListener("click", function() {processCredentials('/processsignup');})