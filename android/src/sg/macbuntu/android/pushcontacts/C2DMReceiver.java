/*
 * Copyright 2010 Google Inc.
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
import android.media.RingtoneManager;
import android.net.Uri;
import android.os.Bundle;
import android.provider.Contacts;
import android.provider.Contacts.People;
import android.util.Log;
import android.widget.Toast;


import com.google.android.c2dm.C2DMBaseReceiver;

public class C2DMReceiver extends C2DMBaseReceiver {
    private static final String TAG = "DataMessageReceiver";

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
           Log.e(TAG, "Name: " + name + ", Phone: " + phone);
           Uri contactUri = insertContact(context, name, phone);
           generateNotification(context, name, phone, contactUri);
      
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
       
       Log.e("C2DM", uri.toString());
       
       return uri;
   }

   private void generateNotification(Context context, String name, String phone, Uri contactUri) {
       int icon = android.R.drawable.stat_notify_sync;
       long when = System.currentTimeMillis();
       String message = name + ": " + phone;

       Notification notification = new Notification(icon, message, when);
       notification.defaults = Notification.DEFAULT_SOUND;
       notification.defaults |= Notification.DEFAULT_VIBRATE;
       notification.flags |= Notification.FLAG_AUTO_CANCEL;
       
       //Launch new Intent to view a new contact added
       Intent notificationIntent = new Intent(Intent.ACTION_VIEW, contactUri);
       PendingIntent contentIntent = PendingIntent.getActivity(this, 0, notificationIntent, 0); 

       notification.setLatestEventInfo(getApplicationContext(), "New contact added", message, contentIntent);
       NotificationManager nm = (NotificationManager)context.getSystemService(Context.NOTIFICATION_SERVICE);
       nm.notify(1, notification);

   }
}
