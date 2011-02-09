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

import com.google.android.c2dm.C2DMessaging;

import android.accounts.Account;
import android.accounts.AccountManager;
import android.app.Activity;
import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.Intent;
import android.content.IntentFilter;
import android.content.SharedPreferences;
import android.os.Bundle;
import android.preference.PreferenceManager;
import android.telephony.SmsMessage;
import android.view.Menu;
import android.view.MenuItem;
import android.view.View;
import android.view.View.OnClickListener;
import android.widget.ArrayAdapter;
import android.widget.Button;
import android.widget.Spinner;
import android.widget.TextView;
import android.widget.Toast;

/** 
 * Main screen - settings, registration, account selection. 
 */
public class ActivityUI extends Activity {
    public static final String UPDATE_UI_ACTION = "sg.macbuntu.android.pushcontacts.UPDATE_UI";
    public static final String AUTH_PERMISSION_ACTION = "sg.macbuntu.android.pushcontacts.AUTH_PERMISSION";
    static final private int PREFS = Menu.FIRST;

    private boolean mPendingAuth = false;
    private Context mContext = null;
    private TextView mTextView;

    @Override
    public void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        mContext = getApplicationContext();
        setContentView(R.layout.main);

        mTextView = (TextView) findViewById(R.id.status);

        Button registerButton = (Button) findViewById(R.id.register);
        registerButton.setOnClickListener(mRegisterButtonListener);

        Spinner accounts = (Spinner) findViewById(R.id.accounts);
        accounts.setAdapter(getGoogleAccounts(this));
        accounts.setPrompt(getString(R.string.accounts));

        registerReceiver(mUpdateUIReceiver, new IntentFilter(UPDATE_UI_ACTION));
        registerReceiver(mAuthPermissionReceiver, new IntentFilter(AUTH_PERMISSION_ACTION));
        //registerReceiver(SmsReceiver, new IntentFilter(SMS_RECEIVED));
        updateStatus();
    }

    @Override
    public void onDestroy() {
        unregisterReceiver(mUpdateUIReceiver);
        unregisterReceiver(mAuthPermissionReceiver);
        //unregisterReceiver(SmsReceiver);
        super.onDestroy();
    }

    private boolean updateStatus() {
        SharedPreferences prefs = Prefs.get(this);
        Button registerButton = (Button) findViewById(R.id.register);

        String deviceRegistrationID = prefs.getString("deviceRegistrationID", null);
        if (deviceRegistrationID == null) {
            mTextView.setText(R.string.status_not_registered);
            registerButton.setText(R.string.register);
            return false;
        } else {
            mTextView.setText(R.string.status_registered);
            registerButton.setText(R.string.unregister);
            return true;
        }
    }

    private ArrayAdapter<String> getGoogleAccounts(Context context) {
        ArrayAdapter<String> adapter =
                new ArrayAdapter<String>(context, android.R.layout.simple_spinner_item);
        adapter.setDropDownViewResource(android.R.layout.simple_spinner_dropdown_item);
        Account[] accounts = AccountManager.get(context).getAccounts();
        for (Account account : accounts) {
            if (account.type.equals("com.google")) {
                adapter.add(account.name);
            }
        }
        return adapter;
    }

    @Override
    protected void onResume() {
        super.onResume();
        if (mPendingAuth) {
            mPendingAuth = false;
            String regId = C2DMessaging.getRegistrationId(mContext);
            if (regId != null) {
                DeviceRegistrar.registerWithServer(mContext, regId);
            } else {
                C2DMessaging.register(mContext, DeviceRegistrar.SENDER_ID);
            }
            mTextView.setText(R.string.status_registering);
        }
    }

    private final OnClickListener mRegisterButtonListener = new OnClickListener() {
        public void onClick(View v) {
            SharedPreferences prefs = Prefs.get(mContext);
            String deviceRegistrationID = prefs.getString("deviceRegistrationID", null);

            if (deviceRegistrationID == null) {  // register
                Spinner accounts = (Spinner) findViewById(R.id.accounts);
                SharedPreferences settings = Prefs.get(mContext);
                SharedPreferences.Editor editor = settings.edit();
                editor.putString("accountName", (String) accounts.getSelectedItem());
                editor.commit();

                C2DMessaging.register(mContext, DeviceRegistrar.SENDER_ID);
                mTextView.setText(R.string.status_registering);
            } else {  // unregister
                C2DMessaging.unregister(mContext);
                mTextView.setText(R.string.status_unregistering);
            }
        }
    };

    private final BroadcastReceiver mUpdateUIReceiver = new BroadcastReceiver() {
        @Override
        public void onReceive(Context context, Intent intent) {
            updateStatus();
        }
    };

    private final BroadcastReceiver mAuthPermissionReceiver = new BroadcastReceiver() {
        @Override
        public void onReceive(Context context, Intent intent) {
            Bundle extras = intent.getBundleExtra("AccountManagerBundle");
            if (extras != null) {
                Intent authIntent = (Intent) extras.get(AccountManager.KEY_INTENT);
                if (authIntent != null) {
                    mPendingAuth = true;
                    startActivity(authIntent);
                }
            }
        }
    };
    
	@Override
	public boolean onCreateOptionsMenu(Menu menu) {
		super.onCreateOptionsMenu(menu);
		
		MenuItem pref = menu.add(0, PREFS, Menu.NONE,"Preferences");
		pref.setIcon(android.R.drawable.ic_menu_preferences);
		
		return true;
	}
	
	@Override
    public boolean onOptionsItemSelected(MenuItem item) {
		super.onOptionsItemSelected(item);
		switch (item.getItemId()) {
			case (PREFS):{
                Intent settingsActivity = new Intent(getBaseContext(),Preferences.class);
                startActivity(settingsActivity);
				break;
			}
		}
		return false;
    }
}
