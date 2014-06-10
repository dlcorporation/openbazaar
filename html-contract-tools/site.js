


// ======================== Data ======================== 
// 
// 



//Variable that contains possible form types, etc
var form_gen_types = [
    {name:'text',type:"text",class:""},
    {name:'nym', type:"text", class:"has-success", min_len:10 ,max_len:80 , regex_validation_rule:"", regex_validation_msg:"Failed to validate data, please re-enter"},
    {name:'btc_addr', type:"text", class:"has-success", min_len:26 ,max_len:33 , regex_validation_rule:"^[13][a-zA-Z0-9]{26,33}$", regex_validation_msg:"~field~ must be a valid bitcoin address."},
    {name:'currency',type:"text",class:"",regex_validation_rule:'^[0-9]+.?[0-9]+$',regex_validation_msg:"~field~ must be a valid currency value"},
    {name:'checkbox',type:"checkbox",class:""},
    {name:'textarea',type:"textarea",class:""},
    {name:'date',type:"datetime",class:"",regex_validation_rule:'^20[1-6][0-9]-[0-1]?[0-9]-[0-3][0-9] [0-2][0-9]:[0-5][0-9]:[0-5][0-9]$',regex_validation_msg:"~field~ must be a valid Date Time (eg 2015-11-23 12:33:11)"}    
];


//Variable that contains possible form types, etc
var form_gen_elements = {
    nym:{dataID:'nym_id',name:"Nym ID", type:'nym',required:true,single_field:true,default_value:"testnym"},
    btc_addr:{dataID:'btc_addr',name:"Your Bitcoin address",type:"btc_addr",required:true,single_field:true,default_value:"1P1GFYLWUhPzFazFKhp2ZHAzaBBKD6AKX1"},
    asset_name:{dataID:'asset_name',name:"Name of item to sell", type:"text",min_len:5,required:true,single_field:true,default_value:"1 french cat"},
    asset_price:{dataID:'asset_price',name:"Price (in BTC) of item to sell", type:"currency",required:true,single_field:true,default_value:"1.0"},
    contract_exp:{dataID:'contract_exp',name:"Offer expiry date", type:"date",required:true,single_field:true,default_value:"2014-07-22 12:00:00"}
            
    };
    

// ======================== Main Docoument Functions ======================== 

//when document ready, run this
$(function() {
    //By default, show the script generator
    $("#page_generator").fadeIn({duration:500});
    
    form_gen_create_list();
    
    //If no keypair exist, prompt for one at startup,
    if(localStorage.PGP_keypair ===undefined)
        {
        $("#popup_content").html($("#template_popup_pgp_load").html());
        $("#popup_modal").modal("show");
        }
   
   
   //Set options to stored values
    if(localStorage.options !==undefined){
        //for each option
        $.each(JSON.parse(localStorage.options),function(i,v){
            //Set the value of the div id for this index to its value
            $("#"+i).val(v);
        });
    }
    
});


//Function for managing the changes of pages/menu
function menu(div){
    //First remove all active elements from the menu
    $(".nav_container li").removeClass("active");
    
    //Hide all the page sections, 
    $('.page_wrap:not(:hidden)').fadeOut(function(){
        //Once hide is completed, fade in the correct div
        $('#'+div).fadeIn();
        //Add the actie class the the appropriate meny div
        $("#menu_li_"+div).addClass("active");
    });
}


function set_option(opt){
    //Prepare an array variable
    var options = {};
    
    //if there is already local options stored,
    if(localStorage.options!==undefined)
        //parse the data to the options var
        options = JSON.parse(localStorage.options);
    
    
    //Set the option into the array
    options[opt]=$("#" + opt).val();
    //Write all options back to local storage
    localStorage.options = JSON.stringify(options);
    
}



