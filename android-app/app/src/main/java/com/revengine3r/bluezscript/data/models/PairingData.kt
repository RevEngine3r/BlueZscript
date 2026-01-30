package com.revengine3r.bluezscript.data.models

import kotlinx.serialization.SerialName
import kotlinx.serialization.Serializable

/**
 * Data class representing pairing information from QR code.
 */
@Serializable
data class PairingData(
    @SerialName("device_id")
    val deviceId: String,
    
    @SerialName("secret")
    val secret: String,
    
    @SerialName("server_url")
    val serverUrl: String
)
