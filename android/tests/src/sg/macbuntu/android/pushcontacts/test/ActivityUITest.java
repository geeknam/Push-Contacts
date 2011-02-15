package sg.macbuntu.android.pushcontacts.test;

import android.test.ActivityInstrumentationTestCase2;
import android.widget.ArrayAdapter;
import android.widget.Spinner;
import android.widget.SpinnerAdapter;
import android.widget.TextView;
import sg.macbuntu.android.pushcontacts.ActivityUI;

public class ActivityUITest extends ActivityInstrumentationTestCase2<ActivityUI> {

    private ActivityUI mActivity; 
    private TextView mStatusView; 
    private Spinner mAccountsSpinner;
    private String status;
    private SpinnerAdapter mAccountAdapter;
    
	public ActivityUITest() {
		super("sg.macbuntu.android.pushcontacts.ActivityUI", ActivityUI.class);
	}

    @Override
    protected void setUp() throws Exception {
        super.setUp();
        mActivity = this.getActivity();
        mStatusView = (TextView) mActivity.findViewById(sg.macbuntu.android.pushcontacts.R.id.status);
        mAccountsSpinner = (Spinner) mActivity.findViewById(sg.macbuntu.android.pushcontacts.R.id.accounts);
        
        mAccountAdapter = mAccountsSpinner.getAdapter();
    }
    
    public void testPreconditions() {	
        assertNotNull(mStatusView);
        assertNotNull(mAccountsSpinner);

        assertTrue(mAccountAdapter != null);
        assertEquals(mAccountAdapter.getCount(),1);
    }
    
    public void testStatusRegisteredText() {
    	status = mActivity.getString(sg.macbuntu.android.pushcontacts.R.string.status_registered);
        assertEquals(status,(String)mStatusView.getText());
    }
    
    public void testStatusNotRegisteredText() {
    	status = mActivity.getString(sg.macbuntu.android.pushcontacts.R.string.status_not_registered);
        assertEquals(status,(String)mStatusView.getText());
    }
}
