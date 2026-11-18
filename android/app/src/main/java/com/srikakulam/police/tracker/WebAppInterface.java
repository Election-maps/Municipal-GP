package com.srikakulam.police.tracker;

import android.content.Context;
import android.content.Intent;
import android.net.Uri;
import android.os.Build;
import android.webkit.JavascriptInterface;

import androidx.core.content.ContextCompat;

public class WebAppInterface {

    private final Context context;

    public WebAppInterface(Context context) {
        this.context = context;
    }

    @JavascriptInterface
    public boolean isNativeApp() {
        return true;
    }

    @JavascriptInterface
    public boolean isTrackingRunning() {
        return LocationTrackingService.isRunning;
    }

    @JavascriptInterface
    public void startNativeTracking(String unitId, String category, String mandal, String unitName, String officer, String phone, String roomCode) {
        Intent intent = new Intent(context, LocationTrackingService.class);
        intent.setAction(LocationTrackingService.ACTION_START);
        intent.putExtra(LocationTrackingService.EXTRA_UNIT_ID, unitId);
        intent.putExtra(LocationTrackingService.EXTRA_CATEGORY, category);
        intent.putExtra(LocationTrackingService.EXTRA_MANDAL, mandal);
        intent.putExtra(LocationTrackingService.EXTRA_UNIT_NAME, unitName);
        intent.putExtra(LocationTrackingService.EXTRA_OFFICER, officer);
        intent.putExtra(LocationTrackingService.EXTRA_PHONE, phone);
        intent.putExtra(LocationTrackingService.EXTRA_ROOM, roomCode);

        ContextCompat.startForegroundService(context, intent);
    }

    @JavascriptInterface
    public void stopNativeTracking() {
        Intent intent = new Intent(context, LocationTrackingService.class);
        intent.setAction(LocationTrackingService.ACTION_STOP);
        context.startService(intent);
    }

    @JavascriptInterface
    public void makePhoneCall(String phoneNumber) {
        if (phoneNumber == null || phoneNumber.trim().isEmpty()) return;
        try {
            String clean = phoneNumber.replaceAll("[^0-9+]", "");
            if (clean.isEmpty()) return;
            Intent intent = new Intent(Intent.ACTION_DIAL, Uri.parse("tel:" + clean));
            intent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK);
            context.startActivity(intent);
        } catch (Exception e) {
            e.printStackTrace();
        }
    }

    @JavascriptInterface
    public void openNavigation(String url) {
        if (url == null || url.trim().isEmpty()) return;
        try {
            Intent intent = new Intent(Intent.ACTION_VIEW, Uri.parse(url));
            intent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK);
            context.startActivity(intent);
        } catch (Exception e) {
            e.printStackTrace();
        }
    }
}
