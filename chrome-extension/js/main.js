contact_url     = "http://pushcontacts.appspot.com/send";
sms_url         = "http://pushcontacts.appspot.com/sms";
check_login_url = "http://pushcontacts.appspot.com/checklogin";

$(document).ready(function(){
	$("#content").hide();
	
	checkLogin();
	
	$("#menu_contact").click(function(){
		showOnly("#contact_form");
	});
	
	$("#menu_sms").click(function(){
		showOnly("#sms_form");
	});
	
	$("#menu_about").click(function(){
		showOnly("#about");
	});
	
	$('#counter').html( getLength($('#sms').val()) + ' chars');
	
	$('#sms').keyup(function(){
		var bytes = getLength($(this).val());
		var chars = $(this).val().length;
		$('#counter').html( (chars == bytes) ? (chars +' chars') : (chars +' chars (' + bytes + ' bytes)'));
	});

});

function getLength(string)
{
	var length = 0;

	for (var i = 0; i < string.length; i++)
	{
		length += (escape(string.charAt(i)).substring(0,2)=='%u') ? 2 : 1;
	}

	return length;
}

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

function checkLogin(){
	$.get(check_login_url, function(data){
		if(data == "LOGGED_IN"){
			$("#checklogin").hide();
			$("#content").show();
			$("#sms_phone").val("Loading contacts...");
			
			chrome.extension.getBackgroundPage().getContacts(onContacts);
			
			showOnly("#sms_form");
		}
		else{
			$("#checklogin").html("<p>Please login to the website before using the extension</p>");
			chrome.tabs.create({url : "http://pushcontacts.appspot.com" });
		}
	});
}

function saveContact(){
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

function sendSms(){
	var phone = $("#sms_phone").val();
	var sms   = $("#sms").val();
	
	$.post(sms_url, {"phone": phone, "sms": sms }, function(data){
		if(data == "OK"){
			$("#sms_response").hide().html("SMS has been pushed to the phone").fadeIn(1000);
			$("#sms_phone").val("");
			$("#sms").val("");
		}
		else if(data == "error_register"){
			$("#response").hide().html("You haven't registered your Android device yet").fadeIn(1000);
		}
		else if(data == "error_c2dm"){
			$("#response").hide().html("There was a problem with C2DM service").fadeIn(1000);
		}
		else{
			$("#sms_response").hide().html("There was unknown problem").fadeIn(1000);
		}
	});
}

function isNumber(n) {
  return !isNaN(parseFloat(n)) && isFinite(n);
}

