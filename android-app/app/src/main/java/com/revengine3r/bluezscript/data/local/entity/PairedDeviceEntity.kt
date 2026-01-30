package com.revengine3r.bluezscript.data.local.entity

import androidx.room.ColumnInfo
import androidx.room.Entity
import androidx.room.PrimaryKey

/**
 * Database entity for a paired Raspberry Pi device.
 */
@Entity(tableName = "paired_devices")
data class PairedDeviceEntity(
    @PrimaryKey
    val id: String,
    
    @ColumnInfo(name = "device_name")
    val deviceName: String,
    
    @ColumnInfo(name = "server_url")
    val serverUrl: String,
    
    @ColumnInfo(name = "secret_key")
    val secretKey: String, // Encrypted by EncryptedSharedPreferences
    
    @ColumnInfo(name = "paired_at")
    val pairedAt: Long,
    
    @ColumnInfo(name = "last_used")
    val lastUsed: Long? = null
)
