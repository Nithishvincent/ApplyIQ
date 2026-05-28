import axios from "axios";

/**
 * Sends a native push notification to a registered Expo push token.
 * 
 * @param expoPushToken The registered token (starts with ExponentPushToken)
 * @param title Notification title
 * @param body Notification body
 * @param data Optional custom JSON payload (e.g. { applicationId: "..." })
 */
export async function sendPushNotification(
  expoPushToken: string | null | undefined,
  title: string,
  body: string,
  data?: Record<string, unknown>
): Promise<void> {
  if (!expoPushToken) {
    console.warn("[Push] Missing push token, skipping notification.");
    return;
  }

  if (!expoPushToken.startsWith("ExponentPushToken")) {
    console.warn(`[Push] Invalid Expo push token prefix: ${expoPushToken}`);
    return;
  }

  try {
    const payload = {
      to: expoPushToken,
      sound: "default",
      title,
      body,
      data: data || {},
    };

    console.log(`[Push] Sending push notification to ${expoPushToken}...`);
    const response = await axios.post("https://exp.host/--/api/v2/push/send", payload, {
      headers: {
        "Accept": "application/json",
        "Accept-Encoding": "gzip, deflate",
        "Content-Type": "application/json",
      },
      timeout: 10000,
    });

    if (response.data?.errors) {
      console.error("[Push] Expo API returned errors:", response.data.errors);
    } else {
      console.log("[Push] Push notification sent successfully:", response.data);
    }
  } catch (error: any) {
    console.error("[Push] Failed to send push notification:", error.message || error);
  }
}
