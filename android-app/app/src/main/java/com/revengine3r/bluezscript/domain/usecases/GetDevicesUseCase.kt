package com.revengine3r.bluezscript.domain.usecases

import com.revengine3r.bluezscript.data.models.PairedDevice
import com.revengine3r.bluezscript.data.repository.DeviceRepository
import kotlinx.coroutines.flow.Flow
import javax.inject.Inject

/**
 * Use case for getting all paired devices.
 */
class GetDevicesUseCase @Inject constructor(
    private val deviceRepository: DeviceRepository
) {
    operator fun invoke(): Flow<List<PairedDevice>> {
        return deviceRepository.getAllDevices()
    }
}
