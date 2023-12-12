const errorMarkOpenTag = '<mark style="color: red; font-size:large; border-radius: 4px; padding: 5px 10px"> <i class="fas fa-exclamation-circle"> </i>';
const successMarkOpenTag = '<mark style="color: green; font-size:large; border-radius: 4px; padding: 5px 10px"> <i class="fas fa-check-circle"> </i>';


// Submit update user profile information after form validation
function submitUpdateUser(oldEmail) {
    const formData = {
        'first_name': document.getElementById('firstName').value,
        'last_name': document.getElementById('lastName').value,
        'password': document.getElementById('password').value,
    };
    const newEmail = document.getElementById('email').value;
    if (newEmail != oldEmail) {
        formData['email'] = newEmail;
    }
    if (formData['first_name'] == '') {
        document.getElementById('error_message-1').innerHTML = errorMarkOpenTag + ' Please enter your first name</mark>';
    } else if (formData['last_name'] == '') {
        document.getElementById('error_message-1').innerHTML = errorMarkOpenTag + ' Please enter your last name</mark>';
    } else if (newEmail == '' || !newEmail.includes('@')) {
        document.getElementById('error_message-1').innerHTML = errorMarkOpenTag + ' Please enter a valid email address</mark>';
    } else if (formData['password'] == '') {
        document.getElementById('error_message-1').innerHTML = errorMarkOpenTag + ' Please enter your password</mark>';
    } else if (formData['password'] != document.getElementById('password2').value) {
        document.getElementById('error_message-1').innerHTML = errorMarkOpenTag + ' Password doesn\'t match. Please try again</mark>';
    } else {
        document.getElementById('error_message-1').innerHTML = '&nbsp;';
        fetch('/' + formData['email'], {
            method: 'GET',
        }).then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        }).then(data => {
            if (data.status == "Exist" && newEmail != oldEmail) {
                document.getElementById('error_message-1').innerHTML = errorMarkOpenTag + ' This email is already registered</mark>';
            } else {
                fetch('/user', {
                    method: 'PUT',
                    body: JSON.stringify(formData),
                }).then(response => {
                    if (!response.ok) {
                        throw new Error('Network response was not ok');
                    }
                    return response.json();
                }).then(data => {
                    if (data.status == 'Error') {
                        document.getElementById("error_message-1").innerHTML = data.message;
                    } else {
                        if (data.href != '') {
                            document.location.href = data.href;
                        } else {
                            document.getElementById('error_message-1').innerHTML = successMarkOpenTag + ' Your profile has been updated successfully!</mark>';
                        }
                    }
                }).catch(error => {
                    console.error('There has been a problem with fetch operation:', error);
                });
            }
        });
    }
}