// ======================== PGP Functions ======================== 
// 
// 
//  function for loading a PGP key
function pgp_file_load(){
    //Get the file to a var
    var file = $('#pgp_key_pair').get(0).files[0];
    
    //Create a file reader for reading the file
    var r = new FileReader();
   
   
    // Set the onload function for when the file has been read by the reader
    r.onload = function(f){
        //Store the PGP keys in temporary val
        
        //
        //console.log(f.target.result);
        //var keysstring = f.target.result;
        //var keysstring = '-----BEGIN PGP PUBLIC KEY BLOCK----- \r\n Version: Mailvelope v0.8.2';
        var pub_key = f.target.result.match(new RegExp('-----BEGIN PGP PUBLIC KEY BLOCK-----[\r\n](.*[\r\n]){2,}-----END PGP PUBLIC KEY BLOCK-----'))[0];
        var priv_key = f.target.result.match(new RegExp('-----BEGIN PGP PRIVATE KEY BLOCK-----[\r\n](.*[\r\n]){2,}-----END PGP PRIVATE KEY BLOCK-----'))[0];
        
        //If either of the keys length is less than 100 than we did not get them
        if(pub_key.length < 100 || priv_key.length < 100){
           console.log("failed to load keys");
        }
        //else store the keys
        else {
            //Store the keys
            localStorage.PGP_keypair = JSON.stringify([pub_key,priv_key]);
            location.reload();
        }
        
    }; 
     
    //Read the file as a text
     r.readAsText(file);
    
}




// ======================== Contract Generation Functions ======================== 

//Function creates list of possible form elements for the generate contracts page
function form_gen_create_list(){
    //For each element
    $.each(form_gen_elements,function(c,o){
        //Add teh link using this element details, and gettin the type
        form_gen_add_link_line(o);
    });
};



//Function returns form gen type data
function form_gen_get_type(type){
    var gen_type_obj ;
    $.each(form_gen_types,function(co,t){
        if(type===t.name)gen_type_obj = form_gen_types[co];
    });
    
    if(gen_type_obj!==undefined)return gen_type_obj;
    
    else console.log("Could not find element type" + type);
    
}

    
//Function returns form gen type data
function form_gen_get_element(elementname){
    var gen_el_obj;
    
    //For each element in the array
    $.each(form_gen_elements,function(c,e){
        //If the element name === the element type, set the var as this element
        if(elementname===e.dataID)gen_el_obj = form_gen_elements[c];
        
    });
    
    if(gen_el_obj!==undefined)return gen_el_obj;
    else console.log("Could not find element " + elementname);
}



//Function adds a linke for a form element to the left menu for adding to the contract
function form_gen_add_link_line(finfo){
    $("#form_gen_field_list").append("<li id='form_gen_add_" + finfo.dataID + "'><a href='#' onclick='gen_add_el(\""+  finfo.dataID  +"\")'>" + finfo.name + "</a></li>");
    
}


//Adds a clicked element from the left menu to the contract
function gen_add_el(elname){
    //Get the element from the array, and the type
    var element = form_gen_get_element(elname);
    var type = form_gen_get_type(element.type);
    
    //Check if this element only allows a single field (on instance of this element)
    if(element.single_field===true){
        //If the element already exists (eg the HTML is not undefined)
        if($("#"+element.dataID).html() !== undefined){
            //Show an alert, and return nothing to exit the function
            alert("This field is not allowed to be added twice to a contract");
            return;
        }
    }
    
    
    //Get the HTMl and prepare to add
    var inputHtml = $("#form_input_template_"+type.type).html();
    
    //If the HTMl is undefined, it means there is no template HTML set for this kind of field
    if(inputHtml === undefined)console.log("Error getting template input format #form_input_template_"+type.type);
    
    //Replace the various elements of the html
    inputHtml = inputHtml.replace("field_id",element.dataID).replace("field_id",element.dataID).replace("fieldname",element.name).replace("fieldtype",type.type);
    
    
    //Append the HTML to the generator fields
    $("#form_gen_fields").append(inputHtml);
    
    //Add any classes to this field if needed
    $("#form_gen_fields :last div input").addClass(type.class);
    
    //If a default value is set, set it in the input feild
    if(element.default_value !== undefined)
        $("#form_gen_fields").children(":last").children('div').children('.form_gen_input').val(element.default_value);
        
    
}


//Deletes a contract item from the current contract
function gen_del_el(cel){
        $(cel).parent().parent().remove();
}

