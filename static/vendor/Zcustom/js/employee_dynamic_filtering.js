// const fetchCountryMask = (countryId) => {
//     let mask = '';
//     $.ajax({
//         url: `/api/get_country_mask/${countryId}/`,
//         type: 'GET',
//         async: false,
//         success: (data) => {
//             mask = data.mask;
//         }
//     });
//     return mask;
// };  
//const $ =   django.jQuery;
// (function($) {
    django.jQuery('#id_country').on('change', function() {
        console.log("Event is not throttled!");
    });
    // django.jQuery(document).on('load',function() {
        window.onload = function() {
        console.log($('#id_country').length); 
        django.jQuery('#id_country').off('change').on('change', function() {
            console.log("Country changed to: " + $(this).val());
            let input     = ".phone-input";
            let countryId = $(this).val();  // Get selected country ID
            alert(countryId);
            // let masking    =   fetchCountryMask(countryId);
            // if (masking) {
            //     $(input).mask(masking, { placeholder: " " }); // Requires jQuery Mask plugin
            // } else {
            //     $(input).unmask(); // Remove any existing mask
            // }
        });
    }
// })(django.jQuery);


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

