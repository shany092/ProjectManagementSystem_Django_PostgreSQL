/*{ <script>
    function loadDropdown(url, sourceId, targetId) {
        const sourceValue = document.getElementById(sourceId).value;
        $.ajax({
            url: url,
            data: { [`${sourceId}`]: sourceValue },
            success: function(data) {
                let targetDropdown = document.getElementById(targetId);
                targetDropdown.innerHTML = "<option value=''>Select</option>";
                data.forEach(item => {
                    targetDropdown.innerHTML += `<option value="${item.id}">${item.name}</option>`;
                });
            }
        });
    }

    // On continent change
    document.getElementById('continent_id').addEventListener('change', function () {
        loadDropdown('/load-countries/', 'continent_id', 'country_id');
        document.getElementById('state_id').innerHTML = "<option value=''>Select State</option>"; // Reset dependent dropdowns
        document.getElementById('city_id').innerHTML = "<option value=''>Select City</option>";
    });

    // On country change
    document.getElementById('country_id').addEventListener('change', function () {
        loadDropdown('/load-states/', 'country_id', 'state_id');
        document.getElementById('city_id').innerHTML = "<option value=''>Select City</option>";
    });

    // On state change
    document.getElementById('state_id').addEventListener('change', function () {
        loadDropdown('/load-cities/', 'state_id', 'city_id');
    });
</script>


document.addEventListener('DOMContentLoaded', function () {
        // Function to apply masks
        function applyMasks(fieldMap) {
            // Remove existing masks
            Inputmask.remove('input');

            // Apply masks based on the fieldMap
            for (const [selector, mask] of Object.entries(fieldMap)) {
                Inputmask(mask).mask(document.querySelector(selector));
            }
        }

        // Listeners for continent_name and country_name
        const continentField = document.querySelector('select[name="continent_name"]');
        const countryField = document.querySelector('select[name="country_name"]');

        if (continentField) {
            continentField.addEventListener('change', function () {
                if (continentField.value === "EU") {
                    applyMasks({
                        'input[name="country_name"]': "(aaa) 999-9999",
                        'input[name="nic_number"]': "99999-9999999-9",
                        'input[name="state_name"]': "(999) 999-9999",
                        'input[name="city_name"]': "A{3,}", // Letters only with min length 3
                        'input[name="passport_number"]': "AA999999",
                        'input[name="phone_number"]': "(999) 999-9999"
                    });
                } else {
                    // Reset masks for non-EU selections
                    Inputmask.remove('input');
                }
            });
        }

        if (countryField) {
            countryField.addEventListener('change', function () {
                if (countryField.value === "London") {
                    applyMasks({
                        'input[name="nic_number"]': "99999-99999999-99",
                        'input[name="state_name"]': "A{2,}",
                        'input[name="city_name"]': "A{2,}",
                        'input[name="passport_number"]': "L999999",
                        'input[name="phone_number"]': "+44 999-999-9999"
                    })
                }
                    if (countryField.value === "Pakistan") {
                        applyMasks({
                            'input[name="nic_number"]': "99999-9999999-9",
                            'input[name="state_name"]': "A{2,}",
                            'input[name="city_name"]': "A{2,}",
                            'input[name="passport_number"]': "L999999",
                            'input[name="phone_number"]': "+92 999-999-9999"
                        });
                } 
            
                    else {
                    // Reset masks for non-London selections
                    Inputmask.remove('input');
                }
            
            });
        }
    });

    function updatePlaceholders() {
        const typeSelector = document.querySelector('#id_employee_type');
        const selectedType = typeSelector.value;

        const placeholders = {
            'Italy Internal': 'Example: MKX1001',
            'Italy External': 'Example: MKX2001',
            'Pakistan Internal': 'Example: MKX3001',
            'Pakistan External': 'Example: MKX4001',
        };

        const placeholderField = document.querySelector('#id_employee_code');
        placeholderField.placeholder = placeholders[selectedType] || 'Example: N/A';
    }
    function loadCountries(continentId) {
        $.ajax({
            url: '/ajax/load-countries/',
            data: {
                'continent_id': continentId
            },
            success: function(data) {
                const countrySelect = $('#id_country');
                countrySelect.empty();
                data.forEach(country => {
                    countrySelect.append(`<option value="${country.id}">${country.name}</option>`);
                });
            }
        });
    }

    function loadStates(countryId) {
        $.ajax({
            url: '/ajax/load-states/',
            data: {
                'country_id': countryId
            },
            success: function(data) {
                const stateSelect = $('#id_state');
                stateSelect.empty();
                data.forEach(state => {
                    stateSelect.append(`<option value="${state.id}">${state.name}</option>`);
                });
            }
        });
    }

    function loadCities(stateId) {
        $.ajax({
            url: '/ajax/load-cities/',
            data: {
                'state_id': stateId
            },
            success: function(data) {
                const citySelect = $('#id_city');
                citySelect.empty();
                data.forEach(city => {
                    citySelect.append(`<option value="${city.id}">${city.name}</option>`);
                });
            }
        });
    }
    document.getElementById('id_continent').setAttribute('placeholder', 'Select Continent');
    document.getElementById('id_country').setAttribute('placeholder', 'Select Country');
    document.getElementById('id_state').setAttribute('placeholder', 'Select State');
    document.getElementById('id_city').setAttribute('placeholder', 'Select City');
 }*/
