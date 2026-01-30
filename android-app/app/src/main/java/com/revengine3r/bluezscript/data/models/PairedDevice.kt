package com.revengine3r.bluezscript.data.models

/**
 * Domain model for a paired device.
 */
data class PairedDevice(
    val id: String,
    val deviceName: String,
    val serverUrl: String,
    val secretKey: String,
    val pairedAt: Long,
    val lastUsed: Long? = null
)
