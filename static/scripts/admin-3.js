let nurseEmail;
let nurseId;
const errorMarkOpenTag = '<mark style="color: red; font-size:large; border-radius: 4px; padding: 5px 10px"> <i class="fas fa-exclamation-circle"> </i>';
const successMarkOpenTag = '<mark style="color: green; font-size:large; border-radius: 4px; padding: 5px 10px"> <i class="fas fa-check-circle"> </i>';


// Function to add a nurse after form validation
function addNurse(event, href) {
    event.preventDefault();
    const formData = {
        'first_name': document.getElementById('firstName-1').value,
        'last_name': document.getElementById('lastName-1').value,
        'email': document.getElementById('email-1').value,
        'hospital_id': document.getElementById('hospital-1').value,
        'password': document.getElementById('password-1').value,
    };
    if (formData['first_name'] == '') {
        document.getElementById('error_message-1').innerHTML = errorMarkOpenTag + ' Please enter nurse first name</mark>';
    } else if (formData['last_name'] == '') {
        document.getElementById('error_message-1').innerHTML = errorMarkOpenTag + ' Please enter nurse last name</mark>';
    } else if (formData['email'] == '') {
        document.getElementById('error_message-1').innerHTML = errorMarkOpenTag + ' Please enter a valid nurse email address</mark>';
    } else if (formData['hospital_id'] == 0) {
        document.getElementById('error_message-1').innerHTML = errorMarkOpenTag + ' Please select nurse assigned hospital</mark>';
    } else if (formData['password'] == '') {
        document.getElementById('error_message-1').innerHTML = errorMarkOpenTag + ' Please enter password for nurse</mark>';
    } else if (formData['password'] != document.getElementById('password2-1').value) {
        document.getElementById('error_message-1').innerHTML = errorMarkOpenTag + ' Password doesn\'t match, Please try again</mark>';
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
            if (data.status == "Exist") {
                document.getElementById('error_message-1').innerHTML = errorMarkOpenTag + ' This email is already registered, Please try again</mark>';
            } else {
                fetch('/nurse', {
                    method: 'POST',
                    body: JSON.stringify(formData),
                }).then((response) => {
                    window.location.href = href;
                });
            }
        }).catch(error => {
            console.error('There has been a problem with fetch operation:', error);
        });
    }
}


// Function to display the update nurse modal with nurse details for editing
function showUpdateNurseModal(id) {
    nurseId = id;
    fetch('/nurse/' + nurseId, {
        method: 'GET',
    }).then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return response.json();
    }).then(data => {
        if (data.status === "Not Exist") {
            alert("Nurse does not exist.");
        } else {
            document.getElementById('firstName-2').value = data.first_name;
            document.getElementById('lastName-2').value = data.last_name;
            document.getElementById('email-2').value = data.email;
            nurseEmail = data.email;
            $('#update_nurse_modal').modal('show');
        }
    }).catch(error => {
        console.error('There has been a problem with fetch operation:', error);
    });
}


// Function to submit updated nurse details
function submitUpdateNurse(event, href) {
    event.preventDefault();
    const formData = {
        'id': nurseId,
        'first_name': document.getElementById('firstName-2').value,
        'last_name': document.getElementById('lastName-2').value,
        'hospital_id': document.getElementById('hospital-2').value,
        'password': document.getElementById('password-2').value,
    };
    const newEmail = document.getElementById('email-2').value;
    if (newEmail != nurseEmail) {
        formData['email'] = newEmail;
    }
    if (formData['first_name'] == '') {
        document.getElementById('error_message-2').innerHTML = errorMarkOpenTag + ' Please enter nurse first name</mark>';
    } else if (formData['last_name'] == '') {
        document.getElementById('error_message-2').innerHTML = errorMarkOpenTag + ' Please enter nurse last name</mark>';
    } else if (newEmail == '' || !newEmail.includes('@')) {
        document.getElementById('error_message-2').innerHTML = errorMarkOpenTag + ' Please enter a valid nurse email address</mark>';
    } else if (formData['password'] == '') {
        document.getElementById('error_message-2').innerHTML = errorMarkOpenTag + ' Please enter nurse password</mark>';
    } else if (formData['password'] != document.getElementById('password2-2').value) {
        document.getElementById('error_message-2').innerHTML = errorMarkOpenTag + ' Password doesn\'t match, Please try again</mark>';
    } else {
        document.getElementById('error_message-2').innerHTML = '&nbsp;';
        // Check if the new email is already registered
        fetch('/' + newEmail, {
            method: 'GET',
        }).then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        }).then(data => {
            if (data.status == "Exist" && newEmail != nurseEmail) {
                document.getElementById('error_message-2').innerHTML = errorMarkOpenTag + ' This email is already registered, Please try again</mark>';
            } else {
                // Update nurse account details via PUT request
                fetch('/nurse', {
                    method: 'PUT',
                    body: JSON.stringify(formData),
                }).then((data) => {
                    document.getElementById('error_message-2').innerHTML = successMarkOpenTag + ' Nurse account has been updated successfully!</mark>';
                });
            }
        }).catch(error => {
            console.error('There has been a problem with fetch operation:', error);
        });
    }
}


// Function to display the delete nurse confirmation modal
function showDeleteNurseModal(id) {
    nurseId = id;
    fetch('/nurse/' + nurseId, {
        method: 'GET',
    }).then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return response.json();
    }).then(data => {
        if (data.status === "Not Exist") {
            alert("Nurse does not exist.");
        } else {
            document.getElementById('nurse_fullname').innerHTML = 'Are you sure you want to remove the nurse, ' + data.first_name + ' ' + data.last_name + ' ?';
            $('#delete_nurse_modal').modal('show');
        }
    }).catch(error => {
        console.error('There has been a problem with fetch operation:', error);
    });
}


// Function to submit deletion of a nurse
function submitDeleteNurse() {
    fetch("/nurse", {
        method: "DELETE",
        body: JSON.stringify({ id: nurseId }),
    }).then((response) => {
        window.location.href = "/nurses";
    });
}


// Function to display the transfer nurse modal
function showTransferNurseModal(id) {
    nurseId = id;
    // Fetch nurse details based on ID
    fetch('/nurse/' + nurseId, {
        method: 'GET',
    }).then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return response.json();
    }).then(data => {
        if (data.status === "Not Exist") {
            alert("Nurse does not exist.");
        } else {
            document.getElementById('firstName-3').innerHTML = '&nbsp;' + data.first_name;
            document.getElementById('lastName-3').innerHTML = '&nbsp;' + data.last_name;
            document.getElementById('currentHospital-3').innerHTML = '&nbsp; Hospital ' + data.hospital;
            $('#transfer_nurse_modal').modal('show');
        }
    }).catch(error => {
        console.error('There has been a problem with fetch operation:', error);
    });
}


// Function to submit the transfer nurse request
function submitTransferNurse(event, href) {
    event.preventDefault();
    const data = {
        'id': nurseId,
    };
    if (document.getElementById('hospital-4').value == 0) {
        document.getElementById('error_message-3').innerHTML = errorMarkOpenTag + ' Select the nurse new assigned hospital</mark>';
    } else {
        document.getElementById('error_message-3').innerHTML = '&nbsp;';
        data['hospital_id'] = document.getElementById('hospital-4').value;
        // Send PUT request to transfer nurse to the selected hospital
        fetch('/nurse/hospital', {
            method: 'PUT',
            body: JSON.stringify(data),
        }).then((response) => {
            window.location.href = href;
        });
    }
}


// Function to fetch nurses based on the provided URL
function fetchNurses(href) {
    document.location.href = href;
}
