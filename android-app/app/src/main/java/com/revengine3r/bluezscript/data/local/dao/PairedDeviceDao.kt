package com.revengine3r.bluezscript.data.local.dao

import androidx.room.*
import com.revengine3r.bluezscript.data.local.entity.PairedDeviceEntity
import kotlinx.coroutines.flow.Flow

/**
 * Data Access Object for paired devices.
 */
@Dao
interface PairedDeviceDao {
    
    @Query("SELECT * FROM paired_devices ORDER BY paired_at DESC")
    fun getAllDevices(): Flow<List<PairedDeviceEntity>>
    
    @Query("SELECT * FROM paired_devices WHERE id = :id")
    suspend fun getDeviceById(id: String): PairedDeviceEntity?
    
    @Query("SELECT * FROM paired_devices WHERE server_url = :serverUrl")
    suspend fun getDeviceByServerUrl(serverUrl: String): PairedDeviceEntity?
    
    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertDevice(device: PairedDeviceEntity)
    
    @Update
    suspend fun updateDevice(device: PairedDeviceEntity)
    
    @Delete
    suspend fun deleteDevice(device: PairedDeviceEntity)
    
    @Query("DELETE FROM paired_devices WHERE id = :id")
    suspend fun deleteDeviceById(id: String)
    
    @Query("UPDATE paired_devices SET last_used = :timestamp WHERE id = :id")
    suspend fun updateLastUsed(id: String, timestamp: Long)
    
    @Query("SELECT COUNT(*) FROM paired_devices")
    fun getDeviceCount(): Flow<Int>
}
