contact_url = "http://pushcontacts.appspot.com/send";
sms_url     = "http://pushcontacts.appspot.com/sms";

$(document).ready(function(){
	showOnly("#sms_form");
	
	$("#menu_contact").click(function(){
		showOnly("#contact_form");
	});
	
	$("#menu_sms").click(function(){
		showOnly("#sms_form");
	});
	
	$("#menu_about").click(function(){
		showOnly("#about");
	});

});

function showOnly(div){
	var all_divs = ["#sms_form","#contact_form","#about"];
	for(i=0; i<all_divs.length; i++){
		if(all_divs[i] == div){
			$(div).show();
		}
		else{
			$(all_divs[i]).hide();
		}
	}
}

function save(){
	var contact_name = encodeURIComponent($("#contact_name").val());
	var phone_number = encodeURIComponent($("#phone_number").val());
	
	get_url = contact_url+"?name="+contact_name+"&phone="+phone_number;
	if(contact_name == '' || phone_number == ''){
		$("#response").hide().html("Fill in all blanks").fadeIn(1000);
	}
	else if(!isNumber(phone_number)){
		$("#response").hide().html("Phone number is invalid").fadeIn(1000);
	}
	else{
		$.get(get_url,function(data){
			if(data == "OK"){
				$("#contact_response").hide().html("Contact has been pushed to the phone").fadeIn(1000);
				$("#contact_name").val("");
				$("#phone_number").val("");
			}
			else if(data == "error_params"){
				$("#response").hide().html("Fill in all blanks").fadeIn(1000);
			}
			else if(data == "error_register"){
				$("#response").hide().html("Please register your device").fadeIn(1000);
			}
			else{
				$("#response").hide().html("Login to service required").fadeIn(1000);
				chrome.tabs.create({url: get_url});
			}	    
		});
	}
}

function sendsms(){
	var phone = $("#sms_phone").val();
	var sms   = $("#sms").val();
	
	$.post(sms_url, {"phone": phone, "sms": sms }, function(data){
		if(data == "OK"){
			$("#sms_response").hide().html("SMS has been pushed to the phone").fadeIn(1000);
			$("#sms_phone").val("");
			$("#sms").val("");
		}
		else{
			$("#sms_response").hide().html("Not pushed").fadeIn(1000);
		}
	});
}

function isNumber(n) {
  return !isNaN(parseFloat(n)) && isFinite(n);
}

