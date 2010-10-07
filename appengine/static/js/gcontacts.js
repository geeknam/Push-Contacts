
var t;
$(document).ready(function() {
	$('a[rel*=facebox]').facebox() 
	$("#smsbox").hide();
	$("#error_sms").hide();
	$("#error_contact").hide();
	$("#contactbox").hide();
	$("#fbcomments").hide();
	
	$("#search").keyup(function(){
		clearTimeout(t);
		t = setTimeout('getMyContacts($("#search").val())',1000);
	});
	
});

// Google Contact Service
google.load("gdata", "1.x");
google.setOnLoadCallback(initFunc);

var contactsService;

function setupContactsService() {
  	contactsService = new google.gdata.contacts.ContactsService('MacbuntuInc-PushContacts-1.0');
}

function logMeIn() {
	var scope = 'http://www.google.com/m8/feeds';
  	var token = google.accounts.user.login(scope);
}

function getMyContacts(search){
	$("#gcontacts").html("");
	
	var feedUri = 'http://www.google.com/m8/feeds/contacts/default/full';
	var query = new google.gdata.contacts.ContactQuery(feedUri);

	// Set the maximum of the result set to be 500
	query.setMaxResults(500);

	// callback method to be invoked when getContactFeed() returns data
	var callback = function(result) {
	  	// An array of contact entries
		var entries = result.feed.entry;
		$("#gcontacts").append("<table>");
	  	// Iterate through the array of contact entries
	  	for (var i = 0; i < entries.length; i++) {
	    	var contactEntry = entries[i];
        	var name = contactEntry.getTitle().getText();

			if(search == null){
				if(name != ""){
					generateContactList(contactEntry);
		        }
			}
			else{
		        if(name != "" && name.toLowerCase().indexOf(search.toLowerCase()) != -1){
					generateContactList(contactEntry)
		        }
			}
	    }
		$("#gcontacts").append("</table>");
	}//callback

	// Error handler
	var handleError = function(error) {
	  $("#gcontacts").html("<img src='/static/css/error.png' width='30px' style='float:left; margin-top:-3px'/><span class='error'>Login to retrieve contacts </span>");
	}

	// Submit the request using the contacts service object
	contactsService.getContactFeed(query, callback, handleError);	
}

function generateContactList(contactEntry){
	var phoneNumbers = contactEntry.getPhoneNumbers();
	var name = contactEntry.getTitle().getText();
    // Iterate through the array of phones belonging to a single contact entry
    if (phoneNumbers.length != 0) {
     	for (var j = 0; j < phoneNumbers.length; j++) {
			var phoneNumber = phoneNumbers[j].getValue().replace(/\s+/g,'').replace(/[\+\-]/,"").replace("-","");
			$("#gcontacts").append("<tr>");
	  		$("#gcontacts").append("<td>"+name+"</td>");
			$("#gcontacts").append("<td>"+phoneNumber+"</td>");
			$("#gcontacts").append("<td><input type=\"button\" value=\"SMS\" onclick=\"fillData("+"'"+name+"','"+phoneNumber+"'"+")\"/></td>");
			$("#gcontacts").append("</tr>");
		}
    }
}

function initFunc() {
  	setupContactsService();
  	getMyContacts();
}

function fillData(contact,phone){
	$("#contact").html(contact);
	$("#phone").val(phone);
	jQuery.facebox({ div: '#smsbox' });
}

function createContact(){
	jQuery.facebox({ div: '#contactbox' });
}

function showCommentBox(){
	jQuery.facebox({ div: '#fbcomments' });
}

function share(url){
    mywin = window.open(url,'Share Android Push Contacts', 'width=700, height=450');
    mywin.moveTo(200,200);
}

function sendContact(){
	var name   = $("input[name='name']:visible").val();
	var phone  = $("input[name='phone']:visible").val();
	
	if(name.length === 0 || phone.length === 0){
		$("#error_contact").fadeIn("slow").show();
	}
	else{
		$.get("/send", { name: name, phone: phone }, function(data){
			$(document).trigger('close.facebox');
			$("#error_contact").hide();
		});		
	}
}

function sendSms(){
	var sms   = $("textarea[name='sms']:visible").val();
	var phone = $("#phone").val();		
	
	if(sms.length === 0){
		$("#error_sms").fadeIn("slow").show();
	}
	else{
		$.post("/sms", { phone: phone, sms: sms }, function(data){
			if(data == "OK"){
				$(document).trigger('close.facebox');
				$("#error_sms").hide();
			}
			else{
				$("#error_sms").html("The service is not available").fadeIn("slow").show();	
			}
		});
	}
}