//Function to generate teh contract
function gen_create_con(){
    //intialise an varialbe to hold an object array of values
    var contract_values = {};
    $("#form_gen_fields").find('input[name="gen_input_field[]"]').each(function(){
        var id = $(this).attr('id');
        contract_values[id] = $(this).val();
    });
    
    //Check the contract values and get reulst to variable.
    var checks = gen_check_con();
    
    //If the checks did not return true, 
    if(checks!==true && checks !==undefined)$("#xml_contract").html(checks).show();
    
    //If all values are correct ,then show the sign and encrypt modal
    else {
        //get parsed data
        var parsedValues = gen_parse_values(contract_values);
        
        $("#xml_contract").html(parsedValues).show();
        $("#popup_content").html($("#input_sign_and_encrypt_PGP").html());
        $("#popup_modal").modal('show');
    }
        
}

//Function parses all variables into a particular type (eg JSON, XML, etc) and returns a string of the parsed values
function gen_parse_values(v){
    
    //get the type from the drop down box
    var type=$("#option_contract_format").val();
    
    //For XML Data
    if(type==="XML"){
        //Prepare a var for holding data
        var resultData = "";
        $.each(v,function( index,value ) {
                        resultData = resultData + "<"+index+">" + value + "</"+index+">\r\n";
        });
        
        //Once completed, return result data
        return resultData;
    }
    else if(type==="JSON")
        return JSON.stringify(v);
    
    //Else parse in HTML type format
    else{
        var resultData = "";
        $.each(v,function( index,value ) {
                        resultData = resultData + index + " : " + value + "\r\n";
        });
        
        //Once completed, return result data
        return resultData;
    }
}

//function to check the submitted contract fields
//
// Calls gen_check_inputs_required function, which 
function gen_check_con(){
    //Check if all required inputs are present
    var required_inputs_check = gen_check_inputs_required();
    
    //Prepare an array for storing the result of checking all values
    var valid_checks = new Array();
    //for each input that is present, Run the validation check
    $("#form_gen_fields").find('input[name="gen_input_field[]"]').each(function(){
        //Change the form appearance
        var res = gen_form_data_change(this);
        
        //If the result is not true, then add it to the errors list
        if(res!==true)
            valid_checks.push(res);
    });
    
    
    
    //If we have errors in the required_inputs_check result, return text/html error
    if(required_inputs_check.length > 0)
        return "Not all required fields are present : <p> " + required_inputs_check.join("<br>") + "</p>";
    
    
    //If we have errors in the valid_checks result, return text/html error
    else if(valid_checks.length > 0 )
        return "Found some errors with Fields :<p> " + valid_checks.join("<br>") + "</p>";
    
    //Else return true :)
    else return true;
    
        
}

//This function should be fired whenever a form data is changed, 
//Runs validation wizard and reports any errors
//Starts by getting the result of the data_validation to a variable
//If the validation is true, we change the color of the input field to green using the gne_form_input_msg function
// If validation is an array, it means it errored, we set the mssages using the same function
//Else if we did not get anything, nothing is right, all validation's should return something (ether, true, false or an array);
function gen_form_data_change(obj){
    //run the validation function
    var validation = data_validation(obj);
    
    //log an entry so we can see what is happening
    //If the result is false, something failed spectaculy,
    if(validation===false)alert("Error validating Data, please make sure there are no modifications to the code")
    else if (validation===true){
        gen_form_input_msg(obj,'','success');
        return true;
    }
    //else if the result is an array
    else if(Object.prototype.toString.call(validation) === '[object Array]' ){
        gen_form_input_msg(obj,validation.join(),'error');
        return validation.join("<br>");
    }
    //else alert that something went wrong, 
    else{
        alert("something went wrong validating the data")
    }
}



//Function modifies the display parameters of each form element
function gen_form_input_msg(element,msgTxt,status){
    //if Status is success, warning, error, or false
    
    //For ease of coding, get the parent object to a var
    var par = $(element).parent().parent();
    //first, remove any classes that may exist on this obj
    par.removeClass("has-error has-warning has-success");
    
    //If there is a helper, remove it
    $(par).children(".help-block").remove();
    
    //append a help block
    $(par).append('<span class="help-block">'+msgTxt+'</span>');
    
    //if the status is not false, set the new class
    if(status!==false)$(par).addClass("has-"+status);
    
    
}

