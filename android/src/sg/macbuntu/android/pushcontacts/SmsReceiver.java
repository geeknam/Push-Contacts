package sg.macbuntu.android.pushcontacts;

import java.io.IOException;
import java.util.ArrayList;
import java.util.List;

import org.apache.http.NameValuePair;
import org.apache.http.client.ClientProtocolException;
import org.apache.http.client.HttpClient;
import org.apache.http.client.entity.UrlEncodedFormEntity;
import org.apache.http.client.methods.HttpPost;
import org.apache.http.impl.client.DefaultHttpClient;
import org.apache.http.message.BasicNameValuePair;
import org.apache.http.protocol.HTTP;

import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.Intent;
import android.content.SharedPreferences;
import android.database.Cursor;
import android.net.Uri;
import android.os.Bundle;
import android.provider.Contacts;
import android.telephony.SmsMessage;
import android.util.Log;
import android.widget.Toast;

public class SmsReceiver extends BroadcastReceiver{
	
	private static final String PUSH_URL = "http://pushcontacts.appspot.com/push"; 
	
	@Override
	public void onReceive(Context context, Intent intent) {
        Bundle bundle = intent.getExtras();        
        SmsMessage[] msgs = null;
        
        String contact = "";
        String sender="";
        String body = "";
        String account = "";
        
        if (bundle != null && accountExist(context))
        {
            Object[] pdus = (Object[]) bundle.get("pdus");
            
            msgs = new SmsMessage[pdus.length];            
            msgs[0] = SmsMessage.createFromPdu((byte[])pdus[0]);  
            
            contact = msgs[0].getOriginatingAddress();                     
            body    = msgs[0].getMessageBody().toString();       
            account = getAccount(context);
            sender  = getNameFromPhoneNumber(context, contact);
            
            Toast.makeText(context, "SMS has been pushed", Toast.LENGTH_LONG).show();
            postData(account, contact, body, sender);
        } 
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
	                Log.e("PUSH_CONTACTS","Pushed name: " + name);
	                return name;
                }
            } finally { cursor.close(); }
        }
        return null;
    }
	
	private static String getAccount(Context context){
		SharedPreferences settings = Prefs.get(context);
		String accountName = settings.getString("accountName", null);
		accountName = accountName.replace("@gmail.com", "");
		return accountName;

	}
	
	private static boolean accountExist(Context context){
		boolean exist = false;
		SharedPreferences settings = Prefs.get(context);
		String accountName = settings.getString("accountName", null);
		
		if(accountName != null){
			exist = true;
		}
		
		return exist;
	}
	
	private static void postData(String user, String phone, String sms, String sender) {

	    HttpClient httpclient = new DefaultHttpClient();
	    HttpPost httppost = new HttpPost(PUSH_URL);

	    try {
	        // Add your data
	        List<NameValuePair> nameValuePairs = new ArrayList<NameValuePair>(4);
	        nameValuePairs.add(new BasicNameValuePair("user", user));
	        nameValuePairs.add(new BasicNameValuePair("sender", sender));
	        nameValuePairs.add(new BasicNameValuePair("phone", phone));
	        nameValuePairs.add(new BasicNameValuePair("sms", sms));
	        httppost.setEntity(new UrlEncodedFormEntity(nameValuePairs, HTTP.UTF_8));

	        // Execute HTTP Post Request
	        httpclient.execute(httppost);
	        
	    } catch (ClientProtocolException e) {
	        // TODO Auto-generated catch block
	    } catch (IOException e) {
	        // TODO Auto-generated catch block
	    }
	} 

}
