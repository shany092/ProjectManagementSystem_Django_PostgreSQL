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
