package com.srikakulam.police.tracker;

import android.app.Activity;
import android.content.Context;
import android.content.Intent;
import android.media.Ringtone;
import android.media.RingtoneManager;
import android.net.Uri;
import android.os.Build;
import android.webkit.JavascriptInterface;
import android.widget.Toast;

import androidx.core.content.ContextCompat;

public class WebAppInterface {

    private final Context context;
    private static Ringtone alarmRingtone = null;

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
            String navDirUrl = "https://www.google.com/maps/dir/?api=1&destination=" + lat + "," + lng + "&travelmode=driving";

            // 1. Try Google Maps Turn-by-Turn Driving Navigation Intent
            try {
                Uri gmmIntentUri = Uri.parse("google.navigation:q=" + lat + "," + lng + "&mode=d");
                Intent mapIntent = new Intent(Intent.ACTION_VIEW, gmmIntentUri);
                mapIntent.setPackage("com.google.android.apps.maps");
                mapIntent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK);
                context.startActivity(mapIntent);
                return;
            } catch (Exception ignored) {}

            // 2. Try Google Maps App with Direct Driving Directions URL
            try {
                Intent dirIntent = new Intent(Intent.ACTION_VIEW, Uri.parse(navDirUrl));
                dirIntent.setPackage("com.google.android.apps.maps");
                dirIntent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK);
                context.startActivity(dirIntent);
                return;
            } catch (Exception ignored) {}

            // 3. Fallback: Any Maps App or Web Browser
            try {
                Intent browserIntent = new Intent(Intent.ACTION_VIEW, Uri.parse(navDirUrl));
                browserIntent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK);
                context.startActivity(browserIntent);
            } catch (Exception e) {
                Toast.makeText(context, "గూగుల్ మ్యాప్స్ తెరవలేకపోయాము", Toast.LENGTH_SHORT).show();
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

    @JavascriptInterface
    public void startAlarmSound() {
        if (context instanceof Activity) {
            ((Activity) context).runOnUiThread(() -> {
                try {
                    if (alarmRingtone != null && alarmRingtone.isPlaying()) {
                        return;
                    }
                    Uri alertUri = RingtoneManager.getDefaultUri(RingtoneManager.TYPE_ALARM);
                    if (alertUri == null) {
                        alertUri = RingtoneManager.getDefaultUri(RingtoneManager.TYPE_RINGTONE);
                    }
                    if (alertUri == null) {
                        alertUri = RingtoneManager.getDefaultUri(RingtoneManager.TYPE_NOTIFICATION);
                    }
                    if (alertUri != null) {
                        alarmRingtone = RingtoneManager.getRingtone(context, alertUri);
                        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.P && alarmRingtone != null) {
                            alarmRingtone.setLooping(true);
                        }
                        if (alarmRingtone != null) {
                            alarmRingtone.play();
                        }
                    }
                } catch (Exception e) {
                    e.printStackTrace();
                }
            });
        }
    }

    @JavascriptInterface
    public void stopAlarmSound() {
        if (context instanceof Activity) {
            ((Activity) context).runOnUiThread(() -> {
                try {
                    if (alarmRingtone != null) {
                        alarmRingtone.stop();
                        alarmRingtone = null;
                    }
                } catch (Exception e) {
                    e.printStackTrace();
                }
            });
        }
    }
}
