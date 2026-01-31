package com.revengine3r.bluezscript.domain.usecases

import com.revengine3r.bluezscript.data.repository.DeviceRepository
import javax.inject.Inject

/**
 * Use case for removing a paired device.
 */
class RemoveDeviceUseCase @Inject constructor(
    private val deviceRepository: DeviceRepository
) {
    suspend operator fun invoke(deviceId: String): Result<Unit> {
        return deviceRepository.removeDevice(deviceId)
    }
}
