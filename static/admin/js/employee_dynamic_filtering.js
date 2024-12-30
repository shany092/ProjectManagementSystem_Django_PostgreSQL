const fetchCountryMask = (countryId) => {
    let country_based_mask = {};
    $.ajax({
        url: `/api/get_country_mask/${countryId}/`,
        type: 'GET',
        async: false,
        success: (data) => {
            country_based_mask  =   data;
        }
    });
    return country_based_mask;
};  
// const $ =   django.jQuery;
(function($) {
    
    $(document).ready(function() {
        console.log($('#id_country').length); 
        if($('#id_country').val()!=''){
            let phone_input     = ".phone-input";
            let nic_number_input     = ".nic_number-input";
            let countryId = $('#id_country').val();  // Get selected country ID
            // alert(countryId);
            let country_based_mask    =   fetchCountryMask(countryId);
            if (typeof(country_based_mask.phone_number_mask)!='undefined') {
                $(phone_input).mask(country_based_mask.phone_number_mask, { placeholder:country_based_mask.phone_number_mask}); // Requires jQuery Mask plugin
                
            } else {
                $(phone_input).unmask(); // Remove any existing mask
                
            }
            if (typeof(country_based_mask.cnic_number_mask)!='undefined') {
                $(nic_number_input).mask(country_based_mask.cnic_number_mask, { placeholder:country_based_mask.cnic_number_mask}); // Requires jQuery Mask plugin
            } 
            else {
                $(nic_number_input).unmask(); // Remove any existing mask
            }
        }
        $('#id_country').on('change', function() {
            console.log("Country changed to: " + $(this).val());
            let phone_input     = ".phone-input";
            let nic_number_input     = ".nic_number-input";
            let countryId = $(this).val();  // Get selected country ID
            // alert(countryId);
            let country_based_mask    =   fetchCountryMask(countryId);
            if (typeof(country_based_mask.phone_number_mask)!='undefined') {
                $(phone_input).mask(country_based_mask.phone_number_mask, { placeholder:country_based_mask.phone_number_mask}); // Requires jQuery Mask plugin
                
            } else {
                $(phone_input).unmask(); // Remove any existing mask
                
            }
            if (typeof(country_based_mask.cnic_number_mask)!='undefined') {
                $(nic_number_input).mask(country_based_mask.cnic_number_mask, { placeholder:country_based_mask.cnic_number_mask}); // Requires jQuery Mask plugin
            } 
            else {
                $(nic_number_input).unmask(); // Remove any existing mask
            }
        });
    });
})(jQuery);


// (function($) {
//     $(document).ready(function() {
//         function updateDropdown(url, field, params) {
//             $.ajax({
//                 url: url,
//                 data: params,
//                 success: function(data) {
//                     var $field = $(field);
//                     $field.empty();
//                     for (var value in data) {
//                         $field.append($("<option>").attr("value", value).text(data[value]));
//                     }
//                 }
//             });
//         }

//         // Listen for changes in Country field
//         $("#id_country").change(function() {
//             var country_id = $(this).val();

//             // Populate States dropdown
//             updateDropdown("/admin/pmpapp/api/states/", "#id_state", { country: country_id });

//             // Populate Cities dropdown
//             updateDropdown("/admin/pmpapp/api/cities/", "#id_city", { country: country_id });

//             // Populate Employee Types dropdown
//             updateDropdown("/admin/pmpapp/api/employee_types/", "#id_employee_type", { country: country_id });
//         });
//     });
// })(jQuery);

