package com.revengine3r.bluezscript.domain.usecases

import com.revengine3r.bluezscript.data.models.PairingData
import com.revengine3r.bluezscript.data.repository.DeviceRepository
import javax.inject.Inject

/**
 * Use case for pairing a new device.
 */
class PairDeviceUseCase @Inject constructor(
    private val deviceRepository: DeviceRepository
) {
    suspend operator fun invoke(
        pairingData: PairingData,
        deviceName: String
    ): Result<Unit> {
        return try {
            deviceRepository.addDevice(pairingData, deviceName)
            Result.success(Unit)
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
}
