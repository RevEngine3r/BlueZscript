package com.revengine3r.bluezscript.data.models

import kotlinx.serialization.SerialName
import kotlinx.serialization.Serializable

/**
 * BLE message sent to Raspberry Pi.
 */
@Serializable
data class BleMessage(
    @SerialName("device_id")
    val deviceId: String,
    
    @SerialName("totp")
    val totp: String,
    
    @SerialName("timestamp")
    val timestamp: Long,
    
    @SerialName("action")
    val action: String
)
