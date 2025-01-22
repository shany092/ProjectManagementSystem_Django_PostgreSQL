
// const $ =   django.jQuery;
(function($) {
    $(document).ready(function() {
        $("[for='id_password']").closest('.row').remove();
        $("[for='id_project_interval']").closest('.row').remove();

        $("[for='idd_continent']").closest('.row').remove();
        $(".delete-related").remove();
        if($('#id_country').val()!=''){
            let countryId = $('#id_country').val();  // Get selected country ID
            fetchCountryData(countryId,true);
        }
        $('#id_country').on('change', function() {
            console.log("Country changed to: ", $(this).val());
            let countryId = $(this).val();
            if (countryId) {
                fetchCountryData(countryId,false);
            }
        });
        $('#id_state').on('change', function() {
            console.log("State changed to: ", $(this).val());
            let stateId = $(this).val();
            if (stateId) {
                fetchStateData($('#id_country').val(),stateId);
            }
        });
    });
})(jQuery);
const fetchCountryData = (countryId,edit) => {
    $.ajax({
        url: `/api/get_country_data/${countryId}/`,
        type: 'GET',
        // async: false,
        success: (data) => {
            let emp_html    =   "<option value=''>Select</option>";
            let state_html    =   "<option value=''>Select</option>";
            let id_employee_type_val    =   $("#id_employee_type").val();
            let id_state_val            =   $("#id_state").val();
            if(data.emp_types.length>0){
                $.each(data.emp_types,function(i,v){
                    emp_html+=`<option value="${v.id}">${v.name}</option>`;
                });
                $("#id_employee_type").html(emp_html);
                if(id_employee_type_val!=""){
                    $("#id_employee_type").val(id_employee_type_val);
                }
                $("#id_employee_type").trigger('change');
            }
            if(data.state_select.length>0){
                $.each(data.state_select,function(i,v){
                    state_html+=`<option value="${v.state_id}">${v.state_name}</option>`;
                });
                $("#id_state").html(state_html);
                if(id_state_val!=""){
                    // alert(id_state_val);
                    $("#id_state").val(id_state_val);
                }
                $("#id_state").trigger('change');
            }
            if (data.masks_list.phone_number_mask) {
                $(".phone-input").mask(data.masks_list.phone_number_mask, { placeholder: data.masks_list.phone_number_mask });
            } else {
                $(".phone-input").unmask();  // Remove existing mask
            }
    
            if (data.masks_list.cnic_number_mask) {
                $(".nic_number-input").mask(data.masks_list.cnic_number_mask, { placeholder: data.masks_list.cnic_number_mask });
            } else {
                $(".nic_number-input").unmask();  // Remove existing mask
            }
        },
        error: (xhr, status, error) => {
            console.error("Error fetching country data: ",xhr,status, error);
        }
    });
   
};  
const fetchStateData = (countryId,stateId) => {
    $.ajax({
        url: `/api/get_state_data/${countryId}/${stateId}/`,
        type: 'GET',
        // async: false,
        success: (data) => {
            // let emp_html    =   "<option value=''>Select</option>";
            let state_Con    =   "<option value=''>Select</option>";
            let id_city_val            =   $("#id_city").val();
            if(data.city_select.length>0){
                $.each(data.city_select,function(i,v){
                    state_Con+=`<option value="${v.city_id}">${v.city_name}</option>`;
                });
                $("#id_city").html(state_Con);
                if(id_city_val!=""){
                    // alert(id_state_val);
                    $("#id_city").val(id_city_val);
                }
                $("#id_city").trigger('change');
            }
        },
        error: (xhr, status, error) => {
            console.error("Error fetching state data: ",xhr, status, error);
        }
    });
   
};