//Function checks all data validation rules in for the named element, 
//Returns true if validation passed,
//Returns array of errors if validation failed 
//Returns false if elname not found in the array
function data_validation(inputObj){
    //Get the element details
    var el = form_gen_get_element($(inputObj).attr("id"));
    
    //if el is false, return false
    if(el===false || el===undefined)return false;
    
    //Make sure the object exists in the form
    var dat = $(inputObj).html();
    if(dat===undefined)
       return "The " + el.name + " field does not exist on the form, can not validate non-existant data";
   
    //Get the type for the field
    var type = form_gen_get_type(el.type);
    
    //if not type, ,return false
    if(type===false || type===undefined)return false;
    
    //Get the value to a var
    var val = $(inputObj).val();
    
    //prepare a var for storing any error messages
    var errors = new Array();
    
    //min_len:26
    //max_len:33
    //regex_validation_rule:"^[13][a-zA-Z0-9]{26,33}$"
    //regex_validation_msg:"~field~ must be a valid bitcoin address."}
   
    //if min lenght is set on the element, check it
    if(el.min_len !==undefined){
        
        //Check the value
        if(val < el.min_len)errors.push(el.name + " must be at least " + el.min_len + " characters long \r\n");
    }
    //Else check if the type has a minimum length
    else if(type.min_len !==undefined){
        //Check the value
        if(val < type.min_len)errors.push(el.name + " must be at least " + type.min_len + " characters long \r\n");
    }
   
    //if element max length is set, 
    if(el.max_len !==undefined){
        //Check the value
        if(val > el.max_len)errors.push(el.name + " must be less than or equal to " + el.min_len + " characters long \r\n");
    }
   
    //else if the type max length is set, 
    else if(type.max_len !==undefined){
        //Check the value
        if(val > type.max_len)errors.push(el.name + " must be less than or equal to " + type.min_len + " characters long \r\n");
    }
   
    //If element regex is set
    if(el.regex_validation_rule !==undefined){
        var re = new RegExp(el.regex_validation_rule,'i');
        
        if(re.test(val)===false)errors.push(el.regex_validation_msg.replace("~field~",el.name)+". Invalid match " + val + "\r\n");
    }
    //else if the type regex is set
    if(type.regex_validation_rule !==undefined){
        var re = new RegExp(type.regex_validation_rule,'i');
        
        if(re.test(val)===false)errors.push(type.regex_validation_msg.replace("~field~",el.name)+"  Invalid match " + val + "\r\n");
    }
    
    if(errors.length < 1)return true;
    else return errors;
    
}

function gen_sign_con(){
    
    
    //First, if the keypair is not set
      if(localStorage.PGP_keypair ===undefined)
        {
        //Show the popup to load the keypair
        $("#popup_content").html($("#template_popup_pgp_load").html());
        $("#popup_modal").modal("show");
        }
    else{
        //Get the key to a val
        var pgp_priv_key = openpgp.key.readArmored(JSON.parse(localStorage.PGP_keypair)[1]).keys[0];
        var pgp_pub_key = openpgp.key.readArmored(JSON.parse(localStorage.PGP_keypair)[0]).keys[0];
        
        
        
        //Attempt to decrypt the public key
        if(pgp_priv_key.decrypt($("#pgp_pass").val())){
           
            
            //Sign the contract with the private key,
            var pgpSignedContract = openpgp.signClearMessage([pgp_priv_key], $("#xml_contract").html());

            //write the contract to the contract location
            $("#xml_contract").html(pgpSignedContract);

            //Set the modal back to blank, and remove all input fields
            $("#popup_content").html("");
            $("#form_gen_fields").html("");

        }
        //If the key decryption failes
        else{
           //notify the user
           $("#decrypt_alert").html('<div class="alert alert-danger alert-dismissable">Failed to decrypt key, do you have the correct passphrase?</div>');
        }
    }
}
  

function gen_check_inputs_required(){
    //Prepare a var for storing messages in 
    var msgs = new Array();
    
    //For each available input field,
     $.each(form_gen_elements,function(c,el){
         var dat = $("#"+el.dataID).html
         
         //If the field does not exist in the html form
         if(dat===undefined)
             if(el.required===true)
                //add the error to the array
                msgs.push("You must include the " + el.name + " field in your contract");
         
    });
    //If the msgs string is set, return it, 
    if(msgs.length >= 1)return msgs;
    //Else return true
    else return true;
}
