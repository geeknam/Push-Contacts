sms_form_url = "http://pushcontacts.appspot.com/smsform";
//sms_form_url = "http://localhost:8093/smsform";

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

function checkLogin(){
	var scope = 'http://www.google.com/m8/feeds';
	return google.accounts.user.checkLogin(scope);
}


function getMyContacts(){
	$("#response").html("");
	// The feed URI that is used for retrieving contacts
	var feedUri = 'http://www.google.com/m8/feeds/contacts/default/full';
	var query = new google.gdata.contacts.ContactQuery(feedUri);

	// Set the maximum of the result set to be 50
	query.setMaxResults(500);

	// callback method to be invoked when getContactFeed() returns data
	var callback = function(result) {
	  // An array of contact entries
		var entries = result.feed.entry;

	  // Iterate through the array of contact entries
	  	for (var i = 0; i < entries.length; i++) {
	    	var contactEntry = entries[i];
	
        	var name = contactEntry.getTitle().getText();
	        if(name != ""){
		    	var phoneNumbers = contactEntry.getPhoneNumbers();
		
			    // Iterate through the array of phones belonging to a single contact entry
			    if (phoneNumbers.length != 0) {
			     	for (var j = 0; j < phoneNumbers.length; j++) {
						var phoneNumber = phoneNumbers[j].getValue();
						url = sms_form_url+"?phone="+ phoneNumber;
				  		$("#response").append("<b>"+name+"</b>: "+phoneNumber+" <a href='"+url+"'>Send SMS</a><br />");
					}
			    } 
	        }
	    }
	}//callback

	// Error handler
	var handleError = function(error) {
	  $("#response").html("Unable to retrieve contacts");
	}

	// Submit the request using the contacts service object
	contactsService.getContactFeed(query, callback, handleError);	
}

function initFunc() {
  	setupContactsService();
  	if(checkLogin()){
		logMeIn();
  	}
  	getMyContacts();
}