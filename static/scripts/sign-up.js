const errorMarkOpenTag = '<mark style="color: red; font-size:large; border-radius: 4px; padding: 5px 10px"> <i class="fas fa-exclamation-circle"> </i>';
const successMarkOpenTag = '<mark style="color: green; font-size:large; border-radius: 4px; padding: 5px 10px"> <i class="fas fa-check-circle"> </i>';

const signUpFirstName = document.getElementById('sign_up_firstName');
const signUpLirstName = document.getElementById('sign_up_lastName');
const signUpEmail = document.getElementById('sign_up_email');
const signUpPwd = document.getElementById('sign_up_pwd');
const signUpPwd2 = document.getElementById('sign_up_pwd2');

// Adding event listeners to detect "Enter" key press on input fields
signUpFirstName.addEventListener('keypress', callSignUpFunction);
signUpLirstName.addEventListener('keypress', callSignUpFunction);
signUpEmail.addEventListener('keypress', callSignUpFunction);
signUpPwd.addEventListener('keypress', callSignUpFunction);
signUpPwd2.addEventListener('keypress', callSignUpFunction);

function callSignUpFunction(event) {
    // If "Enter" key is pressed, call the signUp() function
    if (event.key === 'Enter') {
        signUp();
    }
}


// Function to handle user sign-up process
function signUp() {
    const data = {
        'first_name': document.getElementById('sign_up_firstName').value,
        'last_name': document.getElementById('sign_up_lastName').value,
        'email': document.getElementById('sign_up_email').value,
        'password': document.getElementById('sign_up_pwd').value,
    };
    if (data['email'] == '' || !data['email'].includes('@')) {
        document.getElementById('error_message-1').innerHTML = errorMarkOpenTag + ' Please enter a valid email address</mark>';
    } else if (data['first_name'] == '') {
        document.getElementById('error_message-1').innerHTML = errorMarkOpenTag + ' Please enter your first name</mark>';
    } else if (data['last_name'] == '') {
        document.getElementById('error_message-1').innerHTML = errorMarkOpenTag + ' Please enter your last name</mark>';
    } else if (data['password'] == '') {
        document.getElementById('error_message-1').innerHTML = errorMarkOpenTag + ' Please enter your password</mark>';
    } else if (data['password'] != document.getElementById('sign_up_pwd2').value) {
        document.getElementById('error_message-1').innerHTML = errorMarkOpenTag + ' Password doesn\'t match. Please try again</mark>';
    } else {
        document.getElementById('error_message-1').innerHTML = '&nbsp;';
        fetch('/sign-up', {
            method: 'POST',
            body: JSON.stringify(data),
        }).then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        }).then(data => {
            if (data.status == 'Error') {
                document.getElementById("error_message-1").innerHTML = errorMarkOpenTag + ' &nbsp;' + data.message + '</mark>';
            } else {
                document.location.href = data.href;
            }
        }).catch(error => {
            console.error('There has been a problem with fetch operation:', error);
        });
    }
}
