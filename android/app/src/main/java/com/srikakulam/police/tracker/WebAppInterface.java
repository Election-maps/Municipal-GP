package com.srikakulam.police.tracker;

import android.app.Activity;
import android.content.Context;
import android.content.Intent;
import android.net.Uri;
import android.os.Build;
import android.webkit.JavascriptInterface;
import android.widget.Toast;

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
        final String clean = phoneNumber.replaceAll("[^0-9+]", "");
        if (clean.isEmpty()) return;

        Runnable callAction = () -> {
            try {
                Intent intent = new Intent(Intent.ACTION_DIAL);
                intent.setData(Uri.parse("tel:" + clean));
                intent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK);
                context.startActivity(intent);
            } catch (Exception e) {
                Toast.makeText(context, "ఫోన్ డయలర్ ఓపెన్ కాలేదు: " + clean, Toast.LENGTH_SHORT).show();
            }
        };

        if (context instanceof Activity) {
            ((Activity) context).runOnUiThread(callAction);
        } else {
            callAction.run();
        }
    }

    @JavascriptInterface
    public void openMapsNavigation(double lat, double lng, String label) {
        Runnable navAction = () -> {
            // 1. Try Google Maps App Intent
            try {
                Uri gmmIntentUri = Uri.parse("google.navigation:q=" + lat + "," + lng);
                Intent mapIntent = new Intent(Intent.ACTION_VIEW, gmmIntentUri);
                mapIntent.setPackage("com.google.android.apps.maps");
                mapIntent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK);
                context.startActivity(mapIntent);
                return;
            } catch (Exception ignored) {}

            // 2. Try geo: intent
            try {
                String safeLabel = (label != null && !label.isEmpty()) ? label : "Police SOS Location";
                Uri geoUri = Uri.parse("geo:" + lat + "," + lng + "?q=" + lat + "," + lng + "(" + Uri.encode(safeLabel) + ")");
                Intent geoIntent = new Intent(Intent.ACTION_VIEW, geoUri);
                geoIntent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK);
                context.startActivity(geoIntent);
                return;
            } catch (Exception ignored) {}

            // 3. Fallback to external browser with Google Maps URL
            try {
                String webUrl = "https://www.google.com/maps/dir/?api=1&destination=" + lat + "," + lng;
                Intent browserIntent = new Intent(Intent.ACTION_VIEW, Uri.parse(webUrl));
                browserIntent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK);
                context.startActivity(browserIntent);
            } catch (Exception e) {
                Toast.makeText(context, "మ్యాప్స్ ఓపెన్ కాలేదు", Toast.LENGTH_SHORT).show();
            }
        };

        if (context instanceof Activity) {
            ((Activity) context).runOnUiThread(navAction);
        } else {
            navAction.run();
        }
    }

    @JavascriptInterface
    public void openExternalUrl(String url) {
        if (url == null || url.trim().isEmpty()) return;
        Runnable openAction = () -> {
            try {
                Intent intent = new Intent(Intent.ACTION_VIEW, Uri.parse(url));
                intent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK);
                context.startActivity(intent);
            } catch (Exception e) {
                Toast.makeText(context, "లింక్ తెరవలేకపోయాము", Toast.LENGTH_SHORT).show();
            }
        };

        if (context instanceof Activity) {
            ((Activity) context).runOnUiThread(openAction);
        } else {
            openAction.run();
        }
    }

    @JavascriptInterface
    public void openNavigation(String url) {
        openExternalUrl(url);
    }
}
