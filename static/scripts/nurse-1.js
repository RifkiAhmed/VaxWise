let nurseId;
let nurseEmail;
let hospitalId;
let vaccineId;
const errorMarkOpenTag = '<mark style="color: red; font-size:large; border-radius: 4px; padding: 5px 10px"> <i class="fas fa-exclamation-circle"> </i>';
const successMarkOpenTag = '<mark style="color: green; font-size:large; border-radius: 4px; padding: 5px 10px"> <i class="fas fa-check-circle"> </i>';


// Function to fetch children of a parent
function fetchParentChildren(event) {
    event.preventDefault();
    clearErrorMessage();
    const email = document.getElementById('parent_email').value;
    if (email == '') {
        document.getElementById('error_message-1').innerHTML = errorMarkOpenTag + ' Please enter parent\'s email address</mark>';
    } else {
        fetch('/' + email, {
            method: 'GET',
        }).then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        }).then(data => {
            if (data.status != "Exist") {
                document.getElementById('error_message-1').innerHTML = errorMarkOpenTag + ' No parent is registered with this email. Please try again</mark>';
            } else {
                document.getElementById('error_message-1').innerHTML = "&nbsp;";
                fetch('/user/children', {
                    method: 'POST',
                    body: JSON.stringify({ 'email': email }),
                }).then(response => {
                    if (!response.ok) {
                        throw new Error("Network response was not ok")
                    }
                    return response.json();
                }).then(data => {
                    let select = document.getElementById('children_list');
                    while (select.firstChild) {
                        select.removeChild(select.firstChild);
                    }
                    let option = document.createElement('option');
                    option.value = 0;
                    option.innerHTML = "Select Child";
                    option.disabled = true;
                    option.selected = true;
                    select.appendChild(option);
                    data.forEach(child => {
                        let option = document.createElement('option');
                        option.value = child.id;
                        option.innerHTML = child.first_name + ' ' + child.last_name;
                        select.appendChild(option);
                    });
                    document.getElementById('error_message-1').innerHTML = successMarkOpenTag + ' Please select child to be vaccinated</mark>';
                }).catch(error => {
                    console.log('There has been a problem with fetch operation:', error);
                });
            }
        }).catch(error => {
            console.error('There has been a problem with fetch operation:', error);
        });
    }
}

// function addVaccine(event, hospitalId) {
//     event.preventDefault();
//     const vaccineId = document.getElementById('vaccines_select').value;
//     const hospitalId = hospitalId;
//     const stock = parseInt(document.getElementById('vaccine_stock').value, 10);

//     if (isNaN(stock) || !Number.isInteger(stock) || stock <= 0) {
//         document.getElementById('message-7').innerHTML = errorMarkOpenTag + ' Add a valid quantity</mark>';
//     } else {
//         document.getElementById('message-7').innerHTML = "&nbsp;";
//         fetch('/hospital/add-vaccine', {
//             method: 'POST',
//             body: JSON.stringify({ 'hospital_id': hospitalId, 'vaccine_id': vaccineId, 'stock': stock })
//         }).then(response => {
//             if (!response.ok) {
//                 throw new Error('Network response was not ok');
//             }
//             return response.json();
//         }).then(data => {
//             if (data.status == 'Exist') {
//                 document.getElementById('message-7').innerHTML = errorMarkOpenTag + ' Vaccine already exists</mark>';
//             } else {
//                 document.getElementById('message-7').innerHTML = "&nbsp;";
//                 document.location.href = '/profile';
//             }
//         }).catch(error => {
//             console.log('There has been a problem with fetch operation:', error);
//         })
//     }
// }


// Function to register a child's vaccination at a specific hospital
function childVaccination(hospitalId) {
    clearErrorMessage();
    const childId = document.getElementById("children_list").value;
    const doseId = document.getElementById("dose_list").value;
    if (childId == 0 || doseId == 0) {
        document.getElementById("error_message-2").innerHTML = errorMarkOpenTag + ' Please select child and the required vaccination</mark>';

    } else {
        document.getElementById("error_message-2").innerHTML = "&nbsp;";
        fetch('/hospital/' + hospitalId + '/child/' + childId + '/dose/' + doseId, {
            method: "GET",
        }).then((response) => {
            if (!response.ok) {
                throw new Error();
            }
            return response.json();
        }).then(data => {
            if (data.status == 'Exist') {
                document.getElementById("error_message-2").innerHTML = errorMarkOpenTag + ' The child has already been vaccinated with this dose</mark>';
            } else {
                document.getElementById("error_message-2").innerHTML = successMarkOpenTag + ' The child\'s vaccination registration was successful</mark>';
            }
        })
    }
}


// Function to project future vaccinations based on selected vaccine and time range
function vaccinationTracker() {
    clearErrorMessage();
    const id = document.getElementById('vaccine_tracker').value;
    const range = rangeSlider.value;
    if (id == '0' || range == '0') {
        document.getElementById("error_message-3").innerHTML = errorMarkOpenTag + ' Please select a vaccine and range</mark>';
    } else {
        document.getElementById("error_message-3").innerHTML = '&nbsp;';
        fetch('/dose/' + id + '/range/' + range, {
            method: "GET",
        }).then((response) => {
            if (!response.ok) {
                throw new Error();
            }
            return response.json();
        }).then(data => {
            document.getElementById("succes_message-1").innerHTML = 'In ' + range + ' days ' + data.vaccination + ' children will be vaccinated with ' + data.dose;
            $('#vaccination_tracker').modal('show');
        })
    }
}


// Listen for input changes on the range slider
let rangeSlider = document.getElementById('range_slider');

rangeSlider.addEventListener('input', function () {
    clearErrorMessage();
    // Update the displayed value with the current slider value
    document.getElementById('put_range_value').textContent = ' ' + rangeSlider.value + ' day';
});


// Function to prepare and display a modal for implementing vaccine stock
function implementStock(hId, vId) {
    clearErrorMessage();
    hospitalId = hId;
    vaccineId = vId;
    $('#implement_vaccine_stock').modal('show');
}


// Function to submit vaccine stock quantity to the server
function submitVaccineStock() {
    clearErrorMessage();
    const quantity = parseInt(document.getElementById('vaccine_quantity').value, 10);
    if (isNaN(quantity) || !Number.isInteger(quantity) || quantity <= 0) {
        document.getElementById('error_message-4').innerHTML = errorMarkOpenTag + ' Please add a valid quantity</mark>';
    } else {
        document.getElementById('error_message-4').innerHTML = "&nbsp;";
        fetch('/hospital/' + hospitalId + '/vaccine/' + vaccineId + '/' + quantity, {
            method: 'PUT',
        }).then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        }).then(data => {
            document.location.href = '/nurse/home';
        }).catch(error => {
            console.log('There has been a problem with fetch operation:', error);
        })
    }
}


// Function to clear error messages displayed on the webpage
function clearErrorMessage() {
    document.getElementById('error_message-1').innerHTML = '&nbsp;';
    document.getElementById('error_message-2').innerHTML = '&nbsp;';
    document.getElementById('error_message-3').innerHTML = '&nbsp;';
    document.getElementById('error_message-4').innerHTML = '&nbsp;';
}
