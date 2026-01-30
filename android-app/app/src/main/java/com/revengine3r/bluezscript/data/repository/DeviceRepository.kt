package com.revengine3r.bluezscript.data.repository

import com.revengine3r.bluezscript.data.models.PairedDevice
import com.revengine3r.bluezscript.data.models.PairingData
import kotlinx.coroutines.flow.Flow

/**
 * Repository interface for device management.
 */
interface DeviceRepository {
    
    /**
     * Get all paired devices as a Flow.
     */
    fun getAllDevices(): Flow<List<PairedDevice>>
    
    /**
     * Get a specific device by ID.
     */
    suspend fun getDeviceById(id: String): PairedDevice?
    
    /**
     * Add a new paired device.
     */
    suspend fun addDevice(
        pairingData: PairingData,
        deviceName: String
    ): Result<PairedDevice>
    
    /**
     * Remove a paired device.
     */
    suspend fun removeDevice(deviceId: String): Result<Unit>
    
    /**
     * Update last used timestamp.
     */
    suspend fun updateLastUsed(deviceId: String)
    
    /**
     * Get device count.
     */
    fun getDeviceCount(): Flow<Int>
}
