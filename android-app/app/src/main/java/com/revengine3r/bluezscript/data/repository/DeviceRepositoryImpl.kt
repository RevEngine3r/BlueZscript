package com.revengine3r.bluezscript.data.repository

import com.revengine3r.bluezscript.data.local.AppDatabase
import com.revengine3r.bluezscript.data.local.entity.PairedDeviceEntity
import com.revengine3r.bluezscript.data.models.PairedDevice
import com.revengine3r.bluezscript.data.models.PairingData
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.map
import javax.inject.Inject

/**
 * Implementation of DeviceRepository.
 */
class DeviceRepositoryImpl @Inject constructor(
    private val database: AppDatabase
) : DeviceRepository {
    
    private val dao = database.pairedDeviceDao()
    
    override fun getAllDevices(): Flow<List<PairedDevice>> {
        return dao.getAllDevices().map { entities ->
            entities.map { it.toDomain() }
        }
    }
    
    override suspend fun getDeviceById(id: String): PairedDevice? {
        return dao.getDeviceById(id)?.toDomain()
    }
    
    override suspend fun addDevice(
        pairingData: PairingData,
        deviceName: String
    ): Result<PairedDevice> {
        return try {
            val entity = PairedDeviceEntity(
                id = pairingData.deviceId,
                deviceName = deviceName,
                serverUrl = pairingData.serverUrl,
                secretKey = pairingData.secret,
                pairedAt = System.currentTimeMillis()
            )
            
            dao.insertDevice(entity)
            Result.success(entity.toDomain())
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
    
    override suspend fun removeDevice(deviceId: String): Result<Unit> {
        return try {
            dao.deleteDeviceById(deviceId)
            Result.success(Unit)
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
    
    override suspend fun updateLastUsed(deviceId: String) {
        dao.updateLastUsed(deviceId, System.currentTimeMillis())
    }
    
    override fun getDeviceCount(): Flow<Int> {
        return dao.getDeviceCount()
    }
    
    private fun PairedDeviceEntity.toDomain() = PairedDevice(
        id = id,
        deviceName = deviceName,
        serverUrl = serverUrl,
        secretKey = secretKey,
        pairedAt = pairedAt,
        lastUsed = lastUsed
    )
}
