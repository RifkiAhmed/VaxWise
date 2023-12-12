const errorMarkOpenTag = '<mark style="color: red; font-size:large; border-radius: 4px; padding: 5px 10px"> <i class="fas fa-exclamation-circle"> </i>';
const successMarkOpenTag = '<mark style="color: green; font-size:large; border-radius: 4px; padding: 5px 10px"> <i class="fas fa-check-circle"> </i>';


// Submit update nurse profile information after form validation
function submitUpdateNurse(id, oldEmail) {
    const data = {
        'id': id,
        'first_name': document.getElementById('firstName-2').value,
        'last_name': document.getElementById('lastName-2').value,
        'password': document.getElementById('password-2').value,
    };
    const newEmail = document.getElementById('email-2').value;
    if (newEmail != oldEmail) {
        data['email'] = newEmail;
    }
    if (data['first_name'] == '') {
        document.getElementById('error_message-1').innerHTML = errorMarkOpenTag + ' Please enter your first name</mark>';
    } else if (data['last_name'] == '') {
        document.getElementById('error_message-1').innerHTML = errorMarkOpenTag + ' Please enter your last name</mark>';
    } else if (newEmail == '' || !newEmail.includes('@')) {
        document.getElementById('error_message-1').innerHTML = errorMarkOpenTag + ' Please enter a valid email</mark>';
    } else if (data['password'] == '') {
        document.getElementById('error_message-1').innerHTML = errorMarkOpenTag + ' Please enter the password</mark>';
    } else if (data['password'] != document.getElementById('password2-2').value) {
        document.getElementById('error_message-1').innerHTML = errorMarkOpenTag + ' Password doesn\'t match, Please try again.</mark>';
    } else {
        document.getElementById('error_message-1').innerHTML = '&nbsp;';
        fetch('/' + data['email'], {
            method: 'GET',
        }).then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        }).then(res_data => {
            if (res_data.status == "Exist" && newEmail != oldEmail) {
                document.getElementById('error_message-1').innerHTML = errorMarkOpenTag + ' This email is already registered</mark>';
            } else {
                fetch('/nurse', {
                    method: 'PUT',
                    body: JSON.stringify(data),
                }).then(response => {
                    if (!response.ok) {
                        throw new Error('');
                    }
                    return response.json();
                }).then((res_data) => {
                    if (res_data.href == '/verification') {
                        window.location.href = res_data.href;
                    } else {
                        document.getElementById('error_message-1').innerHTML = successMarkOpenTag + ' Your profile has been updated successfully!</mark>';
                    }
                });
            }
        }).catch(error => {
            console.error('There has been a problem with fetch operation:', error);
        });
    }
}