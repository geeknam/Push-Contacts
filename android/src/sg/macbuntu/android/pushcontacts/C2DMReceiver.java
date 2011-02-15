/*
 * Copyright 2010 Ngo Minh Nam.
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */
package sg.macbuntu.android.pushcontacts;


import android.app.Notification;
import android.app.NotificationManager;
import android.app.PendingIntent;
import android.content.ContentValues;
import android.content.Context;
import android.content.Intent;
import android.content.SharedPreferences;
import android.database.Cursor;
import android.media.RingtoneManager;
import android.net.Uri;
import android.os.Bundle;
import android.preference.PreferenceManager;
import android.provider.Contacts;
import android.provider.Contacts.People;
import android.telephony.SmsManager;
import android.util.Log;
import android.widget.Toast;


import com.google.android.c2dm.C2DMBaseReceiver;

public class C2DMReceiver extends C2DMBaseReceiver {
    private static final String TAG = "DataMessageReceiver";
    private static final int TYPE_CONTACT = 0;
    private static final int TYPE_SMS     = 1;
    private static final Uri THREAD_ID_CONTENT_URI = Uri.parse("content://mms-sms/threadID");
    

    public C2DMReceiver() {
        super(DeviceRegistrar.SENDER_ID);
    }

    @Override
    public void onRegistrered(Context context, String registration) {
        DeviceRegistrar.registerWithServer(context, registration);
    }

    @Override
    public void onUnregistered(Context context) {
        SharedPreferences prefs = Prefs.get(context);
        String deviceRegistrationID = prefs.getString("deviceRegistrationID", null);
        DeviceRegistrar.unregisterWithServer(context, deviceRegistrationID);
    }

    @Override
    public void onError(Context context, String errorId) {
        context.sendBroadcast(new Intent("sg.macbuntu.android.pushcontacts.UPDATE_UI"));
    }

    @Override
    public void onMessage(Context context, Intent intent) {
       Bundle extras = intent.getExtras();
       if (extras != null) {
           String name  = (String) extras.get("contact_name");
           String phone = (String) extras.get("phone_number");
           String sms = (String) extras.get("sms");
    	   Log.e(TAG, "Name: " + name + ", Phone: " + phone);
           
           if(name != null){
               Uri contactUri = insertContact(context, name, phone);
               if(getPrefs()[0]){
                   generateNotification(context, TYPE_CONTACT,name, phone, contactUri);
               }
           }
           else{
        	   Long threadId = getThreadIdFromPhone(context, phone);
        	   sendSMS(phone, sms);
        	   if(getPrefs()[0]){
        		   generateNotification(context, TYPE_SMS, name, phone, Uri.parse("content://mms-sms/conversations/"+threadId));
        	   }
           }
      
       }
       
   }

   private Uri insertContact(Context context, String name, String phone) {
	   
       ContentValues values = new ContentValues();
       values.put(People.NAME, name);
       Uri uri = getContentResolver().insert(People.CONTENT_URI, values);
       Uri numberUri = Uri.withAppendedPath(uri, People.Phones.CONTENT_DIRECTORY);
       values.clear();
       
       values.put(Contacts.Phones.TYPE, People.Phones.TYPE_MOBILE);
       values.put(People.NUMBER, phone);
       getContentResolver().insert(numberUri, values);
       
       return uri;
   }
   
   private void sendSMS(String phone, String message){              
	   ContentValues values = new ContentValues();
	   values.put("address", phone);
	   values.put("body", message);
	   getContentResolver().insert(Uri.parse("content://sms/sent"), values);

	   SmsManager sms = SmsManager.getDefault();
	   //try sendMultipartTextMessage 
	   //http://www.anddev.org/advanced-tutorials-f21/can-not-read-the-sms-when-using-sendmultiparttextmessage-t11581.html
	   //ArrayList<String> messages = sms.divideMessage(message);
	   //sms.sendTextMessage(phone, null, messages, null, null); 
       sms.sendTextMessage(phone, null, message, null, null);   
   }
   
   private static String getNameFromPhoneNumber(Context context, String phone) {
       Cursor cursor = context.getContentResolver().query( Uri.withAppendedPath(Contacts.Phones.CONTENT_FILTER_URL, phone),
    		   											   new String[] { Contacts.Phones.NAME }, 
    		   											   null, null, null);
       if (cursor != null) {
    	   try {
    		   if (cursor.getCount() > 0) {
	               cursor.moveToFirst();
	               String name = cursor.getString(0);
	               Log.e("PUSH_CONTACTS","Found person: " + name);
	               return name;
               }
           } finally { cursor.close(); }
       }
       return null;
   }
   
   private static long getThreadIdFromPhone(Context context, String phone) {
       
       String THREAD_RECIPIENT_QUERY = "recipient";
       
       Uri.Builder uriBuilder = THREAD_ID_CONTENT_URI.buildUpon();
       uriBuilder.appendQueryParameter(THREAD_RECIPIENT_QUERY, phone);
       
       long threadId = 0;
       
       Cursor cursor = context.getContentResolver().query(uriBuilder.build(), 
    		   											  new String[] { "_id" },
    		   											  null, null, null);
       if (cursor != null) {
    	   try {
    		   if (cursor.moveToFirst()) {
    			   threadId = cursor.getLong(0);
               }
           } finally { cursor.close(); }
       }
       return threadId;
	}

   private void generateNotification(Context context, int type, String name, String phone, Uri uri) {
	   int icon = 0;
	   long when = System.currentTimeMillis();
	   String message = null, title = null;
	   
	   switch(type){
	   		case(TYPE_CONTACT):{
			    icon = android.R.drawable.stat_notify_sync;
			    message = name + ": " + phone;
			    title = this.getResources().getString(R.string.notify_contact);
			    break;
	   		}
	   		case(TYPE_SMS):{
		   	    icon = R.drawable.stat_notify_mms;
		   	    if(getNameFromPhoneNumber(context, phone) != null){
		   	    	phone = getNameFromPhoneNumber(context, phone);
		   	    }
		   	    message = this.getResources().getString(R.string.notify_sms_msg) + phone;
		   	    title   = this.getResources().getString(R.string.notify_sms_title);
		   	    break;
	   		}
		   
	   }

       Notification notification = new Notification(icon, message, when);
       boolean settings[] = getPrefs();
       
       if(settings[1]){
           notification.defaults = Notification.DEFAULT_SOUND;
       }
       if(settings[2]){
           notification.defaults |= Notification.DEFAULT_VIBRATE;
       }
       notification.flags |= Notification.FLAG_AUTO_CANCEL;
       
       //Launch new Intent to view a new contact added
       Intent notificationIntent = new Intent(Intent.ACTION_VIEW, uri);
       PendingIntent contentIntent = PendingIntent.getActivity(this, 0, notificationIntent, 0); 
       notification.setLatestEventInfo(getApplicationContext(), title, message, contentIntent);

       NotificationManager nm = (NotificationManager)context.getSystemService(Context.NOTIFICATION_SERVICE);
       nm.notify(1, notification);

   }
   
   private boolean[] getPrefs() {
       SharedPreferences prefs = PreferenceManager.getDefaultSharedPreferences(getBaseContext());
       boolean notificationPreference = prefs.getBoolean("cbNotification", true);
       boolean soundPreference = prefs.getBoolean("cbPush", true);
       boolean vibrationPreference = prefs.getBoolean("cbVibration", true);
       boolean settings[] = {notificationPreference, soundPreference, vibrationPreference};
       return settings;
   }
}
