server_url = "http://pushcontacts.appspot.com/send";

function save(){
	var contact_name = encodeURIComponent($("#contact_name").val());
	var phone_number = encodeURIComponent($("#phone_number").val());
	
	get_url = server_url+"?name="+contact_name+"&phone="+phone_number;
	if(contact_name == '' || phone_number == ''){
		$("#response").hide().html("Fill in all blanks").fadeIn(2000);
	}
	else if(!isNumber(phone_number)){
		$("#response").hide().html("Phone number is invalid").fadeIn(2000);
	}
	else{
		$.get(get_url,function(data){
			if(data == "OK"){
				$("#response").hide().html("Contact pushed to the phone").fadeIn(2000);
				$("#contact_name").val("");
				$("#phone_number").val("");
			}
			else if(data == "error_params"){
				$("#response").hide().html("Fill in all blanks").fadeIn(2000);
			}
			else{
				$("#response").hide().html("There was an error sending the contact").fadeIn(2000);
			}		    
		});
	}

}


function isNumber(n) {
  return !isNaN(parseFloat(n)) && isFinite(n);
}